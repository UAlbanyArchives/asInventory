import os
from archives_tools import dacs
import openpyxl
import sys

__location__ = (os.path.dirname(os.path.realpath(__file__)))
inputPath = os.path.join(__location__, "input")

daoFileList = []


def dateCheck(date, errorCount, lineCount, title):
	if " " in date.strip():
		try:
			print ("Line " + str(lineCount) + ", DATE ERROR, invalid space: (" + str(date) + ")  title: " + title)
		except:
			print ("Line " + str(lineCount) + ", DATE ERROR, invalid space: (" + str(date) + ")")
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

for file in os.listdir(inputPath):
	if file.endswith(".xlsx"):
		filePath = os.path.join(inputPath, file)
		
		wb = openpyxl.load_workbook(filename=filePath, read_only=True)
				
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
				print ("ERROR: incorrect sheet " + sheet.title + " in file " + file)
				
			if checkSwitch == False:
				print ("ERROR: incorrect sheet " + sheet.title + " in file " + file)
			else:
			
				#Read sheet info
				print ("Reading sheet: " + sheet.title)
				lineCount = 0
				errorCount = 0
				for row in sheet.rows:
					lineCount += 1
					if lineCount > 6:
						try:
							date = dacs.iso2DACS(str(row[10].value))
							errorCount = dateCheck(str(row[10].value), errorCount, lineCount, row[8].value)
						except:
							errorCount += 1
							try:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[10].value) + ")  title: " + str(row[8].value))
							except:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[10].value) + ")")
						try:
							date = dacs.iso2DACS(str(row[12].value))
							errorCount = dateCheck(str(row[12].value), errorCount, lineCount, row[8].value)
						except:
							errorCount += 1
							try:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[12].value) + ")  title: " + str(row[8].value))
							except:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[12].value) + ")")
						try:
							date = dacs.iso2DACS(str(row[14].value))
							errorCount = dateCheck(str(row[14].value), errorCount, lineCount, row[8].value)
						except:
							errorCount += 1
							try:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[14].value) + ")  title: " + str(row[8].value))
							except:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[14].value) + ")")
						try:
							date = dacs.iso2DACS(str(row[16].value))
							errorCount = dateCheck(str(row[16].value), errorCount, lineCount, row[8].value)
						except:
							errorCount += 1
							try:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[16].value) + ")  title: " + str(row[8].value))
							except:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[16].value) + ")")
						try:
							date = dacs.iso2DACS(str(row[18].value))
							errorCount = dateCheck(str(row[18].value), errorCount, lineCount, row[8].value)
						except:
							errorCount += 1
							try:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[18].value) + ")  title: " + str(row[8].value))
							except:
								print ("Line " + str(lineCount) + ", DATE ERROR: (" + str(row[18].value) + ")")
							
						if not row[22].value is None:
							if len(str(row[22].value).strip()) > 0:
								daoName = str(row[22].value).strip()
								if not daoName.lower().startswith("http"):
									if daoName in daoFileList:
										errorCount += 1
										print ("DAO ERROR: File listed twice (" + str(row[22].value) + ") line " + str(lineCount))
									else:
										daoFileList.append(daoName)
								
										daoPath = os.path.join(__location__, "dao", daoName)
										
										if not os.path.isfile(daoPath):
											errorCount += 1
											print ("DAO ERROR: File Not Present in dao (" + str(row[22].value) + ") line " + str(lineCount))
						
				
				print ("	" + str(errorCount) + " errors found in " + file)
				
# make sure console doesn't close
print ("Press Enter to continue...")
if sys.version_info >= (3, 0):
	input()
else:
	raw_input()	