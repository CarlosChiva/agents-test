FROM python:3.12-slim

# Copy the requirements file
COPY requirements.txt .

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire repository
WORKDIR /app
COPY . .

# Run the application
CMD ["python", "main.py"]
