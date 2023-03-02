import socket
import pandas as pd
from Config import Config
from MediaHelper import MediaHelper

timeout = 90
socket.setdefaulttimeout(timeout) 

config = Config('config.ini')
mediaHelper = MediaHelper(config)

login_dict = { 'appKey' : config.appKey, 'appName': config.appName, 'appVersion': config.appVersion, 
                'createTokenPwd':config.createTokenPwd, 'deviceId': config.deviceId, 
                'deviceName': config.deviceName, 'encrypt': config.encrypt, 'osVersion':config.osVersion,
                'passwordType': config.passwordType,'platform':config.platform}

df_all_user = pd.DataFrame()

def getDataFrame(sale_report, account):
    meta_col = ["actualSellingDate","approveStatus","headerID","storeId","storeName"]
    df_json = pd.json_normalize(sale_report['data'],record_path=['line'], record_prefix='z_', meta=meta_col)
    df_json = df_json.reindex(sorted(df_json.columns), axis=1)
    df_json.insert(0, 'account', account)
    df_json.insert(1, 'headerID', df_json.pop('headerID'))

    columns_prefix=['account', 'headerID', 'actualSellingDate', 'approveStatus', 'storeId', 'storeName',
            'z_approveStatus', 'z_documentNumber', 'z_lineID', 'z_price', 'z_productID', 'z_productName','z_qty', 'z_snInputTypeStatus']
    columns = df_json.columns.tolist()
    for item in columns_prefix:
        if item in columns:
            columns.remove(item)    
    columns = columns_prefix + columns
    df_json = df_json[columns]
    return df_json

for login_info in config.login_info_list:
    login_dict.update({'account':login_info['account']})
    login_dict.update({'password': login_info['password']})
    login_dict.update({'sign':login_info['sign']})
    
    mediaHelper.login(login_dict)
    profile = mediaHelper.getProfile()
    first_day = config.startDate
    last_day = config.endDate
    page_size = config.size
    print('first_day', first_day,'last_day',last_day)
    sale_report = mediaHelper.getSaleReport(profile, first_day +' 00:00:00', last_day +' 23:59:59', page_size)
    frames = [df_all_user, getDataFrame(sale_report, login_info['account'])]
    df_all_user = pd.concat(frames)

df_all_user.to_excel('All_USER_DATAFILE.xlsx', index=False)