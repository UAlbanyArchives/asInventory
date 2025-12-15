# asInventory
Manage file-level ArchivesSpace inventories with spreadsheets

Version 2.0 now uses [archivessnake](https://github.com/archivesspace-labs/ArchivesSnake)

### Warning note

This tool has been tested with ArchivesSpace 2.x and 3.x. It makes iterative changes through the API. You should always do significant testing on a development instance of ASpace before using it on production data to make sure it acts as you expect.

## Installation

### Install from GitHub (Recommended)

```bash
pip install git+https://github.com/UAlbanyArchives/asInventory.git
```

### Install from local directory

```bash
git clone https://github.com/UAlbanyArchives/asInventory
cd asInventory
pip install .
```

### Development mode (for contributors)

```bash
pip install -e .
```

## Configuration

### ArchivesSnake Configuration

If you don't already have ArchivesSnake configured, create a `~/.archivessnake.yml` with your ArchivesSpace credentials:

```yaml
baseurl: https://your-aspace-instance.edu/api
username: your_username
password: your_password
```

### Repository Configuration (Optional)

Create `~/asinventory.yml` to specify your repository ID:

```yaml
repository: 2
```

If this file doesn't exist, the default repository ID of "2" will be used.

## Required Directories

asInventory requires these directories (will be created automatically when scripts run):
```
input
output
complete
dao
```

## Running the Scripts

After installation, run scripts as console commands or directly with Python:

```bash
# As console commands (if Python Scripts directory is in PATH)
asdownload
asupload
asvalidate

# Or run directly with Python
python asDownload.py
python asUpload.py
python validate.py
```

### Exporting an inventory

1. Run `asdownload` (or `python asDownload.py`)
2. Select the level to export:
	* Select "Resource" (r) to export a folder list from a collection that has no series
	* Select "Archival Object" (ao) to export a folder list from a series, subseries, or other component
3. Enter the ID for the parent of the folder list you want to export:
	* For Resource, use id_0
	![](screenshots/screenshot2.png)
	* For other components use Ref ID
	![](screenshots/screenshot3.png)
4. Click "OK" and a list of files exported will print to the console. This may take some time for large file listings.
5. If the export is successful, you will be given the option to open the output directory to view the exported file
6. A new Spreadsheet file will be placed in the `output` directory. **WARNING: files with the same name in this directory will be overwritten.**

#### To import an inventory

1. Make a copy of asInventory.xlsx, you can name it anything you'd like.
2. Open the spreadsheet and add a folder listing:
	* **Mandatory fields:**
		* Level (I2) must be "resource" for collection level with no series, or "archival object"
		* RefID (I3) must be id_0 for resource parent or ref_id for archival object parent
	* Title (I1) is not mandatory and can be anything, sheet name can also be anything
	* Many columns can be left blank
	* If an ID (column A) is entered, asInventory will find and update an existing record
	* If no ID is entered, asInventory will create a new archival object child
	* If URIs for locations or containers are entered, asInventory will link these records; otherwise, new containers and locations will be created if a label and indicator are listed
	* Accepts up to 5 dates using ISO format (e.g., "1977/1988" or "1903-03-17/1917-01-15")
	* Display dates are optional and are entered in the ASpace Expression field
	* Can make Access Restriction (column T), General Note (column U), and Scope (column V) notes.
	* Can create and link digital objects. This can be a link entered in column W, or the filename of a file placed in the `dao` directory. If dao paths are set up correctly in `local_settings.cfg` asInventory will also rename files to their newly created ASpace IDs and move them to a webserver.
	* ![](screenshots/screenshot5.png)
3. Save the spreadsheet to the `input` directory
4. Run `asupload` (or `python asUpload.py`)
5. The spreadsheet file will be moved into the `complete` directory after the upload is completed. **WARNING: files with the same name in this directory will be overwritten.**

## Dependencies

Requires Python 3.7+

Dependencies are automatically installed with pip:
* [openpyxl](https://openpyxl.readthedocs.io/) (2.6.4)
* [archivessnake](https://github.com/archivesspace-labs/ArchivesSnake)
* [pyyaml](https://pyyaml.org/)

## Additional Tools

### Validation

`asvalidate` (or `python validate.py`) will validate all dates entered in all spreadsheets in the `input` folder. This helps ensure they're compatible with ArchivesSpace to reduce errors during upload.

### Creating digital objects

Digital objects can be created by entering URLs in column W of the upload spreadsheet. The tool will create ArchivesSpace digital object records and link them to the appropriate archival objects.

## Building Executables (Optional)

Executables can be built with PyInstaller:

```bash
pyinstaller --onefile asUpload.py
pyinstaller --onefile asDownload.py
pyinstaller --onefile validate.py
```

## Contributing

Comments and pull requests welcome.

## Authors

Greg Wiedeman

## License

This project is in the public domain
