FROM python:3.10-slim

# Install FFmpeg (used by yt-dlp for processing multimedia).
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy requirements.txt and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files.
COPY bot.py .
COPY health.py .
COPY entrypoint.sh .

# Create directories for cookies and downloads.
RUN mkdir -p cookies downloads

# Ensure the entrypoint script is executable.
RUN chmod +x entrypoint.sh

# Expose port 8000 (for Flask health checks).
EXPOSE 8000

# Set the default command to run the entrypoint script.
CMD ["./entrypoint.sh"]
