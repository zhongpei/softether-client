#!coding: utf-8
import re
import os
import popen2
import subprocess
import shlex
import threading


class Commander:
    def __init__(self, vpn_cmd = "/opt/vpnclient/vpncmd"):
        self.handles = []
        self.VPN_SUCESSED_RESULT = (
            "The command completed successfully",
            "Object not found",
            "The user with the specified name already exists on the Virtual Hub"
        )
        self.VPNCMD = vpn_cmd
    def is_exist(self, source):
        if not os.path.isfile(source) and not os.path.isdir(source):
            print ("%s not found" % source)
            return False
        return True

    def __del__(self):
        for p in self.handles:
            self.__kill(p)

    def kill(self, *args):
        self.__kill(*args)

    def __kill(self, p):
        try:
            if p is None:
                #print ("pid is None")
                return
            #print 'terminate ... '
            p.terminate()
            #print 'kill ... '
            p.kill()
            if p in self.handles:
                self.handles.remove(p)
        except Exception as err:
            pass
            #print err

    def vpn_command(
            self,
            command,
            sucessed_result=None
    ):
        if sucessed_result is None:
            sucessed_result=self.VPN_SUCESSED_RESULT
        VPNCMD = self.VPNCMD
        cwd = os.path.dirname(VPNCMD)
        try:
            rd = ed = []
            is_ok = False
            r, e = self.command2("%s  localhost /CLIENT /CMD %s"%(VPNCMD,command), timeout=60, env=None, cwd=cwd, shell=False)
            rd = r.split("\n")
            re = r.split("\n")
            for l in rd:
                for r in sucessed_result:
                    if l.find(r) != -1:
                        is_ok = True
            if len(sucessed_result) == 0:
                is_ok = True

            # print "command ==> "+str(command)+str(rd)+str(ed)+" ...  "+str(is_ok)+"\n"
            return is_ok, rd, ed
        except Exception as err:
            print str(err)
            return False, rd, ed

    def command2(self, command, timeout=-1, env=None, cwd=os.getcwd(), shell=False):
        rd = ed = ""
        try:
            if shell:
                args = command
            else:
                args = shlex.split(command)
            # print "run ==> shell==" + str( shell) +  " command: " +str(args)
            p = subprocess.Popen(args, env=env, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            self.handles.append(p)
            if timeout != -1:
                t = threading.Timer(timeout, self.kill, (p,))
                t.start()
            rd, ed = p.communicate()
        except Exception as err:
            print "err:" + str(err)
            print (" %s %s" % (command, str(err)))
        return rd, ed

    def command(self, bin, args):
        rd = ed = []
        try:
            command = "%s  %s" % (bin, args)
            r, w, e = popen2.popen3(command)
            rd = r.readlines()
            ed = e.readlines()

            r.close()
            w.close()
            e.close()
        except Exception as err:
            print(" %s %s" % (command, str(err)))
        return rd, ed

    def ls(self, s):
        r, _ = self.commond("ls", "-l " + s)
        return r

    def grep(self, s, pattern):
        return '\n'.join(re.findall(r'^.*%s.*?$' % pattern, s, flags=re.M))

    def ldd(self, source):
        if not self.is_exist(source):
            return ""
        result = []
        r, e = self.commond("ldd", source)
        for l in r:
            s = ""
            if l.find("=>") != -1:
                d = l.split("=>")
                if len(d) < 2:
                    s = d[0].strip()
                else:
                    s = d[1].strip()
                    tmp = s.split("(")
                    s = tmp[0]
            else:
                s = l
            s = s.strip()
            # print "===>",s
            if s != "":
                result.append(s)
        return result

    def whereis(self, source):
        WHEREIS_BIN = '/usr/bin/whereis'
        if not os.path.isfile(WHEREIS_BIN):
            print "whereis not found"
            return ""
        r, e = self.commond(WHEREIS_BIN, source)
        for l in r:
            if l.find(source.strip()) == -1:
                continue
            for s in l.split(" "):
                s = s.strip()
                if s.endswith(source):
                    return s
        return ""

    def getlink(self, source):
        pass

