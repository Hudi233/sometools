#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
from optparse import OptionParser
import re
import json
import tempfile,uuid,os
# start a new nmap scan on localhost with some specific options
class Nmap(object):
    def __init__(self,tid,port_list=None,temp_path=None):
        self.port_list = port_list or '1-65535'
        self.time_out = 180
        self.max_rate = 200000
        self.tid = tid if tid else str(uuid.uuid4())
        self.temp_path = temp_path if temp_path else tempfile.gettempdir()
        self.host_services_jsonfile = os.path.join(self.temp_path,'host_services_%s.json' %self.tid)

    def do_scan(self,ips):
        parsed = None
        options = "-sV -sT --open --host-timeout " + str(self.time_out) + " --max-rate " + str(self.max_rate) + " -p " + str(self.port_list)
        nmproc = NmapProcess(ips,options)
        rc = nmproc.run()
        if rc != 0:
            print("nmap scan failed: {0}".format(nmproc.stderr))

        try:
            parsed = NmapParser.parse(nmproc.stdout)
        except NmapParserException as e:
            print("Exception raised while parsing scan: {0}".format(e.msg))
        return parsed

    def print_scan(self,nmap_report):
        print("Starting Nmap {0} ( http://nmap.org ) at {1}".format(
        nmap_report.version,
        nmap_report.started))

        host_json = []
        for host in nmap_report.hosts:
            each_host_json = {}
            tmp_host = host.address
            each_host_json["IP"] = tmp_host

            print("Nmap scan report for {0} ({1})".format(
            tmp_host,
            host.address))
            print("Host is {0}.".format(host.status))
            print("  PORT     STATE         SERVICE")

            each_host_json["data"] = []
            for serv in host.services:
                each_port = {}
                tmp_port = serv.port
                each_port["port"] = tmp_port
                tmp_protocol = serv.protocol
                tmp_state = serv.state
                tmp_service = serv.service
                each_port["service"] = tmp_service

                if len(serv.banner):
                    tmp_banner = serv.banner
                    product = re.search("(?<=product:\s).*(?=version)",tmp_banner)
                    try:
                        product = product.group(0)
                    except:
                        product = ""

                    version = re.search("(?<=version:\s)\S+",tmp_banner)
                    try:
                        version = version.group(0)
                    except:
                        version = ""

                    extra_info = re.search("(?<=extrainfo:\s).*",tmp_banner)
                    try:
                        extra_info = extra_info.group(0)
                    except:
                        extra_info = ""

                else:
                    product = ""
                    version = ""
                    extra_info = ""

                each_port["banner"] = {}
                each_port["banner"]["product"] = product
                each_port["banner"]["version"] = version
                each_port["banner"]["extrainfo"] = extra_info
                
                each_host_json["data"].append(each_port)

                port_info ="{0:>5s}/{1:3s}  {2:12s}  {3}".format(
                    str(serv.port),
                    serv.protocol,
                    serv.state,
                    serv.service)
                if len(serv.banner):
                    port_info += " ({0})".format(serv.banner)
                print(port_info)
            host_json.append(each_host_json)
    
        print(nmap_report.summary)
        with open(self.host_services_jsonfile,'w+') as f: 
            json.dump(host_json,f)
        return host_json

if __name__ == "__main__":
    usage = "python nmap_port.py -t 192.168.10.1-254"
    parser = OptionParser(usage)
    parser.add_option("-t","--target",dest="target",default="",help="domain,ip or ip range to be scaned, eg: 192.168.10.2 192.168.10.1-254 192.168.10.*")
    parser.add_option("-p","--port",dest="port",default="",help="port range to be scaned, eg: 21,22,80,100-300,8080")
    parser.add_option("-f","--file_path",dest="file_path",default="/tmp",help="Output scan in json,default is '/tmp'")
    
    (options, args) = parser.parse_args()
    
    if not options.target:
        parser.print_help()
    else:
        target = options.target
        port_list = options.port
        file_path = options.file_path
        nmap = Nmap(tid='',port_list=port_list,temp_path=file_path)
        nm_run = nmap.do_scan(target)
        nm_report = nmap.print_scan(nm_run)
        print("nmapResult:" + json.dumps(nm_report))
