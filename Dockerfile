FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
# python==3.10.12, playwright==1.40.0

# RUN apt update
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt && rm requirements.txt

ARG USER=user
ARG USER_UID=1001
ARG USER_HOME=/home/$USER
ARG USER_DATA_DIR=$USER_HOME/user_data_dir
ARG USER_SCRIPTS=$USER_HOME/user_scripts
ARG APP_DIR=$USER_HOME/app
ARG APP_HOST=0.0.0.0
ARG APP_PORT=3000

ENV \
	IN_DOCKER=1 \
	USER=$USER \
	USER_UID=$USER_UID \
	USER_HOME=$USER_HOME \
	USER_DATA_DIR=$USER_DATA_DIR \
	USER_SCRIPTS=$USER_SCRIPTS \
	APP_DIR=$APP_DIR \
	APP_HOST=$APP_HOST \
	APP_PORT=$APP_PORT

RUN useradd -s /bin/bash -m -d $USER_HOME -u $USER_UID $USER
USER $USER

RUN mkdir -p $USER_DATA_DIR $USER_SCRIPTS
COPY --chown=$USER:$USER app $APP_DIR
COPY --chown=$USER:$USER tests.sh $USER_HOME

WORKDIR $USER_HOME
CMD uvicorn --app-dir $APP_DIR main:app --host $APP_HOST --port $APP_PORT
