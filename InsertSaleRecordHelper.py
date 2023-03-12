import pandas as pd
from SaleRecord import SaleRecord

class InsertSaleRecordHelper():
    saleRecord_df = None
    productRecord_df = None
    productRecord_df_flag = False
    saleRecord_account_dict = {}
    productRecord_dict = {}

    def __init__(self, saleExcelFile):
        self.saleRecord_df = pd.read_excel(saleExcelFile)
        self.saleRecord_df.fillna('', inplace=True)
        self.processSaleRecordData(self.saleRecord_df)

    def processSaleRecordData(self, saleRecord_df):

        for col, row in saleRecord_df.iterrows():
            saleRecord = SaleRecord(row)
            saleRecordList = None
            if saleRecord.account in self.saleRecord_account_dict:
                saleRecordList = self.saleRecord_account_dict[saleRecord.account]                
            else:
                saleRecordList = []   
                
            saleRecordList.append(saleRecord)
            self.saleRecord_account_dict.update({saleRecord.account:saleRecordList})

    def initProductRecord_df(self, productRecord_df):        
        self.productRecord_df = productRecord_df
        self.productRecord_df.fillna('', inplace=True)
        for col, row in self.productRecord_df.iterrows():            
            self.productRecord_dict.update({row['itemNumber']:row['itemId']})
        self.productRecord_df_flag = True

    def getTranslatedSaleRecordByAccount(self, account, profile):
        saleRecordList = self.saleRecord_account_dict[account.lower()]
        for record in saleRecordList:
            record.productID = self.translateProductID(record.productID)
            record.dealerId = self.translateDealerId(record.storeId, profile)
            record.storeId = self.translateStoreId(record.storeId, profile)            
        return saleRecordList
    
    def translateProductID(self, productID):
        productID = self.productRecord_dict[productID]
        return productID
    
    def translateDealerId(self, storeId, profile):
        for dealer in profile['__promoterStoreMapList']:
            if dealer['storeName']==storeId: 
                dealerId = dealer['dealerId']
        return dealerId
    
    def translateStoreId(self, storeId, profile):
        for store in profile['__promoterStoreMapList']:
            if store['storeName']==storeId: 
                storeId = store['storeId']
        return storeId