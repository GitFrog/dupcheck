import json
from os import listdir
from os.path import isfile, join, getmtime
from datetime import datetime
import copy
import shutil

import clientModel
import dbEngine as DBE
import blockFunctions as Blocks
import matchingFunctions as Matching
import helper

# RUNNING PYINSTALLER ON COMMAND LINE To COMPILE SCRIPT
# Step 1: run command line as administrator
# Step 2: change folder to C:\Python\Python39
# Step 3: run the following:
# C:\python\python39\scripts\pyinstaller.exe E:\Resources\PythonProjects\PycharmProjects\IIO-Project\main.py
# Step 4: open windows file folder and navigate to C:\Python\Python39\dist
# Step 5: copy that folder to PROD at \\cysbigdcdbmsq06\scripts
# Step 6: remain folder to main_prod (Task Scheduler is pointed at main.exe contained within)

# PROJECT DETAILS
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
# Record Match between OACIS database (MCCSS owned) and Accerta data (inbound JSON file).
# Accerta is the new vendor who will be managing Autism client payments. When new clients "children"
# are entered into Accerta, we need to ensure those same clients are not already in OACIS, which is the
# current MCCSS run Autism payment system.
# Once a day, Accerta will send us a JSON file containing all new clients from the last 24hrs. This script needs to:
#   1. search each client in the JSON file will all clients in OACIS
#   2. report back the results ("duplicate" or "unique") of the search to Accerta for each client in a JSON file.

# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
dirProb = "//cysbigdcdbmsq06/Data/Data Sharing/Accerta/"
dirInbound = dirProb + "FromAccerta/"
dirOutbound = dirProb + "ToAccerta/"
dirCluster = dirProb + "ToCluster/"

dirArchive = "//cysbigdcdbmsq06/Data/Data Sharing/Accerta/Archive/"
dirArchiveInbound = dirArchive + "FromAccerta/"
dirArchiveOutbound = dirArchive + "ToAccerta/"
dirArchiveCluster = dirArchive + "ToCluster/"
dirArchiveExtraFiles = dirArchive + "ExtraFiles/"

# STEP ONE - Import JSON file
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
currentJsonFileName = ""
currentJsonDict = ""
currentFileCount = 0
currentJsonClientCount = 0


currentDateTime = datetime.today().strftime('%Y%m%d_%H%M%S')
helper.log("[" + currentDateTime + "] DUPLICATION SCRIPT STARTS", True, False, False)
#processingFirstFile = False
try:
    #getFiles = filter(isfile, listdir(dirInbound))
    #getFiles = [join(dirInbound, f) for f in getFiles]  # add path to each file
    #getFiles.sort(key=lambda x: getmtime(x))
    getFiles = [f for f in listdir(dirInbound) if isfile(join(dirInbound, f))]
    getFiles.sort(key=lambda f: getmtime(join(dirInbound, f)), reverse=True)
    #getFiles.sort(key=lambda x: getmtime(x))
except:
    helper.log("error: unable to access file network drive", True, True, True)
inboundJsonDict = ""
fileList = []
if len(getFiles) == 0:
    helper.log("progress: no JSON files found to process", True, False, False)
