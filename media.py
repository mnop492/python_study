import socket
import time
import pandas as pd
from Config import Config
from MediaHelper import MediaHelper
from UserInfo import UserInfo
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

df_all_user_saleReport = pd.DataFrame()
df_all_user_profileReport = pd.DataFrame()
df_all_user_productReport = pd.DataFrame()
userInfoDict={}


def reindexSaleReportDataFrame(df_json):
    try:
        df_json.insert(1, 'headerID', df_json.pop('headerID'))
    except TypeError:
        print ('Fail to reindex sale report data frame.')
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
    sleeptime = 5
    userInfo = UserInfo(login_dict['account'])
    while True :
        try:
            mediaHelper.login(login_dict)
            userInfo.profile = mediaHelper.getProfile()
            userInfo.saleReport = getSaleReport(userInfo.profile)
            if df_all_user_productReport.size==0:
                userInfo.product = mediaHelper.getProduct(userInfo.profile)
            userInfo.token = mediaHelper.token
        except Exception as err:              
            print(userInfo.account, 'fail to get sale report.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    return userInfo

for login_info in config.login_info_list:
    login_dict.update({'account':login_info['account']})
    login_dict.update({'password': login_info['password']})
    login_dict.update({'sign':login_info['sign']})
    userInfo = startProcess(login_dict)    
    
    frames = [df_all_user_saleReport, userInfo.getSaleReportDataFrame()]
    df_all_user_saleReport = pd.concat(frames)
    frames = [df_all_user_profileReport, userInfo.getProfileReportDataFrame()]
    df_all_user_profileReport = pd.concat(frames)
    if df_all_user_productReport.size==0:
        frames = [df_all_user_productReport, userInfo.getProductReportDataFrame()]
        df_all_user_productReport = pd.concat(frames)
    userInfoDict.update({userInfo.account: userInfo})
    # sleeptime = 5 + random.randint(1,4)
    # print('Wait', sleeptime, 'seconds to get next account sale report!')
    # time.sleep(sleeptime)

df_all_user_saleReport = reindexSaleReportDataFrame(df_all_user_saleReport)
df_all_user_saleReport.to_excel('All_USER_SALEREPORT.xlsx', index=False)
df_all_user_profileReport.to_excel('All_USER_PROFILE.xlsx', index=False)
df_all_user_productReport.to_excel('All_USER_PRODUCT.xlsx', index=False)