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


def get_object_by_record_id(client, repository, record_id):
    # Non-interactive lookup: a 32-char ID is an archival object ref_id, otherwise a resource id_0.
    resourceLevel = len(record_id) != 32
    try:
        if resourceLevel:
            aq = json.dumps({"query": {"field": "identifier", "value": record_id, "jsonmodel_type": "field_query"}})
            search_results = client.get('repositories/{}/search'.format(repository), params={'page': '1', 'aq': aq}).json()
            object = client.get(search_results['results'][0]['uri']).json() if search_results.get('total_hits', 0) > 0 else None
        else:
            ao_result = client.get('repositories/{}/find_by_id/archival_objects'.format(repository), params={'ref_id[]': record_id}).json()
            object = client.get(ao_result['archival_objects'][0]['ref']).json() if ao_result.get('archival_objects') else None
    except:
        object = None

    if object is None:
        raise ValueError(f"Could not find {'resource' if resourceLevel else 'archival object'} with ID: {record_id}")

    if resourceLevel:
        displayTitle = object['title'].replace("/", "-")
    else:
        displayTitle = object.get('display_string', object.get('title', ''))

    return object, displayTitle, resourceLevel


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


def run_download(base_dir=None, input_path=None, output_path=None, complete_path=None, dao_path=None, interactive=True, record_id=None):
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
        if record_id:
            object, displayTitle, resourceLevel = get_object_by_record_id(client, repository, record_id)
        elif interactive:
            object, displayTitle, resourceLevel = getInput(None, "", False, client, repository)
        else:
            raise ValueError("record_id is required when interactive is False.")
        wb = openpyxl.Workbook()

        simpleTitle = safe_filename(object['title'].replace("/", "-"))
        print ("Reading " + simpleTitle)

        if resourceLevel == True:
            objectID = object['id_0']
        else:
            objectID = object['ref_id']

        worksheet = wb.active
        worksheet["A1"] = "ID"
        worksheet["B1"] = "Location ID"
        worksheet["C1"] = "Location"
        worksheet["D1"] = "Container URI"
        worksheet["E1"] = "Container"
        worksheet["F1"] = "C#"
        worksheet["G1"] = "Folder"
        worksheet["H1"] = "F#"
        worksheet["I1"] = "Title"
        worksheet["J1"] = "Date 1 Display"
        worksheet["K1"] = "Date 1 Normal"
        worksheet["L1"] = "Date 2 Display"
        worksheet["M1"] = "Date 2 Normal"
        worksheet["N1"] = "Date 3 Display"
        worksheet["O1"] = "Date 3 Normal"
        worksheet["P1"] = "Date 4 Display"
        worksheet["Q1"] = "Date 4 Normal"
        worksheet["R1"] = "Date 5 Display"
        worksheet["S1"] = "Date 5 Normal"
        worksheet["T1"] = "Restrictions"
        worksheet["U1"] = "General Note"
        worksheet["V1"] = "Scope"
        worksheet["W1"] = "DAO Filename"

        tableStyle = openpyxl.worksheet.table.TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)

        if resourceLevel == True:
            childrenList = get_children_waypoint(client, object['uri'])
        else:
            resource_uri = object['resource']['ref']
            childrenList = get_children_waypoint(client, resource_uri, object['uri'])

        lineCount = 1
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

        print ("Writing spreadsheet " + objectID + ".xlsx to " + paths.output_path)

        table = openpyxl.worksheet.table.Table(ref='A1:W' + str(lineCount), displayName='Inventory', tableStyleInfo=tableStyle)
        worksheet.add_table(table)

        worksheet.column_dimensions["I"].width = 60.0
        worksheet.column_dimensions["F"].width = 15.0
        worksheet.column_dimensions["J"].width = 15.0
        worksheet.column_dimensions["K"].width = 15.0

        wb.save(filename = os.path.join(paths.output_path, safe_filename(objectID) + ".xlsx"))
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
    record_id = sys.argv[1] if len(sys.argv) > 1 else None
    return run_download(record_id=record_id, interactive=(record_id is None))


if __name__ == "__main__":
    raise SystemExit(main())