else:
    for currentJsonFileName in getFiles:
        helper.log("progress: " + currentJsonFileName + " begin processing", True, False, False)
        if currentJsonFileName[0:2] == 'RC' and currentFileCount == 0:
            currentFileCount += 1
            try:
                with open(dirInbound + currentJsonFileName, 'r', encoding='utf-8') as f:
                    inboundJsonDict = json.load(f)
            except Exception as e:
                helper.log("error: unable to open JSON file", True, True, True)
            # STEP TWO - Unpack JSON file into Person Objects - Store in Accerta List
            #            Scrub and clean data during unpack
            #----------------------------------------------------------------------------------------------
            #----------------------------------------------------------------------------------------------
            header = inboundJsonDict.get("Header")
            if header.get("name") == "Registration Check":
                currentJsonClientCount = int(header.get('clientCount'))
            else:
                helper.log("error: JSON file header not labelled as Registration Check", True, True, True)

            clients = inboundJsonDict['Clients']
            clientAccerta = []
            i = 0
            if len(clients) == currentJsonClientCount:
                for client in clients:
                    i += 1
                    try:
                        clientObj = clientModel.client()
                        clientObj.unpackJson(client)
                        clientAccerta.append(clientObj)
                    except:
                        helper.log("error: unable to access client number " + str(i), True, True, True)
            else:
                helper.log("error: JSON file header client count does not match the actual number of clients", True, True, True)

            # STEP THREE - Record match
            #----------------------------------------------------------------------------------------------
            #----------------------------------------------------------------------------------------------
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

            total_cnt = 0
            match_cnt = 0
            try:
                s8 = DBE.Server()
                s8.open()
            except:
                helper.log("error: Unable to access OACIS database. server: " + s8.server + " database: " + s8.database, True, True, True)
            for personObj in clientAccerta:
                total_cnt += 1
                try:
                    # little side journey first.
                    # we need to check to see if this person has already been checked before.
                    repeatList = s8.readIIOrcJSON(personObj.id)
                    if not len(repeatList) == 0:
                        personObj.repeatMatch(repeatList[0])
                        match_cnt += 1
                except:
                    helper.log("error: unable to check for repeats for " + personObj.id, True, True, True)
                try:
                    if not personObj.match and not Blocks.Block().getDob(personObj, s8, True) == 0:
                        personObjList_FullBlock = Blocks.Block().getDob(personObj, s8, False)
                        personObjList_LocMatch = Matching.Deterministic().city_or_postalcode_fsa_match(personObj, personObjList_FullBlock)
                        personObjList_FinalMatch = Matching.Deterministic().last(personObj, personObjList_LocMatch)
                        if not personObj.isSingleNamePerson():
                            personObjList_FinalMatch = Matching.Deterministic().first(personObj, personObjList_FinalMatch)
                        if not len(personObjList_FinalMatch) == 0:
                            personObj.recordMatch(1, personObjList_FinalMatch[0])
                            match_cnt += 1
                        elif not len(personObjList_LocMatch) == 0:
                            personObjList_FirstMatch = Matching.Deterministic().first(personObj, personObjList_LocMatch)
                            personObjList_FinalMatch = Matching.Deterministic().last_alias_match(personObj, personObjList_FirstMatch)
                            if not len(personObjList_FinalMatch) == 0:
                                personObj.recordMatch(3, personObjList_FinalMatch[0])
                                match_cnt += 1
                            if not personObj.match:
                                personObjList_LastMatch = Matching.Deterministic().last(personObj, personObjList_LocMatch)
                                personObjList_FinalMatch = Matching.Deterministic().first_alias_match(personObj, personObjList_LastMatch)
                                if not len(personObjList_FinalMatch) == 0:
                                    personObj.recordMatch(2, personObjList_FinalMatch[0])
                                    match_cnt += 1
                            if not personObj.match:
                                    personObjList_NameTranspose = Matching.Deterministic().first_last_transposition(personObj, personObjList_LocMatch)
                                    personObjList_FinalMatch = Matching.Deterministic().first_and_last_applicant(personObj, personObjList_NameTranspose)
                                    if not len(personObjList_FinalMatch) == 0:
                                        personObj.recordMatch(4, personObjList_FinalMatch[0])
                                        match_cnt += 1
                                    if not personObj.match:
                                        personObjList_LastMatch = Matching.Deterministic().last(personObj, personObjList_LocMatch)
                                        personObjList_FirstPhonic = Matching.Deterministic().first_phonic_match(personObj, personObjList_LastMatch)
                                        personObjList_FinalMatch = Matching.Deterministic().last_to_last_applicant(personObj, personObjList_FirstPhonic)
                                        if not len(personObjList_FinalMatch) == 0:
                                            personObj.recordMatch(5, personObjList_FinalMatch[0])
                                            match_cnt += 1
                                        if not personObj.match:
                                            personObjList_FirstMatch = Matching.Deterministic().first(personObj, personObjList_LocMatch)
                                            personObjList_LastPhonic = Matching.Deterministic().last_phonic_match(personObj, personObjList_FirstMatch)
                                            personObjList_FinalMatch = Matching.Deterministic().last_applicant(personObj, personObjList_LastPhonic)
                                            if not len(personObjList_FinalMatch) == 0:
                                                personObj.recordMatch(6, personObjList_FinalMatch[0])
                                                match_cnt += 1
                        else:
                            # check if location is wrong but everything else good!
                            personObjList_FirstMatch = Matching.Deterministic().first(personObj, personObjList_FullBlock)
                            personObjList_LastMatch = Matching.Deterministic().last(personObj, personObjList_FirstMatch)
                            personObjList_FirstApplicantMatch = Matching.Deterministic().first_applicant(personObj, personObjList_LastMatch)
                            personObjList_FinalMatch = Matching.Deterministic().last_applicant(personObj, personObjList_FirstApplicantMatch)
                            if not len(personObjList_FinalMatch) == 0:
                                personObj.recordMatch(7, personObjList_FinalMatch[0])
                                match_cnt += 1
                    if not personObj.match and not Blocks.Block().getFsa(personObj, s8, True) == 0:
                        personObjList_FullBlock = Blocks.Block().getFsa(personObj, s8, False)
                        personObjList_DobTranspose = Matching.Deterministic().dob_transpose(personObj, personObjList_FullBlock)
                        if not len(personObjList_DobTranspose) == 0:
                            personObjList_FirstMatch = Matching.Deterministic().first(personObj, personObjList_DobTranspose)
                            personObjList_LastMatch = Matching.Deterministic().last(personObj, personObjList_FirstMatch)
                            personObjList_FinalMatch = Matching.Deterministic().first_applicant(personObj, personObjList_LastMatch)
                            if not len(personObjList_FinalMatch) == 0:
                                personObj.recordMatch(8, personObjList_FinalMatch[0])
                                match_cnt += 1
                            if not personObj.match:
                                personObjList_FirstAliasMatch = Matching.Deterministic().first_alias_match(personObj, personObjList_DobTranspose)
                                personObjList_LastMatch = Matching.Deterministic().last(personObj, personObjList_FirstAliasMatch)
                                personObjList_FinalMatch = Matching.Deterministic().first_and_last_applicant(personObj, personObjList_LastMatch)
                                if not len(personObjList_FinalMatch) == 0:
                                    personObj.recordMatch(9, personObjList_FinalMatch[0])
                                    match_cnt += 1
                                if not personObj.match:
                                    personObjList_FirstAliasMatch = Matching.Deterministic().first(personObj, personObjList_DobTranspose)
                                    personObjList_LastMatch = Matching.Deterministic().last_alias_match(personObj, personObjList_FirstAliasMatch)
                                    personObjList_FinalMatch = Matching.Deterministic().first_and_last_applicant(personObj, personObjList_LastMatch)
                                    if not len(personObjList_FinalMatch) == 0:
                                        personObj.recordMatch(10, personObjList_FinalMatch[0])
                                        match_cnt += 1
                except():
                    helper.log("error: having trouble performing record matching for client id:" + personObj.id, True, True, True)

                print("Progress:" + str(total_cnt) + " Matches:" + str(match_cnt) + " Type:" + str(personObj.matchType))

            s8.close()
            f.close()

            # STEP SIX - Generate JSON and save to folder
            # ---------------------------------------------------
            # ---------------------------------------------------
            dte = datetime.today().strftime('%Y%m%d_%H%M')
            filename1 = "RR_" + dte + ".json"
            filename2 = "AUDIT_" + dte + ".json"
            header1 = {"Header": {"name": "Registration Response",
                   "clientCount": len(clients),
                   "fileDate":  datetime.today().strftime('%Y%m%d'),
                   "fileTime":  datetime.today().strftime('%H:%M')},
                   "Clients": []
                   }
            header2 = copy.deepcopy(header1)
            accertaJson = header1["Clients"]
            auditJson = header2["Clients"]
            try:
                for personObj in clientAccerta:
                    accertaJson.append(personObj.getJsonAccerta())
                    auditJson.append(personObj.getJsonAudit())
                with open(dirOutbound + filename1, 'w') as f1:
                    json.dump(header1, f1)
                #with open(dirArchiveOutbound + filename1, 'w') as f1:
                #    json.dump(header1, f1)
                f1.close()
                with open(dirCluster + filename2, 'w') as f2:
                    json.dump(header2, f2)
                #with open(dirArchiveCluster + filename2, 'w') as f2:
                #    json.dump(header2, f2)
                f2.close()
            except():
                helper.log("error: problem saving results into JSON files", True, True, True)
            shutil.move(dirInbound + currentJsonFileName, dirArchiveInbound + currentJsonFileName)
            print(str(currentFileCount) + " of " + str(len(getFiles)) + " files processed")
            #print("70 second delay begins...")
            #time.sleep(70)
            helper.log("progress: JSON file processed and results saved to " + filename1, True, False, False)
        elif currentFileCount > 0:
            #this means we have extra files....and we just have to move these files OUTA! here
            shutil.move(dirInbound + currentJsonFileName, dirArchiveExtraFiles + currentJsonFileName)
            helper.log("progress: not allowed to process multiple RC files, so this file has been moved to the ExtraFiles folder.", True, False, False)
            print(str(currentFileCount) + " of " + str(len(getFiles)) + " file not processed, moved to ExtraFiles folder.")
        else: #file doesn't start with RC
            shutil.move(dirInbound + currentJsonFileName, dirArchiveExtraFiles + currentJsonFileName)
            helper.log("progress: this file does not start with RC and has not been processed. File has been moved to the ExtraFiles folder.", True, False, False)
            print(str(currentFileCount) + " of " + str(len(getFiles)) + " file not an RC JSON file, moved to ExtraFiles folder.")
    print("COMPLETE!")
    helper.log("complete: duplication script has finished", True, False, False)
    if currentFileCount > 0:
        helper.log("Gandalf the Grey wishing you a pleasant morning. Oh yes....I used my magic on some JSON files overnight, and everything looks rather good!", False, True, False, "me")








