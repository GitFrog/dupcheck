import pymssql
import pypyodbc
import clientModel

#INSERT INTO DBAdmin.dbo.[tblEmails]([body],[recipient],[priority],[module],[created_dt],[sent_dt],[active],[status])
#VALUES(N'your message here', N'recipient email here', 1, 'ACCERTA', getdate(), null, 1, 0)

class Server:

    # create read update delete

    def __init__(self):
        #self.server = "CYSVIGDCDBMSQ04"
        self.server = "CYSBIGDCDBMSQ08"
        self.database = "OAP"
        self.table_client = "[dbo].[tbl_Client]"
        self.table_application = "[dbo].[tbl_Application]"
        self.table_json = "[dbo].[IIO_RC_record]"
        self.conn = ""
        self.cursor = ""
        self.sqlqueryBase = "SELECT DISTINCT c.DB_CLIENT_ID, c.CLIENT_FIRST_NAME, c.CLIENT_MIDDLE_NAME, c.CLIENT_LAST_NAME, " \
            "c.CLIENT_DOB, a.DB_APPLICATION_ID, a.APPLICANT_FIRST_NAME, a.APPLICANT_LAST_NAME, a.APPLICANT_ADDRESS_UNIT, " \
            "a.APPLICANT_ADDRESS_STREET_NUM, a.APPLICANT_STREET, a.APPLICANT_CITY, a.APPLICANT_PC, a.APPLICANT_MAIL_ADDRESS_UNIT, " \
            "a.APPLICANT_MAIL_ADDRESS_STREET_NUM, a.APPLICANT_MAIL_STREET, a.APPLICANT_MAIL_CITY, a.APPLICANT_MAIL_PC, " \
            "c.OAP_CLIENT_NUM, c.CLIENT_COMMENT " \
            "FROM [" + self.database + "]." + self.table_client + " as c " \
            "LEFT JOIN [" + self.database + "]." + self.table_application + " as a ON c.DB_CLIENT_ID = a.CLIENT_DB_ID " \
            "WHERE c.CLIENT_DELETE = 0 AND a.APP_DELETE= 0 AND a.APP_CLOSED_ID NOT IN (69,75,76) AND a.APPLICATION_TYPE <> 18 " \
            "AND ISNULL(a.migration_OAP_Status, 999) NOT BETWEEN 88 AND 93 "
        self.sqlqueryIIOJSON = "SELECT * " \
            "FROM  [" + self.database + "]." + self.table_json + " " \
            "WHERE APPLICATION_ID = '{0}'"

    def open(self):
        self.conn = pymssql.connect(server=self.server, database=self.database)
        self.cursor = self.conn.cursor()

    def openODBC(self):
        conn_string = "Driver={SQL Server};Server=%s;Database=%s;Trusted_Connection=True" % (self.server, self.database)
        self.conn = pypyodbc.connect(conn_string)
        self.cursor = self.conn.cursor()

    def read(self, sqlquery):
        self.cursor.execute(self.sqlqueryBase + sqlquery)
        return self.cursor.fetchall()

    def readAsCount(self, sqlquery):
        self.cursor.execute(sqlquery)
        cnt = self.cursor.fetchone()[0]
        return cnt

    def readAsPersonObjList(self, sqlquery):
        self.cursor.execute(sqlquery)
        dataset_oacis = self.cursor.fetchall()
        clientOacis = []
        currentClientId = ""
        previousClientId = ""
        batch = []
        cnt = 0
        for client in dataset_oacis:
            cnt += 1
            currentClientId = client[0]
            if currentClientId != previousClientId and previousClientId != "" and previousClientId is not None:
                clientObj = clientModel.client()
                clientObj.unpackDbRows(batch)
                clientOacis.append(clientObj)
                batch.clear()
            batch.append(client)
            previousClientId = currentClientId
        if len(batch) > 0:
            clientObj = clientModel.client()
            clientObj.unpackDbRows(batch)
            clientOacis.append(clientObj)
        return clientOacis

    def readIIOrcJSON(self, id):
        sqlquery = self.sqlqueryIIOJSON.format(id)
        self.cursor.execute(sqlquery)
        return self.cursor.fetchall()

    def columns(self, tableName):
        #only works with ODBC connection
        return self.cursor.columns(tableName)

    def sendNotification(self, msg):
        emailAddress = "lee.hulsesmith@ontario.ca"
        sqlquery = "INSERT INTO DBAdmin.dbo.[tblEmails]([body],[recipient],[priority],[module],[created_dt],[sent_dt],[active],[status]) " \
                   "VALUES(N'[{0}', N'{1}', 1, 'ACCERTA', getdate(), null, 1, 0)" \
            .format(msg, emailAddress)
        self.cursor.execute(sqlquery)


    def close(self):
        self.conn.close()


