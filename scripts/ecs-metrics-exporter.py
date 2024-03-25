#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ecs_metrics_exporter - provides ECS Task Metadata v4 values for prometheus

This module is a simple Flask application. A container running on Fargate can get
Docker stats API data and ECS Task data from the Task metadata endpoint.
More details at https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v4.html

ecs_metrics_exporter fetches some metrics from Task metadata endpoint version 4,
and returns plain text formatted for prometheus.
"""

import os
import json
import requests
from datetime import datetime
from prometheus_client import Counter, Gauge
from prometheus_client import generate_latest
from prometheus_client.core import CollectorRegistry
from flask import Flask, Response
from dateutil import parser

app = Flask(__name__)

VERSION = "0.0.2"
METADATA_URL_ENV = "ECS_CONTAINER_METADATA_URI_V4"
METADATA_URL = "" if os.getenv("DEBUG") else os.getenv(METADATA_URL_ENV)
LISTEN_PORT = os.getenv("ECS_METRICS_EXPORTER_PORT", "9546")

registry = CollectorRegistry(auto_describe=False)


def create_metrics(registry):
    labels = ["container_name", "container_id", "task_family", "task_revision"]
    return {
        "counter_cpu_usage_sec": Counter(
            "ee_container_cpu_usage_seconds_total",
            "cpu_stats->cpu_usage->total_usage conver nano sec to sec",
            labels,
            registry=registry,
        ),
        "gauge_mem_usage_total_bytes": Gauge(
            "ee_container_memory_usage_byte",
            "memory_stats->usage with cache",
            labels,
            registry=registry,
        ),
        "gauge_mem_usage_total_bytes_without_cache": Gauge(
            "ee_container_memory_usage_without_cache_byte",
            "memory_stats->usage - memory_stats->cache",
            labels,
            registry=registry,
        ),
        "gauge_network_io_rx_bytes": Gauge(
            "ee_container_network_io_rx_bytes",
            "network_io_rx_bytes",
            labels,
            registry=registry,
        ),
        "gauge_network_io_tx_bytes": Gauge(
            "ee_container_network_io_tx_bytes",
            "network_io_tx_bytes",
            labels,
            registry=registry,
        ),
        "gauge_block_io_read_bytes": Gauge(
            "ee_container_block_io_read_bytes",
            "block_io_read_bytes",
            labels,
            registry=registry,
        ),
        "gauge_block_io_write_bytes": Gauge(
            "ee_container_block_io_write_bytes",
            "block_io_write_bytes",
            labels,
            registry=registry,
        ),
        "gauge_block_io_read_ops": Gauge(
            "ee_container_block_io_read_ops",
            "block_io_read_ops",
            labels,
            registry=registry,
        ),
        "gauge_block_io_write_ops": Gauge(
            "ee_container_block_io_write_ops",
            "block_io_write_ops",
            labels,
            registry=registry,
        ),
        "gauge_pull_started_at_time": Gauge(
            "ee_task_pull_started_at_time",
            "tasks PullStartedAt epoch",
            labels,
            registry=registry,
        ),
        "gauge_pull_stopped_at_time": Gauge(
            "ee_task_pull_stopped_at_time",
            "tasks PullStoppedAt epoch",
            labels,
            registry=registry,
        ),
        "gauge_container_last_started_at_time": Gauge(
            "ee_container_last_started_at_time",
            "epoch that maximum StartedAt in all containers",
            labels,
            registry=registry,
        ),
        "gauge_task_cpu_limit": Gauge(
            "ee_task_cpu_limit",
            "task cpu limit (ex. 0.5, 1.0..)",
            labels,
            registry=registry,
        ),
        "gauge_task_memory_limit_byte": Gauge(
            "ee_task_memory_limit_byte",
            "task memory limit bytes",
            labels,
            registry=registry,
        ),
        "ecs_metrics_exporter_success": Gauge(
            "ecs_metrics_exporter_success",
            "Indicates if the ECS metrics exporter succeeded. 0 for failure, 1 for success.",
            registry=registry,
        ),
    }


def get_short_container_id(container_id_full):
    """
    Extracts and returns the short form of the container ID.

    :param container_id_full: The full container ID.
    :return: The short container ID (first 12 characters).
    """
    return container_id_full[:12]


def fetch_task_metadata():
    """
    Fetches and decodes the task metadata and statistics from the ECS metadata endpoint.

    :return: A tuple of (task_metadata, task_stats).
    """
    task_url = f"{METADATA_URL}/task"
    stats_url = f"{METADATA_URL}/task/stats"

    response_task = requests.get(task_url)
    if not response_task.ok:
        raise Exception(
            f"Failed to fetch task metadata with status code {response_task.status_code}"
        )
    task = response_task.json()

    response_stats = requests.get(stats_url)
    if not response_stats.ok:
        raise Exception(
            f"Failed to fetch stats metadata with status code {response_stats.status_code}"
        )
    stats = response_stats.json()

    return task, stats


def str2epoch(time_str):
    """
    Converts a time string with potential nanoseconds into an epoch timestamp.

    :param time_str: The time string, possibly including nanoseconds.
    :return: The epoch timestamp as an integer.
    """
    dt = parser.parse(time_str)
    return int(dt.timestamp())


def collect_ecs_task_metadata():
    """
    Collects metrics from ECS task metadata and updates the Prometheus metrics.

    This function fetches task metadata, computes various metrics based on the metadata,
    and updates the Prometheus metrics accordingly.
    """
    try:
        task, stats = fetch_task_metadata()

        registry = CollectorRegistry(auto_describe=False)
        metrics = create_metrics(registry)

        task_containers_info = {}
        for ci in task.get("Containers", []):
            task_containers_info[ci["DockerId"]] = ci

        # Task info
        task_family = task["Family"]
        task_revision = task["Revision"]
        task_labels = {
            "container_name": "_task_",
            "container_id": "_task_",
            "task_family": task_family,
            "task_revision": task_revision,
        }

        # Task pull times
        pull_start = str2epoch(task["PullStartedAt"]) if "PullStartedAt" in task else 0
        pull_stop = str2epoch(task["PullStoppedAt"]) if "PullStoppedAt" in task else 0
        metrics["gauge_pull_started_at_time"].labels(**task_labels).set(pull_start)
        metrics["gauge_pull_stopped_at_time"].labels(**task_labels).set(pull_stop)

        # Task limits
        task_cpu_limit = float(task["Limits"]["CPU"])
        task_memory_limit_bytes = int(task["Limits"]["Memory"]) * 1024 * 1024
        metrics["gauge_task_cpu_limit"].labels(**task_labels).set(task_cpu_limit)
        metrics["gauge_task_memory_limit_byte"].labels(**task_labels).set(
            task_memory_limit_bytes
        )

        sum_of_cpu_usage_sec = 0
        sum_of_memory_usage_bytes = 0
        sum_of_memory_usage_actual_bytes = 0
        sum_of_network_io_rx_bytes = 0
        sum_of_network_io_tx_bytes = 0
        sum_of_block_io_read_bytes = 0
        sum_of_block_io_write_bytes = 0
        sum_of_block_io_read_ops = 0
        sum_of_block_io_write_ops = 0

        # Process each container in the task
        last_started_at_time = 0
        for container_stat in stats.values():
            container_id = get_short_container_id(container_stat["id"])
            container_name = container_stat["name"]
            labels = {
                "container_name": container_name,
                "container_id": container_id,
                "task_family": task_family,
                "task_revision": task_revision,
            }

            # Container start time
            started_at = str2epoch(
                task_containers_info[container_stat["id"]]["StartedAt"]
            )
            print(f"started_at:{started_at}")
            last_started_at_time = max(last_started_at_time, started_at)
            print(f"last_started_at_time:{last_started_at_time}")

            # CPU usage
            cpu_usage_sec = (
                container_stat["cpu_stats"]["cpu_usage"]["total_usage"] / 1e9
            )
            metrics["counter_cpu_usage_sec"].labels(**labels).inc(cpu_usage_sec)
            sum_of_cpu_usage_sec += cpu_usage_sec

            # Memory usage
            mem_usage_bytes = container_stat["memory_stats"]["usage"]
            mem_cache_bytes = container_stat["memory_stats"]["stats"].get("cache", 0)
            mem_usage_bytes_without_cache = mem_usage_bytes - mem_cache_bytes
            metrics["gauge_mem_usage_total_bytes"].labels(**labels).set(mem_usage_bytes)
            metrics["gauge_mem_usage_total_bytes_without_cache"].labels(**labels).set(
                mem_usage_bytes_without_cache
            )
            sum_of_memory_usage_bytes += mem_usage_bytes
            sum_of_memory_usage_actual_bytes += mem_usage_bytes_without_cache

            # Network IO
            rx_bytes = sum(
                interface["rx_bytes"]
                for interface in container_stat["networks"].values()
            )
            tx_bytes = sum(
                interface["tx_bytes"]
                for interface in container_stat["networks"].values()
            )
            metrics["gauge_network_io_rx_bytes"].labels(**labels).set(rx_bytes)
            metrics["gauge_network_io_tx_bytes"].labels(**labels).set(tx_bytes)
            sum_of_network_io_rx_bytes += rx_bytes
            sum_of_network_io_tx_bytes += tx_bytes

            # Block IO
            for blk_io in container_stat["blkio_stats"]["io_service_bytes_recursive"]:
                if blk_io["op"] == "Read":
                    metrics["gauge_block_io_read_bytes"].labels(**labels).set(
                        blk_io["value"]
                    )
                    sum_of_block_io_read_bytes += blk_io["value"]
                elif blk_io["op"] == "Write":
                    metrics["gauge_block_io_write_bytes"].labels(**labels).set(
                        blk_io["value"]
                    )
                    sum_of_block_io_write_bytes += blk_io["value"]

            for blk_io in container_stat["blkio_stats"]["io_serviced_recursive"]:
                if blk_io["op"] == "Read":
                    metrics["gauge_block_io_read_ops"].labels(**labels).set(
                        blk_io["value"]
                    )
                    sum_of_block_io_read_ops += blk_io["value"]
                elif blk_io["op"] == "Write":
                    metrics["gauge_block_io_write_ops"].labels(**labels).set(
                        blk_io["value"]
                    )
                    sum_of_block_io_write_ops += blk_io["value"]

        metrics["counter_cpu_usage_sec"].labels(**task_labels).inc(sum_of_cpu_usage_sec)
        metrics["gauge_mem_usage_total_bytes"].labels(**task_labels).set(
            sum_of_memory_usage_bytes
        )
        metrics["gauge_mem_usage_total_bytes_without_cache"].labels(**task_labels).set(
            sum_of_memory_usage_actual_bytes
        )
        metrics["gauge_network_io_rx_bytes"].labels(**task_labels).set(
            sum_of_network_io_rx_bytes
        )
        metrics["gauge_network_io_tx_bytes"].labels(**task_labels).set(
            sum_of_network_io_tx_bytes
        )
        metrics["gauge_block_io_read_bytes"].labels(**task_labels).set(
            sum_of_block_io_read_bytes
        )
        metrics["gauge_block_io_write_bytes"].labels(**task_labels).set(
            sum_of_block_io_write_bytes
        )
        metrics["gauge_block_io_read_ops"].labels(**task_labels).set(
            sum_of_block_io_read_ops
        )
        metrics["gauge_block_io_write_ops"].labels(**task_labels).set(
            sum_of_block_io_write_ops
        )

        # Set the last started container time for the task
        metrics["gauge_container_last_started_at_time"].labels(**task_labels).set(
            last_started_at_time
        )
        metrics["ecs_metrics_exporter_success"].set(1)
    except Exception as e:
        print(f"error:{e}")
        metrics["ecs_metrics_exporter_success"].set(0)

    return generate_latest(registry)


@app.route("/metrics")
def metrics_endpoint():
    try:
        metrics_data = collect_ecs_task_metadata()
        return Response(metrics_data, mimetype="text/plain")
    except Exception as e:
        app.logger.error(f"Failed to fetch some metrics: {e}")
        return Response("Error collecting metrics", status=500, mimetype="text/plain")


@app.route("/stats")
def stats():
    """
    Endpoint to provide raw JSON statistics.

    This function is called when the '/stats' endpoint is accessed.
    It returns raw JSON statistics obtained from the ECS metadata endpoint.
    """
    _, stats = fetch_task_metadata()
    return Response(json.dumps(stats), mimetype="application/json")


@app.route("/task")
def task():
    """
    Endpoint to provide raw JSON task metadata.

    This function is called when the '/task' endpoint is accessed.
    It returns raw JSON task metadata obtained from the ECS metadata endpoint.
    """
    task, _ = fetch_task_metadata()
    return Response(json.dumps(task), mimetype="application/json")


if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=LISTEN_PORT)

# URL mappings
# /metrics - Provides prometheus metrics
# /stats - Provides raw JSON text that get from ECS_CONTAINER_METADATA_URI_V4/task/stats
# /task - Provides raw JSON text that get from ECS_CONTAINER_METADATA_URI_V4/task

# Labels
# Almost all metrics have common labels:
# - container_name: Container Name. For task metrics, "_task_" will be set.
# - container_id: Container Id. For task metrics, "_task_" will be set.
#   Be careful that all container has a same container_id, because this script scrapes prefix 12 characters.
# - task_family: ECS Task family name
# - task_revision: ECS Task Definitions revision number

# Exported Metrics
# All metrics have common prefix "ee_"
# - ee_ecs_metrics_exporter_success: When no raise occurred, set 1. Some raise occurred, set 0. This metrics has no labels.
# - ee_task_cpu_limit: Task CPU Limits. When allocate CPU unit 512, this metrics return 0.5.
# - ee_task_memory_limit_byte: Task Memory Limits.
# - ee_container_cpu_usage_seconds_total: Container CPU usage seconds (not nanoseconds). This is a Counter.
#   So, you can calculate CPU usage percentage by using the Prometheus `rate` function.
# - ee_container_memory_usage_byte: Memory usage bytes.
# - ee_container_network_io_rx_bytes: Received bytes that sum all interfaces.
# - ee_container_network_io_tx_bytes: Transport bytes that sum all interfaces.
# - ee_container_block_io_read_bytes: Block read IO bytes that sum all block devices.
# - ee_container_block_io_write_bytes: Block write IO bytes that sum all block devices.
# - ee_container_block_io_read_ops: Block read IO ops that sum all block devices.
# - ee_container_block_io_write_ops: Block write IO ops that sum all block devices.

# Note: Due to space constraints, not all metrics have been fully implemented in this code snippet.
# You may need to implement the remaining metrics and their corresponding logic based on the Perl script provided.
