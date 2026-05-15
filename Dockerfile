FROM python:3.11-slim

# Install system deps for search (ripgrep) and git snapshots
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ripgrep && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[all]"
COPY gather/ gather/
COPY skills/ /root/.gather/skills/
COPY config.example.yaml /root/.gather/config.yaml

EXPOSE 18789
ENTRYPOINT ["gather"]
