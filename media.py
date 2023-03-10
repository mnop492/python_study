import socket
import time
import sys, getopt
import pandas as pd
from Config import Config
from WebConnectionHelper import WebConnectionHelper
from InsertSaleRecordHelper import InsertSaleRecordHelper
from CancelSaleRecordHelper import CancelSaleRecordHelper
from QuerySaleRecordHelper import QuerySaleRecordHelper
from PushSaleRecordHelper import PushSaleRecordHelper
from QueryInfo import QueryInfo
import ssl
import random
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
    arg = arg.lower()  
    querySaleRecordHelper = QuerySaleRecordHelper()
    for login_info in config.login_info_list:
        if arg=='all' or arg=='a':
            pass
        elif arg==login_info['account'].lower():
            pass
        else:
            continue
        
        login_dict.update({'account':login_info['account']})
        login_dict.update({'password': login_info['password']})
        login_dict.update({'sign':login_info['sign']})
        queryInfo = getQueryInfo(login_dict, querySaleRecordHelper)    
        querySaleRecordHelper.updateQueryInfoList(queryInfo)
    
    querySaleRecordHelper.writeExcel()

def insertSaleRecord(queryInfo, insertSaleRecordHelper):
    account = login_dict['account'].lower()
    if account in insertSaleRecordHelper.insertSaleRecord_account_dict:
        saleRecordList = insertSaleRecordHelper.getTranslatedSaleRecordByAccount(queryInfo.account, queryInfo.profile)
        # saleRecordList = insertSaleRecordHelper.insertSaleRecord_account_dict[account]
        for saleRecord in saleRecordList:
            df = queryInfo.getSaleReportDataFrame()
            isDuplicate = False
            for col, row in df.iterrows():            
                if row['approveStatus'] == 'Approved' and saleRecord.getSaleRecordID() == row['account'].lower() + row['actualSellingDate']:
                    isDuplicate = True
                    break
            if (not isDuplicate):
                sleeptime = 5
                while True :
                    try:
                        webConnectionHelper.insertSaleRecord(queryInfo.profile,companyId, saleRecord)
                        insert_sleeptime = 3 + random.randint(1,4)
                        # sleeptime = 5 + random.randint(1,4)
                        # print('Wait', sleeptime, 'seconds to get next account sale report!')
                        # time.sleep(sleeptime)
                        print("Wait", insert_sleeptime, "seconds to insert next record.")
                        time.sleep(insert_sleeptime)
                    except Exception as err:              
                        print(queryInfo.account, 'fail to insert record.', 'Wait', sleeptime, 'seconds to retry!')   
                        time.sleep(sleeptime)
                        sleeptime += 5
                        continue   
                    break            
            else:
                print(saleRecord.account, saleRecord.actualSellingDate, 'is duplicated, fail to insert.')

def insertSaleRecordCommandSeries(login_dict, insertSaleRecordHelper, querySaleRecordHelper):
    queryInfo = getQueryInfo(login_dict, querySaleRecordHelper)
    querySaleRecordHelper.initProductReport(queryInfo)
    if not insertSaleRecordHelper.productRecord_df_flag :
        insertSaleRecordHelper.initProductRecord_df(querySaleRecordHelper.df_all_user_productReport)
    insertSaleRecord(queryInfo, insertSaleRecordHelper)

def insert(arg):    
    arg = arg.lower()
    querySaleRecordHelper = QuerySaleRecordHelper()
    insertSaleRecordHelper = InsertSaleRecordHelper('All_USER_INSERT.xlsx')    
    for account in insertSaleRecordHelper.insertSaleRecord_account_dict:
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
        
        insertSaleRecordCommandSeries(login_dict, insertSaleRecordHelper, querySaleRecordHelper)
        
        # print ('doing account:', arg, saleRecordList)

