FROM mcr.microsoft.com/playwright/python:v1.43.0
# python==3.10.12, playwright==1.40.0

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt && rm requirements.txt



ARG USER=user
ARG USER_UID=1001
ARG USER_HOME=/home/$USER
ARG USER_DATA_DIR=$USER_HOME/user_data
ARG USER_SCRIPTS_DIR=$USER_HOME/user_scripts
ARG APP_DIR=$USER_HOME/app
ARG APP_HOST=0.0.0.0
ARG APP_PORT=3001
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


SHELL ["/bin/bash", "-c"]

WORKDIR $USER_HOME
EXPOSE $APP_PORT
# to view healthcheck status:
# docker inspect --format "{{json .State.Health }}" <container name> | jq
HEALTHCHECK --interval=30s --timeout=10s CMD curl --fail http://localhost:$APP_PORT/ping || exit 1

CMD uvicorn --app-dir $APP_DIR main:app --host $APP_HOST --port $APP_PORT
