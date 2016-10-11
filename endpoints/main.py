#!coding: utf-8
"""
Usage:
    main.py <host> <username> <password> [-r]  [--port=<port>] [--hub=<hub>] [--pppoe-username=<username>] [--pppoe-password=<password>] [--output=<output>]

Options:
    -h --help                   Show help
    -r                          Change route to make connect to Packetix Server always use default gw
    --env                       Get param from env
    --port=<port>               Packetix Server Port [default: 15555].
    --hub=<hub>                 Packetix Server Hub [default: VPN]
    --pppoe-username=<username> PPPoE username
    --pppoe-password=<password> PPPoE password
    --output=<output>           output file
"""

import sys
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

def writeconf(template,target,**kw):

    with open(template) as f:
        data = f.read()
        with open(target,"w+") as f:
            f.write(data.format(**kw))
            return True
    return False

def init_pppoe(args , status_loop = 10):
    if args.get("--pppoe-username") is None:
        logging.error("not have --pppoe-username")
        return False,"pppoe param error"
    if args.get('--pppoe-password') is None:
        logging.error("not have --pppoe-password")
        return False,"pppoe param error"
    ok = writeconf("/etc/ppp/peers/dsl-provider.tp","/etc/ppp/peers/dsl-provider",username=args["--pppoe-username"])
    if not ok:
        logging.error("write conf /etc/ppp/peers/dsl-provider failed")
        return False,"write conf /etc/ppp/peers/dsl-provider failed"
    ok = writeconf("/etc/ppp/pap-secrets.tp","/etc/ppp/pap-secrets",username=args["--pppoe-username"],password=args['--pppoe-password'])
    if not ok:
        logging.error("write conf /etc/ppp/pap-secrets failed")
        return False,"write conf /etc/ppp/pap-secrets failed"

    c = Commander()
    rd, ed = c.command2("pon dsl-provider")
    if len(ed) > 0:
        logging.error("pon failed")
        return False,"pon failed"

    for i in range(status_loop):
        ok,why = is_pppoe_conneced()
        logging.info("pppoe {ok}({why})".format(ok=ok,why=why))
        if ok:
            return True,why
        time.sleep(1)
    return False,"pppoe error"

def is_pppoe_conneced():
    c = Commander()
    rd, ed = c.command2("plog")
    for l in rd.split("\n"):
        index = l.find("local  IP address")
        if index != -1:
            ip =  l[index+len("local  IP address"):].strip()
            return True,ip
    return False,"error"

def output(args,**kw):
    output = args.get("--output")
    if output is None:
        return False
    with open(output,"a+") as f:
        for k,v in kw.items():
            f.write("{key} : {value}\n".format(key=k,value=v))
        f.write("\n")
    return True

def init_vpn(args, status_loop = 10):
    c = Commander()
    rd, ed = c.command2("service rsyslog start")
    if len(ed) > 0:
        logging.error("start rsyslog failed")
        return False,"start rsyslog failed"
    rd, ed = c.command2("/opt/vpnclient/vpnclient start")
    if len(ed) > 0:
        logging.error("start vpnclient failed")
        return False,"start vpnclient failed"

    time.sleep(1)

    ok, rd, ed = c.vpn_command("NicCreate p1")
    if not ok:
        logging.error("create nic failed")
        return False,"create nic failed"

    time.sleep(1)
    if 'vpn_p1' not in netifaces.interfaces():
        logging.error("create nic failed")
        return False,"create nic failed"
    
    ok, rd, ed = c.vpn_command(
            "AccountCreate {username} /SERVER:{host}:{port} /HUB:VPN /USERNAME:{username} /NICNAME:p1".format(
                username=args["<username>"],
                host=args["<host>"],
                port=15555,
            )
    )
    if not ok:
        logging.error("create account failed")
        return False,"create account failed"

    ok, rd, ed = c.vpn_command(
            "AccountPasswordSet {username} /PASSWORD:{password} /TYPE:standard".format(
                username=args["<username>"],
                password=args["<password>"],
            )
    )
    if not ok:
        logging.error("account set password failed")
        return False,"account set password failed"

    ok, rd, ed = c.vpn_command(
            "AccountConnect {username} ".format(
                username=args["<username>"],
            )
    )
    if not ok:
        logging.error("connect failed")
        return False,"connect failed"

    for i in range(status_loop):
        ok,why = is_vpn_connected()
        logging.info("vpn connect %s (%s)"%(ok,why))
        if ok:
            return True,why
        time.sleep(1)

    return False,"vpn error"

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
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
    )
    #print args
    if args.get("--env"):
        if os.getenv("HOST"):
            args['<host>'] = os.getenv("HOST")
        if os.getenv("USERNAME"):
            args['<username>'] = os.getenv("USERNAME")
        if os.getenv("PASSWORD"):
            args['<password>'] = os.getenv("PASSWORD")
        if os.getenv("PPPOE_USERNAME"):
            args['--pppoe-username'] = os.getenv("PPPOE_USERNAME")
        if os.getenv("PPPOE_PASSWORD"):
            args['--pppoe-password'] = os.getenv("PPPOE_PASSWORD")
    print args

    ok,why = init_vpn(args)
    output(args,vpn=ok,status=why)

    if ok: 
        ok,why = init_pppoe(args)
        output(args,pppoe=ok,ip=why)

    if args['-r']:
        add_route(args['<host>'])
    sys.exit()
