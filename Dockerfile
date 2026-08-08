FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code and the demo-repo (needed for the mutation engine)
COPY backend /app/backend
COPY demo-repo /app/demo-repo

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI server
# The python path needs to include /app/backend
ENV PYTHONPATH=/app/backend
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
