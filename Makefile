APP := app
PROJECT := pss

# AWS settings
ECR_REPOSITORY := 292181225895.dkr.ecr.us-east-1.amazonaws.com

# Git settings
GIT_HASH := $(shell git rev-parse --short HEAD)

# Published image URI
IMAGE_URI := ${ECR_REPOSITORY}/${PROJECT}:${GIT_HASH}

network:
	@docker network create ${PROJECT}-dev || true

image:
	@docker compose build ${APP}

release_image:
	@docker tag ${PROJECT}:latest ${IMAGE_URI}
	@docker push ${IMAGE_URI}
	
pull_image:
	@docker pull ${IMAGE_URI}

shell:
	@docker compose exec ${APP} /bin/bash

dbshell:
	@docker compose exec ${APP} bash -c "python3 manage.py dbshell"

repl:
	@docker compose exec ${APP} bash -c "python3 manage.py shell_plus -- -i scripts/repl.py"

migrate_db:
	@docker compose run --rm ${APP} bash -c "python3 manage.py migrate"

check_migrations:
	@docker compose run --rm ${APP} bash -c "python3 manage.py makemigrations --check"

test:
	@docker compose run --rm ${APP} bash -c "python3 manage.py test --parallel"

fmt:
	@docker compose run --rm ${APP} bash -c "black ."

check_fmt:
	@docker compose run --rm ${APP} bash -c "black --check ."

lint:
	@docker compose run --rm ${APP} bash -c "ruff ."

isort:
	@docker compose run --rm ${APP} bash -c "isort ."

ci_check_standards:
	@ruff .
	@black --check .

ci_test:
	@docker run --env-file docker/env.ci \
		--add-host host.docker.internal:host-gateway \
		--rm ${IMAGE_URI} bash -c 'python3 manage.py test --parallel --failfast --keepdb'
