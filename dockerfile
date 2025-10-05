FROM python:3.13-alpine

# Install system dependencies using Alpine's package manager
RUN apk add --no-cache mpv fontconfig ttf-dejavu

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir mutagen requests

# Copy your TMP code
COPY play.py .

# Create data directory for persistent files
RUN mkdir -p /app/data

# Set environment variables for better terminal support
ENV TERM=xterm-256color
ENV PYTHONUNBUFFERED=1

# Run the player
CMD ["python", "play.py"]