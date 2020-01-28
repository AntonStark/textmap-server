# pull official base image
FROM python:3.8-alpine

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

ENV USER=nonroot
ENV HOME=/home/${USER}
ENV APP_ROOT=${HOME}/textmap
ENV LOG_DIR=/var/log/textmap

# create directory for the app user
RUN addgroup -S ${USER} && adduser -S ${USER} -G ${USER}
RUN mkdir -p ${HOME}
RUN chown -R ${USER}:${USER} ${HOME}

# create directory for logs
RUN mkdir -p ${LOG_DIR}
RUN chown -R ${USER}:${USER} ${LOG_DIR}

# only stub to correspond with non docker development environment
RUN mkdir -p /var/www/textmap/static/

# change to the app user
USER ${USER}

RUN mkdir $APP_ROOT
RUN mkdir $APP_ROOT/staticfiles
RUN mkdir $APP_ROOT/mediafiles
WORKDIR $APP_ROOT

# install dependencies
ENV PATH="${HOME}/.local/bin:${PATH}"
COPY --chown=${USER}:${USER} ./requirements.txt $HOME/requirements.txt
RUN pip install --user -r $HOME/requirements.txt

# copy project  (and entrypoint.sh inside them)
COPY --chown=${USER}:${USER} ./textmap $APP_ROOT

# run entrypoint.sh
ENTRYPOINT ["/home/nonroot/textmap/entrypoint.sh"]
