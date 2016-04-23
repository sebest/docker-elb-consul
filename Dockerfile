FROM alpine

RUN apk -Uuv add groff less python py-pip && \
    pip install awscli && \
    pip install boto && \
    apk --purge -v del py-pip && \
    rm /var/cache/apk/*

ENV CONSUL_VERSION 0.5.2
RUN apk --update add curl ca-certificates && \
    curl -Ls https://circle-artifacts.com/gh/andyshinn/alpine-pkg-glibc/6/artifacts/0/home/ubuntu/alpine-pkg-glibc/packages/x86_64/glibc-2.21-r2.apk > /tmp/glibc-2.21-r2.apk && \
    apk add --allow-untrusted /tmp/glibc-2.21-r2.apk && \
    rm -rf /tmp/glibc-2.21-r2.apk /var/cache/apk/*

ADD https://dl.bintray.com/mitchellh/consul/${CONSUL_VERSION}_linux_amd64.zip /tmp/consul.zip
RUN unzip /tmp/consul.zip \
    && chmod +x consul \
    && rm /tmp/consul.zip

ADD handler.py /
ADD start /

ENTRYPOINT ["/start"]
CMD []
