image_name=ecs-metrics-exporter
tag=0.0.3

build:;
	docker build -t $(image_name):$(tag) -t $(image_name):latest .

test:;
	docker run -it --rm -v $(shell pwd)/tests:/tests -v $(shell pwd)/t:/t $(image_name):$(tag) python -m tests.test_metrics

