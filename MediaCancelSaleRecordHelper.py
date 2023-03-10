import pandas as pd
from SaleRecord import SaleRecord

class MediaCancelSaleRecordHelper():
    cancel_saleRecord_account_dict = {}

    def __init__(self, cancelExcelFile):
        cancelSaleRecord_df = pd.read_excel(cancelExcelFile)
        self.processCancelSaleRecordData(cancelSaleRecord_df)

    def processCancelSaleRecordData(self, cancelSaleRecord_df):
        for index, row in cancelSaleRecord_df.iterrows():
            if row['account'].lower() in self.cancel_saleRecord_account_dict:
                self.cancel_saleRecord_account_dict[row['account'].lower()].append(row['headerID'])            
            else:
                self.cancel_saleRecord_account_dict[row['account'].lower()] = [row['headerID']]