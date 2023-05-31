FROM debian:bullseye

# Add Tor repo and install necessary packages.
RUN \
apt-get update && \
apt-get install -y \
apt-utils \
apt-transport-https \
curl \
gnupg2 && \
curl -sSL https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --dearmor | tee /usr/share/keyrings/tor-archive-keyring.gpg >/dev/null && \
echo "deb [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org bullseye main" > /etc/apt/sources.list.d/tor.list && \
apt-get update && \
apt-get install -y \
deb.torproject.org-keyring \
locales \
procps \
python3-dev \
python3-pip \
runit \
tcpdump \
tor \
uwsgi \
uwsgi-plugin-python3

# Python dependancies.
# Copy requirements.txt in the secretstroll directory.

RUN mkdir -p /testing/data
RUN mkdir -p /testing/code

COPY ./credential.py /testing/code
COPY ./stroll.py /testing/code
COPY ./proof_handler.py /testing/code
COPY ./test_signaturescheme.py /testing/code
COPY ./test_registrationscheme.py /testing/code
COPY ./serialization.py /testing/code
COPY ./measurement.py /testing/code

COPY ./requirements.txt /testing/
RUN rm -rf /testing/code/docker && rm -rf /testing/code/report_template && rm -rf /testing/code/handout && rm -rf /testing/code/tor && rm -rf /testing/code/handout
RUN python3 -m pip install -r /testing/requirements.txt
RUN python3 -m pip install pytest
