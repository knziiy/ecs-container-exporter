# ECS Metrics Exporter

ECS Metrics Exporter is a simple Flask application designed to fetch and expose ECS Task Metadata v4 and Docker stats for Prometheus monitoring. This tool is particularly useful for containers running on AWS Fargate, where traditional monitoring agents may not have full access to the underlying host.

## Features

- Fetches ECS Task Metadata v4 and Docker statistics.
- Exposes metrics in a format compatible with Prometheus.
- Easy to deploy as a sidecar container within ECS tasks.

## Getting Started

### Prerequisites

- Access to ECS Task Metadata v4 endpoint from the running container.
- The container must be running on AWS ECS, ideally on Fargate, to access the Task Metadata endpoint and Docker stats.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/knziiy/ecs-metrics-exporter.git
   ```

2. Navigate to the cloned directory:
   ```bash
   cd ecs-metrics-exporter
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Exporter

1. Set the ECS Container Metadata URI environment variable (if not running on ECS):
   ```bash
   export ECS_CONTAINER_METADATA_URI_V4="http://localhost:51678/v4/"
   ```

2. Run the exporter:
   ```bash
   python scripts/ecs-metrics-exporter.py
   ```

The metrics will be available at `http://localhost:9546/metrics`.

## Docker Deployment

You can also deploy the ECS Metrics Exporter as a Docker container. A `Dockerfile` is included in the repository.

1. Build the Docker image:
   ```bash
   docker build -t ecs-metrics-exporter .
   ```

2. Run the container:
   ```bash
   docker run -p 9546:9546 ecs-metrics-exporter
   ```

3. Or, use make
   ```bash
   make build
   ```

## Tests

1. Build Docker image with make
   ```bash
   make build
   ```

2. Run tests
   ```bash
   make test
   ```

## Configuration

You can configure the ECS Metrics Exporter using environment variables:

- `ECS_METRICS_EXPORTER_PORT`: The port on which the exporter will listen. Defaults to `9546`.

## URL Mappings and Exported Metrics

### URL Mappings

- `/metrics` - Provides Prometheus metrics.
- `/stats` - Provides raw JSON text that get from `ECS_CONTAINER_METADATA_URI_V4/task/stats`.
- `/task` - Provides raw JSON text that get from `ECS_CONTAINER_METADATA_URI_V4/task`.

### Labels

Almost all metrics have common labels:

- `container_name`: Container Name. For task metrics, `_task_` will be set.
- `container_id`: Container Id. For task metrics, `_task_` will be set. Be careful that all containers have the same container_id, because this script scrapes the first 12 characters.
- `task_family`: ECS Task family name.
- `task_revision`: ECS Task Definitions revision number.

### Exported Metrics

All metrics have a common prefix "ee_":

- `ee_ecs_metrics_exporter_success`: Indicates if the ECS metrics exporter succeeded. `0` for failure, `1` for success. This metric has no labels.
- `ee_task_cpu_limit`: Task CPU Limits. When allocating CPU unit 512, this metric returns `0.5`.
- `ee_task_memory_limit_byte`: Task Memory Limits.
- `ee_container_cpu_usage_seconds_total`: Container CPU usage seconds (not nanoseconds). This is a Counter. You can calculate CPU usage percentage by using the Prometheus `rate` function. rate(ee_container_cpu_usage_seconds_total{container_name="name"}[1m]) * 100
  
  Be careful to consider <CPU Limits>. A query provides actual CPU usage percentage is following.

  When set only Task CPU Limits.
  
    rate(ee_container_cpu_usage_seconds_total{container_name="name"}[1m])
    / ignoring(instance) ee_task_cpu_limit * 100

  When set Container CPU Limits. <NOT SUPPORTED>.
  
    For keep it simple, ecs-expoter not consider container CPU Limits.
  
  Task metadata endpoint is refreshed per 10 seconds. So you should set scrape interval larger than 10 seconds.
- `ee_container_memory_usage_byte`: Memory usage in bytes. Represents the total current memory usage by the container, including all caches.
- `ee_container_network_io_rx_bytes`: Total number of bytes received across all network interfaces by the container. Useful for monitoring incoming network traffic.
- `ee_container_network_io_tx_bytes`: Total number of bytes transmitted across all network interfaces by the container. Useful for monitoring outgoing network traffic.
- `ee_container_block_io_read_bytes`: Total number of bytes read from all block devices by the container. Helps in understanding the read I/O pressure caused by the container.
- `ee_container_block_io_write_bytes`: Total number of bytes written to all block devices by the container. Helps in understanding the write I/O pressure caused by the container.
- `ee_container_block_io_read_ops`: Total number of read operations performed on all block devices by the container. This metric complements the byte-oriented read metric by providing insight into the read operation count.
- `ee_container_block_io_write_ops`: Total number of write operations performed on all block devices by the container. This metric complements the byte-oriented write metric by providing insight into the write operation count.

Each of these metrics provides valuable insights into the resource usage and performance characteristics of containers running within ECS tasks, particularly useful for optimization and troubleshooting in production environments.

### Metrics Samples

