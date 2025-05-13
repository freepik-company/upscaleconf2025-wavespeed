FROM python:3.11-slim

# Install locust
RUN pip install locust

# Create a non-root user to run the load tests
RUN useradd -m locust

# Set the working directory
WORKDIR /home/locust

# Copy the locust file and entrypoint script
COPY locustfile.py entrypoint.sh /home/locust/

# Fix permissions as root
RUN chmod +x /home/locust/entrypoint.sh && \
    chown -R locust:locust /home/locust

# Switch to non-root user
USER locust

# Set entrypoint to our script
ENTRYPOINT ["/home/locust/entrypoint.sh"] 