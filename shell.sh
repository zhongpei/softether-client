#!/bin/bash


docker run -it --rm \
--privileged \
--cap-add=NET_ADMIN --device=/dev/ppp \
zhongpei/softether-client bash


#-v "$PWD/endpoints:/endpoints"  \
#-v "$PWD/dsl-provider.tp:/etc/ppp/peers/dsl-provider.tp" \
#-v "$PWD/pap-secrets.tp:/etc/ppp/pap-secrets.tp"  \
#-v "$PWD/run.sh:/opt/vpnclient/run.sh" \
