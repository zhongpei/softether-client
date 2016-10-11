FROM ubuntu:16.04
MAINTAINER zhongpei <zhongpei@vip.qq.com>

ENV VERSION v4.20-9608-rtm-2016.04.17

RUN mkdir -p /opt/vpnclient
WORKDIR /opt/vpnclient
RUN sed -i "s/http:\/\/archive\.ubuntu\.com/http:\/\/mirrors.163.com/" /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y -q gcc make wget python python-pip pppoe
RUN wget http://www.softether-download.com/files/softether/${VERSION}-tree/Linux/SoftEther_VPN_Client/64bit_-_Intel_x64_or_AMD64/softether-vpnclient-${VERSION}-linux-x64-64bit.tar.gz  -O /tmp/softether.tar.gz
RUN tar -xzvf /tmp/softether.tar.gz -C /opt/

RUN cd /opt/vpnclient &&  make i_read_and_agree_the_license_agreement
RUN apt-get install -y -q net-tools pppoeconf
RUN apt-get install -y -q vim rsyslog
ADD requestments.txt .
RUN pip install -r requestments.txt

RUN mkdir -p /etc/ppp/peers/
#RUN apt-get purge -y -q --auto-remove gcc make wget
