FROM ubuntu:22.04

WORKDIR /code
SHELL ["/bin/bash", "--login", "-c"]

# Configure the system environment
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1

# Install the system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  curl \
  libgdal-dev \
  libpango-1.0-0 \
  libpangoft2-1.0-0 \
  libpq-dev \
  postgresql-client \
  python3-dev \
  python3-gi \
  python3-pip

# Install the Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY requirements.dev.txt .
RUN pip3 install -r requirements.dev.txt

# Copy the application code
COPY . .

# Collect Django's static files
RUN python3 manage.py collectstatic --no-input

# Configure the application server
CMD ["gunicorn", "--config", "gunicorn.conf.py"]
