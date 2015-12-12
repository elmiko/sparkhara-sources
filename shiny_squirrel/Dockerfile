FROM fedora:22
MAINTAINER michael mccune <msm@redhat.com>

RUN ["/usr/bin/dnf", "install", "-y", \
     "python-flask", \
     "python-pymongo" \
    ]

ADD shiny_squirrel.py /opt/shiny_squirrel/
ADD static/* /opt/shiny_squirrel/static/
ADD templates/* /opt/shiny_squirrel/templates/
ADD run_shiny_squirrel /

ENV MONGO_URL mongodb://127.0.0.1/

ENTRYPOINT ["/run_shiny_squirrel"]

EXPOSE 9050