def cancelSaleRecord(queryInfo, cancelSaleRecordHelper):
    sleeptime = 5
    while True :
        try:
            account = login_dict['account'].lower()
            if account in cancelSaleRecordHelper.cancel_saleRecord_account_dict:
                cancelSaleRecordList = cancelSaleRecordHelper.cancel_saleRecord_account_dict[account]
                for saleRecord in cancelSaleRecordList:
                    webConnectionHelper.cancelSaleRecord(queryInfo.profile, saleRecord.headerID)            
        except Exception as err:              
            print(queryInfo.account, 'fail to cancel sale record.', 'Wait', sleeptime, 'seconds to retry!')   
            time.sleep(sleeptime)  
            sleeptime += 5
            continue   
        break
    return queryInfo

def cancelSaleRecordCommandSeries(login_dict, cancelSaleRecordHelper):
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
    cancelSaleRecord(queryInfo, cancelSaleRecordHelper)

    
    

def cancel(arg):     
    cancelSaleRecordHelper = CancelSaleRecordHelper('All_USER_CANCEL.xlsx')    
    arg = arg.lower()
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
        
        cancelSaleRecordCommandSeries(login_dict, cancelSaleRecordHelper)
    return

def pushSaleRecordByAccount(login_dict, pushSaleRecordHelper, querySaleRecordHelper, insertSaleRecordHelper, cancelSaleRecordHelper):
    queryInfo = getQueryInfo(login_dict, querySaleRecordHelper)
    querySaleRecordHelper.initProductReport(queryInfo)
    if not insertSaleRecordHelper.productRecord_df_flag :
        insertSaleRecordHelper.initProductRecord_df(querySaleRecordHelper.df_all_user_productReport)
    querySaleRecordHelper.updateQueryInfoList(queryInfo)
    querySaleRecordList = querySaleRecordHelper.getSaleRecordListByAccount(queryInfo.account)

    # if (querySaleRecordList and pushSaleRecordHelper.diffSaleRecordByAccount(queryInfo.account, querySaleRecordList)):
    #     cancelSaleRecordHelper.updateDict()
    #     pushSaleRecordHelper.updateDict()

    # cancelSaleRecordCommandSeries(login_dict, cancelSaleRecordHelper)
    # insertSaleRecordCommandSeries(login_dict, insertSaleRecordHelper, querySaleRecordHelper)
    cancelSaleRecord(queryInfo, cancelSaleRecordHelper)
    insertSaleRecord(queryInfo, insertSaleRecordHelper)
    return queryInfo

def push():     
    pushSaleRecordHelper = PushSaleRecordHelper('All_USER_PUSH.xlsx')    
    querySaleRecordHelper = QuerySaleRecordHelper()
    insertSaleRecordHelper = InsertSaleRecordHelper()
    insertSaleRecordHelper.initByDict(pushSaleRecordHelper.insert_saleRecord_account_dict)
    cancelSaleRecordHelper = CancelSaleRecordHelper()
    cancelSaleRecordHelper.initByDict(pushSaleRecordHelper.cancel_saleRecord_account_dict)

    for account in pushSaleRecordHelper.push_saleRecord_account_dict: 

        login_info = None
        for info in config.login_info_list:
            if info['account'].lower() == account.lower():
                login_info = info

        login_dict.update({'account':login_info['account']})
        login_dict.update({'password': login_info['password']})
        login_dict.update({'sign':login_info['sign']}) 
        
        pushSaleRecordByAccount(login_dict, pushSaleRecordHelper, querySaleRecordHelper, insertSaleRecordHelper, cancelSaleRecordHelper)
    return
    

def main(argv):
    opts, args = getopt.getopt(argv,"hi:c:p",["insert=","cancel="])
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -q <query> -i <insert>')
            sys.exit()      
        elif opt in ("-i", "--insert"):
             insert(arg)
            #  outputfile = arg
        elif opt in ("-c", "--cancel"):
             cancel(arg)
        elif opt in ("-p", "--push"):
             push()

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
