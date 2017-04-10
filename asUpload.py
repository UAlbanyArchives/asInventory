import os
import ConfigParser
from subprocess import Popen, PIPE, STDOUT
import wx
import datetime
import shutil

app = wx.App(False)
app.MainLoop()

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


# input paths
spreadsheetPath = os.path.join(__location__, "input")
if not os.path.isdir(spreadsheetPath):
	os.mkdir(spreadsheetPath)
completePath = os.path.join(__location__, "complete")
if not os.path.isdir(completePath):
	os.mkdir(completePath)
daoPath = os.path.join(__location__, "dao")
if not os.path.isdir(daoPath):
	os.mkdir(daoPath)

#build command list
print ("Calling asInventory master file...")
cmd = [asInventory, "-upload", spreadsheetPath, daoPath, baseURL, repository, user, password]

# call master asInventory
asUpload = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
output = ""
for line in iter(asUpload.stdout.readline, ""):
	print (line)
	output += line
asUpload.wait()
	
exitCode = asUpload.returncode
if exitCode == 0:
	successNotice = wx.MessageDialog(None, "Successfully uploaded to ArchivesSpace.", 'Upload Success', wx.OK | wx.ICON_INFORMATION )
	successNotice.ShowModal()
else:
	outputText = "asUpload error: " + output
	errorOutput = "\n" + "#############################################################\n" + str(datetime.datetime.now()) + "\n#############################################################\n" + outputText + "\n********************************************************************************"
	file = open(os.path.join(__location__, "error.log"), "a")
	file.write(errorOutput)
	file.close()
	errorNotice = wx.MessageDialog(None, "Error uploading to ArchivesSpace. Please check error.log for more details. " + output, 'Upload Error', wx.OK | wx.ICON_ERROR )
	errorNotice.ShowModal()