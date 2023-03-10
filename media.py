import socket
import time
import sys, getopt
import pandas as pd
from Config import Config
from MediaHelper import MediaHelper
from MediaSaleRecordHelper import MediaSaleRecordHelper
from MediaCancelSaleRecordHelper import MediaCancelSaleRecordHelper
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
companyId = 106539

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

def getUserInfo(login_dict):
    sleeptime = 5
    userInfo = UserInfo(login_dict['account'].lower())
    while True :
        try:
            mediaHelper.login(login_dict)
            userInfo.profile = mediaHelper.getProfile()
            userInfo.saleReport = getSaleReport(userInfo.profile)
            if df_all_user_productReport.size==0:
                userInfo.product = mediaHelper.getProduct(userInfo.profile,companyId)
            userInfo.token = mediaHelper.token
        except Exception as err:              
            print(userInfo.account, 'fail to get sale report.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    return userInfo

def insertSaleRecordByAccount(login_dict, saleRecordHelper):
    sleeptime = 5
    userInfo = UserInfo(login_dict['account'])
    while True :
        try:
            mediaHelper.login(login_dict)
            userInfo.profile = mediaHelper.getProfile()   
            if not saleRecordHelper.productRecord_df_flag :
                saleRecordHelper.initProductRecord_df(mediaHelper.getProduct(userInfo.profile,companyId))
            userInfo.token = mediaHelper.token
        except Exception as err:              
            print(userInfo.account, 'fail to login for inserting sale record.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    saleRecordList = saleRecordHelper.getTranslatedSaleRecordByAccount(login_dict['account'], userInfo.profile)
    for saleRecord in saleRecordList:
        mediaHelper.insertSaleRecord(userInfo.profile,companyId, saleRecord)
    return userInfo    
    
def query(arg):    
    for login_info in config.login_info_list:
        if arg=='all' or arg=='a':
            pass
        elif arg==login_info['account']:
            pass
        else:
            continue
        
        login_dict.update({'account':login_info['account']})
        login_dict.update({'password': login_info['password']})
        login_dict.update({'sign':login_info['sign']})
        userInfo = getUserInfo(login_dict)    
        
        global df_all_user_saleReport, df_all_user_profileReport, df_all_user_productReport,userInfoDict

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

def insert(arg):    
    arg = arg.lower()
    saleRecordHelper = MediaSaleRecordHelper('All_USER_INSERT.xlsx')    
    for account in saleRecordHelper.saleRecord_account_dict:
        if arg=='all' or arg=='a':
            pass
        elif arg==account.lower():
            pass
        else:
            continue

        login_info = None
        for info in config.login_info_list:
            if info['account'].lower() == account.lower():
                login_info = info

        login_dict.update({'account':login_info['account']})
        login_dict.update({'password': login_info['password']})
        login_dict.update({'sign':login_info['sign']}) 
        
        insertSaleRecordByAccount(login_dict, saleRecordHelper)
        # print ('doing account:', arg, saleRecordList)

def cancelSaleRecordByAccountAndHeaderID(login_dict, cancelSaleRecordHelper):
    sleeptime = 5
    userInfo = UserInfo(login_dict['account'])
    while True :
        try:
            mediaHelper.login(login_dict)
            userInfo.profile = mediaHelper.getProfile()
            userInfo.token = mediaHelper.token
        except Exception as err:              
            print(userInfo.account, 'fail to login for cancel sale record.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    cancelSaleRecordList = cancelSaleRecordHelper.cancel_saleRecord_account_dict[login_dict['account'].lower()]
    for headerID in cancelSaleRecordList:
        mediaHelper.cancelSaleRecord(userInfo.profile, headerID)
    return userInfo

def cancel(arg):     
    cancelSaleRecordHelper = MediaCancelSaleRecordHelper('All_USER_CANCEL.xlsx')    
    for account in cancelSaleRecordHelper.cancel_saleRecord_account_dict:        
        if arg=='all' or arg=='a':
            pass
        elif arg==account.lower():
            pass
        else:
            continue

        login_info = None
        for info in config.login_info_list:
            if info['account'].lower() == account.lower():
                login_info = info

        login_dict.update({'account':login_info['account']})
        login_dict.update({'password': login_info['password']})
        login_dict.update({'sign':login_info['sign']}) 
        
        cancelSaleRecordByAccountAndHeaderID(login_dict, cancelSaleRecordHelper)
    return

def main(argv):
    opts, args = getopt.getopt(argv,"hi:c:",["insert=","cancel="])
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -q <query> -i <insert>')
            sys.exit()      
        elif opt in ("-i", "--insert"):
             insert(arg)
            #  outputfile = arg
        elif opt in ("-c", "--cancel"):
             cancel(arg)

    if len(opts) == 0 and len(args) == 0:
        query('all')
    # if args[0] == 'query':        
    #     query()
    # elif args[0] == 'insert':
    #     insert()    
    # print(opts, args)
    return

if __name__ == "__main__":
   main(sys.argv[1:])
