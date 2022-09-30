FROM ubuntu:22.04

ENV VIRTUAL_ENV=/root/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install virtualenv -y

# add files
ADD requirements.txt /root/requirements.txt
ADD wapp /root/wapp
ADD wsgi.py /root/wsgi.py

WORKDIR /root
RUN virtualenv -ppython3 venv
RUN pip install -r requirements.txt

# start the cluster
ENTRYPOINT ["python", "wsgi.py"]
CMD []

