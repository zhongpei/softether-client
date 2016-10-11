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


def init(args):
    c = Commander()
    rd, ed = c.command2("service rsyslog start")
    if len(ed) > 0:
        logging.error("start rsyslog failed")
        return False
    rd, ed = c.command2("/opt/vpnclient/vpnclient start")
    if len(ed) > 0:
        logging.error("start vpnclient failed")
        return False

    time.sleep(1)

    ok, rd, ed = c.vpn_command("NicCreate p1")
    if not ok:
        logging.error("create nic failed")
        return False

    time.sleep(1)
    if 'vpn_p1' not in netifaces.interfaces():
        logging.error("create nic failed")
        return False
    
    ok, rd, ed = c.vpn_command(
            "AccountCreate {username} /SERVER:{host}:{port} /HUB:VPN /USERNAME:{username} /NICNAME:p1".format(
                username=args["<username>"],
                host=args["<host>"],
                port=15555,
            )
    )
    if not ok:
        logging.error("create account failed")
        return False

    ok, rd, ed = c.vpn_command(
            "AccountPasswordSet {username} /PASSWORD:{password} /TYPE:standard".format(
                username=args["<username>"],
                password=args["<password>"],
            )
    )
    if not ok:
        logging.error("account set password failed")
        return False

    ok, rd, ed = c.vpn_command(
            "AccountConnect {username} ".format(
                username=args["<username>"],
            )
    )
    if not ok:
        logging.error("connect failed")
        return False

    ok,why = is_vpn_connected()
    print ok,why
    while not ok:
        time.sleep(1)
        ok,why = is_vpn_connected()
        print ok,why
def is_vpn_connected():
    c = Commander()
    ok, rd, ed = c.vpn_command(
            "AccountStatusGet {username} ".format(
                username=args["<username>"],
            )
    )
    if not ok:
        return False,"command not runing"
    #print "\n".join(rd)
    for l in rd:
        if l.find("|") !=  -1:
            key,value = l.split("|")
            if key.find("Session Status") != -1 :
                if value.find("Connection Completed (Session Established)") != -1:
                    return True,value
                else:
                    return False,value
    return False,"error"


if __name__ == '__main__':
    args = docopt(__doc__)
    print args

    ok = init(args)

    if args['-r']:
        add_route(args['<host>'])
