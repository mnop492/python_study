import pandas as pd
from SaleRecord import SaleRecord

class CancelSaleRecordHelper():
    cancel_saleRecord_account_dict = {}

    def __init__(self, cancelExcelFile=None):
        if cancelExcelFile !=None:
            cancelSaleRecord_df = pd.read_excel(cancelExcelFile)
            cancelSaleRecord_df.fillna('', inplace=True)
            self.processCancelSaleRecordData(cancelSaleRecord_df)

    def processCancelSaleRecordData(self, cancelSaleRecord_df):
        # for index, row in cancelSaleRecord_df.iterrows():
        #     if row['headerID']:
        #         row['headerID'] = int(row['headerID']) 
        #         if row['account'].lower() in self.cancel_saleRecord_account_dict:
        #             self.cancel_saleRecord_account_dict[row['account'].lower()].append(row['headerID'])            
        #         else:
        #             self.cancel_saleRecord_account_dict[row['account'].lower()] = [row['headerID']]
        for col, row in cancelSaleRecord_df.iterrows():
            if row['headerID']: 
                row['headerID'] = int(row['headerID']) 
                saleRecord = SaleRecord(row)
                saleRecordList = None
                if saleRecord.account in self.cancel_saleRecord_account_dict:
                    saleRecordList = self.cancel_saleRecord_account_dict[saleRecord.account]                
                else:
                    saleRecordList = []   
                    
                saleRecordList.append(saleRecord)
                self.cancel_saleRecord_account_dict.update({saleRecord.account:saleRecordList})
    
    def initByDataFrame(self, cancel_saleRecord_account_df):
        self.cancel_saleRecord_account_dict = cancel_saleRecord_account_df

    def initByDict(self, cancel_saleRecord_account_dict):
        self.cancel_saleRecord_account_dict = cancel_saleRecord_account_dict
