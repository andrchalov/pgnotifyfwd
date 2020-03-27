FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
  build-essential \
  python \
  python3-pip \
  gosu \
  libpq-dev

ADD requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

ADD ./src /opt/app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "-u", "main.py"]
