"""
  ******************************************************************************
  * @file   : iotconnect-sdk-1.0-firmware-python_msg-2_1.py
  * @author : Softweb Solutions An Avnet Company
  * @modify : 02-January-2023
  * @brief  : Firmware part for Python SDK 1.0
  ******************************************************************************
"""

"""
 * Hope you have installed the Python SDK v1.0 as guided in README.md file or from documentation portal. 
 * Import the IoTConnect SDK package and other required packages
"""

# OTA this sample can perform OTA updates, requirements of the OTA payload
# OTA payload must be a single file of file extension .tar.gz
# OTA update version of the main .py file must be called the same as a previous version otherwise it will not load

app_version: str = "1.0"

import sys
import json
import time
import threading
import random

# if iotconnect module is not installed then use the local one
# note: this is if you are running the sample in the git repository folder
try:
    from iotconnect import IoTConnectSDK
except:
    sys.path.append("iotconnect-sdk-1.0")
    from iotconnect import IoTConnectSDK

from datetime import datetime
import os

import tarfile
import shutil
from urllib.request import urlretrieve 


import credentials
UniqueId: str = credentials.UniqueId 
sdk_identity: str = credentials.sdk_identity
SdkOptions: dict = credentials.SdkOptions

app_paths: dict = {
    "app_name": None,
    "primary_app_dir": None,
    "secondary_app_dir": None,
    "tarball_download_dir": None,
    "tarball_extract_dir": None,
    "module_name": None,
    "main_dir": None
}

ota_finished_need_exit: bool = False

def ota_extract_to_a_and_move_old_a_to_b(tarball_name:str):
    # extract tarball to new directory
    file = tarfile.open(app_paths["main_dir"] + app_paths["tarball_download_dir"] + tarball_name)
    file.extractall(app_paths["main_dir"] + app_paths["tarball_extract_dir"])
    file.close()

    # rm secondary dir
    path = app_paths["main_dir"] + app_paths["secondary_app_dir"]
    shutil.rmtree(path, ignore_errors=True)

    # move primary to secondary
    os.rename(app_paths["main_dir"] + app_paths["primary_app_dir"], app_paths["main_dir"] + app_paths["secondary_app_dir"])

    # copy extracted dir to primary dir
    src = app_paths["main_dir"] + app_paths["tarball_extract_dir"]
    dst = app_paths["main_dir"] + app_paths["primary_app_dir"]
    shutil.copytree(src, dst)

    # delete temp folders
    shutil.rmtree(app_paths["main_dir"] + app_paths["tarball_download_dir"], ignore_errors=True)
    shutil.rmtree(app_paths["main_dir"] + app_paths["tarball_extract_dir"], ignore_errors=True)

def ota_backup_primary():
    src = app_paths["main_dir"] + app_paths["primary_app_dir"]
    dst = app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"]
    shutil.copytree(src, dst)

