FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements_gemini.txt .
RUN pip install --no-cache-dir -r requirements_gemini.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the simple backend
CMD ["python", "simple_backend.py"]