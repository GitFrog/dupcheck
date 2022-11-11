import datetime
import pymssql
import uuid
import re
import xml.etree.ElementTree as ET
import dbEngine as DBE
from metaphone import doublemetaphone

class Deterministic:

    def first_and_last(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.first_match_boolean(poi, sus) + self.last_match_boolean(poi, sus) == 2:
                suspects.append(sus)
        return suspects

    def first(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.first_match_boolean(poi, sus) == 1:
                suspects.append(sus)
        return suspects

    def last(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.last_match_boolean(poi, sus) == 1:
                suspects.append(sus)
        return suspects

    def first_and_last_applicant(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.first_last_applicant_match_boolean(poi, sus) == 1:
                suspects.append(sus)
        return suspects

    def first_applicant(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.first_applicant_match_boolean(poi, sus) == 1:
                suspects.append(sus)
        return suspects

    def last_applicant(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.last_applicant_match_boolean(poi, sus) == 1:
                suspects.append(sus)
        return suspects

    def last_to_last_applicant(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.last_to_last_applicant_match_boolean(poi, sus) == 1:
                suspects.append(sus)
        return suspects

    def first_and_last_and_dob_but_loc_bad(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.first_match_boolean(poi, sus) + self.last_match_boolean(poi, sus) == 2:
                if self.birth_year_boolean(poi, sus) + self.birth_month_boolean(poi, sus) + self.birth_day_boolean(poi, sus) == 3:
                    suspects.append(sus)
        return suspects

    def first_or_last_with_dob_fuzzy_or_transpose(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.first_match_boolean(poi, sus) + self.last_match_boolean(poi, sus) >= 1:
                if self.birth_year_boolean(poi, sus) + self.birth_month_boolean(poi, sus) + self.birth_day_boolean(poi, sus) >= 2:
                    suspects.append(sus)
                elif self.birth_year_boolean(poi, sus) + self.birth_month_day_transpose_boolean(poi, sus) >= 2:
                    suspects.append(sus)
        return suspects


    def dob_transpose(self, poi, lineup):
        suspects = []
        for sus in lineup:
            if self.birth_year_boolean(poi, sus) + self.birth_month_day_transpose_boolean(poi, sus) >= 2:
                suspects.append(sus)
        return suspects

## SINGLE MATCHING QUERIES RETURNING TRUE/FALSE RESULTS
## -----------------------------------------------------
## The idea is you use these to build out more complex match queries.
    
    def first_match_boolean(self, person_of_interest, suspect):
        if person_of_interest.firstName == suspect.firstName:
            return 1
        else:
            return 0

    def last_match_boolean(self, person_of_interest, suspect):
        if person_of_interest.lastName == suspect.lastName:
            return 1
        else:
            return 0

    def first_last_applicant_match_boolean(self, person_of_interest, suspect):
        for address in suspect.applicants:
            for address_of_interest in person_of_interest.applicants:
                if address_of_interest.caregiver_firstName == address.caregiver_firstName and address_of_interest.caregiver_lastName == address.caregiver_lastName:
                    person_of_interest.db_application_id = address.id
                    return 1
        return 0

    def first_applicant_match_boolean(self, person_of_interest, suspect):
        for address in suspect.applicants:
            for address_of_interest in person_of_interest.applicants:
                if address_of_interest.caregiver_firstName == address.caregiver_firstName:
                    person_of_interest.db_application_id = address.id
                    return 1
        return 0

    def last_applicant_match_boolean(self, person_of_interest, suspect):
        for address in suspect.applicants:
            for address_of_interest in person_of_interest.applicants:
                if address_of_interest.caregiver_lastName == address.caregiver_lastName:
                    person_of_interest.db_application_id = address.id
                    return 1
        return 0

    def last_to_last_applicant_match_boolean(self, person_of_interest, suspect):
        for address in suspect.applicants:
            if person_of_interest.lastName == address.caregiver_lastName:
                person_of_interest.db_application_id = address.id
                return 1
        return 0

    def birth_year_boolean(self, person_of_interest, suspect):
        if not isinstance(suspect.dob_asdate, datetime.datetime):
            return 0
        if person_of_interest.dob_asdate.year == suspect.dob_asdate.year:
            return 1
        else:
            return 0

    def birth_month_boolean(self, person_of_interest, suspect):
        if not isinstance(suspect.dob_asdate, datetime.datetime):
            return 0
        if person_of_interest.dob_asdate.month == suspect.dob_asdate.month:
            return 1
        else:
            return 0

    def birth_day_boolean(self, person_of_interest, suspect):
        if not isinstance(suspect.dob_asdate, datetime.datetime):
            return 0
        if person_of_interest.dob_asdate.day == suspect.dob_asdate.day:
            return 1
        else:
            return 0

    def birth_month_day_transpose_boolean(self, person_of_interest, suspect):
        if not isinstance(suspect.dob_asdate, datetime.datetime):
            return 0
        if person_of_interest.dob_asdate.month == suspect.dob_asdate.day and person_of_interest.dob_asdate.day == suspect.dob_asdate.month :
            return 1
        else:
            return 0

    def location_boolean(self, person_of_interest, suspect):
        for address in suspect.applicants:
            for address_of_interest in person_of_interest.applicants:
                if address_of_interest.city == address.city:
                    person_of_interest.db_application_id = address.id
                    return 1
                elif len(address_of_interest.postalCode) == 6 and len(address.postalCode) == 6:
                    if address_of_interest.postalCode[0:3] == address.postalCode[0:3]:
                        person_of_interest.db_application_id = address.id
                        return 1
        return 0

##----------------------------------------------------------------------------
##----------------------------------------------------------------------------

# OLD MATCH FUNCTIONS NOT TRANSITIONS TO  APPROACH
    def city_or_postalcode_fsa_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            grab = False
            for address in suspect.applicants:
                for address_of_interest in person_of_interest.applicants:
                    if address_of_interest.city == address.city:
                        #person_of_interest.db_application_id = address.id
                        grab = True
                    elif len(address_of_interest.postalCode) == 6 and len(address.postalCode) == 6:
                        if address_of_interest.postalCode[0:3] == address.postalCode[0:3]:
                            #person_of_interest.db_application_id = address.id
                            grab = True
            if grab:
                suspects.append(suspect)
        return suspects

    def firstname_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            if person_of_interest.firstName == suspect.firstName:
                suspects.append(suspect)
        return suspects

    def lastname_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            if person_of_interest.lastName == suspect.lastName:
                suspects.append(suspect)
        return suspects

    def first_and_last_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            if person_of_interest.lastName == suspect.lastName and person_of_interest.lastName == suspect.lastName:
                suspects.append(suspect)
        return suspects

    def first_alias_match(self, person_of_interest, lineup):
        suspects = []
        poiNames = str((person_of_interest.firstName + " " + person_of_interest.middleName).lstrip().rstrip()).split(" ")
        for suspect in lineup:
            grab = False
            suspectNames = str((suspect.firstName + " " + suspect.middleName).lstrip().rstrip()).split(" ")
            for poiName in poiNames:
                for suspectName in suspectNames:
                    if poiName == suspectName:
                        grab = True
            for poiName in poiNames:
                if not str(suspect.firstName.strip(" ") + suspect.middleName.strip(" ")).find(poiName) == -1:
                    grab = True
            for suspectName in suspectNames:
                if not str(person_of_interest.firstName.strip(" ") + person_of_interest.middleName.strip(" ")).find(suspectName) == -1:
                    grab = True
            if grab:
                suspects.append(suspect)
        return suspects

    def first_phonic_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            grab = False
            for pioPhon in person_of_interest.phonic_firstName.split(" "):
                for suspectPhon in suspect.phonic_firstName.split(" "):
                    if pioPhon == suspectPhon:
                        grab = True
            if grab:
                suspects.append(suspect)
        return suspects

    def dob_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            if person_of_interest.dob == suspect.dob:
                suspects.append(suspect)
        return suspects

    def birthyear_match(self, person_of_interest, lineup):
        suspects = []
        if len(person_of_interest.dob) > 9:
            for suspect in lineup:
                if isinstance(suspect.dob_asdate, datetime.datetime):
                    if person_of_interest.dob_asdate.year == suspect.dob_asdate.year:
                        suspects.append(suspect)
        return suspects

    def dob_transpose_or_fuzzy(self, person_of_interest, lineup):
        suspects = []
        if len(person_of_interest.dob) > 9:
            for suspect in lineup:
                dobFuzzyCnt = 0
                if isinstance(suspect.dob_asdate, datetime.datetime):
                    if person_of_interest.dob_asdate.year == suspect.dob_asdate.year:
                        dobFuzzyCnt += 1
                    if person_of_interest.dob_asdate.month == suspect.dob_asdate.month:
                        dobFuzzyCnt += 1
                    if person_of_interest.dob_asdate.day == suspect.dob_asdate.day:
                        dobFuzzyCnt += 1
                    if dobFuzzyCnt >= 2:
                        suspects.append(suspect)
                    elif person_of_interest.dob_asdate.year == suspect.dob_asdate.year and person_of_interest.dob_asdate.month == suspect.dob_asdate.day and person_of_interest.dob_asdate.day == suspect.dob_asdate.month:
                        suspects.append(suspect)
        return suspects

    def last_alias_match(self, person_of_interest, lineup):
        suspects = []
        poiNames = str(person_of_interest.lastName.replace("-", " ").lstrip().rstrip()).split(" ")
        for suspect in lineup:
            grab = False
            suspectNames = str(suspect.lastName.replace("-", " ").lstrip().rstrip()).split(" ")
            for f1 in poiNames:
                for f2 in suspectNames:
                    if f1 == f2:
                        grab = True
            for f1 in poiNames:
                if not str(suspect.lastName.strip(" ")).find(f1) == -1:
                    grab = True
            for f2 in suspectNames:
                if not str(person_of_interest.lastName.strip(" ")).find(f2) == -1:
                    grab = True
            if grab:
                suspects.append(suspect)
        return suspects


    def last_phonic_match(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            grab = False
            for poiPhon in person_of_interest.phonic_lastName.split(" "):
                for suspectPhon in suspect.phonic_lastName.split(" "):
                    if poiPhon == suspectPhon:
                        grab = True
            if grab:
                suspects.append(suspect)
        return suspects

    def first_last_dob_transpositions(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            if person_of_interest.dob == suspect.dob and person_of_interest.firstname == suspect.lastname and person_of_interest.lastname == suspect.firstname:
                suspects.append(suspect)
            elif isinstance(suspect.dob_asdate, datetime.datetime):
                if person_of_interest.firstname == suspect.firstname and person_of_interest.lastname == suspect.lastname and person_of_interest.dob_asdate.day == suspect.dob_asdate.month and person_of_interest.dob_asdate.month == suspect.dob_asdate.day:
                    suspects.append(suspect)
        return suspects

    def first_last_transposition(self, person_of_interest, lineup):
        suspects = []
        for suspect in lineup:
            if person_of_interest.firstName == suspect.lastName and person_of_interest.lastName == suspect.firstName:
                suspects.append(suspect)
        return suspects

