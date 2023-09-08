APP := app
PROJECT := pss
ECR_REPOSITORY := 292181225895.dkr.ecr.us-east-1.amazonaws.com
GIT_HASH := $(shell git rev-parse --short HEAD)

network:
	@docker network create ${PROJECT}-dev || true

image:
	@docker compose build ${APP}

release_image:
	@docker tag ${PROJECT}:latest ${ECR_REPOSITORY}/${PROJECT}:${GIT_HASH} 
	@docker push ${ECR_REPOSITORY}/${PROJECT}:${GIT_HASH}

ecr_login:
	@aws --profile pss ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ECR_REPOSITORY}

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
