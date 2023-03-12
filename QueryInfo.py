import pandas as pd

class QueryInfo():
    profile = None
    saleReport = None
    token = None
    account = None
    product = None
    def __init__(self, account, profile, saleReport, token):
        self.account = account
        self.profile = profile
        self.saleReport = saleReport
        self.token = token

    def __init__(self, account):
        self.account = account

    def getSaleReportDataFrame(self):
        meta_col = ["actualSellingDate","approveStatus","headerID","storeId","storeName"]
        if len(self.saleReport['data'])>0 :
            meta_col = list(self.saleReport['data'][0].keys())
            meta_col.remove('line')
        
        df_json = pd.json_normalize(self.saleReport['data'],record_path=['line'], record_prefix='z_', meta=meta_col)
        df_json = df_json.reindex(sorted(df_json.columns), axis=1)
        df_json.insert(0, 'account', self.account)        
        return df_json
    
    def getProfileReportDataFrame(self):
        df_json = pd.json_normalize(self.profile['__promoterStoreMapList'])
        df_json.insert(0, 'account', self.account)
        df_json.insert(1, 'promoterId', self.profile['__promoterId'])       
        df_json.insert(2, 'companyId', self.profile['__companyId'])          
        return df_json
    
    def getProductReportDataFrame(self):
        df_json = pd.json_normalize(self.product)
        df_json.insert(0, 'account', self.account)      
        df_json.insert(1, 'companyId', self.profile['__companyId'])          
        return df_json
