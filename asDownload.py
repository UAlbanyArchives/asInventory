import os
import re
import sys
import json
import datetime
import traceback

import openpyxl
from asnake.client import ASnakeClient

from asinventory_runtime import build_runtime_paths, ensure_runtime_directories, load_repository_id


def safe_filename(s):
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', s).strip().rstrip('.')


def getInput(object, displayTitle, resourceLevel, client, repository):
    print ("Export Resource(r) or archival object(ao):")
    level = input()

    print ("Enter ID:")
    cmpntID = input()

    if len(cmpntID) < 1:
        print ("Missing ID. Please Enter a Ref ID for an Archival Object or an id_0 for a Resource.")
        object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, client, repository)
    else:
        if level.lower().strip() == "resource" or level.lower().strip() == "r":
            print ("Looking for Resource...")
            try:
                aq = json.dumps({"query": {"field": "identifier", "value": cmpntID, "jsonmodel_type": "field_query"}})
                search_results = client.get('repositories/{}/search'.format(repository), params={'page': '1', 'aq': aq}).json()
                if search_results.get('total_hits', 0) > 0:
                    resource_uri = search_results['results'][0]['uri']
                    object = client.get(resource_uri).json()
                    resourceLevel = True
                    displayTitle = object['title'].replace("/", "-")
                else:
                    object = None
            except:
                object = None

            if object is None:
                print ("Try Again\n\n")
                object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, client, repository)
        else:
            if len(cmpntID) != 32:
                print ("It looks like you selcted archival object, but this is not an archival object ref_id. Check that you have the correct ID or select resource instead.\n\n")
                object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, client, repository)
            else:
                print ("Looking for Archival Object...")
                try:
                    ao_result = client.get('repositories/{}/find_by_id/archival_objects'.format(repository), params={'ref_id[]': cmpntID}).json()
                    if ao_result.get('archival_objects'):
                        ao_uri = ao_result['archival_objects'][0]['ref']
                        object = client.get(ao_uri).json()
                        resourceLevel = False
                        displayTitle = object.get('display_string', object.get('title', ''))
                    else:
                        object = None
                except:
                    object = None

                if object is None:
                    print ("Try Again\n\n")
                    object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, client, repository)

    return object, displayTitle, resourceLevel


def get_children_waypoint(client, resource_uri, node_uri=None):
    children = []
    try:
        if node_uri is None:
            tree = client.get(resource_uri + '/tree/root').json()
        else:
            tree = client.get(resource_uri + '/tree/node', params={'node_uri': node_uri}).json()

        max_offset = tree.get('waypoints', 0)

        for i in range(max_offset):
            batch_params = {'offset': i}
            if node_uri is not None:
                batch_params['parent_node'] = node_uri
            batch = client.get(resource_uri + '/tree/waypoint', params=batch_params).json()
            for child in batch:
                children.append({'record_uri': child['uri'], 'title': child.get('title', '')})
    except Exception as e:
        print(f"Error getting children: {e}")
    return children


