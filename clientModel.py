import json
import applicantModel
import piObjects as piObj
from metaphone import doublemetaphone
from datetime import datetime

class client:

    def __init__(self):
        self.id = ""
        self.firstName = ""
        self.middleName = ""
        self.lastName = ""
        self.dob = ""
        self.independentYouth = ""
        self.oapId = ""
        self.comment = ""
        self.applicants = []
        self.dob_asdate = ""
        self.dateformataccerta = "%Y%m%d"
        self.dateformatoacis = "%Y-%m-%d %H:%M:%S"
        self.phonic_firstName = ""
        self.phonic_lastName = ""

        self.origFirstName = ""
        self.origMiddleName = ""
        self.origLastName = ""

        self.match = False
        self.matchType = 0
        self.matchNotes = ""
        self.db_client_id = ""
        self.db_application_id = ""
        self.repeat = False
        self.prevMatch = ""

    def locationIsAvailable(self):
        if len(self.applicants) == 0:
            return False
        else:
            return True

    def isSingleNamePerson(self):
        if self.firstName == "-":
            return True
        else:
            return False

    def unpackJson(self, s):
        self.id = self.noneChk(str(s.get("applicationId")))
        self.firstName = self.noneChk(str(s.get("firstName")))
        self.middleName = self.noneChk(str(s.get("middleName")))
        self.lastName = self.noneChk(str(s.get("lastName")))
        self.origFirstName = self.firstName
        self.origMiddleName = self.middleName
        self.origLastName = self.lastName
        self.dob = str(s.get("dob"))
        self.independentYouth = self.noneChk(str(s.get("independentYouth")))
        addressHomeObj = applicantModel.applicant()
        addressHomeObj.unpackJsonHomeAddress(s)
        self.applicants.append(addressHomeObj)
        addressMailObj = applicantModel.applicant()
        addressMailObj.unpackJsonMailAddress(s)
        self.applicants.append(addressMailObj)
        self.scrubPersonAndAddresses()
        self.phonicNameGenerate()
        self.dob_asdate = self.convertToDateFormat(self.dob, self.dateformataccerta)
        self.dob = piObj.dobObj(self.dateformataccerta).scrub(self.dob)

    def unpackDbRows(self, rows):
        if len(rows) > 0:
            self.id = str(rows[0][0])
            self.firstName = str(rows[0][1])
            self.middleName = str(rows[0][2])
            self.lastName = str(rows[0][3])
            self.dob = str(rows[0][4])
            self.oapId = str(rows[0][18])
            self.comment = str(rows[0][19])

            for r in rows:
                addressHomeObj = applicantModel.applicant()
                addressHomeObj.unpackDbRowHomeAddress(r)
                self.applicants.append(addressHomeObj)
                addressMailObj = applicantModel.applicant()
                addressMailObj.unpackDbRowHomeAddress(r)
                self.applicants.append(addressMailObj)
            self.scrubPersonAndAddresses()
            self.phonicNameGenerate()
            self.dob_asdate = self.convertToDateFormat(self.dob, self.dateformatoacis)
            self.dob = piObj.dobObj(self.dateformatoacis).scrub(self.dob)

    def scrubPersonAndAddresses(self):
        self.scrubPerson()
        for addressObj in self.applicants:
            addressObj.scrubAddress()

    def scrubPerson(self):
        # implements sterilize and clean functions for each data field below
        self.firstName = piObj.firstnameObj().scrub(self.firstName)
        self.middleName = piObj.middlenameObj().scrub(self.middleName)
        self.lastName = piObj.lastnameObj().scrub(self.lastName)
        #self.dob = piObj.dobObj(self.dob).scrub(self.dob)

    def phonicNameGenerate(self):
        self.phonic_firstName = self.phonicNameConversion(self.firstName)
        self.phonic_lastName = self.phonicNameConversion(self.lastName)

    def phonicNameConversion(self, targetNames):
        phonList = ""
        names = targetNames.replace("-", " ")
        for name in names.split(" "):
            for phon in doublemetaphone(name):
                if len(phon) > 0:
                    phonList += phon + " "
        phonList = phonList.rstrip()
        return phonList

    def convertToDateFormat(self, dte, fmt):
        return_date = None
        if dte is not None:
            try:
                return_date = datetime.strptime(dte, fmt)
            except ValueError as e:
                return_date = None
        return return_date

    def getJsonAccerta(self):
        r = "unique"
        if self.repeat:
            r = self.prevMatch
        elif self.match:
            r = "duplicate"
        dic = {"applicationId": self.id,
            "result": r,
            "matchLevel": self.matchType,
            "repeat": self.repeat}
        return dic

    def getJsonAudit(self):
        r = "unique"
        if self.repeat:
            r = self.prevMatch
        elif self.match:
            r = "duplicate"

        dic = {"applicationId": self.id,
               "firstName": self.origFirstName,
               "middleName": self.origMiddleName,
               "lastName": self.origLastName,
               "dob": self.dob,
               "independentYouth": str(self.independentYouth),
               "caregiver_firstName": self.applicants[0].orig_caregiver_firstName,
               "caregiver_lastName": self.applicants[0].orig_caregiver_lastName,
               "homeaddr_unit": self.applicants[0].unit,
               "homeaddr_number": self.applicants[0].number,
               "homeaddr_streetName": self.applicants[0].streetName,
               "homeaddr_city": self.applicants[0].city,
               "homeaddr_postalCode": self.applicants[0].postalCode,
               "mailaddr_unit": self.applicants[1].unit,
               "mailaddr_number": self.applicants[1].number,
               "mailaddr_streetName": self.applicants[1].streetName,
               "mailaddr_city": self.applicants[1].city,
               "mailaddr_postalCode": self.applicants[1].postalCode,
               "result": r,
               "matchLevel": self.matchType,
               "matchNotes": self.matchNotes,
               "db_client_id": self.db_client_id,
               "db_application_id": self.db_application_id,
               "repeat": self.repeat}
        return dic

    def repeatMatch(self, dataRow):
        self.match = True
        self.prevMatch = dataRow[19]
        self.matchType = dataRow[20]
        self.matchNotes = dataRow[21]
        self.db_client_id = dataRow[22]
        self.db_application_id = dataRow[23]
        self.repeat = True


    def recordMatch(self, matchType, personObj):
        self.match = True
        self.matchType = matchType
        self.db_client_id = personObj.id
        if not len(personObj.applicants) == 0:
            self.db_application_id = personObj.applicants[0].id
        startStr = "Duplicate for AccessOAP application id " + self.id + ". "
        if matchType == 1:
            self.matchNotes = startStr + "Exact match for client firstname, lastname, dob. Exact match for applicant location"
        elif matchType == 2:
            self.matchNotes = startStr + "Exact match for client lastname, dob. Alias match for client firstname (" + self.firstName + "). Exact match for applicant location."
        elif matchType == 3:
            self.matchNotes = startStr + "Exact match for firstname, dob. Alias match for lastname (" + self.lastName + "). Exact match for applicant location."
        elif matchType == 4:
            self.matchNotes = startStr + "Exact match for client dob. Transpose match for client firstname and lastname. Exact match for applicant location, applicant lastname to client firstname."
        elif matchType == 5:
            self.matchNotes = startStr + "Exact match for client lastname, dob. Phonic match for client firstname (" + self.firstName + "). Exact match for applicant location, applicant and client lastname."
        elif matchType == 6:
            self.matchNotes = startStr + "Exact match for firstname, dob. Phonic match for lastname (" + self.lastName + "). Exact match for applicant location, lastname."
        elif matchType == 7:
            self.matchNotes = startStr + "Exact match for client firstname, lastname, dob. Exact match for applicant firstname, lastname. No match Applicant location (home postal code " + self.applicants[0].postalCode + " mail postal code " + self.applicants[1].postalCode + ")."
        elif matchType == 8:
            self.matchNotes = startStr + "Exact match for client firstname, lastname. Transposed client dob. Exact match for applicant location."
        elif matchType == 9:
            self.matchNotes = startStr + "Exact match for client lastname. Alias match for client firstname (" + self.firstName + "). Transposed client dob. Exact match for applicant location, firstname, lastname."
        elif matchType == 10:
            self.matchNotes = startStr + "Exact match for client firstname. Alias match for client lastname (" + self.lastName + "). Transposed client dob. Exact match for applicant location, firstname, lastname."

    def noneChk(self, s):
        if s == "None":
            return ""
        else:
            return s.encode("ascii", "ignore").decode()


   #Summary of Record Match Methodology
            #BLOCK - DOB
            #  1. first, last, loc
            #  2. first alias, last, loc
            #  3. first, last alias, loc
            #  4. first-last transpose, loc, app-last = client-first
            #  5. first phonic, last, loc, app-last = client-last
            #  6. first, last-phonic, loc, app-last
            #  7. first, last, app-first, app-last (location wrong or missing)
            #
            #BLOCK - FSA
            #  8. first, last, dob transpose, app-first
            #  9. first alias, last, dob transpose, app-first, app-last
            #  10. first, last alias, dob transpose, app-first, app-last