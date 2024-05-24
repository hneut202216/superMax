FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    iputils-ping \
    nmap \
    dnsutils \
    curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