```
# HELP ee_container_cpu_usage_seconds_total cpu_stats->cpu_usage->total_usage conver nano sec to sec
# TYPE ee_container_cpu_usage_seconds_total counter
ee_container_cpu_usage_seconds_total{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 1.406409934
ee_container_cpu_usage_seconds_total{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 9.159904948
ee_container_cpu_usage_seconds_total{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 567.550708048
ee_container_cpu_usage_seconds_total{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 591.5673553490001
# HELP ee_container_cpu_usage_seconds_created cpu_stats->cpu_usage->total_usage conver nano sec to sec
# TYPE ee_container_cpu_usage_seconds_created gauge
ee_container_cpu_usage_seconds_created{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 1.7113501830088637e+09
ee_container_cpu_usage_seconds_created{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 1.7113501830122013e+09
ee_container_cpu_usage_seconds_created{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 1.7113501830129654e+09
ee_container_cpu_usage_seconds_created{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1.7113501830134087e+09
# HELP ee_container_memory_usage_byte memory_stats->usage with cache
# TYPE ee_container_memory_usage_byte gauge
ee_container_memory_usage_byte{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 2.930688e+07
ee_container_memory_usage_byte{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 4.3556864e+07
ee_container_memory_usage_byte{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 4.56159232e+08
ee_container_memory_usage_byte{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 7.7365248e+08
# HELP ee_container_memory_usage_without_cache_byte memory_stats->usage - memory_stats->cache
# TYPE ee_container_memory_usage_without_cache_byte gauge
ee_container_memory_usage_without_cache_byte{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 2.1331968e+07
ee_container_memory_usage_without_cache_byte{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 3.233792e+07
ee_container_memory_usage_without_cache_byte{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 2.37187072e+08
ee_container_memory_usage_without_cache_byte{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 4.78445568e+08
# HELP ee_container_network_io_rx_bytes network_io_rx_bytes
# TYPE ee_container_network_io_rx_bytes gauge
ee_container_network_io_rx_bytes{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 8.14543607e+08
ee_container_network_io_rx_bytes{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 8.14541574e+08
ee_container_network_io_rx_bytes{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 8.14543561e+08
ee_container_network_io_rx_bytes{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 8.145441927e+09
# HELP ee_container_network_io_tx_bytes network_io_tx_bytes
# TYPE ee_container_network_io_tx_bytes gauge
ee_container_network_io_tx_bytes{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 1.8872594e+07
ee_container_network_io_tx_bytes{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 1.8859034e+07
ee_container_network_io_tx_bytes{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 1.8872066e+07
ee_container_network_io_tx_bytes{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1.88790253e+08
# HELP ee_container_block_io_read_bytes block_io_read_bytes
# TYPE ee_container_block_io_read_bytes gauge
ee_container_block_io_read_bytes{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 8.27392e+06
ee_container_block_io_read_bytes{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 1.2189696e+07
ee_container_block_io_read_bytes{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 7.19163392e+08
ee_container_block_io_read_bytes{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 9.11847424e+08
# HELP ee_container_block_io_write_bytes block_io_write_bytes
# TYPE ee_container_block_io_write_bytes gauge
ee_container_block_io_write_bytes{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 0.0
ee_container_block_io_write_bytes{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 0.0
ee_container_block_io_write_bytes{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 3.065856e+07
ee_container_block_io_write_bytes{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 3.0666752e+07
# HELP ee_container_block_io_read_ops block_io_read_ops
# TYPE ee_container_block_io_read_ops gauge
ee_container_block_io_read_ops{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 140.0
ee_container_block_io_read_ops{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 313.0
ee_container_block_io_read_ops{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 16487.0
ee_container_block_io_read_ops{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 19264.0
# HELP ee_container_block_io_write_ops block_io_write_ops
# TYPE ee_container_block_io_write_ops gauge
ee_container_block_io_write_ops{container_id="6677f4b57434",container_name="nginx",task_family="ecs-task-sample",task_revision="10"} 0.0
ee_container_block_io_write_ops{container_id="6677f4b57434",container_name="ecsExporter",task_family="ecs-task-sample",task_revision="10"} 0.0
ee_container_block_io_write_ops{container_id="6677f4b57434",container_name="app",task_family="ecs-task-sample",task_revision="10"} 1563.0
ee_container_block_io_write_ops{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1565.0
# HELP ee_task_pull_started_at_time tasks PullStartedAt epoch
# TYPE ee_task_pull_started_at_time gauge
ee_task_pull_started_at_time{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1.711347219e+09
# HELP ee_task_pull_stopped_at_time tasks PullStoppedAt epoch
# TYPE ee_task_pull_stopped_at_time gauge
ee_task_pull_stopped_at_time{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1.711347258e+09
# HELP ee_container_last_started_at_time epoch that maximum StartedAt in all containers
# TYPE ee_container_last_started_at_time gauge
ee_container_last_started_at_time{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1.711350183e+09
# HELP ee_task_cpu_limit task cpu limit (ex. 0.5, 1.0..)
# TYPE ee_task_cpu_limit gauge
ee_task_cpu_limit{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 0.25
# HELP ee_task_memory_limit_byte task memory limit bytes
# TYPE ee_task_memory_limit_byte gauge
ee_task_memory_limit_byte{container_id="_task_",container_name="_task_",task_family="ecs-task-sample",task_revision="10"} 1.073741824e+09
# HELP ecs_metrics_exporter_success Indicates if the ECS metrics exporter succeeded. 0 for failure, 1 for success.
# TYPE ecs_metrics_exporter_success gauge
ecs_metrics_exporter_success 1.0
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
