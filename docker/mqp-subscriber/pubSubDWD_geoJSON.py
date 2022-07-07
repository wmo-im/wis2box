#!/usr/bin/python3
import pika 
import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
import sys
import os.path
import json
from jsonschema import validate
import time
from datetime import datetime
import argparse
import ssl
import socket

import logging
from logging.handlers import RotatingFileHandler

import urllib.request
import requests
import shutil
import hashlib
import base64
from websocket import create_connection
import uuid

##### Args #####
################

parser=argparse.ArgumentParser( \
     description='Subscribe to AMQPS message broker with config file' ,\
     formatter_class=argparse.ArgumentDefaultsHelpFormatter )
parser.add_argument('--config', default="", type=str, help='config file name')
args = parser.parse_args()

if args.config == "":
    print("Please use --config and config file name as argument for this script.")
    config_filename = ""
else:
    config_filename = args.config
    configFile = os.path.basename(config_filename)

##### functions #####
#####################

def init_log(logFile, logLevel, loggerName):
    global LOG
    handlers = [ RotatingFileHandler(filename=logFile,
            mode='a',
            maxBytes=512000,
            backupCount=2)
           ]
    logging.basicConfig(handlers=handlers,
                    level=logLevel,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%Y%m%dT%H:%M:%S')
    LOG = logging.getLogger(loggerName)

def timeLag(myPubTime):
    timeNow = datetime.now()
    printTimeNow = timeNow.strftime('%Y%m%dT%H%M%S')
    if "Z" in myPubTime:
        myPubTime = myPubTime.replace("Z","")
    if "z" in myPubTime:
        myPubTime = myPubTime.replace("z","")
    if "." in myPubTime:
        if len(myPubTime) > 22:
            LOG.debug(" - myPubTime reduced to 22 digits")
            myPubTime = myPubTime[0:22]
        pubTimeDate = datetime.strptime(myPubTime, "%Y%m%dT%H%M%S.%f")
    else:
        pubTimeDate = datetime.strptime(myPubTime, "%Y%m%dT%H%M%S")
    if timeNow > pubTimeDate:
        myTimeLag = timeNow - pubTimeDate
        myTimeLagSec = myTimeLag.total_seconds()
        myTimeLagSec = round(myTimeLagSec,2)
    else:
        myTimeLagSec = "now before pubTime"
    return myTimeLagSec

# aria2
def connect2aria2(aria2_ws_url):
    myWebsocket = create_connection(aria2_ws_url)
    return myWebsocket

def getAria2Status(my_gid):
    jsonreq_status = json.dumps({'jsonrpc':'2.0', 'id':'sub_client_wis2box_dwd', 'method': 'aria2.tellStatus', 'params':['token:P3TERX', my_gid, ["status"]]})
    ws.send(jsonreq_status)
    LOG.info(" - tellStatus aria2 for gid: " + str(my_gid) + " is: " + str(jsonreq_status))

def listen4msg(myWebsocket):
    global listen4msg_started, watchlist_downloads, download_targetDir
    list_empty=False
    while not list_empty:
        message = myWebsocket.recv()
        listen4msg_started = True
        msg_json = json.loads(message)
        LOG.debug(msg_json)
        response_params = msg_json["params"][0]
        response_gid = response_params["gid"]
        if "aria2.onDownloadError" in msg_json["method"]:
            LOG.error(" - aria2.onDownloadError for gid: " + str(watchlist_downloads[response_gid]))
            getAria2Status(response_gid)
            if response_gid in watchlist_downloads.keys():
                watchlist_downloads.pop(response_gid)
                count = len(watchlist_downloads.keys())
                LOG.debug(" - watchlist_downloads count: " + str(count))
                if count == 0:
                    list_empty = True
                    listen4msg_started = False
        if "aria2.onDownloadComplete" in msg_json["method"]:
            LOG.info(" - aria2.onDownloadComplete for gid: " + response_gid)
            if response_gid in watchlist_downloads.keys(): 
                # write empty file with data_id in name
                my_data_id = watchlist_downloads[response_gid]["data_id"]
                myFilename = my_data_id.replace("/",data_id_replace)
                myDataIDsDir = os.path.join(download_targetDir,dataID_infoFile_dir)
                if not os.path.exists(myDataIDsDir):
                    os.makedirs(myDataIDsDir)
                fullpath = os.path.join(myDataIDsDir,myFilename)
                dataIDFile = open(fullpath, "w")
                dataIDFile.write("\n")
                dataIDFile.close()
                LOG.info(" - aria2.onDownloadComplete for data_id: " + str(my_data_id))                
                # remove from watchlist_downloads
                watchlist_downloads.pop(response_gid)
                LOG.debug(" - deleted gid " + response_gid + " from watchlist_downloads")
                # watchlist_downloads empty
                count = len(watchlist_downloads.keys())
                LOG.debug(" - watchlist_downloads count: " + str(count))
                if count == 0:
                    list_empty = True
                    listen4msg_started = False
            else:
                LOG.error(" - aria2.onDownloadComplete gid (" + response_gid + ") missed in watchlist_downloads")

def send2aria(aria2_http_url, download_url, data_id):
    global listen4msg_started, watchlist_downloads, ws
    aria2_id = str(uuid.uuid1())
    jsonreq = json.dumps({'jsonrpc':'2.0', 'id':aria2_id, 'method':'aria2.addUri', 'params':['token:P3TERX',[download_url]]})
    aria2_downloadReqResponse = requests.post(aria2_http_url, jsonreq)
    aria2_downloadReqResult = aria2_downloadReqResponse.text
    LOG.debug(aria2_downloadReqResult)
    if "result" in aria2_downloadReqResult:
        aria2_downloadReqResult_json = json.loads(aria2_downloadReqResult)
        download_gid = aria2_downloadReqResult_json['result']
        LOG.info(" - start aria2 download with gid: " + str(download_gid))
        watchlist_item = {download_gid: {"data_id": data_id, "url": download_url}}
        watchlist_downloads.update(watchlist_item)
        LOG.debug(" - added new item to watchlist_downloads: " + str(watchlist_item))
        LOG.debug(" - listen4msg_started is: " + str(listen4msg_started))
        if not listen4msg_started:
            listen4msg(ws)
    else:
        LOG.error(" - send2aria error result: " + str(aria2_downloadReqResult))
        LOG.error(" - send2aria url: " + download_url)
        LOG.error(" - send2aria data_id: " + data_id)

def close_connect2aria2(myWebsocket):
    myWebsocket.close()

# should we download
def alreadyDownloaded(targetDir, my_data_id):
    already_downloaded = False
    myFilename = my_data_id.replace("/",data_id_replace) 
    myDataIDsDir = os.path.join(targetDir,dataID_infoFile_dir)
    if not os.path.exists(myDataIDsDir):
        os.makedirs(myDataIDsDir)
    fullpath = os.path.join(myDataIDsDir,myFilename)
    if os.path.exists(fullpath):
        LOG.info(" - " + myFilename + " already downloaded")
        already_downloaded = True
    return already_downloaded

def inWhitelist(url):
    my_inWhitelist=False
    if download_whitelist != "":
        for item in myWhitelist:
            if item in url:
                my_inWhitelist=True
    else:
        # no whitelist value in config file, download from everywhere
        my_inWhitelist=True
    if not inWhitelist:
        LOG.error(" - domain of " + url + " NOT in whitelist")
    return my_inWhitelist


# mqtt(s)
def on_mqtt_message(client, userdata, message):
    global integrity_method, download_targetDir, ws, aria2_http_url
    pubTime_error = False
    LOG.info(" ---- NEW MESSAGE ----")
    try:
        topic = message.topic
        msg = json.loads(message.payload.decode("utf-8"))
        #validate(instance=msg, schema=schema)
        #LOG.debug("validated msg: " + str(topic))
    #except jsonschema.exceptions.ValidationError as err:
        #LOG.error("validation error occured for msg: " + message.payload.decode("utf-8"))
        #LOG.error(err)
    except Exception as e:
        msg = ""
        LOG.error(" - json loads error occured for msg: " + message.payload.decode("utf-8"))
        LOG.error(" - on_mqtt_message payload error: " + str(e))

    if msg != "":
        # read message fields
        showTimeLag = "False"
        if "publication_datetime" in msg["properties"]:
            time_lag = timeLag(msg["properties"]["publication_datetime"])
            showTimeLag = "True"
        url = ""
        if "links" in msg["properties"].keys():
            LOG.debug("links under properties")
            urlList = msg["properties"]["links"]
            for item in urlList:
                if item["rel"] == "canonical":
                    url = item["href"]
        else:
            if "links" in msg.keys():
                #LOG.debug("links direct in msg")
                urlList = msg["links"]
                for item in urlList:
                    if item["rel"] == "canonical":
                        url = item["href"]
            else:
                LOG.error(" - no links in message: " + message.payload.decode("utf-8"))
                url = ""
        integrity_method = msg["properties"]["integrity"]["method"]
        if integrity_method == "":
            LOG.error(" - no integrity_method in message: " + message.payload.decode("utf-8"))
        else:
            if integrity_method != "md5" and integrity_method != "MD5" and integrity_method != "sha256" and integrity_method != "SHA256" and integrity_method != "sha512" and integrity_method != "SHA512":
                LOG.error(" - integrity_method in message neither md5 nor sha256 nor sha512. Integrity_method: " + integrity_method + "(message: " + message.payload.decode("utf-8") + ")")

        data_identifier = ""
        if "data_id" in msg["properties"]:
            data_identifier = msg["properties"]["data_id"]
            data_identifier = data_identifier.replace("//","/")
        LOG.info(" - message data id: " + str(data_identifier))

        # write message to log if config show_message
        if show_message == "True":
            LOG.info(" - message topic:       " + str(topic))
            LOG.info(" - message id:       " + str(msg["id"]))
            LOG.info(" - message data id:     " + str(data_identifier))
            if showTimeLag == "True":
                LOG.info(" - message publication_datetime:     " +  str(msg["properties"]["publication_datetime"]))
                LOG.info(" - message time lag:    " + str(time_lag) + "[sec]")
                LOG.info(" - message url:         " + str(url))
                LOG.info(" - message content:     " + message.payload.decode("utf-8"))

        # msg_store
        if msg_store is not None and msg_store != "":
            fname_identifer = data_identifier.replace("/",data_id_replace)
            fname = fname_identifer
            toFilename = msg_store +  printTimeNow + "_msg_" + str(fname) + ".txt"
            toFile = open(toFilename, "w")
            toFile.write(topic + "\n")
            toFile.write(str(message.payload.decode("utf-8")))
            toFile.close()

        # download
        if withDownload == "True":
            # aria2 download start
            already_there = False
            already_there = alreadyDownloaded(download_targetDir, data_identifier)
            LOG.debug(" - alreadyDownloaded: " + str(already_there))
            if not already_there:
                inWhilelist = inWhitelist(url)
                if inWhilelist:
                    LOG.debug(" - domain in whitelist, url: " + str(url))
                    send2aria(aria2_http_url, url, str(data_identifier))
                else:
                    LOG.error(" - domain of URL not in Whitelist: " + str(url))

            # write txt file if content in message
            if content_encoding != "" and content_value != "":
                fname = "missingFilename"
                if "data_id" in msg["properties"]:
                    fname_identifer = data_identifier.replace("/",data_id_replace)
                    fname = fname_identifer
                else:
                    LOG.error(" - missing data_id in msg with content")
                LOG.debug("info - download filename is: " + fname)
                downloadFile  = (download_targetDir + '/' + fname).replace('//','/')
                # already written
                already_written=False
                already_written=alreadyDownloaded(download_targetDir, data_identifier)
                if not already_written:
                    if url == "":
                        fileContent = '{"topic":"' + method.routing_key + '", "content_encoding":"' + content_encoding + '", "content_value":"' + content_value +'", "msg_id":"' + str(msg["id"]) +'"}'
                    else:
                        fileContent = '{"downloadFilename":"' + downloadFile + '", "integrity":"' + msg["properties"]["integrity"]["value"] + '", "integrity_method":"' + integrity_method + '", "sourceUrl": "' + url + '", "content_encoding":"' + content_encoding + '", "content_value":"' + content_value +'", "data_id":"' + str(msg["properties"]["data_id"]) + '"}'
                    fileContentJSON = json.loads(fileContent)
                    if "topic" in fileContentJSON.keys():
                        toDownloadFile = "msgContent_" + printTimeNow + ".json"
                        newDownload = open(download_targetDir + toDownloadFile,"w")
                        newDownload.write(json.dumps(fileContentJSON, indent=4))
                        newDownload.close()

# mqtt(s)
def on_connect(client, userdata, flags, rc, properties=None):
    global Connected
    LOG.info(" ---- NEW MQTT CONNECT ----")
    LOG.info(" - on_connect code is: " + str(rc))
    timeNow = datetime.now()
    printTimeNow = timeNow.strftime('%Y%m%dT%H%M%S')
    if rc==0:
       Connected=True
       client.connected_flag=True
       result = client.subscribe(sub_topic, qos=1, options=None, properties=None)
       if result[0] == 0:
           LOG.info(" - subscribed to topic: " + str(sub_topic) + " as " + sub_clientname)
           Subscribed=True
       else:
           LOG.error(" - connection failed with result code: " + str(rc))
           # MQTT on_connect result codes: 
           # 1 - Connection rejected for unsupported protocol version, 
           # 2 - Connection rejected for rejected client ID, 
           # 3 - Connection rejected for unavailable server, 
           # 4 - Connection rejected for damaged username or password, 
           # 5 - Connection rejected for unauthorized

def on_disconnect(client, userdata, rc, properties=None):
  global Connected
  global Subscribed
  Connected=False
  client.connected_flag = False
  Subscribed=False

##### declaration #####
#######################

Connected=False
channel_closed = True
connection_closed = True
toBeClosed = False
Subscribed=False
integrity_method = ""
withDownload = "False"
toPublish = "False"
toSubscribe = "False"
content_encoding = ""
content_value = ""
reconnect_count = 1
timeNow = datetime.now()
printTimeNow = timeNow.strftime('%Y%m%dT%H%M%S')
aria2_ws_url = "ws://aria2-pro:6800/jsonrpc"
aria2_http_url = "http://aria2-pro:6800/jsonrpc"
watchlist_downloads = json.loads('{}')
listen4msg_started = False
data_id_replace = "__"
download_whitelist = ""
dataID_infoFile_dir = "dataIDs/"

##### read config file #####
############################

configFile = configFile.replace(".json","")
if config_filename == "":
    print("error - config file: no config file.")
else:
    ## read config
    with open(config_filename, 'r') as myConfigFile:
        data = myConfigFile.read()
    myConfig = json.loads(data)

    ## subscribe
    if "toSubscribe" in myConfig.keys():
        toSubscribe = myConfig["toSubscribe"]
    else:
        print("error - config file: missing toSubscribe in config file, set value to False")
        toSubscribe = "False"
    if toSubscribe == "True":
        # mandatory
        if "sub_protocol" in myConfig.keys() and "sub_host" in myConfig.keys() and "sub_port" in myConfig.keys() and "sub_user" in myConfig.keys() and "sub_password" in myConfig.keys():
            sub_protocol = myConfig["sub_protocol"]
            sub_host = myConfig["sub_host"]
            sub_port = myConfig["sub_port"]
            sub_user = myConfig["sub_user"]
            sub_password = myConfig["sub_password"]
        else:
            print("error - config file: missing mandatory value in config file. Mandatory values are: sub_protocol, sub_host, sub_port, sub_user, sub_password")

        if "sub_logfile" in myConfig.keys():
            sub_logfile = myConfig["sub_logfile"]
        else:
            sub_logfile = "sub_connect_" + printTimeNow  + ".log"
        if "sub_loglevel" in myConfig.keys():
            sub_loglevel = myConfig["sub_loglevel"]
        else:
            sub_loglevel = "INFO"

        if sub_protocol == "mqtts" or sub_protocol == "mqtt":
            sub_cacert = myConfig["sub_cacert"]
            sub_topic = myConfig["sub_topic"]
            if "sub_maxMSGsize" in myConfig.keys():
                sub_maxMSGsize = myConfig["sub_maxMSGsize"]
            sub_clientname = socket.gethostname()
            
            if "sub_clientname" in myConfig.keys():
                if myConfig["sub_clientname"] != "":
                    sub_clientname = sub_clientname + "_" + myConfig["sub_clientname"]
            if sub_clientname == sub_host or sub_host == "localhost":
                sub_clientname = sub_clientname + "_subClient"
            if "sub_protocol_version" in myConfig.keys():
                sub_protocol_version = myConfig["sub_protocol_version"]
            else:
                sub_protocol_version = "MQTTv5"
        sub_brokerAddress = sub_protocol + "://" + sub_user + ":" + sub_password + "@" + sub_host + ":" + sub_port
        message_broker = sub_protocol + "://" + sub_user + ":[passwd]@" + sub_host + ":" + sub_port

    show_message =  myConfig["show_message"]

    ## msg_store 
    if "msg_store" in myConfig.keys():
        msg_store = myConfig["msg_store"]
    else:
        msg_store = None

    ## download
    if "withDownload" in myConfig.keys():
        withDownload = myConfig["withDownload"]
    else:
        print("error -  config file: missing withDownload in config file, set value to False")
        withDownload = "False"
    if withDownload == "True":
        if "download_targetDir" in myConfig.keys():
            download_targetDir = myConfig["download_targetDir"]
        if "filedownloadURL" in myConfig.keys(): 
            filedownloadURL = myConfig["filedownloadURL"]
        else:
            filedownloadURL = "True"
        if "download_proxy" in myConfig.keys():
            download_proxy = myConfig["download_proxy"]
        else:
            download_proxy = ""
        if "download_restricted" in myConfig.keys():
            download_restricted = myConfig["download_restricted"]
        else:
            download_restricted = "False"
        if download_restricted == "True":
            if "download_username" in myConfig.keys():
                download_username = myConfig["download_username"]
            else:
                download_username = ""
            if "download_password" in myConfig.keys():
                download_password =  myConfig["download_password"]
            else:
                download_password = ""
        if "download_whitelist" in myConfig.keys():
            download_whitelist = myConfig["download_whitelist"]
        else:
            download_whitelist = ""

myWhitelist = []
if download_whitelist != "":
    with open(download_whitelist) as fp:
        for line in fp:
            line = line.replace("\n","")
            if line not in myWhitelist:
                myWhitelist.append(line)


##### programm #####
####################

# LOG
loggerName = "subscribe" + str(configFile)
LOG = None
init_log(sub_logfile,sub_loglevel,loggerName)
LOG.info(" ---- NEW SCRIPT RUN ----")
LOG.info(" whitelist is: " + download_whitelist)
for item in myWhitelist:
    LOG.info(" in whitelist: " + str(item))

schema = json.load(open("message-schema.json"))

# start connection to aria2 websocket
ws = connect2aria2(aria2_ws_url)

# subscribe
if toSubscribe == "True":
        if sub_protocol == "mqtts" or sub_protocol == "mqtt":
            LOG.info(" - subscribed with protocol mqtt(s)") 
            if not toBeClosed:
                if sub_protocol_version == "MQTTv5":
                    client = mqtt.Client(sub_clientname, protocol=mqtt.MQTTv5)
                else:
                    client = mqtt.Client(sub_clientname, protocol=mqtt.MQTTv311)
                client.username_pw_set(sub_user, password=sub_password)
                if sub_protocol == "mqtts":
                    if sub_cacert != "":
                        #client.tls_set(ca_certs=sub_cacert,tls_version=ssl.PROTOCOL_TLSv1_2,cert_reqs=ssl.CERT_NONE)
                        client.tls_set(ca_certs=sub_cacert,tls_version=ssl.PROTOCOL_TLSv1_2)
                    else:
                        client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
                    if sub_host == "localhost" or sub_host == "127.0.0.1":
                        client.tls_insecure_set(True)
                client.connected_flag=False
                client.on_message=on_mqtt_message
                client.on_connect=on_connect
                client.on_disconnect=on_disconnect
                if sub_protocol_version == "MQTTv5":
                    sub_properties=Properties(PacketTypes.CONNECT)
                    sub_properties.MaximumPacketSize=sub_maxMSGsize
                else:
                    sub_properties=None
                client.connect(sub_host,port=int(sub_port),properties=sub_properties)
                client.loop_start()
                time.sleep(2)
                if not client.connected_flag:
                    for x in range(5):
                        if not client.connected_flag:
                            LOG.info(" - in wait loop to connect")
                            time.sleep(2)
                if not client.connected_flag:
                    LOG.error(" - no initial sub connection possible")
                    toBeClosed = True
                    client.disconnect()
                    client.loop_stop() 
                try:
                    if client.connected_flag:
                        while True:
                            if not client.connected_flag:
                                if not toBeClosed:
                                    client.connect(sub_host,port=int(sub_port),properties=sub_properties) #connect to broker
                except KeyboardInterrupt:
                    print("info - exiting")
                    client.disconnect()
                    client.loop_stop() #stop the loop
            else:
                LOG.info(" - exiting")

close_connect2aria2(ws)
