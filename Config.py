import configparser
from collections import OrderedDict

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)
            

appKey=None
appName=None
appVersion=None
createTokenPwd=None
deviceId=None
deviceName=None
encrypy=None
osVersion=None
passwordType=None
platform=None        
account=None
enableProxy=None
server=None
port=None

enableProxy=None
server=None
port=None

size=None
startDate=None
endDate=None
login_info_list=[]

def loadConfig():
    global appKey, appName, appVersion,createTokenPwd, deviceId, deviceName,encrypy
    global osVersion, passwordType, password, platform
    # global account, password, sign 
    global enableProxy, server, port
    global size, startDate, endDate

    config = configparser.RawConfigParser(dict_type=MultiOrderedDict, strict=False)
    config.read(['config.ini'])

    #load INFO section
    appKey=config.get('INFO', 'appKey')
    appName=config.get('INFO', 'appName')
    appVersion=config.get('INFO', 'appVersion')
    createTokenPwd=config.get('INFO', 'createTokenPwd')
    deviceId=config.get('INFO', 'deviceId')
    deviceName=config.get('INFO', 'deviceName')
    encrypy=config.get('INFO', 'encrypy')
    osVersion=config.get('INFO', 'osVersion')
    passwordType=config.get('INFO', 'passwordType')
    platform=config.get('INFO', 'platform')        

    #load PROXY section
    enableProxy=config.get('PROXY', 'enableProxy')
    server=config.get('PROXY', 'server')
    port=config.get('PROXY', 'port')

    #load SALEREPORT section
    size=config.get('SALEREPORT', 'size')
    startDate=config.get('SALEREPORT', 'startDate')
    endDate=config.get('SALEREPORT', 'endDate')

    processLoginInfo(config.get('LOGIN', 'loginInfo'))
    
def processLoginInfo(loginInfo):
    login_list = loginInfo.split('\n')
    print(login_list)
    global login_info_list
    for userInfo in login_list:
        login = {}
        userInfo_list = userInfo.split(',')
        login.update({'account':userInfo_list[0]})
        login.update({'password':userInfo_list[1]})
        login.update({'sign':userInfo_list[2]})
        print(login['account'], login['password'], login['sign'])      
        login_info_list.append(login)
    return None

loadConfig()
print(login_info_list)
