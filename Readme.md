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
- `ee_container_cpu_usage_seconds_total`: Container CPU usage seconds (not nanoseconds). This is a Counter. You can calculate CPU usage percentage by using the Prometheus `rate` function.
- `ee_container_memory_usage_byte`: Memory usage in bytes. Represents the total current memory usage by the container, including all caches.
- `ee_container_network_io_rx_bytes`: Total number of bytes received across all network interfaces by the container. Useful for monitoring incoming network traffic.
- `ee_container_network_io_tx_bytes`: Total number of bytes transmitted across all network interfaces by the container. Useful for monitoring outgoing network traffic.
- `ee_container_block_io_read_bytes`: Total number of bytes read from all block devices by the container. Helps in understanding the read I/O pressure caused by the container.
- `ee_container_block_io_write_bytes`: Total number of bytes written to all block devices by the container. Helps in understanding the write I/O pressure caused by the container.
- `ee_container_block_io_read_ops`: Total number of read operations performed on all block devices by the container. This metric complements the byte-oriented read metric by providing insight into the read operation count.
- `ee_container_block_io_write_ops`: Total number of write operations performed on all block devices by the container. This metric complements the byte-oriented write metric by providing insight into the write operation count.

Each of these metrics provides valuable insights into the resource usage and performance characteristics of containers running within ECS tasks, particularly useful for optimization and troubleshooting in production environments.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
