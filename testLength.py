import os
import configparser
import openpyxl
from archives_tools import aspace as AS

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

inputPath = os.path.join(__location__, "input")

print ("Reading input directory...")
spreadsheetCount = 0
for spreadFile in os.listdir(inputPath):
	
	#find and load sheets
	if spreadFile.endswith(".xlsx"):
		spreadsheetCount += 1
		spreadsheet = os.path.join(inputPath, spreadFile)
		print ("Reading " + spreadFile)
		wb = openpyxl.load_workbook(filename=spreadsheet, read_only=True)
		
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
					resourceTree = AS.getTree(session, object, loginData)
					childrenList = resourceTree.children
				else:
					resourceLevel = False
					print ("Looking for archival object matching " + str(displayName) + "...")
					object = AS.getArchObjID(session, repository, refID, loginData)
					childTree = AS.getChildren(session, object, loginData)
					childrenList = childTree.children
					
				recordCount = 0
				for child in childrenList:
					recordCount += 1
					
				sheetCount = 0
				rowCount = 0
				for row in sheet.rows:
					rowCount = rowCount + 1
					if rowCount > 6:
						sheetCount = rowCount - 6
						
				print ("	RecordCount = " + str(recordCount))
				print ("	SpreadsheetCount = " + str(sheetCount))
						
						
				