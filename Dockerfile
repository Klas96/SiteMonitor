FROM python:3.9-slim

# Create and switch to a non-root user
RUN useradd -m appuser
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies as root user
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Install texlive for LaTeX support
RUN apt-get update && \
    apt-get install -y texlive-latex-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create the logs, data, and cover_letters directories and adjust permissions for the appuser
RUN mkdir -p /app/logs /app/data /app/cover_letters && \
    chown -R appuser:appuser /app/logs /app/data /app/cover_letters && \
    chmod -R 755 /app/logs /app/data /app/cover_letters

# Switch to non-root user
USER appuser

# Make sure the app listens on port 8080
ENV PORT=8080
EXPOSE 8080

# Activate virtual environment and run app
CMD ["/app/venv/bin/python", "main.py"]