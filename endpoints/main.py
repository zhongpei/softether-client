#!coding: utf-8
"""
Usage:
    main.py <host> <username> <password> [-r]  [--port=<port>] [--hub=<hub>] [--pppoe-username=<username>] [--pppoe-password=<password>]

Options:
    -h --help                   Show help
    -r                          Change route to make connect to Packetix Server always use default gw
    --port=<port>               Packetix Server Port [default: 15555].
    --hub=<hub>                 Packetix Server Hub [default: VPN]
    --pppoe-username=<username> PPPoE username
    --pppoe-password=<password> PPPoE password
"""

from docopt import docopt
import time
from command import Commander
import netifaces
import logging


def add_route(packetix_host):
    import socket
    from socket import AF_INET
    from pyroute2 import IPRoute
    gws = netifaces.gateways()
    default_gw = gws['default'][netifaces.AF_INET]
    logging.INFO('default gw %s' + str(default_gw))
    dst_ip = socket.gethostbyname(packetix_host)
    logging.INFO('packetix server : %s', dst_ip)
    ip = IPRoute()
    ip.route(
        'add',
        dst=dst_ip,
        gateway=default_gw[0],
        metrics={
            'mtu': 1500,
            'hoplimit': 16
        }
    )


def init():
    c = Commander()
    rd, ed = c.command2("service rsyslog start")
    if len(ed) > 0:
        logging.error("start rsyslog failed")
        return False
    rd, ed = c.command2("./vpnclient start")
    if len(ed) > 0:
        logging.error("start vpnclient failed")
        return False

    time.sleep(1)

    ok, rd, ed = c.vpn_command(" localhost /CLIENT /CMD NicCreate p1")
    if not ok:
        logging.error("create nic failed")
        return False

    time.sleep(1)
    if 'vpn_p1' not in netifaces.interfaces():
        logging.error("create nic failed")
        return False


if __name__ == '__main__':
    args = docopt(__doc__)
    print args

    ok = init()

    if args['-r']:
        add_route(args['<host>'])
