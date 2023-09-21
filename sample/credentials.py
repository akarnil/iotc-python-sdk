"""
* ## Prerequisite parameter to run this sample code
* cpId         :: It need to get from the IoTConnect platform "Settings->Key Vault". 
* uniqueId     :: Its device ID which register on IotConnect platform and also its status has Active and Acquired
* env          :: It need to get from the IoTConnect platform "Settings->Key Vault". 
* interval     :: send data frequency in seconds
* sdkOptions   :: It helps to define the path of self signed and CA signed certificate as well as define the offline storage configuration.
"""


sdk_identity: str = "<< Get `Identity` from https://avnet.iotconnect.io/key-vault with options Language: Python and Version: 3.10.1 selected >>"
UniqueId: str = "<< `Unique ID` from your device on https://avnet.iotconnect.io/device/1 >>"


"""
* sdkOptions is optional. Mandatory for "certificate" X.509 device authentication type
* "certificate" : It indicated to define the path of the certificate file. Mandatory for X.509/SSL device CA signed or self-signed authentication type only.
* 	- SSLKeyPath: your device key
* 	- SSLCertPath: your device certificate
* 	- SSLCaPath : Root CA certificate
* 	- Windows + Linux OS: Use "/" forward slash (Example: Windows: "E:/folder1/folder2/certificate", Linux: "/home/folder1/folder2/certificate")
* "offlineStorage" : Define the configuration related to the offline data storage 
* 	- disabled : false = offline data storing, true = not storing offline data 
* 	- availSpaceInMb : Define the file size of offline data which should be in (MB)
* 	- fileCount : Number of files need to create for offline data
* "devicePrimaryKey" : It is optional parameter. Mandatory for the Symmetric Key Authentication support only. It gets from the IoTConnect UI portal "Device -> Select device -> info(Tab) -> Connection Info -> Device Connection".
    - - "devicePrimaryKey": "<<your Key>>"
* Note: sdkOptions is optional but mandatory for SSL/x509 device authentication type only. Define proper setting or leave it NULL. If you not provide the offline storage it will set the default settings as per defined above. It may harm your device by storing the large data. Once memory get full may chance to stop the execution.
"""
SdkOptions: dict ={
	"certificate" : { 
#		"SSLKeyPath"  : "",    #aws=pk_devicename.pem   ||   #az=device.key
#		"SSLCertPath" : "",    #aws=cert_devicename.crt ||   #az=device.pem
		"SSLCaPath"   : "./aws_cert/root-CA.pem"     #aws=root-CA.pem         ||   #az=rootCA.pem 
        
	},
    "devicePrimaryKey":"<< (OPTIONAL) Device -> Select device -> info(Tab) -> Connection Info -> Device Connection >>",
    "offlineStorage":{
        "disabled": False,
	    "availSpaceInMb": 0.01,
	    "fileCount": 5,
        #"keepalive":60
    }
    #"skipValidation":False,
	# As per your Environment(Azure or Azure EU or AWS) uncomment single URL and comment("#") rest of URLs.
    #"discoveryUrl":"https://eudiscovery.iotconnect.io", #Azure EU environment 
    #"discoveryUrl":"https://discovery.iotconnect.io", #Azure All Environment 
    #"discoveryUrl":"http://52.204.155.38:219", #AWS pre-QA Environment
    #"IsDebug": False
}

