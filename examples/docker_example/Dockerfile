FROM python:3.9

RUN apt-get update && apt-get -y install cron && mkdir /etc/carbonblack/

COPY ./examples/docker_example/crontab_process_server /etc/cron.d/crontab
COPY ./examples/docker_example/credentials.cbc /etc/carbonblack/credentials.cbc
RUN /usr/local/bin/pip install carbon-black-cloud-threat-intelligence-connector

RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]
