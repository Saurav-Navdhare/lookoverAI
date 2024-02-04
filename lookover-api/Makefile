# Define variables
IMAGE_NAME := lookover-api
CONTAINER_NAME := lookover-api

# Build the Docker image
build:
    docker build -t $(IMAGE_NAME) .

# Run the Docker container
run:
    docker run -d -p 5001:5001 --rm --name $(CONTAINER_NAME) $(IMAGE_NAME)

# Stop the Docker container
stop:
    docker stop $(CONTAINER_NAME)

# Clean up unused Docker images and containers
clean:
    docker system prune -a --force