def run_download(base_dir=None, input_path=None, output_path=None, complete_path=None, dao_path=None, interactive=True):
    paths = build_runtime_paths(base_dir, input_path, output_path, complete_path, dao_path)
    ensure_runtime_directories(paths)

    try:
        client = ASnakeClient()
        client.authorize()
        print ("ASpace Connection Successful")
    except:
        raise ValueError("ERROR: ArchivesSpace login failed. Please check archivessnake configuration")

    repository = load_repository_id()

    try:
        object, displayTitle, resourceLevel = getInput(None, "", False, client, repository)
        wb = openpyxl.Workbook()

        simpleTitle = safe_filename(object['title'].replace("/", "-"))
        print ("Reading " + simpleTitle)

        if resourceLevel == True:
            objectID = object['id_0']
        else:
            objectID = object['ref_id']

        worksheet = wb.active
        worksheet["H1"] = "Title"
        worksheet["I1"] = displayTitle
        worksheet["H2"] = "Level"
        if resourceLevel == True:
            worksheet["I2"] = "resource"
        else:
            worksheet["I2"] = "archival object"
        worksheet["H3"] = "Ref ID"
        worksheet["I3"] = objectID

        worksheet["A6"] = "ID"
        worksheet["B6"] = "Location ID"
        worksheet["C6"] = "Location"
        worksheet["D6"] = "Container URI"
        worksheet["E6"] = "Container"
        worksheet["F6"] = "C#"
        worksheet["G6"] = "Folder"
        worksheet["H6"] = "F#"
        worksheet["I6"] = "Title"
        worksheet["J6"] = "Date 1 Display"
        worksheet["K6"] = "Date 1 Normal"
        worksheet["L6"] = "Date 2 Display"
        worksheet["M6"] = "Date 2 Normal"
        worksheet["N6"] = "Date 3 Display"
        worksheet["O6"] = "Date 3 Normal"
        worksheet["P6"] = "Date 4 Display"
        worksheet["Q6"] = "Date 4 Normal"
        worksheet["R6"] = "Date 5 Display"
        worksheet["S6"] = "Date 5 Normal"
        worksheet["T6"] = "Restrictions"
        worksheet["U6"] = "General Note"
        worksheet["V6"] = "Scope"
        worksheet["W6"] = "DAO Filename"

        tableStyle = openpyxl.worksheet.table.TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)

        if resourceLevel == True:
            childrenList = get_children_waypoint(client, object['uri'])
        else:
            resource_uri = object['resource']['ref']
            childrenList = get_children_waypoint(client, resource_uri, object['uri'])

        lineCount = 6
        for child in childrenList:
            childObject = client.get(child['record_uri']).json()
            lineCount = lineCount + 1
            worksheet["A" + str(lineCount)] = childObject['ref_id']
            worksheet["I" + str(lineCount)] = childObject['title']
            try:
                print ("\texporting " + childObject['title'])
            except:
                print ("\texporting non-ascii file...")

            if len(childObject.get('instances', [])) > 0:
                if "sub_container" in childObject['instances'][0]:
                    container = childObject['instances'][0]['sub_container']
                    containerURI = container['top_container']['ref']
                    worksheet["D" + str(lineCount)] = containerURI
                    if "type_2" in container:
                        worksheet["G" + str(lineCount)] = container['type_2']
                    if "indicator_2" in container:
                        worksheet["H" + str(lineCount)] = container['indicator_2']

                    containerObject = client.get(containerURI).json()
                    worksheet["E" + str(lineCount)] = containerObject['type']
                    worksheet["F" + str(lineCount)] = containerObject['indicator']

                    locationCount = 0
                    for location in containerObject.get('container_locations', []):
                        locationCount = locationCount + 1
                        locationObject = client.get(location['ref']).json()
                        if "area" in locationObject:
                            locationCoordinates = locationObject['area'] + "-" + locationObject['coordinate_1_indicator']
                        else:
                            locationCoordinates = locationObject['room'] + "-" + locationObject['coordinate_1_indicator']
                        if "coordinate_2_indicator" in locationObject:
                            locationCoordinates = locationCoordinates + "-" + locationObject['coordinate_2_indicator']
                        if "coordinate_3_indicator" in locationObject:
                            locationCoordinates = locationCoordinates + "-" + locationObject['coordinate_3_indicator']
                        if locationCount < 2:
                            worksheet["B" + str(lineCount)] = locationObject['uri']
                            worksheet["C" + str(lineCount)] = locationCoordinates
                        else:
                            worksheet["B" + str(lineCount)] = worksheet["B" + str(lineCount)].value + "; " + locationObject['uri']
                            worksheet["C" + str(lineCount)] = worksheet["C" + str(lineCount)].value + "; " + locationCoordinates

            dateCount = 0
            for date in childObject.get('dates', []):
                dateCount = dateCount + 1
                if dateCount == 1:
                    displayCell = "J"
                    normalCell = "K"
                elif dateCount == 2:
                    displayCell = "L"
                    normalCell = "M"
                elif dateCount == 3:
                    displayCell = "N"
                    normalCell = "O"
                elif dateCount == 4:
                    displayCell = "P"
                    normalCell = "Q"
                elif dateCount == 5:
                    displayCell = "R"
                    normalCell = "S"
                elif dateCount > 5:
                    raise ValueError("ERROR more than 5 dates for " + "uri: " + childObject['uri'] + " ref_id: " + childObject['ref_id'])
                if "end" in date:
                    worksheet[normalCell + str(lineCount)] = date['begin'] + "/" + date['end']
                else:
                    worksheet[normalCell + str(lineCount)] = date['begin']
                if "expression" in date:
                    worksheet[displayCell + str(lineCount)] = date['expression']
                if "certainty" in date:
                    if worksheet[displayCell + str(lineCount)].value is None:
                        worksheet[displayCell + str(lineCount)] = date['certainty']
                    else:
                        worksheet[displayCell + str(lineCount)] = date['certainty'] + " " + worksheet[displayCell + str(lineCount)].value

            for note in childObject.get('notes', []):
                if note['type'] == "accessrestrict":
                    subCount = 0
                    for subnote in note.get('subnotes', []):
                        subCount = subCount + 1
                        if subCount < 1:
                            worksheet["T" + str(lineCount)] = worksheet["T" + str(lineCount)] + "; " +  subnote['content']
                        else:
                            worksheet["T" + str(lineCount)] = subnote['content']
                elif note['type'] == "odd":
                    subCount = 0
                    for subnote in note.get('subnotes', []):
                        subCount = subCount + 1
                        if subCount < 1:
                            worksheet["U" + str(lineCount)] = worksheet["U" + str(lineCount)] + "; " +  subnote['content']
                        else:
                            worksheet["U" + str(lineCount)] = subnote['content']
                elif note['type'] == "scopecontent":
                    subCount = 0
                    for subnote in note.get('subnotes', []):
                        subCount = subCount + 1
                        if subCount < 1:
                            worksheet["V" + str(lineCount)] = worksheet["V" + str(lineCount)] + "; " +  subnote['content']
                        else:
                            worksheet["V" + str(lineCount)] = subnote['content']

        print ("Writing spreadsheet " + simpleTitle + ".xlsx to " + paths.output_path)

        table = openpyxl.worksheet.table.Table(ref='A6:W' + str(lineCount), displayName='Inventory', tableStyleInfo=tableStyle)
        worksheet.add_table(table)

        worksheet["H1"].style = "Accent1"
        worksheet["H2"].style = "Accent1"
        worksheet["H3"].style = "Accent1"

        worksheet.column_dimensions["I"].width = 60.0
        worksheet.column_dimensions["F"].width = 15.0
        worksheet.column_dimensions["J"].width = 15.0
        worksheet.column_dimensions["K"].width = 15.0

        wb.save(filename = os.path.join(paths.output_path, simpleTitle + ".xlsx"))
        print ("Export Successful.\n\nSuccessfully exported archival object from ArchivesSpace to spreadsheet at " + paths.output_path + ".")

        if interactive:
            print ("Press any key to continue. Enter Yes(y) to open output folder.")
            openFolder = input()
            if openFolder.lower().strip() == "y" or openFolder.lower().strip() == "yes":
                openCmd = "start " + paths.output_path
                os.system(openCmd)
        return 0
    except:
        exceptMsg = traceback.format_exc()
        outputText = "asDownload error: " + exceptMsg
        print (outputText)
        errorOutput = "\n" + "#############################################################\n" + str(datetime.datetime.now()) + "\n#############################################################\n" + outputText + "\n*****************************************************************************************************************************************"
        file = open(paths.error_log_path, "a")
        file.write(errorOutput)
        file.close()

        if interactive:
            print ("Press anykey to continue...")
            input()
        return 1


def main():
    return run_download()


if __name__ == "__main__":
    raise SystemExit(main())
