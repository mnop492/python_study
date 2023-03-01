import configparser
from collections import OrderedDict

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)
            
class Config():
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

    def __init__(self, path):
        config = configparser.RawConfigParser(dict_type=MultiOrderedDict, strict=False)
        config.read([path])

        #load INFO section
        self.appKey=config.get('INFO', 'appKey')
        self.appName=config.get('INFO', 'appName')
        self.appVersion=config.get('INFO', 'appVersion')
        self.createTokenPwd=config.get('INFO', 'createTokenPwd')
        self.deviceId=config.get('INFO', 'deviceId')
        self.deviceName=config.get('INFO', 'deviceName')
        self.encrypy=config.get('INFO', 'encrypy')
        self.osVersion=config.get('INFO', 'osVersion')
        self.passwordType=config.get('INFO', 'passwordType')
        self.platform=config.get('INFO', 'platform')        

        #load PROXY section
        self.enableProxy=config.get('PROXY', 'enableProxy')
        self.server=config.get('PROXY', 'server')
        self.port=config.get('PROXY', 'port')

        #load SALEREPORT section
        self.size=config.get('SALEREPORT', 'size')
        self.startDate=config.get('SALEREPORT', 'startDate')
        self.endDate=config.get('SALEREPORT', 'endDate')
        self.processLoginInfo(config.get('LOGIN', 'loginInfo'))       
                
    def processLoginInfo(self, loginInfo):       
        login_list = loginInfo.split('\n')
        for userInfo in login_list:            
            login = {}
            userInfo_list = userInfo.split(',')
            login.update({'account':userInfo_list[0]})
            login.update({'password':userInfo_list[1]})
            login.update({'sign':userInfo_list[2]})
            # print(login['account'], login['password'], login['sign'])      
            self.login_info_list.append(login)
        return None
