import pandas as pd
from QueryInfo import QueryInfo
from SaleRecord import SaleRecord

class QuerySaleRecordHelper():
    df_all_user_saleReport = pd.DataFrame()
    df_all_user_profileReport = pd.DataFrame()
    df_all_user_productReport = pd.DataFrame()
    queryInfoDict={}
    saleRecord_account_dict = {}

    def __init__(self):
        return

    def isProductReportEmpty(self):
        if self.df_all_user_productReport.size==0:
            return True
        else:
            return False
        
    def reindexSaleReportDataFrame(self, df_json):
        try:
            df_json.insert(1, 'headerID', df_json.pop('headerID'))
        except TypeError:
            print ('Fail to reindex sale report data frame.')
            return df_json 
        
        columns_prefix=['account', 'headerID', 'actualSellingDate', 'approveStatus', 'storeId', 'storeName',
                'z_approveStatus', 'z_documentNumber', 'z_lineID', 'z_price', 'z_productID', 'z_productName','z_qty', 'z_snInputTypeStatus']
        columns = df_json.columns.tolist()
        for item in columns_prefix:
            if item in columns:
                columns.remove(item)    
        columns = columns_prefix + columns
        df_json = df_json[columns]
        return df_json

    def initProductReport(self, queryInfo):
        if self.isProductReportEmpty():
            frames = [self.df_all_user_productReport, queryInfo.getProductReportDataFrame()]
            self.df_all_user_productReport = pd.concat(frames)

    def updateQueryInfoList(self, queryInfo):
        frames = [self.df_all_user_saleReport, queryInfo.getSaleReportDataFrame()]
        self.df_all_user_saleReport = pd.concat(frames)
        self.initProductReport(queryInfo)
        frames = [self.df_all_user_profileReport, queryInfo.getProfileReportDataFrame()]
        self.df_all_user_profileReport = pd.concat(frames)    
        self.queryInfoDict.update({queryInfo.account: queryInfo})
        self.updateSaleRecord_account_dict(queryInfo.getSaleReportDataFrame())

    def updateSaleRecord_account_dict(self, dataFrame):
        for col, row in dataFrame.iterrows():            
            saleRecord = SaleRecord(row)
            saleRecordList = None
            if saleRecord.account in self.saleRecord_account_dict:
                saleRecordList = self.saleRecord_account_dict[saleRecord.account]                
            else:
                saleRecordList = []   
            
            saleRecordList.append(saleRecord)
            self.saleRecord_account_dict.update({saleRecord.account:saleRecordList})


    def getSaleRecordListByAccount(self, account):
        return self.saleRecord_account_dict[account]

    def writeExcel(self):
        self.df_all_user_saleReport = self.reindexSaleReportDataFrame(self.df_all_user_saleReport)
        self.df_all_user_saleReport.to_excel('All_USER_SALEREPORT.xlsx', index=False)
        self.df_all_user_profileReport.to_excel('All_USER_PROFILE.xlsx', index=False)
        self.df_all_user_productReport.to_excel('All_USER_PRODUCT.xlsx', index=False)
