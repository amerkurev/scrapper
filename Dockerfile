FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
# python==3.10.12, playwright==1.40.0

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt && rm requirements.txt

LABEL org.opencontainers.image.title=Scrapper
LABEL org.opencontainers.image.description="Web scraper with a simple REST API living in Docker and using a Headless browser and Readability.js for parsing."
LABEL org.opencontainers.image.url=https://scrapper.dev
LABEL org.opencontainers.image.documentation="https://github.com/amerkurev/scrapper#usage"
LABEL org.opencontainers.image.vendor="amerkurev"
LABEL org.opencontainers.image.licenses=Apache-2.0
LABEL org.opencontainers.image.source="https://github.com/amerkurev/scrapper"

ARG GIT_BRANCH
ARG GITHUB_SHA

ARG USER=user
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

RUN useradd -s /bin/bash -m -d $USER_HOME -u $USER_UID $USER
USER $USER

RUN mkdir -p $USER_DATA_DIR $USER_SCRIPTS
COPY --chown=$USER:$USER app $APP_DIR
COPY --chown=$USER:$USER runtest.sh $USER_HOME
COPY --chown=$USER:$USER .coveragerc $USER_HOME
COPY --chown=$USER:$USER .pylintrc $USER_HOME

SHELL ["/bin/bash", "-c"]
RUN \
    rev=${GIT_BRANCH}-${GITHUB_SHA:0:7}-$(date +%Y%m%dT%H:%M:%S) && \
    echo "revision = '$rev'" | tee $APP_DIR/version.py

WORKDIR $USER_HOME
EXPOSE $APP_PORT
# to view healthcheck status:
# docker inspect --format "{{json .State.Health }}" <container name> | jq
HEALTHCHECK --interval=30s --start-period=5s --start-interval=1s --timeout=10s CMD curl --fail http://localhost:$APP_PORT/ping || exit 1

CMD uvicorn --app-dir $APP_DIR main:app --host $APP_HOST --port $APP_PORT
