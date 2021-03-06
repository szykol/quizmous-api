FROM python:3

WORKDIR /usr/local/api
COPY quizmous_api ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN export CODENAME=$(grep -oP 'VERSION_CODENAME=\K\w*' /etc/os-release)
RUN echo $CODENAME
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ `grep -oP 'VERSION_CODENAME=\K\w*' /etc/os-release`-pgdg main" | tee  /etc/apt/sources.list.d/pgdg.list
RUN apt-get update
RUN apt-get install -y vim nano tmux postgresql-client-12

ENV PGUSER=api
ENV PGDATABASE=quiz
ENV PGPASSWORD=foobar
ENV PGHOST=postgres_api

CMD ["python", "./run.py"]
