import urllib
import urllib.parse
import urllib.request
import http.cookiejar
import socket
import json
import base64
import hashlib
import gzip
import pandas as pd
from pyDes import des, CBC, PAD_PKCS5
from Config import Config
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
    data_dict.pop('sign')
    data_dict = dict(sorted(data_dict.items()))
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
# init()
config = Config('config.ini')


headers = {"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent" : "com.midea.map.en/5.1.8 (iPhone; iOS 16.2; Scale/3.00)",
        "Accept-Encoding" : "gzip, deflate, br",
        "Accept-Language" : "zh-Hant-HK;q=1, yue-Hant-HK;q=0.9, en-GB;q=0.8, ja-HK;q=0.7, zh-Hans-HK;q=0.6",
        "X-Requested-With" : "com.mannings.app",
        "Upgrade-Insecure-Requests" : "1",
        "Cookie": "PHPSESSID=ehlu07th5pmprrb214r4f4e2c5"
        }
json_header = headers.copy()
json_header.update({'Content-Type':'application/json'})

cj = http.cookiejar.CookieJar()        
if config.enableProxy == "" or config.enableProxy == False:        
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
else:    
    proxyAddrAndPort = config.server+':'+config.port
    ProxyHandler = urllib.request.ProxyHandler({'http' : proxyAddrAndPort, 'https' : proxyAddrAndPort})
    opener = urllib.request.build_opener(ProxyHandler, urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)
token = None
# return None

def login(login_dict):
    login_dict.update({'password': des_encrypt_b64(login_dict['appKey'], login_dict['password'])})
    # sign_str = sign(login_dict)
    # print(sign_str)
        
    login_data = urllib.parse.urlencode(login_dict)
    req = urllib.request.Request("https://mapsales.midea.com/muc/v5/app/emp/login", str.encode(login_data), headers)
    response = opener.open(req)
    response_body = response.read()  
    try : 
        response_body = gzip.decompress(response_body) 
    except Exception as e :
        print("Caught it!")
    
    response_body = response_body.decode("utf-8")
    response_json = json.loads(response_body)    
    return response_json['data']['accessToken']

def getProfile():
    url = "https://irms.midea.com:8080/isales/basis/profile"
    data = {"token":token,"language":"en","isApp":1,"appVersion":"5.0"}

    req = urllib.request.Request(url, json.dumps(data).encode('utf8'), json_header)
    response = opener.open(req)
    response_body = response.read()  
    try : 
        response_body = gzip.decompress(response_body) 
    except Exception as e :
        print("Caught it!")
    response_body = response_body.decode("utf-8") 
    profile_data = json.loads(response_body)
    profile_data = profile_data['data']['profile']
    profile_data.update({'__appVersion': "5.0"})
    profile_data.update({'__isApp': 1})
    return profile_data
 
def getSaleReport(profile_data, startDate, endDate, pageSize):
    url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/query"
    data = {'__page':1,'__pagesize':pageSize, 'approveStatus':'', 'conditions':'','saleStatus':''}
    data.update({'startDate':startDate})
    data.update({'endDate':endDate})    
    data.update({'profile':profile_data})
    data.update({'promoterID':profile_data['__promoterId']})

    req = urllib.request.Request(url, json.dumps(data).encode('utf8'), json_header)
    response = opener.open(req)
    response_body = response.read()  
    try : 
        response_body = gzip.decompress(response_body) 
    except Exception as e :
        print("Not a GZIP file")
    response_body = response_body.decode("utf-8")  
    report_data = json.loads(response_body)
    data_json = report_data['data']
    header_id = None
    for obj in data_json:
        header_id = obj['headerID']
        obj['line'] = getEntity(header_id, profile_data)

    
    return report_data

def getEntity(header_id, profile_data):
    url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/getentity"
    data = {'headerID':header_id,'profile':profile_data}
    req = urllib.request.Request(url, json.dumps(data).encode('utf8'), json_header)
    response = opener.open(req)
    response_body = response.read()  
    try : 
        response_body = gzip.decompress(response_body) 
    except Exception as e :
        print("Caught it!")
    response_body = response_body.decode("utf-8")
    report_data = json.loads(response_body)    
    report_data = report_data['data']['line']
    return report_data

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



login_dict = { 'appKey' : config.appKey, 'appName': config.appName, 'appVersion': config.appVersion, 
                'createTokenPwd':config.createTokenPwd, 'deviceId': config.deviceId, 
                'deviceName': config.deviceName, 'encrypt': config.encrypt, 'osVersion':config.osVersion,
                'passwordType': config.passwordType,'platform':config.platform}

df_all_user = pd.DataFrame()

for login_info in config.login_info_list:
    login_dict.update({'account':login_info['account']})
    login_dict.update({'password': login_info['password']})
    login_dict.update({'sign':login_info['sign']})
    
    token = login(login_dict)
    profile = getProfile()
    first_day = config.startDate
    last_day = config.endDate
    page_size = config.size
    print('first_day', first_day,'last_day',last_day)
    sale_report = getSaleReport(profile, first_day +' 00:00:00', last_day +' 23:59:59', page_size)
    frames = [df_all_user, getDataFrame(sale_report, login_info['account'])]
    df_all_user = pd.concat(frames)

df_all_user.to_excel('All_USER_DATAFILE.xlsx', index=False)