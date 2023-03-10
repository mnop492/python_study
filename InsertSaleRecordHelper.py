import pandas as pd
from SaleRecord import SaleRecord

class InsertSaleRecordHelper():
    saleRecord_df = None
    productRecord_df = None
    productRecord_df_flag = False
    insertSaleRecord_account_dict = {}
    productRecord_dict = {}

    def __init__(self, saleExcelFile=None):
        if saleExcelFile != None:
            self.saleRecord_df = pd.read_excel(saleExcelFile)
            self.saleRecord_df.fillna('', inplace=True)
            self.processSaleRecordData(self.saleRecord_df)

    def processSaleRecordData(self, saleRecord_df):

        for col, row in saleRecord_df.iterrows():
            saleRecord = SaleRecord(row)
            saleRecordList = None
            if saleRecord.account in self.insertSaleRecord_account_dict:
                saleRecordList = self.insertSaleRecord_account_dict[saleRecord.account]                
            else:
                saleRecordList = []   
                
            saleRecordList.append(saleRecord)
            self.insertSaleRecord_account_dict.update({saleRecord.account:saleRecordList})

    def initByDict(self, saleRecord_account_dict):
        self.insertSaleRecord_account_dict = saleRecord_account_dict
        
    def initProductRecord_df(self, productRecord_df):        
        self.productRecord_df = productRecord_df
        self.productRecord_df.fillna('', inplace=True)
        for col, row in self.productRecord_df.iterrows():            
            self.productRecord_dict.update({row['itemNumber']:row['itemId']})
        self.productRecord_df_flag = True

    def getSaleRecordByAccount(self, account):
        saleRecordList = self.insertSaleRecord_account_dict[account.lower()]            
        return saleRecordList
    
    def getTranslatedSaleRecordByAccount(self, account, profile):
        saleRecordList = self.insertSaleRecord_account_dict[account.lower()]
        for record in saleRecordList:
            record.productID = self.translateProductID(record.productName)
            record.dealerId = self.translateDealerId(record.storeName, profile)
            record.storeId = self.translateStoreId(record.storeName, profile)
            record.dealerName = self.translateDealerName(record.storeName, profile)         
        return saleRecordList
    
    def translateProductID(self, productName):
        productID = self.productRecord_dict[productName]
        return productID
    
    def translateDealerId(self, storeName, profile):
        for dealer in profile['__promoterStoreMapList']:
            if dealer['storeName']==storeName: 
                dealerId = dealer['dealerId']
                dealerId = dealer['dealerId']
        return dealerId
    
    def translateStoreId(self, storeName, profile):
        for store in profile['__promoterStoreMapList']:
            if store['storeName']==storeName: 
                storeId = store['storeId']
        return storeId
    
    def translateDealerName(self, storeName, profile):
        for store in profile['__promoterStoreMapList']:
            if store['storeName']==storeName: 
                dealerName = store['dealerName']
        return dealerName
