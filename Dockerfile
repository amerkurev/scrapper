FROM mcr.microsoft.com/playwright/python:v1.51.0-noble
# python==3.12.3

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ARG GIT_SHA
ARG GIT_TAG

LABEL org.opencontainers.image.title="Scrapper"
LABEL org.opencontainers.image.description="Web scraper with a simple REST API living in Docker and using a Headless browser and Readability.js for parsing"
LABEL org.opencontainers.image.url="https://scrapper.dev"
LABEL org.opencontainers.image.documentation="https://github.com/amerkurev/scrapper#usage"
LABEL org.opencontainers.image.vendor="amerkurev"
LABEL org.opencontainers.image.licenses="MIT License"
LABEL org.opencontainers.image.source="https://github.com/amerkurev/scrapper"

ARG USER=pwuser
ARG USER_UID=1001
ARG USER_HOME=/home/$USER
ARG USER_DATA_DIR=$USER_HOME/user_data
ARG USER_SCRIPTS_DIR=$USER_HOME/user_scripts
ARG APP_DIR=$USER_HOME/app
ARG APP_HOST=0.0.0.0
ARG APP_PORT=3000
ARG BROWSER_CONTEXT_LIMIT=20
ARG SCREENSHOT_TYPE=jpeg
ARG SCREENSHOT_QUALITY=80

ENV \
	IN_DOCKER=1 \
	GIT_SHA=$GIT_SHA \
	GIT_TAG=$GIT_TAG \
	USER=$USER \
	USER_UID=$USER_UID \
	USER_HOME=$USER_HOME \
	USER_DATA_DIR=$USER_DATA_DIR \
	USER_SCRIPTS_DIR=$USER_SCRIPTS_DIR \
	APP_DIR=$APP_DIR \
	APP_HOST=$APP_HOST \
	APP_PORT=$APP_PORT \
	BROWSER_CONTEXT_LIMIT=$BROWSER_CONTEXT_LIMIT \
	SCREENSHOT_TYPE=$SCREENSHOT_TYPE \
	SCREENSHOT_QUALITY=$SCREENSHOT_QUALITY

USER $USER
RUN mkdir -p $USER_DATA_DIR $USER_SCRIPTS_DIR

COPY --chown=$USER:$USER app $APP_DIR

SHELL ["/bin/bash", "-c"]

WORKDIR $APP_DIR
EXPOSE $APP_PORT
# to view healthcheck status:
# docker inspect --format "{{json .State.Health }}" <container name> | jq
HEALTHCHECK --interval=30s --start-period=5s --start-interval=1s --timeout=10s CMD curl --fail http://localhost:$APP_PORT/ping || exit 1

CMD ["python", "main.py"]
