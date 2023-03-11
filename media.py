import socket
import time
import sys, getopt
import pandas as pd
from Config import Config
from WebConnectionHelper import WebConnectionHelper
from InsertSaleRecordHelper import InsertSaleRecordHelper
from CancelSaleRecordHelper import CancelSaleRecordHelper
from QuerySaleRecordHelper import QuerySaleRecordHelper
from QueryInfo import QueryInfo
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

timeout = 30
socket.setdefaulttimeout(timeout) 

config = Config('config.ini')
webConnectionHelper = WebConnectionHelper(config)

login_dict = { 'appKey' : config.appKey, 'appName': config.appName, 'appVersion': config.appVersion, 
                'createTokenPwd':config.createTokenPwd, 'deviceId': config.deviceId, 
                'deviceName': config.deviceName, 'encrypt': config.encrypt, 'osVersion':config.osVersion,
                'passwordType': config.passwordType,'platform':config.platform}

companyId = 106539

def getSaleReport(profile):    
    first_day = config.startDate
    last_day = config.endDate
    page_size = config.size
    sale_report = webConnectionHelper.getSaleReport(profile, first_day +' 00:00:00', last_day +' 23:59:59', page_size)
    if sale_report['data']:        
        print(profile['__userName'], 'successfully get sale report from', first_day, 'to', last_day)        
    else:
        print(profile['__userName'], 'has no record from', first_day, 'to', last_day)
    return sale_report

def getQueryInfo(login_dict, querySaleRecordHelper, isGetSaleReport=True):
    sleeptime = 5
    queryInfo = QueryInfo(login_dict['account'].lower())
    while True :
        try:
            webConnectionHelper.login(login_dict)
            queryInfo.profile = webConnectionHelper.getProfile()
            if isGetSaleReport:
                queryInfo.saleReport = getSaleReport(queryInfo.profile)
            if querySaleRecordHelper.isProductReportEmpty():
                queryInfo.product = webConnectionHelper.getProduct(queryInfo.profile,companyId)
            queryInfo.token = webConnectionHelper.token
        except Exception as err:              
            print(queryInfo.account, 'fail to query report.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)
            sleeptime += 5
            continue   
        break
    return queryInfo

def query(arg):    
    querySaleRecordHelper = QuerySaleRecordHelper()
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
        queryInfo = getQueryInfo(login_dict, querySaleRecordHelper)    
        querySaleRecordHelper.updateQueryInfoList(queryInfo)
        
        # sleeptime = 5 + random.randint(1,4)
        # print('Wait', sleeptime, 'seconds to get next account sale report!')
        # time.sleep(sleeptime)
    querySaleRecordHelper.writeExcel()

def insertSaleRecordByAccount(login_dict, insertSaleRecordHelper, querySaleRecordHelper):
    queryInfo = getQueryInfo(login_dict, querySaleRecordHelper, isGetSaleReport=False)
    querySaleRecordHelper.initProductReport(queryInfo)
    if not insertSaleRecordHelper.productRecord_df_flag :
        insertSaleRecordHelper.initProductRecord_df(querySaleRecordHelper.df_all_user_productReport)
    saleRecordList = insertSaleRecordHelper.getTranslatedSaleRecordByAccount(login_dict['account'], queryInfo.profile)
    for saleRecord in saleRecordList:
        webConnectionHelper.insertSaleRecord(queryInfo.profile,companyId, saleRecord)
    return queryInfo    

def insert(arg):    
    arg = arg.lower()
    querySaleRecordHelper = QuerySaleRecordHelper()
    insertSaleRecordHelper = InsertSaleRecordHelper('All_USER_INSERT.xlsx')    
    for account in insertSaleRecordHelper.saleRecord_account_dict:
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
        
        insertSaleRecordByAccount(login_dict, insertSaleRecordHelper, querySaleRecordHelper)
        # print ('doing account:', arg, saleRecordList)

def cancelSaleRecordByAccountAndHeaderID(login_dict, cancelSaleRecordHelper):
    sleeptime = 5
    queryInfo = QueryInfo(login_dict['account'])
    while True :
        try:
            webConnectionHelper.login(login_dict)
            queryInfo.profile = webConnectionHelper.getProfile()
            queryInfo.token = webConnectionHelper.token
        except Exception as err:              
            print(queryInfo.account, 'fail to login for cancel sale record.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    cancelSaleRecordList = cancelSaleRecordHelper.cancel_saleRecord_account_dict[login_dict['account'].lower()]
    for headerID in cancelSaleRecordList:
        webConnectionHelper.cancelSaleRecord(queryInfo.profile, headerID)
    return queryInfo

def cancel(arg):     
    cancelSaleRecordHelper = CancelSaleRecordHelper('All_USER_CANCEL.xlsx')    
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
