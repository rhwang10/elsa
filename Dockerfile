FROM python:3.11-slim-bullseye

ENV RUNTIME_DEPENDENCIES="ffmpeg"

RUN apt-get update \
    && apt-get install -y $RUNTIME_DEPENDENCIES \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "-m", "bot.bot"]