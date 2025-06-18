import os
import re
import sys
import datetime
import traceback
from subprocess import Popen, PIPE, STDOUT

#non-standard dependencies
import configparser
import openpyxl
from archives_tools import aspace as AS
from archives_tools import uaLocations

def safe_filename(s):
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', s).strip().rstrip('.')

def getInput(object, displayTitle, resourceLevel, session):
	
	#get ID value
	print ("Export Resource(r) or archival object(ao):")
	if sys.version_info >= (3, 0):
		level = input()
	else:
		level = raw_input()
	
	#get ID value
	print ("Enter ID:")
	if sys.version_info >= (3, 0):
		cmpntID = input()
	else:
		cmpntID = raw_input()
	
	#basic error handling:
	if len(cmpntID) < 1:
		print ("Missing ID. Please Enter a Ref ID for an Archival Object or an id_0 for a Resource.")
		object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, session)
	else:
		if level.lower().strip() == "resource" or level.lower().strip() == "r":
			print ("Looking for Resource...")
			object = AS.getResourceID(session, repository, cmpntID, loginData)		
			if object is None:
				print ("Try Again\n\n")
				object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, session)
			else:
				resourceLevel = True
				displayTitle = object.title.replace("/", "-")
		else:
			if len(cmpntID) != 32:
				print ("It looks like you selcted archival object, but this is not an archival object ref_id. Check that you have the correct ID or select resource instead.\n\n")
				object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, session)
			else:
				print ("Looking for Archival Object...")
				object = AS.getArchObjID(session, repository, cmpntID, loginData)
				if object is None:
					print ("Try Again\n\n")
					object, displayTitle, resourceLevel = getInput(object, displayTitle, resourceLevel, session)
				else:
					resourceLevel = False
					displayTitle = object.display_string
			
	return object, displayTitle, resourceLevel

