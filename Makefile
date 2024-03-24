image_name=ecs-metrics-exporter
tag=0.0.1

build:;
	docker build -t $(image_name):$(tag) -t $(image_name):latest .

