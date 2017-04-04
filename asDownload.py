import os
import sys
import ConfigParser
from subprocess import Popen, PIPE, STDOUT
import wx
import datetime
import shutil

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
	
		__location__ = os.path.dirname(os.path.abspath(__file__))

		# get local_settings
		configPath = os.path.join(__location__, "local_settings.cfg")
		config = ConfigParser.ConfigParser()
		config.read(configPath)

		baseURL = config.get('ArchivesSpace', 'baseURL')
		repository = config.get('ArchivesSpace', 'repository')
		user = config.get('ArchivesSpace', 'user')
		password = config.get('ArchivesSpace', 'password')
		
		#check if asInventory is updated
		masterPath = config.get('asInventory', 'path')
		masterFile = ""
		for file in os.listdir(masterPath):
			if file.startswith("asInventory") and file.endswith(".exe"):
				masterFile = file
		if len(masterFile) == 0:
			errorNotice = wx.MessageDialog(None, "Error: Could not find master asInventory file in " + masterPath, 'No Master File', wx.OK | wx.ICON_ERROR )
			errorNotice.ShowModal()
		masterVersion = os.path.splitext(masterFile)[0].split("-")[1]
		localFile = ""
		for file in os.listdir(__location__):
			if file.startswith("asInventory") and file.endswith(".exe"):
				localFile = file
		localVersion = os.path.splitext(localFile)[0].split("-")[1]
		if masterVersion > localVersion:
			print "Updating asInventory"
			os.remove(os.path.join(__location__, localFile))
			shutil.copy2(os.path.join(masterPath, masterFile), __location__)
			asInventory = os.path.join(__location__, masterFile)
		else:
			asInventory = os.path.join(__location__, localFile)

		# output path
		outputPath = os.path.join(__location__, "output")
		if not os.path.isdir(outputPath):
			os.mkdir(outputPath)


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
			cmd = [asInventory, "-download", outputPath, level, cmpntID, baseURL, repository, user, password]
			# call master asInventory
			#print cmd
			asDownload = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
			
			# busy dialog
			self.Hide()
			msg = "Please wait while we export the data you requested from ArchivesSpace..."
			print (msg)
			#busyDlg = wx.BusyInfo(msg)
			
			asDownload.wait()
			output = ""
			for line in iter(asDownload.stdout.readline, ""):
				print (line)
				output += line
			exitCode = asDownload.returncode
			#busyDlg = None
			if exitCode == 0:
				successNotice = wx.MessageDialog(None, "Export Successful.\n\nSuccessfully exported archival object from ArchivesSpace to spreadsheet at " + masterPath + ".\n\nWould you like to open the ouput folder?" , 'Export Successful', wx.YES_NO | wx.ICON_INFORMATION)
				successResponse = successNotice.ShowModal()
				if successResponse == wx.ID_YES:
					openCmd = "start " + outputPath
					openDir = Popen(openCmd, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = openDir.communicate()
					print stdout
					print stderr
			else:
				outputText = "asDownload error: " + output
				errorOutput = "\n" + "#############################################################\n" + str(datetime.datetime.now()) + "\n#############################################################\n" + outputText + "\n********************************************************************************"
				file = open(os.path.join(__location__, "error.log"), "a")
				file.write(errorOutput)
				file.close()
				errorNotice = wx.MessageDialog(None, "Error exporting archival object from ArchivesSpace. Please check error.log for more details. " + output, 'Export Error', wx.OK | wx.ICON_ERROR )
				errorNotice.ShowModal()
				
			self.Destroy()

# Initialize wx App
app = wx.App()
frame = getCmpntDialog().ShowModal()
app.MainLoop()

