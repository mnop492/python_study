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

    def __init__(self, account, profile, saleReport, token):
        self.account = account
        self.profile = profile
        self.saleReport = saleReport
        self.token = token

    def __init__(self, account):
        self.account = account

    def toDict(self):
        dict = {'documentNumber':self.documentNumber, 'price':self.price, 'productID': self.productID, 
                'qty':self.qty, 'serialNoType':self.serialNoType, 'serialNumber':self.serialNumber}
        list = [dict]
        # dict = {'salesReportLinesParam':list}        
        return list
