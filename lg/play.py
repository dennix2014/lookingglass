# # from binascii import unhexlify
# # from pprint import pprint

# # from sflow import decode


# # # Example datagram taken from http://packetlife.net/captures/protocol/sflow/

# # raw = '0000000500000001ac15231100000001000001a6673f36a00000000100000002' +\
# #       '0000006c000021280000040c0000000100000001000000580000040c00000006' +\
# #       '0000000005f5e100000000010000000300000000018c6e9400009b9e00029062' +\
# #       '0001f6c400000000000000000000000000000000005380600000a0de0000218a' +\
# #       '000008d7000000000000000000000000'

# # data = unhexlify(raw)

# # pprint(decode(data))


import subprocess
from json import loads

p = subprocess.Popen(
['/usr/local/bin/sflowtool','-j'],
stdout=subprocess.PIPE,
stderr=subprocess.STDOUT
)
lines = iter(p.stdout.readline,'')
for line in lines:

      datagram = loads(line)
      localtime = datagram["localtime"]
      switch = datagram["datagramSourceIP"]
      samples = datagram["samples"]
      for sample in samples:
            sampleType = sample["sampleType"]
            elements = sample["elements"]
            if sampleType == "FLOWSAMPLE":
                  for element in elements:
                        tag = element["flowBlock_tag"]
                        if tag == "0:1":
                              try:
                                    srcip = element["srcIP"]
                                    dstip = element["dstIP"]
                                    srcmac = element['srcMAC']
                                    dstmac = element['dstMAC']
                                    pktsize = element["sampledPacketSize"]
                                    print(f'{switch} - {srcmac}<=>{srcip} - {dstmac}<=>{dstip} - {pktsize}')
                              except KeyError:
                                    pass
 


