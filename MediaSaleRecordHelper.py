import pandas as pd
from SaleRecord import SaleRecord

class MediaSaleRecordHelper():
    saleRecord_df = None
    productRecord_df = None
    productRecord_df_flag = False
    saleRecord_account_dict = {}

    def __init__(self, saleExcelFile):
        self.saleRecord_df = pd.read_excel(saleExcelFile)
        self.saleRecord_df.fillna('', inplace=True)
        self.processSaleRecordData(self.saleRecord_df)

    def processSaleRecordData(self, saleRecord_df):

        for index, row in saleRecord_df.iterrows():
            saleRecord= SaleRecord(row['account'].lower())
            saleRecord.remark = row['remark']
            saleRecord.productID = row['productID']
            saleRecord.price = row['price']
            saleRecord.qty = row['qty']
            saleRecord.serialNoType = row['serialNoType']
            saleRecord.serialNumber = row['serialNumber']
            saleRecord.documentNumber = row['documentNumber']
            saleRecord.deliveryMode = row['deliveryMode']
            saleRecord.installation = row['installation']
            saleRecord.paymentMode = row['paymentMode']
            saleRecord.storeId = row['storeId']
            saleRecord.dealerId = row['dealerId']

            saleRecordList = None
            if saleRecord.account in self.saleRecord_account_dict:
                saleRecordList = self.saleRecord_account_dict[saleRecord.account]                
            else:
                saleRecordList = []   
                
            saleRecordList.append(saleRecord)
            self.saleRecord_account_dict.update({saleRecord.account:saleRecordList})

    def initProductRecord_df(self, productRecord):
        productRecord_df = pd.json_normalize(productRecord)
        self.productRecord_df = productRecord_df
        self.productRecord_df.fillna('', inplace=True)
        self.productRecord_df_flag = True

    def getTranslatedSaleRecordByAccount(self, account, profile):
        saleRecordList = self.saleRecord_account_dict[account.lower()]
        for record in saleRecordList:
            record.productID = self.translateProductID(record.productID)
            record.storeId = self.translateStoreId(record.storeId, profile)
            record.dealerId = self.translateDealerId(record.dealerId, profile)
        return saleRecordList
    
    def translateProductID(self, productID):
        for index, row in self.productRecord_df.iterrows():
            if row['itemNumber'] == productID:
                productID = row['itemId']
            break
        return productID
    
    def translateDealerId(self, dealerId, profile):
        for dealer in profile['__promoterStoreMapList']:
            if dealer['dealerName']==dealerId: 
                dealerId = dealer['dealerId']
        return dealerId
    
    def translateStoreId(self, storeId, profile):
        for store in profile['__promoterStoreMapList']:
            if store['storeName']==storeId: 
                storeId = store['storeId']
        return storeId