import socket
import urllib
import urllib.parse
import urllib.request
import http.cookiejar
import gzip
import json
import base64
import hashlib
from pyDes import des, CBC, PAD_PKCS5
from Config import Config
from datetime import datetime

class MediaHelper():
    # timeout in seconds
    timeout = 30
    socket.setdefaulttimeout(timeout)   
    headers = {"Accept" : "*/*",
        "User-Agent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/mideaConnect MissonWebKit/220720001/zh-Hans/com.midea.link.appstore (AppStore)/MissonWKCordova",
        "Accept-Encoding" : "br, gzip, deflate",
        "Accept-Language" : "zh-tw",
        "Upgrade-Insecure-Requests" : "1",   
        "Connection": "keep-alive"     
        }
    json_header = headers.copy()
    json_header.update({'Content-Type':'application/json;charset=UTF-8'})
    cj = None        
    token = None
    config = None
    opener = None
    
    def __init__(self, config):
        self.config = config
        self.cj=http.cookiejar.CookieJar()
        if config.enableProxy == "" or config.enableProxy == False:        
            self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        else:    
            proxyAddrAndPort = config.server+':'+config.port
            ProxyHandler = urllib.request.ProxyHandler({'http' : proxyAddrAndPort, 'https' : proxyAddrAndPort})
            self.opener = urllib.request.build_opener(ProxyHandler, urllib.request.HTTPCookieProcessor(self.cj))
        urllib.request.install_opener(self.opener)

    def des_encrypt_b64(self, secret_key, password):
        bArr = [1, 2, 3, 4, 5, 6, 7, 8]
        input_text = password
        iv = bytearray(bArr)
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(input_text, padmode=PAD_PKCS5)
        return str(base64.b64encode(en),'utf-8')

    def sign(self, data_dict):
        SECRET = 'mx-muc5.0-sign' 
        data_dict.pop('sign')
        data_dict = dict(sorted(data_dict.items()))
        str = ""
        for key in data_dict:
            str += key
            str += data_dict[key]        
        md5 = hashlib.md5((SECRET + str +SECRET).encode("utf8")).hexdigest()   
        return md5
        
    def login(self, login_dict):
        login_dict = login_dict.copy()
        login_dict.update({'password': self.des_encrypt_b64(login_dict['appKey'], login_dict['password'])})
        # sign_str = sign(login_dict)
        # print(sign_str)
            
        login_data = urllib.parse.urlencode(login_dict)
        req = urllib.request.Request("https://mapsales.midea.com/muc/v5/app/emp/login", str.encode(login_data), self.headers)
        response = self.opener.open(req)
        response_body = response.read()  
        try : 
            response_body = gzip.decompress(response_body) 
        except Exception as e :
            print("Not a GZIP file")
        
        response_body = response_body.decode("utf-8")
        response_json = json.loads(response_body)    
        self.token = response_json['data']['accessToken']
        return self.token

    def getProfile(self):
        url = "https://irms.midea.com:8080/isales/basis/profile"
        data = {"token":self.token,"language":"en","isApp":1,"appVersion":"5.0"}

        req = urllib.request.Request(url, json.dumps(data).encode('utf8'), self.json_header)
        response = self.opener.open(req)
        response_body = response.read()  
        try : 
            response_body = gzip.decompress(response_body) 
        except Exception as e :
            print("Not a GZIP file")
        response_body = response_body.decode("utf-8") 
        profile_data = json.loads(response_body)
        profile_data = profile_data['data']['profile']
        profile_data.update({'__appVersion': "5.0"})
        profile_data.update({'__isApp': 1})
        return profile_data
    
    def getSaleReport(self, profile_data, startDate, endDate, pageSize):
        url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/query"
        data = {'__page':1,'__pagesize':pageSize, 'approveStatus':'', 'conditions':'','saleStatus':''}
        data.update({'startDate':startDate})
        data.update({'endDate':endDate})    
        data.update({'profile':profile_data})
        data.update({'promoterID':profile_data['__promoterId']})

        req = urllib.request.Request(url, json.dumps(data).encode('utf8'), self.json_header)
        response = self.opener.open(req)
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
            obj['line'] = self.getEntity(header_id, profile_data)
        
        return report_data

    def getEntity(self, header_id, profile_data):
        url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/getentity"
        data = {'headerID':header_id,'profile':profile_data}
        req = urllib.request.Request(url, json.dumps(data).encode('utf8'), self.json_header)
        response = self.opener.open(req)
        response_body = response.read()  
        try : 
            response_body = gzip.decompress(response_body) 
        except Exception as e :
            print("Not a GZIP file")
        response_body = response_body.decode("utf-8")
        report_data = json.loads(response_body)    
        report_data = report_data['data']['line']
        return report_data 

    def getProduct(self, profile_data, companyId):
        url = "https://irms.midea.com:8080/isales/basis/item/app/v1/query"
        data = {'__page':'','__pagesize':'','companyId':companyId,
                'itemType':'Product','itemNumber':'',
                'profile':profile_data}
        req = urllib.request.Request(url, json.dumps(data).encode('utf8'), self.json_header)
        response = self.opener.open(req)
        response_body = response.read()  
        try : 
            response_body = gzip.decompress(response_body) 
        except Exception as e :
            print("Not a GZIP file")
        response_body = response_body.decode("utf-8")
        report_data = json.loads(response_body)    
        report_data = report_data['data']
        return report_data   
    
    def insertSaleRecord(self, profile_data, companyId, saleRecord):
        url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/insert"
        data = {'companyId':companyId, 'promoterID':profile_data['__promoterId'],
                'customerID':'', 'paymentMode':'', 'deliveryMode':'','installation':''}  
        
        current_dateTime = datetime.now()
        dt_string = current_dateTime.strftime("%Y-%m-%d %H:%M:%S")

        data.update({'actualSellingDate':'2023-04-07 17:15:34'})
        data.update({'profile':profile_data})
        data.update({'remark':saleRecord.remark})
        data.update({'storeId':saleRecord.storeId})
        data.update({'dealerId':saleRecord.dealerId})
        data.update({'salesReportLinesParam':saleRecord.toDict()})

        req = urllib.request.Request(url, json.dumps(data).encode('utf8'), self.json_header)
        response = self.opener.open(req)
        response_body = response.read()  
        try : 
            response_body = gzip.decompress(response_body) 
        except Exception as e :
            print("Not a GZIP file")
        response_body = response_body.decode("utf-8")  
        report_data = json.loads(response_body)
        statusCode = report_data['__statusCode']
        if statusCode=='S':
            print('Insert sale record successfully!')     

    def cancelSaleRecord(self, profile_data, headerID):
        url = "https://irms.midea.com:8080/isales/app/v1/salesReportHeader/cancel"
        data = {'headerID':headerID, 'invalidReason':'Wrong data','invalidType':'1',
                'profile':profile_data}  
    
        req = urllib.request.Request(url, json.dumps(data).encode('utf8'), self.json_header)
        response = self.opener.open(req)
        response_body = response.read()  
        try : 
            response_body = gzip.decompress(response_body) 
        except Exception as e :
            print("Not a GZIP file")
        response_body = response_body.decode("utf-8")  
        report_data = json.loads(response_body)
        statusCode = report_data['__statusCode']
        if statusCode=='S':
            print(profile_data['__userName'], 'cancel sale record', headerID, 'successfully!') 
            return
        else :
            print(profile_data['__userName'], 'fail to cancel sale record', headerID) 
