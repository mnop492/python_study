import json
from Cryption import Cryption 

class SaleRecord():
    account = None
    remark = None
    productID = None
    price = None
    qty = None
    serialNoType = None
    serialNumber = None
    documentNumber = None
    deliveryMode = None
    installation = None
    paymentMode = None
    storeId = None
    dealerId = None
    actualSellingDate = None
    productName = None
    storeName = None
    dealerName = None
    saleStatus = None
    gift1 = None
    gift1ID = None
    gift2 = None
    gift2ID = None
    gift3 = None
    gift3ID = None

    headerID = None
    lineID = None

    # def __init__(self, row):
    #     self.account = row['account'].lower()
    #     self.remark = row['remark']
    #     self.productID = row['productID']
    #     self.price = row['price']
    #     self.qty = row['qty']
    #     self.serialNoType = row['serialNoType']
    #     self.serialNumber = row['serialNumber']
    #     self.documentNumber = row['documentNumber']
    #     self.deliveryMode = row['deliveryMode']
    #     self.installation = row['installation']
    #     self.paymentMode = row['paymentMode']
    #     self.storeId = row['storeId']
    #     self.dealerId = row['dealerId']
    #     self.actualSellingDate = row['actualSellingDate']
    #     self.productName = row['productID']
    #     self.storeName = row['storeId']
    #     self.dealerName = row['dealerId']

    def __init__(self, row):
        self.account = row['account'].lower()        
        self.price = row['z_price']
        self.qty = row['z_qty']
        self.documentNumber = row['z_documentNumber']
        self.deliveryMode = row['deliveryModeMeaning']
        self.installation = row['installationMeaning']
        self.paymentMode = row['paymentModeMeaning']
        self.actualSellingDate = row['actualSellingDate']

        self.productID = row['z_productID']
        self.productName = row['z_productName']
        self.storeId = row['storeId']        
        self.storeName = row['storeName']

        self.serialNoType = row['z_snInputTypeStatus']
        self.serialNumber = row['z_serialNumber']
        self.remark = row['z_remark']
        self.saleStatus = row['saleStatus']
        self.gift1 = row['z_gift1']
        self.gift1ID = row['z_gift1ID']
        self.gift2 = row['z_gift2']
        self.gift2ID = row['z_gift2ID']
        self.gift3 = row['z_gift3']
        self.gift3ID = row['z_gift3ID']

        self.headerID = row['headerID']
        self.lineID = row['z_lineID']

    def toDict(self):
        dict = {'documentNumber':self.documentNumber, 'price':self.price, 'productID': self.productID, 
                'qty':self.qty, 'serialNoType':self.serialNoType, 'serialNumber':self.serialNumber}
        list = [dict]        
        return list
    
    def getSaleRecordID(self):
        return self.account + self.actualSellingDate
    
    def toString(self):
        str = self.account + self.remark + self.productID + self.price + self.qty 
        str += self.serialNoType + self.serialNumber + self.documentNumber + self.deliveryMode + self.installation 
        str += self.paymentMode + self.storeId + self.dealerId + self.actualSellingDate + self.productName 
        str += self.storeName + self.dealerName + self.saleStatus + self.gift1 + self.gift1ID 
        str += self.gift2 + self.gift2ID + self.gift3 + self.gift3ID
        return str
    
    def hash(self):
        return Cryption.signString(self.toString())

