#!/bin/bash


docker run -it --rm \
-v "$PWD/run.sh:/opt/vpnclient/run.sh" \
-v "$PWD/dsl-provider:/etc/ppp/peers/dsl-provider" \
-v "$PWD/pap-secrets:/etc/ppp/pap-secrets"  \
--privileged --cap-add=NET_ADMIN --device=/dev/ppp \
zhongpei/softether-client bash
