IMAGE_NAME := coat-fastapi-poc
CONTAINER_NAME := coat-fastapi-poc
AWS_PROFILE := modernisation-platform-sandbox

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run --rm \
		-p 3000:3000 \
		-v ~/.aws:/home/appuser/.aws:ro \
		-e AWS_PROFILE=$(AWS_PROFILE) \
		-e APP_ENV=development \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

stop:
	-docker stop $(CONTAINER_NAME)

shell:
	docker exec -it $(CONTAINER_NAME) /bin/sh

health:
	curl http://localhost:3000/health