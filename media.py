import socket
import time
import random
import pandas as pd
from Config import Config
from MediaHelper import MediaHelper
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

timeout = 30
socket.setdefaulttimeout(timeout) 

config = Config('config.ini')
mediaHelper = MediaHelper(config)

login_dict = { 'appKey' : config.appKey, 'appName': config.appName, 'appVersion': config.appVersion, 
                'createTokenPwd':config.createTokenPwd, 'deviceId': config.deviceId, 
                'deviceName': config.deviceName, 'encrypt': config.encrypt, 'osVersion':config.osVersion,
                'passwordType': config.passwordType,'platform':config.platform}

df_all_user = pd.DataFrame()

def reindexSaleReportDataFrame(df_json):
    try:
        df_json.insert(1, 'headerID', df_json.pop('headerID'))
    except TypeError:
        return df_json 
    
    columns_prefix=['account', 'headerID', 'actualSellingDate', 'approveStatus', 'storeId', 'storeName',
            'z_approveStatus', 'z_documentNumber', 'z_lineID', 'z_price', 'z_productID', 'z_productName','z_qty', 'z_snInputTypeStatus']
    columns = df_json.columns.tolist()
    for item in columns_prefix:
        if item in columns:
            columns.remove(item)    
    columns = columns_prefix + columns
    df_json = df_json[columns]
    return df_json

def getDataFrameByAccount(sale_report, account):
    meta_col = ["actualSellingDate","approveStatus","headerID","storeId","storeName"]
    df_json = pd.json_normalize(sale_report['data'],record_path=['line'], record_prefix='z_', meta=meta_col)
    df_json = df_json.reindex(sorted(df_json.columns), axis=1)
    df_json.insert(0, 'account', account)        
    return df_json

def getSaleReport(profile):    
    first_day = config.startDate
    last_day = config.endDate
    page_size = config.size
    sale_report = mediaHelper.getSaleReport(profile, first_day +' 00:00:00', last_day +' 23:59:59', page_size)
    if sale_report['data']:        
        print(profile['__userName'], 'successfully get sale report from', first_day, 'to', last_day)        
    else:
        print(profile['__userName'], 'has no record from', first_day, 'to', last_day)
    return sale_report

def startProcess(login_dict):
    sale_report = None
    sleeptime = 5
    while True :
        try:
            mediaHelper.login(login_dict)
            profile = mediaHelper.getProfile()
            sale_report = getSaleReport(profile)
        except Exception as err:              
            print (login_dict['account'], 'fail get sale report.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    return sale_report

for login_info in config.login_info_list:
    login_dict.update({'account':login_info['account']})
    login_dict.update({'password': login_info['password']})
    login_dict.update({'sign':login_info['sign']})
    sale_report = startProcess(login_dict)    
    
    frames = [df_all_user, getDataFrameByAccount(sale_report, login_info['account'])]
    df_all_user = pd.concat(frames)
    # sleeptime = 5 + random.randint(1,4)
    # print('Wait', sleeptime, 'seconds to get next account sale report!')
    # time.sleep(sleeptime)

df_all_user = reindexSaleReportDataFrame(df_all_user)
df_all_user.to_excel('All_USER_DATAFILE.xlsx', index=False)