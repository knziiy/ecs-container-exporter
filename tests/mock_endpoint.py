"""
Mock endpoints for testing ECS metrics exporter.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

test_json = {
    "stats": {
        "49e756135b1849cf98cd6a12c78bc6ea-1059602171": {
            "read": "2021-01-02T03:04:35.883623666Z",
            "preread": "2021-01-02T03:04:25.883788203Z",
            "pids_stats": {},
            "blkio_stats": {
                "io_service_bytes_recursive": [
                    {"major": 254, "minor": 160, "op": "Read", "value": 100},
                    {"major": 254, "minor": 160, "op": "Write", "value": 200},
                    {"major": 254, "minor": 160, "op": "Sync", "value": 300},
                    {"major": 254, "minor": 160, "op": "Async", "value": 400},
                    {"major": 254, "minor": 160, "op": "Total", "value": 1000},
                    {"major": 254, "minor": 128, "op": "Read", "value": 1},
                    {"major": 254, "minor": 128, "op": "Write", "value": 2},
                    {"major": 254, "minor": 128, "op": "Sync", "value": 3},
                    {"major": 254, "minor": 128, "op": "Async", "value": 4},
                    {"major": 254, "minor": 128, "op": "Total", "value": 10},
                ],
                "io_serviced_recursive": [
                    {"major": 254, "minor": 160, "op": "Read", "value": 100},
                    {"major": 254, "minor": 160, "op": "Write", "value": 200},
                    {"major": 254, "minor": 160, "op": "Sync", "value": 300},
                    {"major": 254, "minor": 160, "op": "Async", "value": 400},
                    {"major": 254, "minor": 160, "op": "Total", "value": 1000},
                    {"major": 254, "minor": 128, "op": "Read", "value": 1},
                    {"major": 254, "minor": 128, "op": "Write", "value": 2},
                    {"major": 254, "minor": 128, "op": "Sync", "value": 3},
                    {"major": 254, "minor": 128, "op": "Async", "value": 4},
                    {"major": 254, "minor": 128, "op": "Total", "value": 10},
                ],
                "io_queue_recursive": [],
                "io_service_time_recursive": [],
                "io_wait_time_recursive": [],
                "io_merged_recursive": [],
                "io_time_recursive": [],
                "sectors_recursive": [],
            },
            "num_procs": 0,
            "storage_stats": {},
            "cpu_stats": {
                "cpu_usage": {
                    "total_usage": 1234567890,
                    "percpu_usage": [1238771746, 914806657],
                    "usage_in_kernelmode": 580000000,
                    "usage_in_usermode": 1170000000,
                },
                "system_cpu_usage": 26860260000000,
                "online_cpus": 2,
                "throttling_data": {
                    "periods": 0,
                    "throttled_periods": 0,
                    "throttled_time": 0,
                },
            },
            "precpu_stats": {
                "cpu_usage": {
                    "total_usage": 9876543210,
                    "percpu_usage": [1238510014, 914403980],
                    "usage_in_kernelmode": 580000000,
                    "usage_in_usermode": 1170000000,
                },
                "system_cpu_usage": 26853170000000,
                "online_cpus": 2,
                "throttling_data": {
                    "periods": 0,
                    "throttled_periods": 0,
                    "throttled_time": 0,
                },
            },
            "memory_stats": {
                "usage": 30000000,
                "max_usage": 22126592,
                "stats": {
                    "active_anon": 4104192,
                    "active_file": 122880,
                    "cache": 10000000,
                    "dirty": 0,
                    "hierarchical_memory_limit": 1073741824,
                    "hierarchical_memsw_limit": 9223372036854772000,
                    "inactive_anon": 0,
                    "inactive_file": 16744448,
                    "mapped_file": 10678272,
                    "pgfault": 6831,
                    "pgmajfault": 66,
                    "pgpgin": 8349,
                    "pgpgout": 3236,
                    "rss": 8269824,
                    "rss_huge": 0,
                    "total_active_anon": 4104192,
                    "total_active_file": 122880,
                    "total_cache": 12570624,
                    "total_dirty": 0,
                    "total_inactive_anon": 0,
                    "total_inactive_file": 16744448,
                    "total_mapped_file": 10678272,
                    "total_pgfault": 6831,
                    "total_pgmajfault": 66,
                    "total_pgpgin": 8349,
                    "total_pgpgout": 3236,
                    "total_rss": 8269824,
                    "total_rss_huge": 0,
                    "total_unevictable": 0,
                    "total_writeback": 0,
                    "unevictable": 0,
                    "writeback": 0,
                },
                "limit": 9223372036854772000,
            },
            "name": "containerA",
            "id": "49e756135b1849cf98cd6a12c78bc6ea-1059602171",
            "networks": {
                "eth1.7": {
                    "rx_bytes": 100,
                    "rx_packets": 200,
                    "rx_errors": 300,
                    "rx_dropped": 400,
                    "tx_bytes": 500,
                    "tx_packets": 600,
                    "tx_errors": 700,
                    "tx_dropped": 800,
                }
            },
            "network_rate_stats": {
                "rx_bytes_per_sec": 2359.7388271426616,
                "tx_bytes_per_sec": 16623.17351769706,
            },
        },
        "49e756135b1849cf98cd6a12c78bc6ea-2485339635": {
            "read": "2021-01-02T03:04:38.594139343Z",
            "preread": "2021-01-02T03:04:28.593406898Z",
            "pids_stats": {},
            "blkio_stats": {
                "io_service_bytes_recursive": [
                    {"major": 254, "minor": 160, "op": "Read", "value": 0},
                    {"major": 254, "minor": 160, "op": "Write", "value": 0},
                    {"major": 254, "minor": 160, "op": "Sync", "value": 0},
                    {"major": 254, "minor": 160, "op": "Async", "value": 0},
                    {"major": 254, "minor": 160, "op": "Total", "value": 0},
                    {"major": 254, "minor": 16, "op": "Read", "value": 0},
                    {"major": 254, "minor": 16, "op": "Write", "value": 0},
                    {"major": 254, "minor": 16, "op": "Sync", "value": 0},
                    {"major": 254, "minor": 16, "op": "Async", "value": 0},
                    {"major": 254, "minor": 16, "op": "Total", "value": 0},
                ],
                "io_serviced_recursive": [
                    {"major": 254, "minor": 160, "op": "Read", "value": 0},
                    {"major": 254, "minor": 160, "op": "Write", "value": 0},
                    {"major": 254, "minor": 160, "op": "Sync", "value": 0},
                    {"major": 254, "minor": 160, "op": "Async", "value": 0},
                    {"major": 254, "minor": 160, "op": "Total", "value": 0},
                    {"major": 254, "minor": 16, "op": "Read", "value": 0},
                    {"major": 254, "minor": 16, "op": "Write", "value": 0},
                    {"major": 254, "minor": 16, "op": "Sync", "value": 0},
                    {"major": 254, "minor": 16, "op": "Async", "value": 0},
                    {"major": 254, "minor": 16, "op": "Total", "value": 0},
                ],
                "io_queue_recursive": [],
                "io_service_time_recursive": [],
                "io_wait_time_recursive": [],
                "io_merged_recursive": [],
                "io_time_recursive": [],
                "sectors_recursive": [],
            },
            "num_procs": 0,
            "storage_stats": {},
            "cpu_stats": {
                "cpu_usage": {
                    "total_usage": 0,
                    "percpu_usage": [2086053505, 1901064345],
                    "usage_in_kernelmode": 730000000,
                    "usage_in_usermode": 3090000000,
                },
                "system_cpu_usage": 26860260000000,
                "online_cpus": 2,
                "throttling_data": {
                    "periods": 0,
                    "throttled_periods": 0,
                    "throttled_time": 0,
                },
            },
            "precpu_stats": {
                "cpu_usage": {
                    "total_usage": 0,
                    "percpu_usage": [2084819021, 1901028034],
                    "usage_in_kernelmode": 730000000,
                    "usage_in_usermode": 3090000000,
                },
                "system_cpu_usage": 26853170000000,
                "online_cpus": 2,
                "throttling_data": {
                    "periods": 0,
                    "throttled_periods": 0,
                    "throttled_time": 0,
                },
            },
            "memory_stats": {
                "usage": 0,
                "max_usage": 32034816,
                "stats": {
                    "active_anon": 0,
                    "active_file": 0,
                    "cache": 0,
                    "dirty": 0,
                    "hierarchical_memory_limit": 0,
                    "hierarchical_memsw_limit": 0,
                    "inactive_anon": 0,
                    "inactive_file": 0,
                    "mapped_file": 0,
                    "pgfault": 0,
                    "pgmajfault": 0,
                    "pgpgin": 0,
                    "pgpgout": 0,
                    "rss": 0,
                    "rss_huge": 0,
                    "total_active_anon": 0,
                    "total_active_file": 0,
                    "total_cache": 0,
                    "total_dirty": 0,
                    "total_inactive_anon": 0,
                    "total_inactive_file": 0,
                    "total_mapped_file": 0,
                    "total_pgfault": 0,
                    "total_pgmajfault": 0,
                    "total_pgpgin": 0,
                    "total_pgpgout": 0,
                    "total_rss": 0,
                    "total_rss_huge": 0,
                    "total_unevictable": 0,
                    "total_writeback": 0,
                    "unevictable": 0,
                    "writeback": 0,
                },
                "limit": 0,
            },
            "name": "containerB",
            "id": "49e756135b1849cf98cd6a12c78bc6ea-2485339635",
            "networks": {
                "eth1.7": {
                    "rx_bytes": 0,
                    "rx_packets": 0,
                    "rx_errors": 0,
                    "rx_dropped": 0,
                    "tx_bytes": 0,
                    "tx_packets": 0,
                    "tx_errors": 0,
                    "tx_dropped": 0,
                }
            },
            "network_rate_stats": {
                "rx_bytes_per_sec": 0.0,
                "tx_bytes_per_sec": 0.0,
            },
        },
    },
    "task": {
        "Cluster": (
            "arn:aws:ecs:ap-northeast-1:123456789012:cluster/"
            "cluster-name-test"
        ),
        "TaskARN": (
            "arn:aws:ecs:ap-northeast-1:123456789012:task/"
            "cluster-name-test/49e756135b1849cf98cd6a12c78bc6ea"
        ),
        "Family": "taskdef-name-test",
        "Revision": "123",
        "DesiredStatus": "RUNNING",
        "KnownStatus": "RUNNING",
        "Limits": {"CPU": 0.5, "Memory": 1024},
        "PullStartedAt": "1970-01-01T00:00:10.000000000Z",
        "PullStoppedAt": "1970-01-01T00:00:20.000000000Z",
        "AvailabilityZone": "ap-northeast-1a",
        "Containers": [
            {
                "DockerId": "49e756135b1849cf98cd6a12c78bc6ea-1059602171",
                "Name": "containerA",
                "DockerName": "containerA",
                "Image": (
                    "123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/"
                    "image-name-test:1.0"
                ),
                "ImageID": (
                    "sha256:"
                    "7fd55a3ecafd3b5fe7b77ee9e548df0134c3ccf397a8e211ab59c19d8bed6246"
                ),
                "Labels": {
                    "com.amazonaws.ecs.cluster": (
                        "arn:aws:ecs:ap-northeast-1:123456789012:"
                        "cluster/cluster-name-test"
                    ),
                    "com.amazonaws.ecs.container-name": "containerA",
                    "com.amazonaws.ecs.task-arn": (
                        "arn:aws:ecs:ap-northeast-1:123456789012:task/"
                        "cluster-name-test/49e756135b1849cf98cd6a12c78bc6ea"
                    ),
                    "com.amazonaws.ecs.task-definition-family": (
                        "taskdef-name-test"
                    ),
                    "com.amazonaws.ecs.task-definition-version": "123",
                },
                "DesiredStatus": "RUNNING",
                "KnownStatus": "RUNNING",
                "Limits": {"CPU": 2},
                "CreatedAt": "1970-01-01T00:00:30.000000000Z",
                "StartedAt": "1970-01-01T00:00:40.000000000Z",
                "Type": "NORMAL",
                "Volumes": [
                    {
                        "DockerName": "taskdef-name-test-509-logoutputvol",
                        "Destination": "/var/bar",
                    },
                    {
                        "DockerName": "taskdef-name-test-509-grokconfvol",
                        "Destination": "/foo",
                    },
                ],
                "Networks": [
                    {
                        "NetworkMode": "awsvpc",
                        "IPv4Addresses": ["172.20.1.2"],
                        "AttachmentIndex": 0,
                        "MACAddress": "06:0b:1a:ac:ba:c1",
                        "IPv4SubnetCIDRBlock": "172.20.1.0/23",
                        "DomainNameServers": ["172.20.0.2"],
                        "PrivateDNSName": (
                            "ip-172-20-1-2.ap-northeast-1.compute.internal"
                        ),
                        "SubnetGatewayIpv4Address": "172.20.1.1/23",
                    }
                ],
                "ContainerARN": (
                    "arn:aws:ecs:ap-northeast-1:123456789012:container/"
                    "cluster-name-test/49e756135b1849cf98cd6a12c78bc6ea/"
                    "14a55dac-fb57-46ef-b665-a1970797f35f"
                ),
                "LogOptions": {
                    "awslogs-group": "loggroupnametest",
                    "awslogs-region": "ap-northeast-1",
                    "awslogs-stream": (
                        "containerA/containerA/"
                        "49e756135b1849cf98cd6a12c78bc6ea"
                    ),
                },
                "LogDriver": "awslogs",
            },
            {
                "DockerId": "49e756135b1849cf98cd6a12c78bc6ea-2485339635",
                "Name": "containerB",
                "DockerName": "containerB",
                "Image": (
                    "123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/"
                    "image-name-containerB:1.00-01"
                ),
                "ImageID": (
                    "sha256:"
                    "3f1330724f81041dbec36aaea568982280e8804bd02b5ff51203944cf07a853f"
                ),
                "Labels": {
                    "com.amazonaws.ecs.cluster": (
                        "arn:aws:ecs:ap-northeast-1:123456789012:"
                        "cluster/cluster-name-test"
                    ),
                    "com.amazonaws.ecs.container-name": "containerB",
                    "com.amazonaws.ecs.task-arn": (
                        "arn:aws:ecs:ap-northeast-1:123456789012:task/"
                        "cluster-name-test/49e756135b1849cf98cd6a12c78bc6ea"
                    ),
                    "com.amazonaws.ecs.task-definition-family": (
                        "taskdef-name-test"
                    ),
                    "com.amazonaws.ecs.task-definition-version": "123",
                },
                "DesiredStatus": "RUNNING",
                "KnownStatus": "RUNNING",
                "Limits": {"CPU": 2},
                "CreatedAt": "2021-01-02T23:59:28.583606691Z",
                "StartedAt": "2021-01-02T23:59:28.583606691Z",
                "Type": "NORMAL",
                "Networks": [
                    {
                        "NetworkMode": "awsvpc",
                        "IPv4Addresses": ["172.20.1.2"],
                        "AttachmentIndex": 0,
                        "MACAddress": "06:0b:1a:ac:ba:c1",
                        "IPv4SubnetCIDRBlock": "172.20.1.0/23",
                        "DomainNameServers": ["172.20.0.2"],
                        "PrivateDNSName": (
                            "ip-172-20-50-87.ap-northeast-1.compute.internal"
                        ),
                        "SubnetGatewayIpv4Address": "172.20.1.1/23",
                    }
                ],
                "ContainerARN": (
                    "arn:aws:ecs:ap-northeast-1:123456789012:container/"
                    "cluster-name-test/49e756135b1849cf98cd6a12c78bc6ea/"
                    "93cb605a-155b-4dd3-afa7-f6ea191e6942"
                ),
                "LogOptions": {
                    "awslogs-group": "loggroupnametest",
                    "awslogs-region": "ap-northeast-1",
                    "awslogs-stream": (
                        "containerB/containerB/"
                        "49e756135b1849cf98cd6a12c78bc6ea"
                    ),
                },
                "LogDriver": "awslogs",
            },
        ],
        "LaunchType": "FARGATE",
    },
}


@app.get("/task")
async def task():
    """
    Endpoint to provide mock task metadata.
    """
    return JSONResponse(content=test_json["task"])


@app.get("/task/stats")
async def task_stats():
    """
    Endpoint to provide mock task statistics.
    """
    return JSONResponse(content=test_json["stats"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
