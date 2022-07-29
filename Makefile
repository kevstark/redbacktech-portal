IMAGE=redbacktech-portal
CONTAINER=redbacktech-stats

build:
	docker build -t $(IMAGE) .

kill:
	-docker kill $(CONTAINER)
	-docker rm $(CONTAINER)

run: build kill
	docker run -d -v "${PWD}/prod:/app/env" --name $(CONTAINER) --restart unless-stopped $(IMAGE)
