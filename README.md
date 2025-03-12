# Downloading and Running the Docker Container

## Prerequisites

Ensure you have Docker and Docker Compose installed on your system.

## Downloading the Latest Docker Image

To pull the latest Docker image, follow these steps:

1. Set up your Google Cloud authentication:

   ```sh
   export GCP_AUTH=<your-auth-token>
   ```

2. Authenticate with Docker:

   ```sh
   echo $GCP_AUTH | docker login europe-west3-docker.pkg.dev/sereact/sereact-agravis  -u _json_key_base64 --password-stdin
   ```

3. Pull the Docker image from the repository:

   ```sh
   docker pull europe-west3-docker.pkg.dev/sereact/sereact-agravis/agravis_interface:v0.0.1
   ```

4. Tag the image for easier reference:

   ```sh
   docker tag europe-west3-docker.pkg.dev/sereact/sereact-agravis/agravis_interface:v0.0.1 agravis_interface
   ```

## Running the Docker Container

To run the container, use the provided `docker-compose.yml` file and configure the following parameters:

- **SEREACT_PORT=8000** → The local port for the Sereact interface
- **agravis_URL=http://localhost:8001** → The URL/URI for the agravis system

Start the container with:

```sh
docker-compose up -d
```

You can log the running container with:

```sh
docker logs agravis-interface-agravis_interface-1 -f
```

Stop the container with:

```sh
docker-compose down
```

## Notes

- Ensure your environment variables are correctly set before running the container.
- Modify the `docker-compose.yml` file as needed to fit your setup.
