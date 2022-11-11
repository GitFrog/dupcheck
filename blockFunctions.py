from metaphone import doublemetaphone

class Block:

    # In each case, you are returning either an integer count OR a full list of Person Objects with embedded
    # Address Objects ready for you to query and filter down using matchingFunctions

    def getOap(self, personObj, s8, justReturnCount):
        t=0

    def getDob(self, personObj, s8, justReturnCount):
        return self.runQuery("{0} AND c.CLIENT_DOB = '{1}' ORDER BY c.DB_CLIENT_ID, a.DB_APPLICATION_ID DESC".format(
            self.loadSelectString(s8), str(personObj.dob)), s8, justReturnCount)

    def getFsa(self, personObj, s8, justReturnCount):
        if len(personObj.applicants) > 0:
            query_builder = ""
            for address in personObj.applicants:
                if len(address.postalCode) == 6:
                    query_builder += "a.APPLICANT_PC LIKE '{0}%' OR a.APPLICANT_MAIL_PC LIKE '{0}%' OR ".format(str(address.postalCode)[0:3])
            if not query_builder == "":
                return self.runQuery("{0} AND ({1}) ORDER BY c.DB_CLIENT_ID, a.DB_APPLICATION_ID DESC".format(
                self.loadSelectString(s8), query_builder[0:len(query_builder)-3]), s8, justReturnCount)
            else:
                return self.nullReturn(justReturnCount)
        else:
            return self.nullReturn(justReturnCount)

# HELPER FUNCTIONS----------------------------------------------------------

    def runQuery(self, sqlquery, s8, justReturnCount):
        if justReturnCount:
            sqlquery = sqlquery.replace("*", "COUNT(*)")
            sqlquery = sqlquery.replace("ORDER BY c.DB_CLIENT_ID, a.DB_APPLICATION_ID DESC", "")
            return s8.readAsCount(sqlquery)
        else:
            addin = "DISTINCT c.DB_CLIENT_ID, c.CLIENT_FIRST_NAME, c.CLIENT_MIDDLE_NAME, c.CLIENT_LAST_NAME, " \
            "c.CLIENT_DOB, a.DB_APPLICATION_ID, a.APPLICANT_FIRST_NAME, a.APPLICANT_LAST_NAME, a.APPLICANT_ADDRESS_UNIT, " \
            "a.APPLICANT_ADDRESS_STREET_NUM, a.APPLICANT_STREET, a.APPLICANT_CITY, a.APPLICANT_PC, a.APPLICANT_MAIL_ADDRESS_UNIT, " \
            "a.APPLICANT_MAIL_ADDRESS_STREET_NUM, a.APPLICANT_MAIL_STREET, a.APPLICANT_MAIL_CITY, a.APPLICANT_MAIL_PC, " \
            "c.OAP_CLIENT_NUM, c.CLIENT_COMMENT"
            sqlquery = sqlquery.replace("*", addin)
            return s8.readAsPersonObjList(sqlquery)

    def nullReturn(self, justReturnCount):
        if justReturnCount:
            return 0
        else:
            return []

    def loadSelectString(self,s8):
        return "SELECT * " \
            "FROM [" + s8.database + "]." + s8.table_client + " as c " \
            "LEFT JOIN [" + s8.database + "]." + s8.table_application + " as a ON c.DB_CLIENT_ID = a.CLIENT_DB_ID " \
            "WHERE c.CLIENT_DELETE = 0 AND a.APP_DELETE= 0 AND a.APP_CLOSED_ID NOT IN (69,75,76) AND a.APPLICATION_TYPE <> 18 " \
            "AND ISNULL(a.migration_OAP_Status, 999) NOT BETWEEN 88 AND 93 "




