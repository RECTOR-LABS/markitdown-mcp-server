# Use Apify's Python base image
FROM apify/actor-python:3.11

# Copy requirements.txt to the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# SECURITY: Create non-root user for running the application
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy the Actor source code
COPY . ./

# SECURITY: Set ownership to non-root user
RUN chown -R appuser:appgroup /usr/src/app

# SECURITY: Switch to non-root user
USER appuser

# Set the entrypoint to run the main.py script
CMD ["python", "-m", "src.main"]
