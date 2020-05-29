import aspace as AS

session = AS.getSession()

repo = "2"

"""
accession = AS.makeAccession()
accession.accession_date = "2002-01-01"
accession.id_0 = "2002.001"
accession.title = "Michelle Crone Papers"
accession.disposition = "Donor Name: Person"
accession.provenance = "The collection includes material documenting the National March on Washington, Women's Encampment, Elword Productions, Gay Games, Full Circle Festival: Equinox '89, Lesbian & Gay Film & Video Festival, Rhythm Fest, and other events and groups."
accession.condition_description = "oversize posters in  need of preservation treatment are @ L-12-7"

accession.related_resources.append({"ref": "/repositories/2/resources/1513"})

accession = AS.makeExtent(accession, "21", "cubic ft.")

accession = AS.makeDate(accession, "1974-01-04", "1994-08-30")

AS.postAccession(session, repo, accession)
"""

accessions = AS.getAccessions(session, repo,  "all")
AS.pp(accessions)

#collection = AS.getResourceID(session, repo, "nam_apap335")
#print collection.keys()

#archObj = AS.getArchObjID(session, repo)
#AS.pp(archObj)

"""
for note in collection.notes:
	if note.type == "accessrestrict":
		note.publish = True
		for subnote in note.subnotes:
			subnote.publish = True
			print ":)"
"""
"""
for collection in AS.getResources(session, repo, "all"):
	if collection.ead_id.endswith("apap313"):
		print "found " + collection.title
		print collection.uri
"""


"""
for collection in AS.getResources(session, repo, "all"):
	if collection.ead_id.endswith("apap139"):
		print "found " + collection.title
		tree = AS.getTree(session, collection)
		for child in tree.children:
			print "	" + child.title
			for file in child.children:
				if "Cement" in file.title:
					print file.title
					print file.record_uri
					
					object = AS.getArchObj(session, file.record_uri)
					print object.title
					for date in object.dates:
						print date.expression
"""