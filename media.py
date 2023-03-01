import urllib
import urllib.parse
import urllib.request
import http.cookiejar
import datetime
import socket
import json
import base64
import hashlib
import calendar
import gzip
import pandas as pd
from pyDes import des, CBC, PAD_PKCS5
# from pandas.io.json import json_normalize

# proxyAddrAndPort = None
# headers = None
# cj = None        
# ProxyHandler = None
# opener = None

def des_encrypt_b64(secret_key, password):
    bArr = [1, 2, 3, 4, 5, 6, 7, 8]
    input_text = password
    iv = bytearray(bArr)
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(input_text, padmode=PAD_PKCS5)
    return str(base64.b64encode(en),'utf-8')

def sign(data_dict):
    SECRET = 'mx-muc5.0-sign'
    str = ""
    for key in data_dict:
        str += key
        str += data_dict[key]        
    md5 = hashlib.md5((SECRET + str +SECRET).encode("utf8")).hexdigest()   
    return md5

# timeout in seconds
timeout = 90
socket.setdefaulttimeout(timeout)

# def init():
proxyAddrAndPort = '127.0.0.1:8888'

headers = {"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent" : "com.midea.map.en/5.1.8 (iPhone; iOS 16.2; Scale/3.00)",
        "Accept-Encoding" : "gzip, deflate, br",
        "Accept-Language" : "zh-Hant-HK;q=1, yue-Hant-HK;q=0.9, en-GB;q=0.8, ja-HK;q=0.7, zh-Hans-HK;q=0.6",
        "X-Requested-With" : "com.mannings.app",
        "Upgrade-Insecure-Requests" : "1",
        "Cookie": "PHPSESSID=ehlu07th5pmprrb214r4f4e2c5"
        }
cj = http.cookiejar.CookieJar()        
ProxyHandler = urllib.request.ProxyHandler({'http' : proxyAddrAndPort, 'https' : proxyAddrAndPort})
if ProxyHandler==None:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
else:
    opener = urllib.request.build_opener(ProxyHandler, urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)
token = None
# return None

def login(account, password, sign_str):
    secret_key = '1c38dedb'
    encrypted_pw = des_encrypt_b64(secret_key, password)
    # print (encrypted_pw)
    login_dict = {'account' : account, 'appKey' : secret_key, 'appName': 'LetsLink', 'appVersion': '5.1.8', 'createTokenPwd':'1',                                     
            'deviceId':'A6F531E4-3146-4C00-AD97-363A58D44EC8', 'deviceName':'iPhone13,2', 'encrypt':'1', 'osVersion':'16.2',
            'password':encrypted_pw, 'passwordType':'0','platform':'1'}
    # sign_str = sign(login_dict)
    # # print (sign_str)
    # sign_str = '9b320b7eff7a6dbd74c4894cdf7b5150'
    login_dict.update({'sign':sign_str})

    login_data = urllib.parse.urlencode(login_dict)

    req = urllib.request.Request("https://mapsales.midea.com/muc/v5/app/emp/login", str.encode(login_data), headers)
    response = opener.open(req)
    response_body = response.read()  
    response_body = gzip.decompress(response_body)
    response_body = response_body.decode("utf-8")
    response_json = json.loads(response_body)    
    return response_json['data']['accessToken']

def getProfile():
    json_header = headers
    json_header.update({'Content-Type':'application/json'})
    url = "https://irms.midea.com:8080/isales/basis/profile"
    data = {"token":token,"language":"en","isApp":1,"appVersion":"5.0"}

    req = urllib.request.Request(url, json.dumps(data).encode('utf8'), json_header)
    response = opener.open(req)
    response_body = response.read()  
    response_body = gzip.decompress(response_body)
    response_body = response_body.decode("utf-8") 
    profile_data = json.loads(response_body)
    profile_data = profile_data['data']['profile']
    profile_data.update({'__appVersion': "5.0"})
    profile_data.update({'__isApp': 1})
    return profile_data
 
def getSaleReport(profile_data, startDate, endDate, pageSize):
    json_header = headers
    json_header.update({'Content-Type':'application/json'})
    url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/query"
    data = {'__page':1,'__pagesize':pageSize, 'approveStatus':'', 'conditions':'','saleStatus':''}
    data.update({'startDate':startDate})
    data.update({'endDate':endDate})    
    data.update({'profile':profile_data})
    data.update({'promoterID':profile_data['__promoterId']})

    req = urllib.request.Request(url, json.dumps(data).encode('utf8'), json_header)
    response = opener.open(req)
    response_body = response.read()  
    response_body = gzip.decompress(response_body)
    response_body = response_body.decode("utf-8")  
    report_data = json.loads(response_body)
    data_json = report_data['data']
    header_id = None
    for obj in data_json:
        header_id = obj['headerID']
        # print(header_id)
        obj['line'] = getEntity(header_id, profile_data)

    
    return report_data
    # return response_body

def getEntity(header_id, profile_data):
    json_header = headers
    json_header.update({'Content-Type':'application/json'})
    url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/getentity"
    data = {'headerID':header_id,'profile':profile_data}
    req = urllib.request.Request(url, json.dumps(data).encode('utf8'), json_header)
    response = opener.open(req)
    response_body = response.read()  
    response_body = gzip.decompress(response_body)
    response_body = response_body.decode("utf-8")
    report_data = json.loads(response_body)    
    report_data = report_data['data']['line']
    return report_data

def writeExcel(sale_report):
    # df_json = pd.read_json(json.dumps(sale_report['data']))
    # meta_col = ["actualSellingDate","approveStatus","consumerName",
    #     "creationDate","deliveryModeMeaning","headerID","installationMeaning",
    #     "invalidType","isNeedApproval","mobile","paymentModeMeaning","saleStatus","storeId","storeName"]
    meta_col = ["actualSellingDate","approveStatus","headerID","storeId","storeName"]
    df_json = pd.json_normalize(sale_report['data'],record_path=['line'], record_prefix='z_', meta=meta_col)
    # df = pd.json_normalize(json.dumps(sale_report['data'], 'locations', ['date', 'number', 'name'], record_prefix='locations_')
    df_json = df_json.reindex(sorted(df_json.columns), axis=1)
    df_json.insert(0, 'account', account)
    df_json.insert(1, 'headerID', df_json.pop('headerID'))
    columns=['z_gift1', 'z_gift1ID', 'z_gift1Image', 'z_gift1Qty', 
                                    'z_gift2', 'z_gift2ID', 'z_gift2Image', 'z_gift2Qty', 'z_gift3',
                                     'z_gift3ID', 'z_gift3Image', 'z_gift3Qty','z_productImage', 'z_remark','z_serialNumber','z_snInputTypeStatus']

    df_copy = df_json[columns].copy()
    df_json.drop(columns=columns, inplace=True)
    frames = [df_json, df_copy]
    df_json = pd.concat(frames)
    df_json.to_excel(account +'_DATAFILE.xlsx', index=False)
    return 0

# init()
account = 'ex_lily.hon'
password = 'Qa7Ly4Tj4Y'
sign_str = '9b320b7eff7a6dbd74c4894cdf7b5150'
token = login(account, password, sign_str)
profile = getProfile()
first_day = datetime.date(2023, 2, 1).strftime('%Y-%m-%d')
last_day = datetime.date(2023, 2, calendar.monthrange(2023, 2)[1]).strftime('%Y-%m-%d')
print('first_day', first_day,'last_day',last_day)
sale_report = getSaleReport(profile, first_day +' 00:00:00', last_day +' 23:59:59', 500)
writeExcel(sale_report)
