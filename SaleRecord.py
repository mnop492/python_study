import json

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

    def __init__(self, row):
        self.account = row['account'].lower()
        self.remark = row['remark']
        self.productID = row['productID']
        self.price = row['price']
        self.qty = row['qty']
        self.serialNoType = row['serialNoType']
        self.serialNumber = row['serialNumber']
        self.documentNumber = row['documentNumber']
        self.deliveryMode = row['deliveryMode']
        self.installation = row['installation']
        self.paymentMode = row['paymentMode']
        self.storeId = row['storeId']
        self.dealerId = row['dealerId']
        self.actualSellingDate = row['actualSellingDate']

    def toDict(self):
        dict = {'documentNumber':self.documentNumber, 'price':self.price, 'productID': self.productID, 
                'qty':self.qty, 'serialNoType':self.serialNoType, 'serialNumber':self.serialNumber}
        list = [dict]
        # dict = {'salesReportLinesParam':list}        
        return list
