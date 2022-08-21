ARG DEBIAN_VERSION=buster-slim

FROM debian:$DEBIAN_VERSION

LABEL Description="gpiodtest"

RUN apt-get update && apt-get install -y \
    libcurl4 \
    libgnutls30 \
    libsasl2-2  \
    libuuid1 \
    libssl1.1 \
    libgcrypt20  \
    libmicrohttpd12 \
    libltdl7 \
    libatomic1 \
    libjson-c3 \
    liblept5 \
    libmosquitto1 \
    libunistring2 \
    gpiod \
    && rm -rf /var/lib/apt/lists/*

# without running a user context, no exec is possible and without the dialout group no access to usb ir reader possible
RUN useradd -M -G dialout vz
USER vz