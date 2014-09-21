#!/usr/bin/python
#credits : https://gist.github.com/TheCrazyT/11263599

import socket
import ssl
import select
import time
import re
import sys 
from thread import start_new_thread
from struct import pack
from random import randint

class lakkucast:
    def __init__(self):
        self.status = None
        self.session_id = None
        self.protocolVersion = 0
        self.source_id = "sender-0"
        self.destination_id = "receiver-0"
        self.chromecast_server = "192.168.1.197" #living room audio
        self.socket = 0
        self.type_enum = 0
        self.type_string = 2
        self.type_bytes = self.type_string
        self.session = 0
        self.play_state = None
        self.media_dirs = ["/data/media/TV-Shows/English/Friends", "/data/media/TV-Shows/English/That 70s Show"]

    def clean(self,s):
        return re.sub(r'[\x00-\x1F\x7F]', '?',s)

    def getType(self, fieldId,t):
        return (fieldId << 3) | t

    def getLenOf(self, s):
        x = ""
        l = len(s)
        while(l > 0x7F):
            x += pack("B",l & 0x7F | 0x80)
            l >>= 7
        x += pack("B",l & 0x7F)
        return x

    def init_status(self):
        self.socket = socket.socket()
        self.socket = ssl.wrap_socket(self.socket)
        #print "connecting ..."
        self.socket.connect((self.chromecast_server,8009))
        payloadType = 0 #0=string
        data = "{\"type\":\"CONNECT\",\"origin\":{}}"
        lnData = self.getLenOf(data)
        #print len(lnData),len(data),lnData.encode("hex")
        namespace = "urn:x-cast:com.google.cast.tp.connection"
        msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" %
                        (len(self.source_id),
                         len(self.destination_id), 
                         len(namespace),
                         len(lnData),
                         len(data)), 
                         self.getType(1,self.type_enum),
                         self.protocolVersion,
                         self.getType(2,self.type_string), 
                         len(self.source_id),
                         self.source_id,
                         self.getType(3,self.type_string), 
                         len(self.destination_id),
                         self.destination_id,
                         self.getType(4,self.type_string), 
                         len(namespace),
                         namespace,
                         self.getType(5,self.type_enum), 
                         payloadType,
                         self.getType(6,self.type_bytes),
                         lnData,
                         data)
        msg = pack(">I%ds" % (len(msg)),len(msg),msg)
        #print msg.encode("hex")
        #print "Connecting ..."
        self.socket.write(msg)

        payloadType = 0 #0=string
        data = "{\"type\":\"GET_STATUS\",\"requestId\":46479000}"
        lnData = self.getLenOf(data)
        namespace = "urn:x-cast:com.google.cast.receiver"
        msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % (len(self.source_id),
                                        len(self.destination_id),
                                        len(namespace),
                                        len(lnData),
                                        len(data)),
                                        self.getType(1,self.type_enum),
                                        self.protocolVersion,
                                        self.getType(2,self.type_string),
                                        len(self.source_id),
                                        self.source_id,
                                        self.getType(3,self.type_string),
                                        len(self.destination_id),
                                        self.destination_id,
                                        self.getType(4,self.type_string),
                                        len(namespace),
                                        namespace,
                                        self.getType(5,self.type_enum),
                                        payloadType,
                                        self.getType(6,self.type_bytes),
                                        lnData,
                                        data)
        msg = pack(">I%ds" % (len(msg)),len(msg),msg)
        #print "sending status request..."
        self.socket.write(msg)
     
        m1=None
        m3=None
        result=""
        count = 0
        while m1==None and m3==None:
            lastresult = self.socket.read(2048)
            result += lastresult
            #print "#"+lastresult.encode("hex")
            #if lastresult != "":
            #    print self.clean("\nH!"+lastresult)
            #print result
            m1 = re.search('"sessionId":"(?P<session>[^"]+)"', result)
            m2 = re.search('"statusText":"(?P<status>[^"]+)"', result)
            m3 = re.search('"playerState":"(?P<play_state>[^"]+)"', result)
            count = count + 1
            if count > 100:
                break
            #print "#%i" % (m==None)
        if m1 != None:
            #print "session:",m1.group("session")
            self.session = m1.group("session")
        if m2 != None:
            #print "status:",m2.group("status")
            self.status = m2.group("status")
        if m3 != None:
            #print "play_state:",m3.group("play_state")
            self.play_state = m3.group("play_state")

    def get_status(self):
        print "status: " , self.status
        print "play state:" , self.play_state

    def ready_to_play(self):
        print self.status
        if self.status == "Now Casting":
            return False
        if self.status == "Ready To Cast" or self.status == None:
            if self.play_state == None:
                return True
            if self.play_state == "IDLE":
                return True
            if self.play_state == "PLAYING":
                return False
            if self.play_state == "BUFFERING":
                return False
            return True
        else:
            return False
    def close_connection(self):
        self.socket.close()

    def play_url(self, url):
        payloadType = 0 #0=string
        data = "{\"type\":\"LAUNCH\",\"requestId\":46479001,\"appId\":\"CC1AD845\"}"
        lnData = self.getLenOf(data)
        namespace = "urn:x-cast:com.google.cast.receiver"
        msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % 
                                (len(self.source_id),
                                 len(self.destination_id),
                                 len(namespace),
                                 len(lnData),
                                 len(data)),
                                 self.getType(1,self.type_enum),
                                 self.protocolVersion,
                                 self.getType(2,self.type_string),
                                 len(self.source_id),
                                 self.source_id,
                                 self.getType(3,self.type_string),
                                 len(self.destination_id),
                                 self.destination_id,
                                 self.getType(4,self.type_string),
                                 len(namespace),
                                 namespace,
                                 self.getType(5,self.type_enum),
                                 payloadType,
                                 self.getType(6,self.type_bytes),
                                 lnData,
                                 data)
        msg = pack(">I%ds" % (len(msg)),len(msg),msg)
        #print msg.encode("hex")
        #print "sending ..."
        self.socket.write(msg)
         
        m=None
        result=""
        while m==None:
            lastresult = self.socket.read(2048)
            result += lastresult
            #print "#"+lastresult.encode("hex")
            #print clean("!"+lastresult)
            m = re.search('"transportId":"(?P<transportId>[^"]+)"', result)
        self.destination_id = m.group("transportId")

        payloadType = 0 #0=string
        data = "{\"type\":\"CONNECT\",\"origin\":{}}"
        lnData = self.getLenOf(data)
        #print len(lnData),len(data),lnData.encode("hex")
        namespace = "urn:x-cast:com.google.cast.tp.connection"
        msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % 
                                (len(self.source_id),
                                 len(self.destination_id),
                                 len(namespace),
                                 len(lnData),
                                 len(data)),
                                 self.getType(1,self.type_enum),
                                 self.protocolVersion,
                                 self.getType(2,self.type_string),
                                 len(self.source_id),
                                 self.source_id,
                                 self.getType(3,self.type_string),
                                 len(self.destination_id),
                                 self.destination_id,
                                 self.getType(4,self.type_string),
                                 len(namespace),
                                 namespace,
                                 self.getType(5,self.type_enum),
                                 payloadType,
                                 self.getType(6,self.type_bytes),
                                 lnData,
                                 data)
        msg = pack(">I%ds" % (len(msg)),len(msg),msg)
        #print msg.encode("hex")
        #print "sending ..."
        self.socket.write(msg)
        payloadType = 0 #0=string
        data = "{\"type\":\"LOAD\",\"requestId\":46479002,\"sessionId\":\""+self.session+"\",\"media\":{\"contentId\":\""+url+"\",\"streamType\":\"buffered\",\"contentType\":\"video/mp4\"},\"autoplay\":true,\"currentTime\":0,\"customData\":{\"payload\":{\"title:\":\"\"}}}"

         
        lnData = self.getLenOf(data)
        namespace = "urn:x-cast:com.google.cast.media"
        msg = pack(">BBBB%dsBB%dsBB%dsBBB%ds%ds" % 
                                (len(self.source_id),
                                 len(self.destination_id),
                                 len(namespace),
                                 len(lnData),
                                 len(data)),
                                 self.getType(1,self.type_enum),
                                 self.protocolVersion,
                                 self.getType(2,self.type_string),
                                 len(self.source_id),
                                 self.source_id,
                                 self.getType(3,self.type_string),
                                 len(self.destination_id),
                                 self.destination_id,
                                 self.getType(4,self.type_string),
                                 len(namespace),
                                 namespace,
                                 self.getType(5,self.type_enum),
                                 payloadType,
                                 self.getType(6,self.type_bytes),
                                 lnData,
                                 data)
        msg = pack(">I%ds" % (len(msg)),len(msg),msg)
        #print msg.encode("hex")
        #print "sending ..."
        #print "LOADING"
        self.socket.write(msg)
        self.close_connection()
         
        #try:
        # while True:
        #     print "before lastresult"
        #     lastresult = self.socket.read(2048)
        #     if lastresult!="":
        #         #print "#"+lastresult.encode("hex")
        #         print self.clean("! In loop:"+lastresult)
        # finally:
        #   print "final"
        #   socket.close()
        #   print "socket closed"

        def random_play(self, num_play):
            rand_main = randint(0, (len(self.media_dirs)-1))
            if os.path.isdir(self.media_dirs[rand_main]):
                for x in xrange(1, num_play ):


if __name__ == '__main__':
    l = lakkucast()
    l.init_status()
    url = "http://192.168.1.98/media/Other-Videos/big_buck_bunny.mp4"
    print url
    if l.ready_to_play():
        l.play_url(url)
    else:
        print "not ready"
    l.get_status()
    print "Waiting."
    time.sleep(2)
    l.init_status()
    l.get_status()
    while not l.ready_to_play():
        l.init_status()
        l.get_status()
        time.sleep(15)
        #print ".",
    print "\n"
    url = "http://192.168.1.98/media/Music-Videos/Indian/Item%20Songs/%e2%80%aaKhallas.mp4"
    print url
    l = lakkucast()
    l.init_status()
    l.play_url(url)
