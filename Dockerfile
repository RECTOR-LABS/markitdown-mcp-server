# Use Apify's Python base image
FROM apify/actor-python:3.11

# Copy requirements.txt to the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Actor source code
COPY . ./

# Set the entrypoint to run the main.py script
CMD ["python", "-m", "src.main"]
