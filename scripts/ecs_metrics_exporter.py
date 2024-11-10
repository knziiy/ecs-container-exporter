#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ecs_metrics_exporter - provides ECS Task Metadata v4 values for prometheus

This module is a simple FastAPI application. A container running on Fargate can get
Docker stats API data and ECS Task data from the Task metadata endpoint.
More details at https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v4.html

ecs_metrics_exporter fetches some metrics from Task metadata endpoint version 4,
and returns plain text formatted for prometheus.
"""

import os
import json
import requests
import uvicorn
import logging
from datetime import datetime
from prometheus_client import Counter, Gauge
from prometheus_client import generate_latest
from prometheus_client.core import CollectorRegistry
from fastapi import FastAPI, Response
from dateutil import parser
from starlette.responses import PlainTextResponse, JSONResponse

VERSION = "0.1.1"
METADATA_URL_ENV = "ECS_CONTAINER_METADATA_URI_V4"
LISTEN_PORT = os.getenv("ECS_METRICS_EXPORTER_PORT", "9546")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

registry = CollectorRegistry(auto_describe=False)


def create_metrics(registry):
    """
    Creates and returns a dictionary of Prometheus metrics for ECS containers and tasks.

    Args:
        registry: The Prometheus registry to which the metrics will be registered.

    Returns:
        dict: A dictionary containing Prometheus Counter and Gauge metrics with the following keys:
            - "counter_cpu_usage_sec": Counter for total CPU usage in seconds.
            - "gauge_mem_usage_total_bytes": Gauge for total memory usage in bytes (including cache).
            - "gauge_mem_usage_total_bytes_without_cache": Gauge for memory usage in bytes (excluding cache).
            - "gauge_network_io_rx_bytes": Gauge for network I/O received bytes.
            - "gauge_network_io_tx_bytes": Gauge for network I/O transmitted bytes.
            - "gauge_block_io_read_bytes": Gauge for block I/O read bytes.
            - "gauge_block_io_write_bytes": Gauge for block I/O write bytes.
            - "gauge_block_io_read_ops": Gauge for block I/O read operations.
            - "gauge_block_io_write_ops": Gauge for block I/O write operations.
            - "gauge_pull_started_at_time": Gauge for task pull start time in epoch.
            - "gauge_pull_stopped_at_time": Gauge for task pull stop time in epoch.
            - "gauge_container_last_started_at_time": Gauge for the last container start time in epoch.
            - "gauge_task_cpu_limit": Gauge for task CPU limit.
            - "gauge_task_memory_limit_byte": Gauge for task memory limit in bytes.
            - "ecs_metrics_exporter_success": Gauge indicating if the ECS metrics exporter succeeded (0 for failure, 1 for success).
    """
    
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
    METADATA_URL = os.getenv(METADATA_URL_ENV)
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
    registry = CollectorRegistry(auto_describe=False)
    metrics = create_metrics(registry)

    try:
        task, stats = fetch_task_metadata()

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
            last_started_at_time = max(last_started_at_time, started_at)

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
        logger.error(f"Failed to fetch some metrics: {e}")
        metrics["ecs_metrics_exporter_success"].set(0)

    return generate_latest(registry)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics_endpoint():
    metrics_data = collect_ecs_task_metadata()
    return Response(content=metrics_data, media_type="text/plain")


@app.get("/stats", response_class=JSONResponse)
def stats():
    """
    Endpoint to provide raw JSON statistics.

    This function is called when the '/stats' endpoint is accessed.
    It returns raw JSON statistics obtained from the ECS metadata endpoint.
    """
    _, stats = fetch_task_metadata()
    return JSONResponse(content=stats)


@app.get("/task", response_class=JSONResponse)
def task():
    """
    Endpoint to provide raw JSON task metadata.

    This function is called when the '/task' endpoint is accessed.
    It returns raw JSON task metadata obtained from the ECS metadata endpoint.
    """
    task, _ = fetch_task_metadata()
    return JSONResponse(content=task)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(LISTEN_PORT), reload=False)