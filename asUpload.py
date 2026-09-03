import os
import datetime
import shutil
import traceback
import json
import sys

import openpyxl
from asnake.client import ASnakeClient

import aspace_templates
import aspace_helpers as helpers
import ua_locations
from asValidate import run_validate
from asinventory_runtime import build_runtime_paths, ensure_runtime_directories, load_repository_id


def run_upload(base_dir=None, input_path=None, output_path=None, complete_path=None, dao_path=None, interactive=True):
    paths = build_runtime_paths(base_dir, input_path, output_path, complete_path, dao_path)
    ensure_runtime_directories(paths)
    repository = load_repository_id()

    print ("Validating input directory before upload...")
    validationErrorCount = run_validate(base_dir=base_dir, input_path=input_path, output_path=output_path, complete_path=complete_path, dao_path=dao_path, interactive=False)
    if validationErrorCount > 0:
        print (f"Validation found {validationErrorCount} error(s). Fix these issues and re-run validation before uploading.")
        if interactive:
            print ("Press Enter to continue...")
            if sys.version_info >= (3, 0):
                input()
            else:
                raw_input()
        return 1

    try:
        print ("Reading input directory...")
        spreadsheetCount = 0
        for spreadFile in os.listdir(paths.input_path):
            if spreadFile.endswith(".xlsx"):
                spreadsheetCount += 1
                spreadsheet = os.path.join(paths.input_path, spreadFile)
                print ("Reading " + spreadFile)
                wb = openpyxl.load_workbook(filename=spreadsheet, read_only=True)
                boxSession = {}

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
                        print ("Reading sheet: " + sheet.title)

                        displayName = sheet["I1"].value
                        level = sheet["I2"].value
                        refID = sheet["I3"].value

                        try:
                            client = ASnakeClient()
                            client.authorize()
                        except:
                            raise ValueError("ERROR: ArchivesSpace login failed. Please check archivessnake configuration")

                        if level.lower().strip() == "resource":
                            resourceLevel = True
                            print ("Looking for resource matching " + str(displayName) + "...")
                            object = helpers.get_resource_by_id(client, repository, refID)
                            if object is None:
                                raise ValueError(f"Could not find resource with ID: {refID}")
                            resourceURI = object['uri']
                            print ("Found " + object['title'])
                        else:
                            resourceLevel = False
                            try:
                                print ("Looking for archival object matching " + str(displayName) + "...")
                            except:
                                print ("Looking for archival object matching [non-ascii component name]...")
                            object = helpers.get_archival_object_by_ref_id(client, repository, refID)
                            if object is None:
                                raise ValueError(f"Could not find archival object with ref_id: {refID}")
                            try:
                                print ("Found " + str(object['title']))
                            except:
                                print ("Found archival object matching [non-ascii component name].")
                            resourceURI = object['resource']['ref']
                            parentURI = object['uri']

                        if resourceLevel:
                            children = helpers.get_children_waypoint(client, resourceURI)
                        else:
                            children = helpers.get_children_waypoint(client, resourceURI, parentURI)
                        childCount = len(children)

                        rowCount = 0
                        for row in sheet.rows:
                            rowCount = rowCount + 1
                            if rowCount > 6:
                                fileCount = rowCount - 6
                                itemCount = fileCount + childCount

                                if not row[8].value is None:
                                    if row[0].value is None:
                                        fileObject = aspace_templates.archival_object()
                                        fileObject['level'] = "file"
                                        if resourceLevel == True:
                                            fileObject['resource'] = {"ref": resourceURI}
                                        else:
                                            fileObject['parent'] = {"ref": parentURI}
                                            fileObject['resource'] = {"ref": resourceURI}
                                    else:
                                        fileObject = helpers.get_archival_object_by_ref_id(client, repository, str(row[0].value).strip())
                                        if fileObject is None:
                                            raise ValueError(f"Could not find archival object with ref_id: {row[0].value}")

                                    fileObject['title'] = row[8].value.strip()
                                    fileObject['position'] = int(itemCount)
                                    fileObject['dates'] = []

                                    def updateDate(fileObject, normal, display):
                                        if display.lower().strip() == "none":
                                            display = ""
                                        if "/" in normal:
                                            if len(display) > 0:
                                                fileObject = helpers.add_date_to_object(fileObject, normal.split("/")[0].strip(), normal.split("/")[1].strip(), display)
                                            else:
                                                fileObject = helpers.add_date_to_object(fileObject, normal.split("/")[0].strip(), normal.split("/")[1].strip())
                                        else:
                                            if len(display) > 0:
                                                fileObject = helpers.add_date_to_object(fileObject, normal, None, display)
                                            else:
                                                fileObject = helpers.add_date_to_object(fileObject, normal)
                                        return fileObject

                                    def clearExcelEscape(dateString):
                                        if dateString.startswith('="') and dateString.endswith('"'):
                                            dateString = dateString[2:][:-1]
                                        return dateString

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

                                    if not row[21].value is None:
                                        fileObject = helpers.remove_notes_by_type(fileObject, "scopecontent")
                                        fileObject = helpers.add_note_to_object(fileObject, "scopecontent", row[21].value)
                                    if not row[20].value is None:
                                        fileObject = helpers.remove_notes_by_type(fileObject, "odd")
                                        fileObject = helpers.add_note_to_object(fileObject, "odd", row[20].value)
                                    if not row[19].value is None:
                                        fileObject = helpers.remove_notes_by_type(fileObject, "accessrestrict")
                                        fileObject['restrictions_apply'] = True
                                        fileObject = helpers.add_note_to_object(fileObject, "accessrestrict", row[19].value)

                                    if not row[4].value is None and not row[5].value is None:
                                        if not row[3].value is None or str(row[4].value) + " " + str(row[5].value) in boxSession.keys():
                                            if row[3].value is None:
                                                boxUri = boxSession[str(row[4].value) + " " + str(row[5].value)]
                                            else:
                                                boxUri = str(row[3].value).strip()
                                                boxSession[str(row[4].value) + " " + str(row[5].value)] = boxUri
                                            boxObject = client.get(boxUri).json()
                                            foundBox = False
                                            newInstances = []
                                            for instance in fileObject.get('instances', []):
                                                if "sub_container" in instance:
                                                    if instance['sub_container']['top_container']['ref'] == boxUri:
                                                        foundBox = True
                                                        newInstances.append(instance)
                                                elif "digital_object" in instance:
                                                    newInstances.append(instance)
                                            fileObject['instances'] = newInstances
                                            if foundBox == False:
                                                fileObject = helpers.add_container_to_object(fileObject, boxUri, None, None)

                                            for instance in fileObject.get('instances', []):
                                                if "sub_container" in instance:
                                                    if instance["sub_container"]["top_container"]["ref"] == boxUri:
                                                        if not row[4].value is None:
                                                            instance["sub_container"]["type_1"] = str(row[4].value).strip()
                                                            boxObject['type'] = str(row[4].value).strip()
                                                        if not row[5].value is None:
                                                            instance["sub_container"]["indicator_1"] = str(row[5].value).strip()
                                                            boxObject['indicator'] = str(row[5].value).strip()
                                                        if not row[6].value is None:
                                                            instance["sub_container"]["type_2"] = str(row[6].value).strip()
                                                        if not row[7].value is None:
                                                            instance["sub_container"]["indicator_2"] = str(row[7].value).strip()
                                            if not row[19].value is None:
                                                boxObject['restricted'] = True

                                            if not row[1].value is None:
                                                for locationURI in str(row[1].value).split(";"):
                                                    locTest = False
                                                    for location in boxObject.get('container_locations', []):
                                                        if location["ref"] == locationURI.strip():
                                                            locTest = True
                                                    if locTest == False:
                                                        boxObject = helpers.add_location_to_container(boxObject, locationURI)
                                            elif not row[2].value is None:
                                                boxObject['container_locations'] = []
                                                locCount = 0
                                                for locationSet in str(row[2].value).split(";"):
                                                    locCount = locCount + 1
                                                    if "(" in locationSet:
                                                        coordinates = locationSet.split("(")[0].strip()
                                                        locationNote = locationSet.split("(")[1].replace(")", "").strip()
                                                    else:
                                                        coordinates = locationSet.strip()
                                                        locationNote = None

                                                    coordList = ua_locations.location_to_aspace(coordinates.strip(), locationNote)
                                                    if coordList[1] is False:
                                                        locTitle = coordList[0]["Title"]
                                                        locationURI = ua_locations.find_location_uri(client, locTitle, coordList[0])
                                                        if len(coordList[0]["Note"]) > 0:
                                                            if locCount > 1:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI, coordList[0]["Note"], "previous", "2999-01-01")
                                                            else:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI, coordList[0]["Note"])
                                                        else:
                                                            if locCount > 1:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI, None, "previous", "2999-01-01")
                                                            else:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI)
                                                    else:
                                                        for location in coordList[0]:
                                                            locTitle = location["Title"]
                                                            locationURI = ua_locations.find_location_uri(client, locTitle, location)
                                                            if len(location["Note"]) > 0:
                                                                if locCount > 1:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
                                                                else:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI, location["Note"])
                                                            else:
                                                                if locCount > 1:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI, None, "previous", "2999-01-01")
                                                                else:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI)
                                                print ("        Added location(s) to containers")
                                        else:
                                            fileObject = helpers.remove_container_instances(fileObject)
                                            boxObject = aspace_templates.top_container(str(row[4].value).strip(), str(row[5].value).strip())
                                            boxResponse = helpers.post_container(client, repository, boxObject)
                                            boxUri = boxResponse.json()['uri']
                                            boxSession[str(row[4].value).strip() + " " + str(row[5].value).strip()] = boxUri
                                            if not row[6].value is None:
                                                childContainer = str(row[6].value).strip()
                                            else:
                                                childContainer = None
                                            if not row[7].value is None:
                                                childIndicator = str(row[7].value).strip()
                                            else:
                                                childIndicator = None
                                            fileObject = helpers.add_container_to_object(fileObject, boxUri, childContainer, childIndicator)
                                            if not row[19].value is None:
                                                boxObject['restricted'] = True
                                            boxObject = client.get(boxUri).json()

                                            if not row[1].value is None:
                                                for locationURI in str(row[1].value).split(";"):
                                                    locTest = False
                                                    for location in boxObject.get('container_locations', []):
                                                        if location["ref"] == locationURI.strip():
                                                            locTest = True
                                                    if locTest == False:
                                                        boxObject = helpers.add_location_to_container(boxObject, locationURI)
                                            elif not row[2].value is None:
                                                boxObject['container_locations'] = []
                                                locCount = 0
                                                for locationSet in str(row[2].value).split(";"):
                                                    locCount = locCount + 1
                                                    if "(" in locationSet:
                                                        coordinates = locationSet.split("(")[0].strip()
                                                        locationNote = locationSet.split("(")[1].replace(")", "").strip()
                                                    else:
                                                        coordinates = locationSet.strip()
                                                        locationNote = None

                                                    coordList = ua_locations.location_to_aspace(coordinates.strip(), locationNote)
                                                    if coordList[1] is False:
                                                        locTitle = coordList[0]["Title"]
                                                        locationURI = ua_locations.find_location_uri(client, locTitle, coordList[0])
                                                        if len(coordList[0]["Note"]) > 0:
                                                            if locCount > 1:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI, coordList[0]["Note"], "previous", "2999-01-01")
                                                            else:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI, coordList[0]["Note"])
                                                        else:
                                                            if locCount > 1:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI, None, "previous", "2999-01-01")
                                                            else:
                                                                boxObject = helpers.add_location_to_container(boxObject, locationURI)
                                                    else:
                                                        for location in coordList[0]:
                                                            locTitle = location["Title"]
                                                            locationURI = ua_locations.find_location_uri(client, locTitle, location)
                                                            if len(location["Note"]) > 0:
                                                                if locCount > 1:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
                                                                else:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI, location["Note"])
                                                            else:
                                                                if locCount > 1:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI, None, "previous", "2999-01-01")
                                                                else:
                                                                    boxObject = helpers.add_location_to_container(boxObject, locationURI)
                                                print ("        Added location(s) to containers")

                                        postResponse = client.post(boxObject['uri'], json=boxObject)
                                        if postResponse.status_code == 200:
                                            print ("        Posted " + str(row[4].value) + " " + str(row[5].value))
                                        else:
                                            print ("    Failed to post " +  str(row[4].value) + " " + str(row[5].value) + ", error code " + str(postResponse.status_code))
                                            print(json.dumps(boxObject, indent=2))

                                    fileObject['publish'] = True
                                    postAO = helpers.post_archival_object(client, repository, fileObject)

                                    if postAO.status_code == 200:
                                        try:
                                            print ("    Posted " + row[8].value)
                                        except:
                                            print ("    Posted non-ascii text")
                                    else:
                                        print (postAO.text)
                                        raise ValueError("    Failed to post, error code " + str(postAO))

                                    if not row[22].value is None:
                                        if str(row[22].value).strip().lower().startswith("http"):
                                            if postAO.status_code == 200:
                                                print ("    -->Uploading dao for " + str(row[22].value))
                                                aoURI = postAO.json()["uri"]
                                                ao = client.get(aoURI).json()
                                                finalFile = str(row[22].value).strip()
                                                fileTitle = os.path.basename(row[22].value)
                                                if len(fileTitle) < 1:
                                                    fileTitle = str(row[8].value).strip()
                                                daoLink = finalFile

                                                daoObject = aspace_templates.digital_object(fileTitle, daoLink)
                                                daoObject["publish"] = True
                                                postDAO = helpers.post_digital_object(client, repository, daoObject)
                                                if postDAO.status_code == 200:
                                                    daoURI = postDAO.json()["uri"]
                                                    ao = helpers.add_digital_object_to_object(ao, daoURI)
                                                    postAO = helpers.post_archival_object(client, repository, ao)
                                                    if not postAO.status_code == 200:
                                                        raise ValueError("Error posting archival object with digital object " + str(row[22].value) + " HTTP response " + str(postAO.status_code) + ". Object: " + json.dumps(ao, indent=2))
                                                else:
                                                    raise ValueError("Error posting digital object " + row[22].value)

                wb._archive.close()
                print ("Moving " + spreadFile + " to complete directory...")
                if os.path.isfile(os.path.join(paths.complete_path, spreadFile)):
                    shutil.copy2(os.path.join(paths.input_path, spreadFile), os.path.join(paths.complete_path, os.path.splitext(spreadFile)[0] + str(datetime.datetime.now()).split(".")[0].replace(":", "_") + ".xlsx"))
                else:
                    shutil.copy2(os.path.join(paths.input_path, spreadFile), paths.complete_path)
            else:
                print ("ERROR: incorrect file " + spreadFile + " in input path.")

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
        file = open(paths.error_log_path, "a")
        file.write(errorOutput)
        file.close()
        if interactive:
            print (outputText)
            print ("Press Enter to continue...")
            if sys.version_info >= (3, 0):
                input()
            else:
                raw_input()
        return 1

    if interactive:
        print ("Press Enter to continue...")
        if sys.version_info >= (3, 0):
            input()
        else:
            raw_input()
    return 0


def main():
    return run_upload()


if __name__ == "__main__":
    raise SystemExit(main())
