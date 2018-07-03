import os
import sys
import wx
import datetime
import traceback
from subprocess import Popen, PIPE, STDOUT

#non-standard dependencies
import configparser
import openpyxl
from archives_tools import aspace as AS
from archives_tools import uaLocations

# GUI Dialog to get Level and ID to Export
class getCmpntDialog(wx.Dialog):

	#----------------------------------------------------------------------
	def __init__( self ):
		wx.Dialog.__init__ ( self, None, id = wx.ID_ANY, title = u"asDownload", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText4 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"What Collection, Series, or Subseries would you like to export?", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		bSizer2.Add( self.m_staticText4, 0, wx.ALL, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText3 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Level to Export:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		bSizer6.Add( self.m_staticText3, 0, wx.ALL, 5 )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_radioBtn2 = wx.RadioButton( self.m_panel1, wx.ID_ANY, u"Resource", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.m_radioBtn2, 0, wx.ALL, 5 )
		
		self.m_radioBtn3 = wx.RadioButton( self.m_panel1, wx.ID_ANY, u"Archival Object", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_radioBtn3.SetValue( True ) 
		bSizer7.Add( self.m_radioBtn3, 0, wx.ALL, 5 )
		
		bSizer6.Add( bSizer7, 1, wx.EXPAND, 5 )
		
		bSizer2.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText2 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		bSizer5.Add( self.m_staticText2, 0, wx.ALL, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl2.SetFocus()
		bSizer5.Add( self.m_textCtrl2, 1, wx.ALL, 5 )
		
		
		bSizer2.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		self.m_staticline1 = wx.StaticLine( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer2.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )
			
		bSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_button2 = wx.Button( self.m_panel1, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.Bind(wx.EVT_BUTTON, self.getCmpnt)
		bSizer8.Add( self.m_button2, 0, wx.ALL, 5 )
		
		self.m_button3 = wx.Button( self.m_panel1, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.Bind(wx.EVT_BUTTON, self.closeDialog)
		bSizer8.Add( self.m_button3, 0, wx.ALL, 5 )
		
		bSizer2.Add( bSizer8, 1, wx.EXPAND, 5 )
		
		self.m_panel1.SetSizer( bSizer2 )
		self.m_panel1.Layout()
		bSizer2.Fit( self.m_panel1 )
		bSizer1.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		bSizer1.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def closeDialog( self, event ):
		self.Destroy()
		sys.exit()

	#----------------------------------------------------------------------
	def getCmpnt(self, event):
	
		
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

			#get ID value entered in GUI
			cmpntID = self.m_textCtrl2.GetValue()
			if self.m_radioBtn2.GetValue() == True:
				level = "resource"
			else:
				level = "archivalObject"
			if len(cmpntID) < 1:
				noIDNotice = wx.MessageDialog(None, 'Please Enter a Ref ID for an Archival Objector an id_0 for a Resource.', 'Missing ID', wx.OK | wx.ICON_EXCLAMATION )
				noIDNotice.ShowModal()
			elif level == "archivalObject" and len(cmpntID) != 32:
				wrongIDNotice = wx.MessageDialog(None, 'It looks like you selcted archival object, but this is not an archival object ref_id. Check that you have the correct ID or select resource instead.', 'Incorrect ID', wx.OK | wx.ICON_EXCLAMATION)
				wrongIDNotice.ShowModal()
			else:

				#build command list
				cmd = ["cmd", "-download", outputPath, level, cmpntID, baseURL, repository, user, password]
				
				# busy dialog
				self.Hide()
				msg = "Please wait while we export the data you requested from ArchivesSpace..."
				print (msg)
				#busyDlg = wx.BusyInfo(msg)
				#busyDlg = None
				
				#Connect to ASpace
				session = AS.getSession(loginData)
				if session is None:
					raise ValueError("ERROR: ArchivesSpace login failed. Please check settings in local_settings.cfg")
					
				#create Workbook object
				wb = openpyxl.Workbook()
				
				if level.lower().strip() == "resource":
					resourceLevel = True
					print ("Looking for resource")
				else:
					resourceLevel = False
					print ("Looking for  archival object")
				
				if resourceLevel == True:
					object = AS.getResourceID(session, repository, cmpntID, loginData)		
					displayTitle = object.title.replace("/", "-")
				else:	
					object = AS.getArchObjID(session, repository, cmpntID, loginData)
					displayTitle = object.display_string
					
				simpleTitle = object.title.replace("/", "-")
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
				print ("Export Complete!")
			

				successNotice = wx.MessageDialog(None, "Export Successful.\n\nSuccessfully exported archival object from ArchivesSpace to spreadsheet at " + outputPath + ".\n\nWould you like to open the ouput folder?" , 'Export Successful', wx.YES_NO | wx.ICON_INFORMATION)
				successResponse = successNotice.ShowModal()
				if successResponse == wx.ID_YES:
					openCmd = "start " + outputPath
					openDir = Popen(openCmd, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = openDir.communicate()
					print stdout
					print stderr
				self.Destroy()
		except:
			exceptMsg = traceback.format_exc()
			outputText = "asDownload error: " + exceptMsg
			errorOutput = "\n" + "#############################################################\n" + str(datetime.datetime.now()) + "\n#############################################################\n" + outputText + "\n*****************************************************************************************************************************************"
			file = open(os.path.join(__location__, "error.log"), "a")
			file.write(errorOutput)
			file.close()
			errorNotice = wx.MessageDialog(None, "Error exporting archival object from ArchivesSpace. Please check error.log for more details. " + exceptMsg, 'Export Error', wx.OK | wx.ICON_ERROR )
			errorNotice.ShowModal()
			
			self.Destroy()

# Initialize wx App
app = wx.App()
frame = getCmpntDialog().ShowModal()
app.MainLoop()

