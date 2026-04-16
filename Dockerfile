# STAGE 1: Build Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# STAGE 2: Build Backend & Final Image
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy all project files
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV KORTEX_LLM_PROVIDER=gemini
ENV KORTEX_LLM_MODEL=gemini-2.0-flash

# Run ingestion to bake the FAISS index into the image
RUN python -m backend.data.ingest

# Hugging Face Spaces uses port 7860 by default
EXPOSE 7860

# Command to run the application
# We use uvicorn to serve the FastAPI app which now also serves the frontend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
