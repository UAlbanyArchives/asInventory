import os
import ConfigParser
from subprocess import Popen, PIPE, STDOUT
import wx

__location__ = os.path.dirname(os.path.abspath(__file__))

# get local_settings
configPath = os.path.join(__location__, "local_settings.cfg")
config = ConfigParser.ConfigParser()
config.read(configPath)

baseURL = config.get('ArchivesSpace', 'baseURL')
repository = config.get('ArchivesSpace', 'repository')
user = config.get('ArchivesSpace', 'user')
password = config.get('ArchivesSpace', 'password')

masterPath = config.get('asInventory', 'path')

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
cmd = [masterPath, "-upload", spreadsheetPath, daoPath, baseURL, repository, user, password]

# call master asInventory
asUpload = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
output = ""
for line in iter(asUpload.stdout.readline, ""):
	print (line)
	output += line
	
asUpload.wait()
exitCode = asUpload.returncode
if exitCode == 0:
	successNotice = wx.MessageDialog(None, "Successfully uploaded to ArchivesSpace..", 'Upload Success', wx.OK | wx.ICON_INFORMATION )
	successNotice.ShowModal()
else:
	errorNotice = wx.MessageDialog(None, "Error uploading to ArchivesSpace. Please check error.log for more details.", 'Upload Error', wx.OK | wx.ICON_ERROR )
	errorNotice.ShowModal()