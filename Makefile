APP := app
PROJECT := aprecisioncompany
ECR_REPOSITORY := 121854965079.dkr.ecr.us-east-1.amazonaws.com
GIT_HASH := dev #FIXME: configure git hash

network:
	@docker network create ${PROJECT}-dev || true

image:
	@docker compose build ${APP}

release: ecr_login
	@docker tag ${PROJECT}-${APP} ${ECR_REPOSITORY}/${PROJECT}:${GIT_HASH} 
	@docker push ${ECR_REPOSITORY}/${PROJECT}:${GIT_HASH}

ecr_login:
	@aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ECR_REPOSITORY}

shell:
	@docker compose exec ${APP} /bin/bash

dbshell:
	@docker compose exec ${APP} bash -c "python3 manage.py dbshell"

repl:
	@docker compose exec ${APP} bash -c "python3 manage.py shell_plus -- -i scripts/repl.py"

migrate_db:
	@docker compose exec ${APP} bash -c "python3 manage.py migrate"

check_migrations:
	@docker compose exec ${APP} bash -c "python3 manage.py makemigrations --check"

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
