import pandas as pd

class UserInfo():
    profile = None
    saleReport = None
    token = None
    account = None
    def __init__(self, account, profile, saleReport, token):
        self.account = account
        self.profile = profile
        self.saleReport = saleReport
        self.token = token

    def __init__(self, account):
        self.account = account

    def getSaleReportDataFrame(self):
        meta_col = ["actualSellingDate","approveStatus","headerID","storeId","storeName"]
        df_json = pd.json_normalize(self.saleReport['data'],record_path=['line'], record_prefix='z_', meta=meta_col)
        df_json = df_json.reindex(sorted(df_json.columns), axis=1)
        df_json.insert(0, 'account', self.account)        
        return df_json
    
    def getProfileReportDataFrame(self):
        df_json = pd.json_normalize(self.profile['__promoterStoreMapList'])
        df_json.insert(0, 'account', self.account)
        df_json.insert(1, 'promoterId', self.profile['__promoterId'])                
        return df_json
