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
password=None
platform=None        
account=None
sign=None   

def readIni():
    config = configparser.RawConfigParser(dict_type=MultiOrderedDict, strict=False)
    config.read(['config.ini'])
    login = config.get('LOGIN', 'loginInfo')
    login_list = login.split('\n')
    print(login_list)
    for userInfo in login_list:
        userInfo_list = userInfo.split(',')
        account = userInfo_list[0]
        password = userInfo_list[1]
        sign = userInfo_list[1]
        print(account, password, sign)

readIni()
