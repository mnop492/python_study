import pandas as pd
from SaleRecord import SaleRecord

class PushSaleRecordHelper():
    push_saleRecord_account_dict = {}

    def __init__(self, pushExcelFile):
        self.pushSaleRecord_df = pd.read_excel(pushExcelFile)
        self.pushSaleRecord_df.fillna('', inplace=True)
        self.processSaleRecordData(self.pushSaleRecord_df)

    def processSaleRecordData(self, pushSaleRecord_df):

        for col, row in pushSaleRecord_df.iterrows():
            saleRecord = SaleRecord(row)
            saleRecordList = None
            if saleRecord.account in self.push_saleRecord_account_dict:
                saleRecordList = self.push_saleRecord_account_dict[saleRecord.account]                
            else:
                saleRecordList = []   
                
            saleRecordList.append(saleRecord)
            self.push_saleRecord_account_dict.update({saleRecord.account:saleRecordList})
