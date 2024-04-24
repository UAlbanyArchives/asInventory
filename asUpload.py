import os
from subprocess import Popen, PIPE, STDOUT
import requests
import datetime
import shutil
import traceback
import json
import sys

#non-standard dependencies
import configparser
import openpyxl
from archives_tools import aspace as AS
from archives_tools import uaLocations
from archives_tools.dacs import iso2DACS

# Main error handleing
try:

    __location__ = os.path.dirname(os.path.abspath(__file__))

    # get local_settings
    configPath = os.path.join(__location__, "local_settings.cfg")
    if not os.path.isfile(configPath):
        raise ValueError("ERROR: Could not find local_settings.cfg")
    config = configparser.ConfigParser()
    config.read(configPath)

    baseURL = config.get('ArchivesSpace', 'baseURL')
    repository = config.get('ArchivesSpace', 'repository')
    user = config.get('ArchivesSpace', 'user')
    password = config.get('ArchivesSpace', 'password')
    loginData = (baseURL, user, password)

    # required directories, make them if they don't exist
    inputPath = os.path.join(__location__, "input")
    if not os.path.isdir(inputPath):
        os.mkdir(inputPath)
    outputPath = os.path.join(__location__, "output")
    if not os.path.isdir(outputPath):
        os.mkdir(outputPath)
    completePath = os.path.join(__location__, "complete")
    if not os.path.isdir(completePath):
        os.mkdir(completePath)
    daoPath = os.path.join(__location__, "dao")
    if not os.path.isdir(daoPath):
        os.mkdir(daoPath)

    
    print ("Reading input directory...")
    spreadsheetCount = 0
    for spreadFile in os.listdir(inputPath):
        
        #find and load sheets
        if spreadFile.endswith(".xlsx"):
            spreadsheetCount += 1
            spreadsheet = os.path.join(inputPath, spreadFile)
            print ("Reading " + spreadFile)
            wb = openpyxl.load_workbook(filename=spreadsheet, read_only=True)
            
            #this insures Boxes with the same numbers in the entire worksheet will make only one ArchviesSpace container
            boxSession = {}
            
            #validate sheets
            for sheet in wb.worksheets:
                checkSwitch = True
                try:
                    if sheet["H1"].value.lower().strip() != "title":
                        checkSwitch = False
                    elif sheet["H2"].value.lower().strip() != "level":
                        checkSwitch = False
                    elif sheet["H3"].value.lower().strip() != "ref id":
                        checkSwitch = False
                    elif sheet["J6"].value.lower().strip() != "date 1 display":
                        checkSwitch = False
                    elif sheet["D6"].value.lower().strip() != "container uri":
                        checkSwitch = False
                except:
                    print ("ERROR: incorrect sheet " + sheet.title + " in file " + spreadFile)
                    
                if checkSwitch == False:
                    print ("ERROR: incorrect sheet " + sheet.title + " in file " + spreadFile)
                else:
                
                    #Read sheet info
                    print ("Reading sheet: " + sheet.title)
                    
                    displayName = sheet["I1"].value
                    level = sheet["I2"].value
                    refID = sheet["I3"].value
                    
                    #login to ArchivesSpace
                    session = AS.getSession(loginData)
                    if session is None:
                        raise ValueError("ERROR: ArchivesSpace login failed. Please check settings in local_settings.cfg")
                    
                    if level.lower().strip() == "resource":
                        resourceLevel = True
                        print ("Looking for resource matching " + str(displayName) + "...")
                        object = AS.getResourceID(session, repository, refID, loginData)
                        resourceURI = object.uri
                        print ("Found " + object.title)
                    else:
                        resourceLevel = False
                        try:
                             print ("Looking for archival object matching " + str(displayName) + "...")
                        except:
                            print ("Looking for archival object matching [non-ascii component name]...")
                        object = AS.getArchObjID(session, repository, refID, loginData)
                        try:
                            print ("Found " + str(object.title))
                        except:
                            print ("Found archival object matching [non-ascii component name].")
                        resourceURI = object.resource.ref
                        parentURI = object.uri
                        
                    #get count of existing items
                    childCount = 0
                    for objectChild in AS.getChildren(session, object, loginData).children:
                        childCount += 1
                        
                    rowCount = 0
                    for row in sheet.rows:
                        rowCount = rowCount + 1
                        if rowCount > 6:
                            fileCount = rowCount - 6
                            itemCount = fileCount + childCount
                            
                            #make sure there is a title
                            if not row[8].value is None:
                            
                                #make new file object if its new
                                if row[0].value is None:
                                    fileObject = AS.makeArchObj()
                                    fileObject.level = "file"
                                    if resourceLevel == True:
                                        fileObject.resource = {"ref": resourceURI}
                                    else:
                                        fileObject.parent = {"ref": parentURI}
                                        fileObject.resource = {"ref": resourceURI}
                                else:
                                    #else get existing object
                                    fileObject = AS.getArchObjID(session, repository, str(row[0].value).strip(), loginData)
                                    
                                #set title and position
                                fileObject.title = row[8].value.strip()
                                #print (str(row[8].value) + " --> position " + str(itemCount) )
                                fileObject.position = int(itemCount)
                                #print (fileObject.position)
                                #clear dates
                                fileObject.dates = []
                                
                                def updateDate(fileObject, normal, display):
                                    if display.lower().strip() == "none":
                                        display = ""
                                    if "/" in normal:
                                        #date range
                                        if len(display) > 0:
                                            fileObject = AS.makeDate(fileObject, normal.split("/")[0].strip(), normal.split("/")[1].strip(), display)
                                        else:
                                            fileObject = AS.makeDate(fileObject, normal.split("/")[0].strip(), normal.split("/")[1].strip())
                                    else:
                                        #single date
                                        if len(display) > 0:
                                            fileObject = AS.makeDate(fileObject, normal, "", display)
                                        else:
                                            fileObject = AS.makeDate(fileObject, normal)
                                    return fileObject
                                
                                def clearExcelEscape(dateString):
                                    if dateString.startswith("=\"") and dateString.endswith("\""):
                                        dateString = dateString[2:][:-1]
                                    return dateString
                                
                                #enter dates
                                if not row[10].value is None:
                                    if len(str(row[10].value).strip()) > 0:
                                        fileObject = updateDate(fileObject, clearExcelEscape(str(row[10].value).strip()), str(row[9].value).strip())
                                if not row[12].value is None:
                                    if len(str(row[12].value).strip()) > 0:
                                        fileObject = updateDate(fileObject, clearExcelEscape(str(row[12].value).strip()), str(row[11].value).strip())
                                if not row[14].value is None:
                                    if len(str(row[14].value).strip()) > 0:
                                        fileObject = updateDate(fileObject, clearExcelEscape(str(row[14].value).strip()), str(row[13].value).strip())
                                if not row[16].value is None:
                                    if len(str(row[16].value).strip()) > 0:
                                        fileObject = updateDate(fileObject, clearExcelEscape(str(row[16].value).strip()), str(row[15].value).strip())
                                if not row[18].value is None:
                                    if len(str(row[18].value).strip()) > 0:
                                        fileObject = updateDate(fileObject, clearExcelEscape(str(row[18].value).strip()), str(row[17].value).strip())
                                    
                                #scope note
                                if not row[21].value is None:
                                    newNotes = []
                                    for note in fileObject.notes:
                                        if note.type == "scopecontent":
                                            pass
                                        else:
                                            newNotes.append(note)
                                    fileObject.notes = newNotes
                                    fileObject = AS.makeMultiNote(fileObject, "scopecontent", row[21].value)
                                #general note
                                if not row[20].value is None:
                                    newNotes = []
                                    for note in fileObject.notes:
                                        if note.type == "odd":
                                            pass
                                        else:
                                            newNotes.append(note)
                                    fileObject.notes = newNotes
                                    fileObject = AS.makeMultiNote(fileObject, "odd", row[20].value)
                                #access restrict note
                                if not row[19].value is None:
                                    newNotes = []
                                    for note in fileObject.notes:
                                        if note.type == "accessrestrict":
                                            pass
                                        else:
                                            newNotes.append(note)
                                    fileObject.notes = newNotes
                                    fileObject.restrictions_apply = True
                                    fileObject = AS.makeMultiNote(fileObject, "accessrestrict", row[19].value)
                                
                                
                                
                                #containers
                                #print (boxSession)
                                if not row[4].value is None and not row[5].value is None:
                                    #if there is container info entered in spreadsheet
                                    if not row[3].value is None or str(row[4].value) + " " + str(row[5].value) in boxSession.keys():
                                        #existing container
                                        if row[3].value is None:
                                            boxUri = boxSession[str(row[4].value) + " " + str(row[5].value)]
                                        else:
                                            boxUri = str(row[3].value).strip()
                                            boxSession[str(row[4].value) + " " + str(row[5].value)] = boxUri
                                        boxObject = AS.getContainer(session, boxUri, loginData)
                                        #look for existing box link
                                        foundBox = False
                                        newInstances = []
                                        for instance in fileObject.instances:
                                            if "sub_container" in instance.keys():
                                                if instance.sub_container.top_container.ref == boxUri:
                                                    foundBox = True
                                                    newInstances.append(instance)
                                            elif "digital_object" in instance.keys():
                                                newInstances.append(instance)
                                        fileObject.instances = newInstances
                                        if foundBox == False:
                                            #link to existing box
                                            fileObject = AS.addToContainer(session, fileObject, boxUri, None, None, loginData)
                                            
                                        #modify existing box
                                        for instance in fileObject.instances:
                                            if "sub_container" in instance.keys():
                                                if instance["sub_container"]["top_container"]["ref"] == boxUri:
                                                    if not row[4].value is None:
                                                        instance["sub_container"]["type_1"] = str(row[4].value).strip()
                                                        boxObject.type = str(row[4].value).strip()
                                                    if not row[5].value is None:
                                                        instance["sub_container"]["indicator_1"] = str(row[5].value).strip()
                                                        boxObject.indicator = str(row[5].value).strip()
                                                    if not row[6].value is None:
                                                        instance["sub_container"]["type_2"] = str(row[6].value).strip()
                                                        instance["sub_container"]["type_2"] = str(row[6].value).strip()
                                                    if not row[7].value is None:
                                                        instance["sub_container"]["indicator_2"] = str(row[7].value).strip()
                                                        instance["sub_container"]["indicator_2"] = str(row[7].value).strip()
                                        #add any restrictions to box
                                        if not row[19].value is None:
                                            boxObject.restricted = True
                                        
                                        
                                        #update locations
                                        if not row[1].value is None:
                                            for locationURI in str(row[1].value).split(";"):
                                                locTest = False
                                                for location in boxObject.container_locations:
                                                    if location["ref"] == locationURI.strip():
                                                        locTest = True
                                                if locTest == False:
                                                    boxObject = AS.addToLocation(boxObject, locationURI)
                                        elif not row[2].value is None:
                                            #remove existing locations
                                            boxObject.container_locations = []
                                            
                                            #location, but without URI
                                            locCount = 0
                                            for locationSet in str(row[2].value).split(";"):
                                                locCount = locCount + 1
                                                if "(" in locationSet:
                                                    coordinates = locationSet.split("(")[0].strip()
                                                    locationNote = locationSet.split("(")[1].replace(")", "").strip()
                                                else:
                                                    coordinates = locationSet.strip()
                                                    locationNote = None
                                                
                                                coordList = uaLocations.location2ASpace(coordinates.strip(), locationNote)
                                                if coordList[1] is False:
                                                    #single location
                                                    locTitle = coordList[0]["Title"]
                                                    locationURI = AS.findLocation(session, locTitle, loginData)
                                                    if len(coordList[0]["Note"]) > 0:
                                                        if locCount > 1:
                                                            boxObject = AS.addToLocation(boxObject, locationURI, coordList[0]["Note"], "previous", "2999-01-01")
                                                        else:
                                                            boxObject = AS.addToLocation(boxObject, locationURI, coordList[0]["Note"])
                                                    else:
                                                        if locCount > 1:
                                                            boxObject = AS.addToLocation(boxObject, locationURI, None, "previous", "2999-01-01")
                                                        else:
                                                            boxObject = AS.addToLocation(boxObject, locationURI)
                                                else:
                                                    #multiple locations
                                                    for location in coordList[0]:
                                                        locTitle = location["Title"]
                                                        locationURI = AS.findLocation(session, locTitle, loginData)
                                                        if len(location["Note"]) > 0:
                                                            if locCount > 1:
                                                                boxObject = AS.addToLocation(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
                                                            else:
                                                                boxObject = AS.addToLocation(boxObject, locationURI, location["Note"])
                                                        else:
                                                            if locCount > 1:
                                                                boxObject = AS.addToLocation(boxObject, locationURI, None, "previous", "2999-01-01")
                                                            else:
                                                                boxObject = AS.addToLocation(boxObject, locationURI)
                                            print ("        Added location(s) to containers")
                                                
                                        
                                    else:
                                        #new box
                                        
                                        #delete existing boxes
                                        newInstances = []
                                        for instance in fileObject.instances:
                                            if "sub_container" in instance.keys():
                                                pass
                                            else:
                                                newInstances.append(instance)
                                        fileObject.instances = newInstances
                                        #makes and posts a new container
                                        boxObject = AS.makeContainer(session, repository, str(row[4].value).strip(), str(row[5].value).strip(), loginData)
                                        #update dict of new boxes for this sheet
                                        boxSession[str(row[4].value).strip() + " " + str(row[5].value).strip()] = boxObject.uri
                                        if not row[6].value is None:
                                            childContainer = str(row[6].value).strip()
                                        else:
                                            childContainer = None
                                        if not row[7].value is None:
                                            childIndicator = str(row[7].value).strip()
                                        else:
                                            childIndicator = None
                                        fileObject = AS.addToContainer(session, fileObject, boxObject.uri, childContainer,  childIndicator, loginData)
                                        #add any restrictions to box
                                        if not row[19].value is None:
                                            boxObject.restricted = True
                                            
                                        #update locations
                                        if not row[1].value is None:
                                            for locationURI in str(row[1].value).split(";"):
                                                locTest = False
                                                for location in boxObject.container_locations:
                                                    if location["ref"] == locationURI.strip():
                                                        locTest = True
                                                if locTest == False:
                                                    boxObject = AS.addToLocation(boxObject, locationURI)
                                        elif not row[2].value is None:
                                            #remove existing locations from boxObject
                                            boxObject.container_locations = []
                                        
                                            #location, but without URI
                                            locCount = 0
                                            for locationSet in str(row[2].value).split(";"):
                                                locCount = locCount + 1
                                                if "(" in locationSet:
                                                    coordinates = locationSet.split("(")[0].strip()
                                                    locationNote = locationSet.split("(")[1].replace(")", "").strip()
                                                else:
                                                    coordinates = locationSet.strip()
                                                    locationNote = None
                                                
                                                coordList = uaLocations.location2ASpace(coordinates.strip(), locationNote)
                                                if coordList[1] is False:
                                                    #single location
                                                    locTitle = coordList[0]["Title"]
                                                    locationURI = AS.findLocation(session, locTitle, loginData)
                                                    if len(coordList[0]["Note"]) > 0:
                                                        if locCount > 1:
                                                            boxObject = AS.addToLocation(boxObject, locationURI, coordList[0]["Note"], "previous", "2999-01-01")
                                                        else:
                                                            boxObject = AS.addToLocation(boxObject, locationURI, coordList[0]["Note"])
                                                    else:
                                                        if locCount > 1:
                                                            boxObject = AS.addToLocation(boxObject, locationURI, None, "previous", "2999-01-01")
                                                        else:
                                                            boxObject = AS.addToLocation(boxObject, locationURI)
                                                else:
                                                    #multiple locations
                                                    for location in coordList[0]:
                                                        locTitle = location["Title"]
                                                        locationURI = AS.findLocation(session, locTitle, loginData)
                                                        if len(location["Note"]) > 0:
                                                            if locCount > 1:
                                                                boxObject = AS.addToLocation(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
                                                            else:
                                                                boxObject = AS.addToLocation(boxObject, locationURI, location["Note"])
                                                        else:
                                                            if locCount > 1:
                                                                boxObject = AS.addToLocation(boxObject, locationURI, None, "previous", "2999-01-01")
                                                            else:
                                                                boxObject = AS.addToLocation(boxObject, locationURI)
                                            print ("        Added location(s) to containers")
                                        
                                    #post top container object
                                    postBox = AS.postContainer(session, repository, boxObject, loginData)
                                    if postBox.status_code == 200:
                                        print ("        Posted " + str(row[4].value) + " " + str(row[5].value))
                                    else:
                                        print ("    Failed to post " +  str(row[4].value) + " " + str(row[5].value) + ", error code " + str(postBox))
                                        AS.pp(boxObject)
                                
                                    
                                
                                #post file object
                                fileObject.publish = True
                                #postAO = AS.postArchObj(session, repository, fileObject, loginData)
                                aoString = json.dumps(fileObject)
                                aoObj = json.loads(aoString)                                
                                if "ref_id" in fileObject:
                                    aoID = fileObject.uri.split("/archival_objects/")[1]
                                    postAO = requests.post(loginData[0] + "/repositories/" + str(repository) + "/archival_objects/" + aoID, json=aoObj, headers=session)
                                else:
                                    postAO = requests.post(loginData[0] + "/repositories/" + str(repository) + "/archival_objects", json=aoObj, headers=session)
                                AS.checkError(postAO)
                                
                                if postAO.status_code == 200:
                                    try:
                                        print ("    Posted " + row[8].value)
                                    except:
                                        print ("    Posted non-ascii text")
                                else:
                                    print (postAO.text)
                                    raise ValueError("    Failed to post, error code " + str(postAO))
                                
                                #Digital Object
                                if not row[22].value is None:
                                    #if post was successful
                                    
                                    # will now ignore non-http daos, must upload to Hyrax and get uris first
                                    if str(row[22].value).strip().lower().startswith("http"):
                                        if postAO.status_code == 200:
                                            print ("    -->Uploading dao for " + str(row[22].value))
                                            
                                            #get nessessary parent data
                                            aoURI = postAO.json()["uri"]
                                            ao = AS.getArchObj(session, aoURI, loginData)
                                            aoRef = ao["ref_id"]
                                            resourceURI = ao["resource"]["ref"]
                                            coll = AS.getResource(session, repository, resourceURI.split("/resources/")[1], loginData)
                                            resourceID = coll["id_0"]
                                            
                                            if not str(row[22].value).strip().lower().startswith("http"):
                                                
                                                pass
                                                # will now ignore non-http daos, must upload to Hyrax and get uris first
                                                    
                                            else:
                                                #for simple http links
                                                finalFile = str(row[22].value).strip()
                                                fileTitle = os.path.basename(row[22].value)
                                                if len(fileTitle) < 1:
                                                    fileTitle = str(row[8].value).strip()
                                                daoLink = finalFile                        
                                            
                                            daoObject = AS.makeDAO(fileTitle, daoLink)
                                            #untested change here
                                            daoObject["publish"] = True
                                            postDAO = AS.postDAO(session, repository, daoObject, loginData)
                                            if postDAO.status_code == 200:
                                                daoURI = postDAO.json()["uri"]
                                                
                                                ao = AS.addDAO(ao, daoURI, False)
                                                postAO = AS.postArchObj(session, repository, ao, loginData)
                                                if not postAO.status_code == 200:
                                                    raise ValueError("Error posting archival object with digital object " + str(row[22].value) + " HTTP response " + str(postAO.status_code) + ". Object: " + json.dumps(ao, indent=2))
                                                                                                
                                            else:
                                                raise ValueError("Error posting digital object " + row[22].value)
                                                                                
                                    
                                
            wb._archive.close()
            print ("Moving " + spreadFile + " to complete directory...")
            completeDir = os.path.join(os.path.dirname(inputPath), "complete")
            if os.path.isfile(os.path.join(completeDir, spreadFile)):
                shutil.copy2(os.path.join(inputPath, spreadFile), os.path.join(completeDir, os.path.splitext(spreadFile)[0] + str(datetime.datetime.now()).split(".")[0].replace(":", "_") + ".xlsx"))        
            else:
                shutil.copy2(os.path.join(inputPath, spreadFile), completeDir)
            #os.remove(os.path.join(inputPath, spreadFile))
        else:
            print ("ERROR: incorrect file " + spreadFile + " in input path.")
    
    #notify user of upload result
    if spreadsheetCount > 0:
        if spreadsheetCount == 1:
            resultMsg = "Successfully uploaded " + str(spreadsheetCount) + " spreadsheet to ArchivesSpace."
        else:
            resultMsg = "Successfully uploaded " + str(spreadsheetCount) + " spreadsheets to ArchivesSpace."
        print (resultMsg)
    else:
        resultMsg = "No valid spreadsheets found in input directory."
        print (resultMsg)


except:
    exceptMsg = traceback.format_exc()
    outputText = "asUpload error: " + exceptMsg
    errorOutput = "\n" + "#############################################################\n" + str(datetime.datetime.now()) + "\n#############################################################\n" + exceptMsg + "\n********************************************************************************"
    file = open(os.path.join(__location__, "error.log"), "a")
    file.write(errorOutput)
    file.close()
	
# make sure console doesn't close
print ("Press Enter to continue...")
if sys.version_info >= (3, 0):
	input()
else:
	raw_input()