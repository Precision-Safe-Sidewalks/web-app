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
	@docker compose run --rm ${APP} bash -c "python3 manage.py test"

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

ci_check_migrations:
	@docker run --env-file docker/env.ci \
		--volume ${PWD}:/code \
		--add-host host.docker.internal:host-gateway \
		--rm ${IMAGE_URI} bash -c 'scripts/check_migrations.sh'

ci_test:
	@docker run --env-file docker/env.ci \
		--add-host host.docker.internal:host-gateway \
		--rm ${IMAGE_URI} bash -c 'python3 manage.py test --parallel --failfast --keepdb'

ci_run_migrations:
	@docker run \
		-e DJANGO_SETTINGS_MODULE=app.settings.development \
		-e DJANGO_SECRET_KEY=fake \
		-e DB_HOST=${DB_HOST} \
		-e DB_USER=${DB_USER} \
		-e DB_PASSWORD=${DB_PASSWORD} \
		-e DB_NAME=${DB_NAME} \
		--rm ${IMAGE_URI} bash -c 'python3 manage.py migrate'
