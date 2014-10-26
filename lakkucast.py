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
from subprocess import call
import os
import fnmatch
import argparse
import logging


class lakkucast:
    def __init__(self):
        self.status = None
        self.session_id = None
        self.protocolVersion = 0
        self.source_id = "sender-0"
        self.destination_id = "receiver-0"
        self.chromecast_server = "192.168.1.23" #living room audio
        self.socket = 0
        self.type_enum = 0
        self.type_string = 2
        self.type_bytes = self.type_string
        self.session = 0
        self.play_state = None
        self.sleep_between_media = 5
        self.content_id = None
        self.socket_fail_count = 100

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
            m4 = re.search('"contentId":"(?P<content_id>[^"]+)"', result)
            count = count + 1
            if count > self.socket_fail_count:
                self.status = None
                self.play_state = None
                self.status = None
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
        if m4 != None:
            #print "contentid:",m4.group("content_id")
            self.content_id = m4.group("content_id")


        payloadType = 0 #0=string
        data = "{MESSAGE_TYPE: 'SET_VOLUME','volume': {'level': 0.2}}"
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




    def get_status(self):
        return " ".join(["main_status:" , self.get_main_status() , "play_status:" , self.get_play_status()])

    def get_main_status(self):
        if self.status == None:
            status_str = "None"
        else:
            status_str = self.status
        return (status_str)

    def get_play_status(self):
        if self.play_state == None:
            play_state_str = "None"
        else:
            play_state_str = self.play_state
        return (play_state_str)


    def ready_to_play(self):
        if self.status == "Now Casting":
            return False
        if self.status == "Ready To Cast" or self.status == None or self.status == "Chromecast Home Screen":
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

        payloadType = 0 #0=string
        volume = min(max(0, round(0.1, 1)), 1)

        data = "{MESSAGE_TYPE: 'SET_VOLUME','volume': {'level': volume}}"
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

class manage_lightwave:
    def __init__(self):
        self.room = "Main\ Bedroom"
        self.device = "Screen"
        self.lightwave_cmd = "/usr/local/bin/lightwaverf"

    def start_screen(self):
        cmd = " ".join([self.lightwave_cmd, self.room, self.device, "on", ">cmd.log", "2>&1"])
        os.system(cmd)
        return(cmd)

    def stop_screen(self):
        cmd = " ".join([self.lightwave_cmd, self.room, self.device, "off", ">cmd.log", "2>&1"])
        os.system(cmd)
        return(cmd)

class lakkucast_media:
    def __init__(self):
        self.top_dir = "/data"
        self.top_url = "http://192.168.1.98"
        #self.media_dirs = ["media/test/sample1", "media/test/sample2"]
        self.media_dirs = ["media/TV-Shows/English/Friends", "media/TV-Shows/English/That 70s Show", "media/TV-Shows/English/Big Bang Theory"]
        self.media_data = "/data/webapps/lakku/lakkucast/media.dat"

    def random_play(self, num_play):
        count_dir = 0
        num_dirs = len(self.media_dirs)
        while count_dir < num_dirs:
            rand_main = randint(0, (len(self.media_dirs)-1))
            url_list = []
            sel_dir = os.path.join(self.top_dir, self.media_dirs[rand_main])
            if os.path.isdir(sel_dir):
                count_dir = count_dir + 1
                matches = []
                for root, dirnames, filenames in os.walk(sel_dir):
                    for filename in fnmatch.filter(filenames, '*.mp4'):
                        matches.append(os.path.join(root, filename).replace(self.top_dir,''))
                count = 1
                loop_count = 1
                while count <= num_play:
                    file_rand = randint(0, (len(matches)-1))
                    file_name = "".join([self.top_url , matches[file_rand]])
                    if self.played_before(file_name) == False:
                        if file_name not in url_list:
                            url_list.append(file_name)
                            count = count + 1
                    loop_count = loop_count + 1 
                    if loop_count == (len(matches)-1):
                        break
                if count < num_play:
                    continue
                else:
                    fhand = open(self.media_data, 'a+')
                    for u in url_list:
                        fhand.write(u+'\n')
                    fhand.close()
                    return url_list

    def played_before(self, media_name):
        if media_name in open(self.media_data).read():
            return True
        return False

    def reset_media_history(self):
        fhand = open(self.media_data, 'w')
        fhand.truncate()
        fhand.close()
  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="lakkucast")
    parser.add_argument("--play", help="Play x videos ")
    parser.add_argument("--stop", help="Stop playing and shutdown", action='store_true')
    parser.add_argument("--reset", help="Stop playing", action='store_true')
    parser.add_argument("--reset_media_history", help="Reset media history", action='store_true')

    args = parser.parse_args()

    log_file = "/data/webapps/lakku/lakkucast/lakkucast.log"
    log_level = logging.INFO
    logging.basicConfig(filename=log_file, level=log_level,
                        format='%(asctime)s [%(levelname)s] %(message)s')

    logging.info("Starting lakkucast.")

    if args.play:
        num_play = int(args.play) * 2
        logging.info("Play count: %s"
                % (args.play))
 
        lm = lakkucast_media()
        lwrf = manage_lightwave()
        logging.info("Sending start command to lwrf")
        logging.info(lwrf.start_screen())
        lwrf.start_screen()
        logging.info("Sleeping after lwrf start")
        url_list = lm.random_play(num_play)
        time.sleep(20)
        if url_list != None:
            logging.info("Got %d urls to play"
                % (len(url_list)))
            for u in url_list:
                logging.info("Trying URL: %s"
                    % (u))
                l = lakkucast()
                logging.info("Sleeping before main init")
                time.sleep(l.sleep_between_media)
                l.init_status()
                logging.info(l.get_status())
                if l.ready_to_play():
                    logging.info("Playing URL: %s"
                    % (u))
                    l.play_url(u)
                l.init_status()
                logging.info(l.get_status())
                while not l.ready_to_play():
                    time.sleep(l.sleep_between_media)
                    l.init_status()
                    logging.info(l.get_status())
            time.sleep(l.sleep_between_media)
            logging.info("Sending stop command to lwrf")
            logging.info(lwrf.stop_screen())
        else:
            logging.info("No urls returned by player")
            l.play_url("http://192.168.1.98/media/test/water.mp4")
            time.sleep(l.sleep_between_media)
            lwrf = manage_lightwave()
            logging.info("Sending stop command to lwrf")
            logging.info(lwrf.stop_screen())

    if args.stop:
        l = lakkucast()
        l.init_status()
        logging.info("Calling stop")
        logging.info(l.get_status())
        l.play_url("http://192.168.1.98/media/test/water.mp4")
        time.sleep(10)
        lwrf = manage_lightwave()
        logging.info("Sending stop command to lwrf")
        logging.info(lwrf.stop_screen())

    if args.reset:
        l = lakkucast()
        l.init_status()
        logging.info("Calling reset")
        logging.info(l.get_status())
        l.play_url("http://192.168.1.98/media/test/water.mp4")


    if args.reset_media_history:
        logging.info("Calling Reset media history")
        lm = lakkucast_media()
        lm.reset_media_history()
