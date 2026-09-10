FROM python:3.11-slim-bookworm
RUN sed -i -e 's|http://deb.debian.org/debian|https://ftp.debian.org/debian|g' -e 's|https://ftp.debian.org/debian-security|https://security.debian.org/debian-security|g' /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y --no-install-recommends libsndfile1 espeak-ng && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV TTS_OUTPUT_DIR=/data/audio
VOLUME ["/data"]
EXPOSE 8090
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
