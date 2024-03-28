FROM python:3.11-slim

WORKDIR /app

COPY ./app /app
COPY ./requirements.txt /app

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg; \
    rm -rf /var/lib/apt/lists/*; \
    pip3 install --upgrade pip; \
    pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "/app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]