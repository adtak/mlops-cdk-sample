.PHONY: up-container build-container run-container rm-container

up-container: build-container run-container

build-container:
				docker build \
				-f dev.Dockerfile \
				-t mlops-cdk-sample \
				.

run-container:
				docker run \
				--name mlops-cdk-sample \
				-itd \
				-v $(PWD):/usr/src/app \
				mlops-cdk-sample:latest

rm-container:
				docker rm \
				-f \
				mlops-cdk-sample