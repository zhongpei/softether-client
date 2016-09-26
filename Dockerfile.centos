FROM centos:7
MAINTAINER zhongpei <zhongpei@vip.qq.com>

ENV VERSION v4.20-9608-rtm-2016.04.17

RUN mkdir -p /opt/vpnclient
WORKDIR /opt/vpnclient
RUN yum -y install epel-release tar gcc make wget python python-pip pppoe pppoeconf net-tools
RUN wget http://www.softether-download.com/files/softether/${VERSION}-tree/Linux/SoftEther_VPN_Client/64bit_-_Intel_x64_or_AMD64/softether-vpnclient-${VERSION}-linux-x64-64bit.tar.gz  -O /tmp/softether.tar.gz
RUN tar -xzvf /tmp/softether.tar.gz -C /opt/

RUN cd /opt/vpnclient &&  make i_read_and_agree_the_license_agreement
RUN yum -y install rp-pppoe
