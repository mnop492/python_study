import pandas as pd
from SaleRecord import SaleRecord

class PushSaleRecordHelper():
    push_saleRecord_account_dict = {}
    cancel_saleRecord_account_dict = {}
    insert_saleRecord_account_dict = {}

    def __init__(self, pushExcelFile):
        self.pushSaleRecord_df = pd.read_excel(pushExcelFile)
        self.pushSaleRecord_df.fillna('', inplace=True)
        self.processSaleRecordData(self.pushSaleRecord_df)

    def processSaleRecordData(self, pushSaleRecord_df):
        for col, row in pushSaleRecord_df.iterrows():
            if row.empty:
                continue

            saleRecord = SaleRecord(row)
            pushSaleRecordList = None
            cancelSaleRecordList = None
            insertSaleRecordList = None

            if saleRecord.account in self.push_saleRecord_account_dict:
                pushSaleRecordList = self.push_saleRecord_account_dict[saleRecord.account]                
            else:
                pushSaleRecordList = []   

            pushSaleRecordList.append(saleRecord)
            self.push_saleRecord_account_dict.update({saleRecord.account:pushSaleRecordList})
            
            if row['approveStatus'] == 'Cancelled' and row['headerID']:
                if saleRecord.account in self.cancel_saleRecord_account_dict:
                    cancelSaleRecordList = self.cancel_saleRecord_account_dict[saleRecord.account]                
                else:
                    cancelSaleRecordList = []

                cancelSaleRecordList.append(saleRecord)
                self.cancel_saleRecord_account_dict.update({saleRecord.account:cancelSaleRecordList})

            if not row['headerID']:
                if saleRecord.account in self.insert_saleRecord_account_dict:
                    insertSaleRecordList = self.insert_saleRecord_account_dict[saleRecord.account]                
                else:
                    insertSaleRecordList = []
                
                insertSaleRecordList.append(saleRecord)
                self.insert_saleRecord_account_dict.update({saleRecord.account:insertSaleRecordList})

            

            

    def diffSaleRecordByAccount(self, account, querySaleRecordList):
        diff = False
        pushSaleRecordList = self.push_saleRecord_account_dict[account]
        modified_headerID_list = []

        for pushSaleRecord in pushSaleRecordList:
            for querySaleRecord in querySaleRecordList:
                if (pushSaleRecord.lineID == querySaleRecord.lineID and querySaleRecord.headerID not in modified_headerID_list):
                    if pushSaleRecord.hash() !=  querySaleRecord.hash(): #the record is modified
                        #add headerID to modified_headerID_list
                        modified_headerID = querySaleRecord.headerID
                        modified_headerID_list.append()
                        #cancel all line under same HeaderID
                        cancelSaleRecordList = self.cancel_saleRecord_account_dict[account]
                        insertSaleRecordList = self.insert_saleRecord_account_dict[account]

                        if account in self.cancel_saleRecord_account_dict:
                            cancelSaleRecordList = self.cancel_saleRecord_account_dict[account]                
                        else:
                            cancelSaleRecordList = []
                        #insert all line under same HeaderID
                        if account in self.insert_saleRecord_account_dict:
                            insertSaleRecordList = self.insert_saleRecord_account_dict[account]                
                        else:
                            insertSaleRecordList = []

                        for modifiedSaleRecord in querySaleRecord :
                            if modifiedSaleRecord.headerID == modified_headerID:
                                cancelSaleRecordList.append(modifiedSaleRecord)
                                self.cancel_saleRecord_account_dict.update({modifiedSaleRecord.account:cancelSaleRecordList})

                                insertSaleRecordList.append(modifiedSaleRecord)
                                self.insert_saleRecord_account_dict.update({modifiedSaleRecord.account:insertSaleRecordList})

        return diff




