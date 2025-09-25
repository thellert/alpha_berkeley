FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies relative to workspace root context
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK resources
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader punkt_tab
RUN python -m nltk.downloader averaged_perceptron_tagger
RUN python -m nltk.downloader stopwords

# Copy server files (local src -> /app/src) relative to workspace root context
# COPY ./src/ ./src/

# Set environment variables
ARG PV_FINDER_PORT
ENV HOST=0.0.0.0
ENV PORT=${PV_FINDER_PORT}
ENV TRANSPORT=sse

# Expose the port
EXPOSE ${PV_FINDER_PORT}

# Run the MCP server
# CMD ["python", "src/main.py"] 