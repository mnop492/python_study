import random
import hashlib

def dictToArray(dict):
    arr = []
    for key in dict:
        str = "" + key
        str += dict[key]
        arr.append(str)
    return arr

def sign(arr):
    SECRET = 'mx-muc5.0-sign'
    str = SECRET
    str = ""
    for val in arr:
        str += val        
##    md5 = hashlib.md5((SECRET + str +SECRET).encode("utf8")).hexdigest()    
    return SECRET + str +SECRET

login_dict = {'account' : 'ex_lily.hon', 'appKey' : '1c38dedb', 'appName': 'LetsLink', 'appVersion': '5.1.8', 'createTokenPwd':'1',                                     
              'deviceId':'A6F531E4-3146-4C00-AD97-363A58D44EC8', 'deviceName':'iPhone13,2', 'encrypt':'1', 'osVersion':'16.2',
              'password':'8+egoMajyx9/j5Rhef9fi4qVqNu07ie5k4hlFAe9K6SG9OQazfGTtQ==', 'passwordType':'1','platform':'1'}
loginArray = dictToArray(login_dict)
print(loginArray)

while True :
    random.shuffle(loginArray)
    str = sign(loginArray)
    md5 = hashlib.md5(str.encode("utf8")).hexdigest()
    if str == '9b320b7eff7a6dbd74c4894cdf7b5150':
        print('s1 and s2 are equal ')
        print(str)
        print('\n')
        break
    else:
        print ('failed: ')
        print (str)
        
