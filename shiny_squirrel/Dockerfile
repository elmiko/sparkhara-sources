FROM fedora:22
MAINTAINER michael mccune <msm@redhat.com>

RUN dnf install -y python-flask python-pymongo && \
    dnf clean all

ADD shiny_squirrel.py /opt/shiny_squirrel/
ADD static/* /opt/shiny_squirrel/static/
ADD templates/* /opt/shiny_squirrel/templates/
ADD run_shiny_squirrel /

ENTRYPOINT ["/run_shiny_squirrel"]

EXPOSE 9050
