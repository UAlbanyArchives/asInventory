import os
import ConfigParser
from subprocess import Popen, PIPE

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
daoPath = os.path.join(__location__, "dao")
if not os.path.isdir(daoPath):
	os.mkdir(daoPath)

#build command list
cmd = [masterPath, "-upload", spreadsheetPath, daoPath, baseURL, repository, user, password]

# call master asInventory
asUpload = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = asUpload.communicate()
if len(stdout) > 0:
	print (stdout)
if len(stderr) > 0:
	print (stderr)