FROM fedora:22
MAINTAINER michael mccune <msm@redhat.com>

RUN ["/usr/bin/dnf", "install", "-y", \
     "git", \
     "python-flask", \
     "python-pymongo" \
    ]

WORKDIR /opt
RUN ["/usr/bin/git", "clone", "-b", "amqp", \
     "https://github.com/elmiko/sparkhara-sources.git" \
    ]

ADD run_shiny_squirrel /

WORKDIR /
ENTRYPOINT ["/run_shiny_squirrel"]

EXPOSE 9050
