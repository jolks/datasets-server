# environment variables for the commands (docker-compose, poetry)
export PORT_ADMIN := 9081
export PORT_API := 9080
export PORT_REVERSE_PROXY := 9000
export TEST_MONGO_PORT := 27050
export TEST_ROWS_MAX_NUMBER := 4
export TEST_COMPOSE_PROJECT_NAME := e2e
export TEST_HF_ENDPOINT := https://hub-ci.huggingface.co
export TEST_HF_TOKEN := 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
# makefile variables
TEST_DOCKER_COMPOSE := ../tools/docker-compose-datasets-server-from-remote-images.yml
DOCKER_IMAGES := ../chart/docker-images.yaml

include ../tools/Python.mk
include ../tools/DockerRemoteImages.mk
include ../tools/Docker.mk

.PHONY: e2e
e2e:
	make test

.PHONY: openapi
openapi:
	poetry run python -m openapi_spec_validator ../chart/static-files/openapi.json
