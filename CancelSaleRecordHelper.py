import pandas as pd

class CancelSaleRecordHelper():
    cancel_saleRecord_account_dict = {}

    def __init__(self, cancelExcelFile=None):
        if cancelExcelFile !=None:
            cancelSaleRecord_df = pd.read_excel(cancelExcelFile)
            self.processCancelSaleRecordData(cancelSaleRecord_df)

    def processCancelSaleRecordData(self, cancelSaleRecord_df):
        for index, row in cancelSaleRecord_df.iterrows():
            if row['account'].lower() in self.cancel_saleRecord_account_dict:
                self.cancel_saleRecord_account_dict[row['account'].lower()].append(row['headerID'])            
            else:
                self.cancel_saleRecord_account_dict[row['account'].lower()] = [row['headerID']]
    
    def initByDataFrame(self, cancel_saleRecord_account_df):
        self.cancel_saleRecord_account_dict = cancel_saleRecord_account_df

