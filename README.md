### Getting started
This application is containerized using Docker and orchestrated locally using Docker Compose. This includes the web application and PostgreSQL database.
- Instructions to install [Docker Engine](https://docs.docker.com/engine/install/)
- Instructions to install [Docker Compose](https://docs.docker.com/compose/install/)

This application uses Microsoft Active Directory to authenticate and manage users. In order to use the application, the following environment variables must be set in the `docker/env.secrets` file. Please note that these values are **secret** and are not committed to the repository. If they are exposed, they should be rotated immediately. The values may be retrieved and managed from the Azure developer portal.
- `MICROSOFT_AUTH_TENANT_ID`
- `MICROSOFT_AUTH_CLIENT_ID`
- `MICROSOFT_AUTH_CLIENT_SECRET`

With Docker installed and Microsoft Active Directory configured, use the following commands to get up and running:
- `make image` to build the Docker image
- `docker compose up` to start the development server and initialize the database if it doesn't exist
  * This may take ~10s to start the web server because it depends on the database
  * If the server fails to start because of a bad database connection, restart `docker compose up`
- `make migrate_db` to run any database migrations
- The web server should be available at `http://localhost:8000`

### Development commands
To make development easier, the following `make` commands are available:
- `make image` to build the Docker image
- `make shell` to access the container (Ubuntu) shell
- `make dbshell` to access a PostgreSQL shell
- `make repl` to access a Python shell
- `make check_migrations` to check if any migrations are missing
- `make migrate_db` to run the database migrations
- `make test` to run the unit tests
- `make fmt` to automatically reformat according to the code standards
- `make check_fmt` to check the code formatting standards
- `make lint` to lint the application (check syntax and code standards)
- `make isort` to automatically sort the import statements
