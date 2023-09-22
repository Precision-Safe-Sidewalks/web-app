APP := app
PROJECT := pss

# AWS settings
ECR_REGISTRY_URL := 292181225895.dkr.ecr.us-east-1.amazonaws.com

# Git settings
GIT_HASH := $(shell git rev-parse --short HEAD)

# Published image URI
APP_IMAGE_URI := ${ECR_REGISTRY_URL}/${PROJECT}:${GIT_HASH}
GEO_IMAGE_URI := ${ECR_REGISTRY_URL}/${PROJECT}-lambda-geocoding:${GIT_HASH}
PRI_IMAGE_URI := ${ECR_REGISTRY_URL}/${PROJECT}-lambda-pricing-sheet:${GIT_HASH}

network:
	@docker network create ${PROJECT}-dev || true

images: image_app image_geocoding image_pricing_sheet

image_app:
	@docker build -t ${PROJECT}:latest -f docker/Dockerfile.app .
	
image_geocoding:
	@docker build -t ${PROJECT}-lambda-geocoding:latest -f docker/Dockerfile.lambda.geocoding .

image_pricing_sheet:
	@docker build -t ${PROJECT}-lambda-pricing-sheet:latest -f docker/Dockerfile.lambda.pricing_sheet .

release_images:
	@docker tag ${PROJECT}:latest ${APP_IMAGE_URI}
	@docker tag ${PROJECT}-lambda-geocoding:latest ${GEO_IMAGE_URI}
	@docker tag ${PROJECT}-lambda-pricing_sheet:latest ${PRI_iMAGE_URI}
	@docker push ${APP_IMAGE_URI}
	@docker push ${GEO_IMAGE_URI}
	@docker push ${PRI_IMAGE_URI}
	
pull_image:
	@docker pull ${APP_IMAGE_URI}

shell:
	@docker compose exec ${APP} /bin/bash

dbshell:
	@docker compose exec ${APP} bash -c "python3 manage.py dbshell"

repl:
	@docker compose exec ${APP} bash -c "python3 manage.py shell_plus -- -i scripts/repl.py"

migrate_db:
	@docker compose run --rm ${APP} bash -c "python3 manage.py migrate"

check_migrations:
	@docker compose run --rm ${APP} bash -c "scripts/check_migrations.sh"

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
		--rm ${APP_IMAGE_URI} bash -c 'scripts/check_migrations.sh'

ci_test:
	@docker run --env-file docker/env.ci \
		--add-host host.docker.internal:host-gateway \
		--rm ${APP_IMAGE_URI} bash -c 'python3 manage.py test --parallel --failfast --keepdb'

ci_run_migrations:
	@docker run \
		-e DJANGO_SETTINGS_MODULE=app.settings.development \
		-e DJANGO_SECRET_KEY=fake \
		-e DB_HOST=${DB_HOST} \
		-e DB_USER=${DB_USER} \
		-e DB_PASSWORD=${DB_PASSWORD} \
		-e DB_NAME=${DB_NAME} \
		--rm ${APP_IMAGE_URI} bash -c 'python3 manage.py migrate'
