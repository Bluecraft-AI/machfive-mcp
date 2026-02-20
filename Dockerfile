FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server
COPY server.py .

# Railway sets PORT automatically; default 8000
ENV PORT=8000

EXPOSE ${PORT}

CMD ["python", "server.py"]
