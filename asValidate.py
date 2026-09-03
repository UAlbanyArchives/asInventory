import os
import sys

import openpyxl

import aspace_helpers as helpers
from asinventory_runtime import build_runtime_paths, ensure_runtime_directories, resolve_interactive


daoFileList = []

container_names = [
    "box",
    "carton",
    "case",
    "folder",
    "frame",
    "object",
    "reel",
    "Box",
    "Folder",
    "Reel",
    "Inventory",
    "Item",
    "Web-Archive",
    "WARC",
    "Oversized",
    "Artifact-box",
    "Flat-File",
    "Cassette",
    "CD",
    "Video-Tape",
    "Oversize",
    "VHS",
    "Film",
    "Map-Tube",
    "Umatic",
    "Roll",
    "3.5in-Floppy",
    "Phonograph-Record",
    "DVD",
    "Microfilm",
    "Oversized_Folder",
    "MPEG",
    "AVI",
    "PPT",
    "Floppy-Disk",
    "USB",
    "Zip-Disk",
    "Mini-DV",
    "5.25in-Floppy",
    "Microcassette",
    "Drawer",
    "Record",
    "CD-R",
    "MagneticTape",
    "Card-File",
    "item",
    "Call-Number",
    "PDF",
    "Volume",
    "Issue",
    "File",
    "Tray",
    "Compartment",
    "Collection",
    "1-inch Type C",
    "Digital Audio Tape",
    "DVCPro",
    "LP",
    "Beta",
    "Map-File",
    "FlatFile",
    "DVCAM",
    "Minicartridge",
    "VHS-C",
    "Page",
    "A/V Box",
]

def dateCheck(date, errorCount, lineCount, title):
    if " " in date.strip():
        try:
            print ("Line " + str(lineCount) + ", DATE ERROR, invalid space: (" + str(date) + ")  title: " + title)
        except:
            print ("Line " + str(lineCount) + ", DATE ERROR, invalid space: (" + str(date) + ")")
        errorCount += 1
    acceptList = ["/", "-", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    if date != "None":
        for character in str(date).strip():
            if not character in acceptList:
                print (character)
                try:
                    print ("Line " + str(lineCount) + ", DATE ERROR, invalid character: (" + str(date) + ")  title: " + title)
                except:
                    print ("Line " + str(lineCount) + ", DATE ERROR, invalid character: (" + str(date) + ")")
                errorCount += 1
    if "/" in date:
        start, end = date.split("/")
        if start > end:
            try:
                print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(date) + ")  title: " + title)
            except:
                print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(date) + ")")
            errorCount += 1
    if "undated" in date.lower():
        try:
            print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(date) + ")  title: " + title)
        except:
            print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(date) + ")")
        errorCount += 1
    return errorCount


def run_validate(base_dir=None, input_path=None, output_path=None, complete_path=None, dao_path=None, interactive=True):
    interactive = resolve_interactive(interactive)
    paths = build_runtime_paths(base_dir, input_path, output_path, complete_path, dao_path)
    ensure_runtime_directories(paths)
    daoFileList.clear()
    totalErrorCount = 0

    for file in os.listdir(paths.input_path):
        if file.endswith(".xlsx"):
            filePath = os.path.join(paths.input_path, file)
            refID = os.path.splitext(file)[0].strip()
            wb = openpyxl.load_workbook(filename=filePath, read_only=True)

            for sheet in wb.worksheets:
                checkSwitch = True
                try:
                    if sheet["A1"].value.lower().strip() != "id":
                        checkSwitch = False
                    elif sheet["I1"].value.lower().strip() != "title":
                        checkSwitch = False
                    elif sheet["J1"].value.lower().strip() != "date 1 display":
                        checkSwitch = False
                    elif sheet["D1"].value.lower().strip() != "container uri":
                        checkSwitch = False
                except:
                    print ("ERROR: incorrect sheet " + sheet.title + " in file " + file)
                    totalErrorCount += 1

                if len(refID) < 1:
                    print (f"ERROR: incorrect filename {file} - missing or invalid ID")
                    totalErrorCount += 1

                if checkSwitch == False:
                    print ("ERROR: incorrect sheet " + sheet.title + " in file " + file)
                    totalErrorCount += 1
                else:
                    print ("Reading sheet: " + sheet.title)
                    lineCount = 0
                    errorCount = 0
                    for row in sheet.rows:
                        lineCount += 1
                        if lineCount > 1:
                            # Container name check
                            for index in [4, 6]:
                                if row[index].value and len(row[index].value.strip()) > 0:
                                    if row[index].value.strip() not in container_names:
                                        errorCount += 1
                                        try:
                                            print ("Line " + str(lineCount) + ", CONTAINER ERROR: (" + str(row[index].value) + ")  title: " + str(row[8].value))
                                        except:
                                            print ("Line " + str(lineCount) + ", CONTAINER ERROR: (" + str(row[index].value) + ")")

                            # Date check
                            for index in [10, 12, 14, 16, 18]:
                                try:
                                    helpers.iso2DACS(str(row[index].value))
                                    errorCount = dateCheck(str(row[index].value), errorCount, lineCount, row[8].value)
                                except:
                                    errorCount += 1
                                    try:
                                        print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[index].value) + ")  title: " + str(row[8].value))
                                    except:
                                        print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[index].value) + ")")

                            if not row[22].value is None:
                                if len(str(row[22].value).strip()) > 0:
                                    daoName = str(row[22].value).strip()
                                    if not daoName.lower().startswith("http"):
                                        if daoName in daoFileList:
                                            errorCount += 1
                                            print ("DAO ERROR: File listed twice (" + str(row[22].value) + ") line " + str(lineCount))
                                        else:
                                            daoFileList.append(daoName)

                    print ("\t" + str(errorCount) + " errors found in " + file)
                    totalErrorCount += errorCount
            wb._archive.close()

    if interactive:
        print ("Press Enter to continue...")
        if sys.version_info >= (3, 0):
            input()
        else:
            raw_input()
    return totalErrorCount


def main():
    return run_validate()


if __name__ == "__main__":
    raise SystemExit(main())
