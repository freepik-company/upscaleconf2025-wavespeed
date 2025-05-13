FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - ensure src directory is in the right place
COPY src/ /app/src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Add troubleshooting command
RUN echo "Checking directory structure:" && \
    ls -la /app && \
    echo "Python modules available:" && \
    python -c "import sys; print(sys.path)" && \
    echo "Src directory contents:" && \
    ls -la /app/src

# Default command will be overridden by Kubernetes
CMD ["python", "-m", "src.api_server"] 