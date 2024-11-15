FROM python:3.10.12

# Create and switch to a non-root user
RUN useradd -m appuser
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y texlive-latex-base gettext && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies as root user
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    python -m pip install --no-cache-dir -r requirements.txt

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

# Run the application
CMD ["/app/venv/bin/python", "main.py"]