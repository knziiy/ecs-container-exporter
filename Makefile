image_name=ecs-metrics-exporter
tag=0.1.2

build:;
	docker build -t $(image_name):$(tag) -t $(image_name):latest .

test:;
	docker run -it --rm \
	  -v $(shell pwd)/tests:/tests \
	  -v $(shell pwd)/scripts:/scripts \
	  $(image_name):$(tag) pytest tests -v