# Main error handling
try:
	if getattr(sys, 'frozen', False):
		# Running as a PyInstaller bundle
		__location__ = os.path.dirname(sys.executable)
	else:
		# Running as a normal Python script
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
		
	#Connect to ASpace
	session = AS.getSession(loginData)
	if session is None:
		raise ValueError("ERROR: ArchivesSpace login failed. Please check settings in local_settings.cfg")
		
	# get user input and the object
	object, displayTitle, resourceLevel = getInput(None, "", False, session)
		
	#create Workbook object
	wb = openpyxl.Workbook()
		
	simpleTitle = safe_filename(object.title.replace("/", "-"))
	print ("Reading " + simpleTitle)
	
	
	if resourceLevel == True:
		objectID = object.id_0
	else:
		objectID = object.ref_id
	
	#make a sheet
	worksheet = wb.active
	#worksheet = wb.create_sheet(title=simpleTitle)
	worksheet["H1"] = "Title"
	worksheet["I1"] = displayTitle
	worksheet["H2"] = "Level"
	if resourceLevel == True:
		worksheet["I2"] = "resource"
	else:
		worksheet["I2"] = "archival object"
	worksheet["H3"] = "Ref ID"
	worksheet["I3"] = objectID
	
	#setup table headings
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
	
	#get table styles
	tableStyle = openpyxl.worksheet.table.TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)
	
	if resourceLevel == True:
		resourceTree = AS.getTree(session, object, loginData)
		childrenList = resourceTree.children
	else:
		childTree = AS.getChildren(session, object, loginData)
		childrenList = childTree.children
		
	lineCount = 6
	for child in childrenList:
		childObject = AS.getArchObj(session, child.record_uri, loginData)
		lineCount = lineCount + 1
		worksheet["A" + str(lineCount)] = childObject.ref_id
		worksheet["I" + str(lineCount)] = childObject.title
		try:
			print ("	exporting " + childObject.title)
		except:
			print ("	exporting non-ascii file...")
		
		# containers and locations		 
		if len(childObject.instances) > 0:
			if "sub_container" in childObject.instances[0].keys():
				container = childObject.instances[0].sub_container
				containerURI = container.top_container.ref
				worksheet["D" + str(lineCount)] = containerURI
				if "type_2" in container.keys():
					worksheet["G" + str(lineCount)] = container.type_2
				if "indicator_2" in container.keys():
					worksheet["H" + str(lineCount)] = container.indicator_2
					
				containerObject = AS.getContainer(session, containerURI, loginData)
				worksheet["E" + str(lineCount)] = containerObject.type
				worksheet["F" + str(lineCount)] = containerObject.indicator
				
				locationCount = 0
				for location in containerObject.container_locations:
					locationCount = locationCount + 1
					locationObject = AS.getLocation(session, location.ref, loginData)
					if "area" in locationObject.keys():
						locationCoordinates = locationObject.area + "-" + locationObject.coordinate_1_indicator
					else:
						locationCoordinates = locationObject.room + "-" + locationObject.coordinate_1_indicator
					if "coordinate_2_indicator" in locationObject.keys():
						locationCoordinates = locationCoordinates + "-" + locationObject.coordinate_2_indicator
					if "coordinate_3_indicator" in locationObject.keys():
						locationCoordinates = locationCoordinates + "-" + locationObject.coordinate_3_indicator
					if locationCount < 2:
						worksheet["B" + str(lineCount)] = locationObject.uri
						worksheet["C" + str(lineCount)] = locationCoordinates
					else:
						worksheet["B" + str(lineCount)] = worksheet["B" + str(lineCount)].value + "; " + locationObject.uri
						worksheet["C" + str(lineCount)] = worksheet["C" + str(lineCount)].value + "; " + locationCoordinates					
				
		
		#dates
		dateCount = 0
		for date in childObject.dates:
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
				raise ValueError("ERROR more than 5 dates for " + "uri: " + childObject.uri + " ref_id: " + childObject.ref_id)
			if "end" in date.keys():
				worksheet[normalCell + str(lineCount)] = date.begin + "/" + date.end
			else:
				worksheet[normalCell + str(lineCount)] = date.begin
			if "expression" in date.keys():
				worksheet[displayCell + str(lineCount)] = date.expression
			if "certainty" in date.keys():
				if worksheet[displayCell + str(lineCount)].value is None:
					worksheet[displayCell + str(lineCount)] = date.certainty
				else:
					worksheet[displayCell + str(lineCount)] = date.certainty + " " + worksheet[displayCell + str(lineCount)].value
		
		for note in childObject.notes:
			if note.type == "accessrestrict":
				subCount = 0
				for subnote in note.subnotes:
					subCount = subCount + 1
					if subCount < 1:
						worksheet["T" + str(lineCount)] = worksheet["T" + str(lineCount)] + "; " +  subnote.content
					else:
						worksheet["T" + str(lineCount)] = subnote.content
			elif note.type == "odd":
				subCount = 0
				for subnote in note.subnotes:
					subCount = subCount + 1
					if subCount < 1:
						worksheet["U" + str(lineCount)] = worksheet["U" + str(lineCount)] + "; " +  subnote.content
					else:
						worksheet["U" + str(lineCount)] = subnote.content
			elif note.type == "scopecontent":
				subCount = 0
				for subnote in note.subnotes:
					subCount = subCount + 1
					if subCount < 1:
						worksheet["V" + str(lineCount)] = worksheet["V" + str(lineCount)] + "; " +  subnote.content
					else:
						worksheet["V" + str(lineCount)] = subnote.content
		
	print ("Writing spreadsheet " + simpleTitle + ".xlsx to " + outputPath)
	
	table = openpyxl.worksheet.table.Table(ref='A6:W' + str(lineCount), displayName='Inventory', tableStyleInfo=tableStyle)
	worksheet.add_table(table)
	
	#styles for sheet info on top
	worksheet["H1"].style = "Accent1"
	worksheet["H2"].style = "Accent1"
	worksheet["H3"].style = "Accent1"
	
	#set column widths
	worksheet.column_dimensions["I"].width = 60.0
	worksheet.column_dimensions["F"].width = 15.0
	worksheet.column_dimensions["J"].width = 15.0
	worksheet.column_dimensions["K"].width = 15.0
	
	
	wb.save(filename = os.path.join(outputPath, simpleTitle + ".xlsx"))
	print ("Export Successful.\n\nSuccessfully exported archival object from ArchivesSpace to spreadsheet at " + outputPath + ".")
	#print ("Export Complete!")
	
	# make sure console doesn't close
	print ("Press any key to continue. Enter Yes(y) to open output folder.")
	if sys.version_info >= (3, 0):
		openFolder = input()
	else:
		openFolder = raw_input()

	if openFolder.lower().strip() == "y" or openFolder.lower().strip() == "yes":
		openCmd = "start " + outputPath
		os.system(openCmd)
		
except:
	exceptMsg = traceback.format_exc()
	outputText = "asDownload error: " + exceptMsg
	print (outputText)
	errorOutput = "\n" + "#############################################################\n" + str(datetime.datetime.now()) + "\n#############################################################\n" + outputText + "\n*****************************************************************************************************************************************"
	file = open(os.path.join(__location__, "error.log"), "a")
	file.write(errorOutput)
	file.close()

	# make sure console doesn't close
	print ("Press anykey to continue...")
	if sys.version_info >= (3, 0):
		input()
	else:
		raw_input()
