import streamlit as st
import docker
import os
import time

# Debug: Check if the Docker socket exists
socket_path = "/var/run/docker.sock"
if not os.path.exists(socket_path):
    st.error(f"Docker socket not found at {socket_path}. Ensure the socket is mounted with -v /var/run/docker.sock:/var/run/docker.sock.")
    st.stop()

# Initialize the Docker client
try:
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    # Test the connection by fetching the Docker version
    version = client.version()
    st.write(f"Connected to Docker daemon. Docker version: {version['Version']}")
except Exception as e:
    st.error(f"Failed to connect to Docker: {e}")
    st.stop()

# Streamlit app UI
st.title("Docker Container Launcher")
st.write("This app automatically builds and runs a Docker container using the existing Dockerfile when it starts.")

# Automatically build and run the Docker container when the app loads
try:
    # Step 1: Build the Docker image using the existing Dockerfile
    st.write("Building Docker image from the existing Dockerfile...")
    image_name = "unhided-app-image"
    image, build_logs = client.images.build(
        path=".",  # Use the current directory (where the Dockerfile is located)
        tag=image_name,
        rm=True  # Remove intermediate containers to save space
    )
    for log in build_logs:
        if "stream" in log:
            st.write(log["stream"].strip())
    st.success("Docker image built successfully!")

    # Add a small delay to ensure the image is ready
    time.sleep(2)

    # Step 2: Run the Docker container
    st.write("Starting Docker container...")
    container_name = "unhided-app-container"
    # Stop and remove any existing container with the same name
    try:
        existing_container = client.containers.get(container_name)
        existing_container.stop()
        existing_container.remove()
        st.write("Removed existing container.")
    except docker.errors.NotFound:
        pass  # Container doesn't exist, no need to stop/remove

    # Run the new container
    container = client.containers.run(
        image_name,
        name=container_name,
        ports={'7860/tcp': 7860},  # Map port 7860 in the container to 7860 on the host
        detach=True
    )
    st.success(f"Container {container_name} started successfully! Access it at http://localhost:7860")

except Exception as e:
    st.error(f"An error occurred: {e}")

# Display container status
try:
    container = client.containers.get("unhided-app-container")
    st.write(f"Container Status: {container.status}")
except docker.errors.NotFound:
    st.write("Container not found or failed to start.")