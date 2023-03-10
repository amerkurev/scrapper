FROM mcr.microsoft.com/playwright/python:v1.31.0-focal

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ENV \
	IN_DOCKER=1 \
	# Docker user
    APP_USER=user \
    APP_UID=1001 \
    APP_HOME=/home/user/app \
    STATIC_DIR=/home/user/static

RUN adduser -u $APP_UID $APP_USER

USER user
COPY app $APP_HOME
COPY static $STATIC_DIR

WORKDIR $APP_HOME
CMD waitress-serve --host 0.0.0.0 --port=3000 main:app
