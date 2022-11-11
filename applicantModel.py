import json
import piObjects as piObj

class applicant:

    def __init__(self):
        self.id = ""
        self.caregiver_firstName = ""
        self.caregiver_lastName = ""
        self.unit = ""
        self.number = ""
        self.streetName = ""
        self.city = ""
        self.postalCode = ""

        self.orig_caregiver_firstName = ""
        self.orig_caregiver_lastName = ""


    def unpackJsonHomeAddress(self, s):
        self.caregiver_firstName = self.noneChk(str(s.get("caregiver_firstName")))
        self.caregiver_lastName = self.noneChk(str(s.get("caregiver_lastName")))
        self.unit = self.noneChk(str(s.get("homeaddr_unit")))
        self.number = self.noneChk(str(s.get("homeaddr_number")))
        self.streetName = self.noneChk(str(s.get("homeaddr_streetName")))
        self.city = self.noneChk(str(s.get("homeaddr_city")))
        self.postalCode = self.noneChk(str(s.get("homeaddr_postalCode")))
        self.orig_caregiver_firstName =  self.caregiver_firstName
        self.orig_caregiver_lastName = self.caregiver_lastName

    def unpackJsonMailAddress(self, s):
        self.caregiver_firstName = self.noneChk(str(s.get("caregiver_firstName")))
        self.caregiver_lastName = self.noneChk(str(s.get("caregiver_lastName")))
        self.unit = self.noneChk(str(s.get("mailaddr_unit")))
        self.number = self.noneChk(str(s.get("mailaddr_number")))
        self.streetName = self.noneChk(str(s.get("mailaddr_streetName")))
        self.city = self.noneChk(str(s.get("mailaddr_city")))
        self.postalCode = self.noneChk(str(s.get("mailaddr_postalCode")))
        self.orig_caregiver_firstName = self.caregiver_firstName
        self.orig_caregiver_lastName = self.caregiver_lastName

    def unpackDbRowHomeAddress(self, r):
        self.id = str(r[5])
        self.caregiver_firstName = str(r[6])
        self.caregiver_lastName = str(r[7])
        self.unit = str(r[8])
        self.number = str(r[9])
        self.streetName = str(r[10])
        self.city = str(r[11])
        self.postalCode = str(r[12])

    def unpackDbRowMailAddress(self, r):
        self.id = str(r[5])
        self.caregiver_firstName = str(r[6])
        self.caregiver_lastName = str(r[7])
        self.unit = str(r[13])
        self.number = str(r[14])
        self.streetName = str(r[15])
        self.city = str(r[16])
        self.postalCode = str(r[17])

    def scrubAddress(self):
        # implements sterilize and clean functions for each data field below
        self.caregiver_firstName = piObj.firstnameObj().scrub(self.caregiver_firstName)
        self.caregiver_lastName = piObj.lastnameObj().scrub(self.caregiver_lastName)
        self.city = piObj.cityObj().scrub(self.city)
        self.postalCode = piObj.postalcodeObj().scrub(self.postalCode)

    def noneChk(self, s):
        if s == "None":
            return ""
        else:
            return s.encode("ascii", "ignore").decode()