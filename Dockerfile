FROM python:3.12-slim

RUN apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY ./scripts/ecs-metrics-exporter.py /scripts/ecs-metrics-exporter.py

EXPOSE 9546

CMD ["python", "/scripts/ecs-metrics-exporter.py"]