def ota_restore_primary():
    shutil.rmtree(app_paths["main_dir"] + app_paths["primary_app_dir"], ignore_errors=True)
    os.rename(app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"], app_paths["main_dir"] + app_paths["primary_app_dir"])

def ota_delete_primary_backup():
    shutil.rmtree(app_paths["main_dir"] + app_paths["primary_app_backup_folder_name"], ignore_errors=True)

Sdk=None
interval = 30
directmethodlist={}
ACKdirect=[]
device_list=[]



"""
 * Type    : Callback Function "DeviceCallback()"
 * Usage   : Firmware will receive commands from cloud. You can manage your business logic as per received command.
 * Input   :  
 * Output  : Receive device command, firmware command and other device initialize error response 
"""

def DeviceCallback(msg):
    global Sdk
    print("\n--- Command Message Received in Firmware ---")
    print(json.dumps(msg))
    cmdType = None
    if msg != None and len(msg.items()) != 0:
        cmdType = msg["ct"] if "ct"in msg else None
    # Other Command
    if cmdType == 0:
        """
        * Type    : Public Method "sendAck()"
        * Usage   : Send device command received acknowledgment to cloud
        * 
        * - status Type
        *     st = 6; // Device command Ack status 
        *     st = 4; // Failed Ack
        * - Message Type
        *     msgType = 5; // for "0x01" device command 
        """
        data=msg
        if data != None:
            #print(data)
            if "id" in data:
                if "ack" in data and data["ack"]:
                    Sdk.sendAckCmd(data["ack"],7,"successful",data["id"])  #fail=4,executed= 5,success=7,6=executed ack
            else:
                if "ack" in data and data["ack"]:
                    Sdk.sendAckCmd(data["ack"],7,"successful") #fail=4,executed= 5,success=7,6=executed ack
    else:
        print("rule command",msg)

    # Firmware Upgrade
def DeviceFirmwareCallback(msg):
    global Sdk,device_list, ota_finished_need_exit
    print("\n--- firmware Command Message Received ---")
    print(json.dumps(msg))
    cmdType = None
    if msg != None and len(msg.items()) != 0:
        cmdType = msg["ct"] if msg["ct"] != None else None

    if cmdType == 1:
        """
        * Type    : Public Method "sendAck()"
        * Usage   : Send firmware command received acknowledgement to cloud
        * - status Type
        *     st = 7; // firmware OTA command Ack status 
        *     st = 4; // Failed Ack
        * - Message Type
        *     msgType = 11; // for "0x02" Firmware command
        """
        # data = msg
        # if data != None:
        #     if ("urls" in data) and data["urls"]:
        #         for url_list in data["urls"]:
        #             if "tg" in url_list:
        #                 for i in device_list:
        #                     if "tg" in i and (i["tg"] == url_list["tg"]):
        #                         Sdk.sendOTAAckCmd(data["ack"],0,"successful",i["id"]) #Success=0, Failed = 1, Executed/DownloadingInProgress=2, Executed/DownloadDone=3, Failed/DownloadFailed=4
        #             else:
        #                 Sdk.sendOTAAckCmd(data["ack"],0,"successful") #Success=0, Failed = 1, Executed/DownloadingInProgress=2, Executed/DownloadDone=3, Failed/DownloadFailed=4

        payload_valid: bool = False
        data = msg

        if data != None:
            if ("urls" in data) and len(data["urls"]) == 1:                
                if ("url" in data["urls"][0]) and ("fileName" in data["urls"][0]):
                    if (data["urls"][0]["fileName"].endswith(".gz")):
                        payload_valid = True   

            if payload_valid is True:
                urls = data["urls"][0]
                Sdk.sendOTAAckCmd(data["ack"],2,"downloading payload")
                
                # download tarball from url to download_dir
                url: str = urls["url"]
                download_filename: str = urls["fileName"]
                final_folder_dest:str = app_paths["main_dir"] + app_paths["tarball_download_dir"]
                if os.path.exists(final_folder_dest) == False:
                    os.mkdir(final_folder_dest)
                urlretrieve(url, final_folder_dest + download_filename)

                Sdk.sendOTAAckCmd(data["ack"],3,"payload downloaded")
                
                ota_finished_need_exit = False
                ota_backup_primary()
                try:
                    ota_extract_to_a_and_move_old_a_to_b(download_filename)
                    ota_finished_need_exit = True
                except:
                    ota_restore_primary()
                    Sdk.sendOTAAckCmd(data["ack"],4,"OTA FAILED")
                    ota_finished_need_exit = False

                if ota_finished_need_exit:
                    ota_delete_primary_backup()
                    Sdk.sendOTAAckCmd(data["ack"],0,"OTA complete, restarting")
                    return
        
    Sdk.sendOTAAckCmd(data["ack"],4,"OTA FAILED, invalid payload")


def DeviceConnectionCallback(msg):  
    cmdType = None
    if msg != None and len(msg.items()) != 0:
        cmdType = msg["ct"] if msg["ct"] != None else None
    #connection status
    if cmdType == 116:
        #Device connection status e.g. data["command"] = true(connected) or false(disconnected)
        print(json.dumps(msg))

"""
 * Type    : Public Method "UpdateTwin()"
 * Usage   : Update the twin reported property
 * Input   : Desired property "key" and Desired property "value"
 * Output  : 
"""
# key = "<< Desired property key >>"; // Desired property key received from Twin callback message
# value = "<< Desired Property value >>"; // Value of respective desired property
# Sdk.UpdateTwin(key,value)

"""
 * Type    : Callback Function "TwinUpdateCallback()"
 * Usage   : Manage twin properties as per business logic to update the twin reported property
 * Input   : 
 * Output  : Receive twin Desired and twin Reported properties
"""
def TwinUpdateCallback(msg):
    global Sdk
    if msg:
        print("--- Twin Message Received ---")
        print(json.dumps(msg))
        if ("desired" in msg) and ("reported" not in msg):
            for j in msg["desired"]:
                if ("version" not in j) and ("uniqueId" not in j):
                    Sdk.UpdateTwin(j,msg["desired"][j])

"""
 * Type    : Public data Method "SendData()"
 * Usage   : To publish the data on cloud D2C 
 * Input   : Predefined data object 
 * Output  : 
"""
def sendBackToSDK(sdk, dataArray):
    sdk.SendData(dataArray)
    time.sleep(interval)

def DirectMethodCallback1(msg,methodname,rId):
    global Sdk,ACKdirect
    print(msg)
    print(methodname)
    print(rId)
    data={"data":"succeeded"}
    #return data,200,rId
    ACKdirect.append({"data":data,"status":200,"reqId":rId})
    #Sdk.DirectMethodACK(data,200,rId)

def DirectMethodCallback(msg,methodname,rId):
    global Sdk,ACKdirect
    print(msg)
    print(methodname)
    print(rId)
    data={"data":"fail"}
    #return data,200,rId
    ACKdirect.append({"data":data,"status":200,"reqId":rId})
    #Sdk.DirectMethodACK(data,200,rId)

def DeviceChangCallback(msg):
    print(msg)

def InitCallback(response):
    print(response)

def delete_child_callback(msg):
    print(msg)

def attributeDetails(data):
    print ("attribute received in firmware")
    print (data)
    



def main(app_paths_in:dict):
    global sdk_identity,SdkOptions,Sdk,ACKdirect,device_list

    global app_paths 
    app_paths = app_paths_in

    global ota_finished_need_exit

    print("basic sample version " + app_version)
    try:
        """
        if SdkOptions["certificate"]:
            for prop in SdkOptions["certificate"]:
                if os.path.isfile(SdkOptions["certificate"][prop]):
                    pass
                else:
                    print("please give proper path")
                    break
        else:
            print("you are not use auth type CA sign or self CA sign ") 
        """    
        """
        * Type    : Object Initialization "IoTConnectSDK()"
        * Usage   : To Initialize SDK and Device connection
        * Input   : cpId, uniqueId, sdkOptions, env as explained above and DeviceCallback and TwinUpdateCallback is callback functions
        * Output  : Callback methods for device command and twin properties
        """
        with IoTConnectSDK(UniqueId,sdk_identity,SdkOptions,DeviceConnectionCallback) as Sdk:
            try:
                """
                * Type    : Public Method "GetAllTwins()"
                * Usage   : Send request to get all the twin properties Desired and Reported
                * Input   : 
                * Output  : 
                """
                Sdk.onDeviceCommand(DeviceCallback)
                Sdk.onTwinChangeCommand(TwinUpdateCallback)
                Sdk.onOTACommand(DeviceFirmwareCallback)
                Sdk.onDeviceChangeCommand(DeviceChangCallback)
                Sdk.getTwins()
                device_list=Sdk.Getdevice()
                #Sdk.delete_child("childid",delete_child_callback)

                #Sdk.UpdateTwin("ss01","mmm")
                #sdk.GetAllTwins()
                # Sdk.GetAttributes(attributeDetails)
                while True:

                    if ota_finished_need_exit == True:
                        print("OTA is complete, exiting")
                        break
                    #Sdk.GetAttributes()
                    """
                    * Non Gateway device input data format Example:
					
                    """

                    
                    data = {
                    "sw_version": app_version,
                    "temperature":random.randint(30, 50),
                    "long1":random.randint(6000, 9000),
                    "integer1": random.randint(100, 200),
                    "decimal1":random.uniform(10.5, 75.5),
                    "date1":datetime.utcnow().strftime("%Y-%m-%d"),
                    "time1":"11:55:22",
                    "bit1":1,
                    "string1":"red",
                    "datetime1":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "gyro": {
                        'bit1':0,
                        'boolean1': True,
                        'date1': datetime.utcnow().strftime("%Y-%m-%d"),
                        "datetime1": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        "decimal1":random.uniform(10.5, 75.5),
                        "integer1":random.randint(60, 600),
                        "latlong1":[random.uniform(10.5, 75.5),random.uniform(10.5, 75.5)],
                        "long1":random.randint(60, 600000),
                        "string1":"green",
                        "time1":"11:44:22",
                        "temperature":random.randint(50, 90)
                        }
                        }
                    dObj = [{
                        "uniqueId": UniqueId,
                        "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        "data": data
                    }]
                    

                    """
                    * Gateway device input data format Example:
                    """
                    
                    
                    # dObj = [{
                    #             "uniqueId":UniqueId,
                    #             "time":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    #             "data": {
                    #                     "temperature":-2147483649,
                    #                     "decimal1":8121.2,
                    #                     "long1":9007199254740991,
                    #                     "gyro": {
                    #                         'bit1':0,
                    #                         'boolean1': True,
                    #                         'date1': datetime.utcnow().strftime("%Y-%m-%d"),
                    #                         "datetime1": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    #                         "decimal1":2.555,
                    #                         "integer1":884,
                    #                         "latlong1":78945,
                    #                         "long1":999,
                    #                         "string1":"green",
                    #                         "time1":"11:44:22",
                    #                         "temperature":22
                    #                         }
                    #                     }
                    #             },
                    #             {
                    #             "uniqueId":UniqueId+"c",
                    #             "time":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    #             "data": {
                    #                     "temperature":2323,
                    #                     "decimal1":2.555,
                    #                     "long1":36544,
                    #                     "gyro": {
                    #                         'bit1':0,
                    #                         'boolean1': True,
                    #                         'date1': datetime.utcnow().strftime("%Y-%m-%d"),
                    #                         "datetime1": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    #                         "decimal1":2.555,
                    #                         "integer1":884,
                    #                         "latlong1":78945,
                    #                         "long1":999,
                    #                         "string1":"green",
                    #                         "time1":"11:44:22",
                    #                         "temperature":10
                    #                         }
                    #                     }
                    #             }
                                # {
                                # "uniqueId":UniqueId+"c1",
                                # "time":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                # "data": {
                                #         "Temperature":"hi",
                                #         "gyro": {
                                #             'bit1':0,
                                #             'boolean1': True,
                                #             'date1': datetime.utcnow().strftime("%Y-%m-%d"),
                                #             "datetime1": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                #             "decimal1":2.555,
                                #             "integer1":884,
                                #             "latlong1":78945,
                                #             "long1":999,
                                #             "string1":"green",
                                #             "time1":"11:44:22",
                                #             "temperature":10
                                #             }
                                #         }
                                # }
                            # ]
                                

                    
                    """
                    * Add your device attributes and respective value here as per standard format defined in sdk documentation
                    * "time" : Date format should be as defined //"2021-01-24T10:06:17.857Z" 
                    * "data" : JSON data type format // {"temperature": 15.55, "gyroscope" : { 'x' : -1.2 }}
                    """
                    #dataArray.append(dObj)
                    #print (dObj)      
                    sendBackToSDK(Sdk, dObj)
                    
            except KeyboardInterrupt:
                print ("Keyboard Interrupt Exception")
                # os.execl(sys.executable, sys.executable, *sys.argv)
                os.abort()
                # sys.exit(0)
                
                
    except Exception as ex:
        # print(ex.message)
        sys.exit(0)

if __name__ == "__main__":
    print("execute from main.py")
