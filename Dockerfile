FROM python:3.10

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev build-essential musl-dev

# Upgrade pip and install required packages
RUN python -m ensurepip
RUN pip install --no-cache --upgrade pip setuptools
RUN pip install cython
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Add execute permissions to the entrypoint script
RUN chmod +x /usr/src/app/docker-entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]
