#!/bin/bash

./vpnclient start
VPNCMD="./vpncmd localhost /CLIENT /CMD"

$VPNCMD NicCreate p1
$VPNCMD AccountCreate taizhou /SERVER:taizhou.yun.hahado.cn:15555 /HUB:VPN /USERNAME:duoipetnlscdm /NICNAME:p1
$VPNCMD AccountPasswordSet taizhou /PASSWORD:dobuK36NJno0J /TYPE:standard
$VPNCMD AccountConnect taizhou
$VPNCMD AccountStatusGet taizhou
