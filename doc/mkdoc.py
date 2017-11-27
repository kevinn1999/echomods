#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------
# (c) kelu124
# cc-by-sa/4.0/
# -------------------------
# Requires GraphViz and Wand
# -------------------------

'''Description: script to build autodocumentation. module for autodocumentation generation.'''

__author__      = "kelu124"
__copyright__   = "Copyright 2016, Kelu124"
__license__ 	= "cc-by-sa/4.0/"

import chardet   
import os
import os.path, time
from glob import glob
import markdown
import re
import pyexiv2
import graphviz as gv
import functools
# Wand for SVG to PNG Conversion
from wand.api import library
import wand.color
import wand.image
import Image
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
import urllib2
from datetime import datetime




# -------------------------
# Get icons for compiler log
# -------------------------

tagAuto = "[](@autogenerated - invisible comment)"
tagDesc = "[](@description"
log = []
GreenMark = ":white_check_mark:"
RedMark = ":no_entry:"
WarningMark = ":warning:"
ValidH = ["h1","h2","h3","h4","h5"]

ModulesChaptDeux = ["tobo","retroATL3","goblin","elmo","alt.tbo"]
ModulesChaptDeuxRT = ["mogaba","toadkiller"]
ModulesChaptTrois = ["silent","cletus","croaker","doj","tomtom","loftus","wirephantom"]
ModulesChaptTroisRT= ["sleepy","oneeye"]

ModulesList = ModulesChaptDeux+ModulesChaptTrois
ModulesRetiredList = ModulesChaptDeuxRT+ModulesChaptTroisRT

ListOfMurgenSessions = ["Session_1.md","Session_2.md","Session_3.md","Session_4.md","Session_4b.md","Session_5.md","Session_6.md","Session_7.md","Session_8.md","Session_9_ATL.md",]

ToBeReplaced = ["/include/NDT.md"]
Replaced = ["/Chapter1/ndt.md"]

ExcludeDirs = ["include","tools",".git","gh-pages","doc","gitbook","bomanz","hannin"]
ExcludeDirsRetired = ExcludeDirs+["retired"]


# -------------------------
# Graph customised
# -------------------------

styles = {
    'graph': {
        'label': 'my mind',
	'layout':"neato",
	'fontsize':"26",
	'outputorder':'edgesfirst',
	#"overlap":"false",
        'rankdir': 'BT',
    }
}


# -------------------------
# Aide pour le graphe
# -------------------------

graph = functools.partial(gv.Graph, format='svg')
digraph = functools.partial(gv.Digraph, format='svg')

def Svg2Png(svgfile):
	output_filename = svgfile+'.png'
	input_filename = svgfile+'.svg'

	svg_file = open(input_filename,"r")

	with wand.image.Image() as image:
	    with wand.color.Color('transparent') as background_color:
		library.MagickSetBackgroundColor(image.wand, background_color.resource) 
	    image.read(blob=svg_file.read())
	    png_image = image.make_blob("png32")

	with open(output_filename, "wb") as out:
	    out.write(png_image)

def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph

# -------------------------
# Get Murgen Stats
# -------------------------

def GetMurgenStats():
	MurgenURL = "https://hackaday.io/project/9281-murgen-open-source-ultrasound-imaging"
	page = urllib2.urlopen(MurgenURL)
	soup = BeautifulSoup(page.read())
	print soup.find_all("div","section-profile-stats")[0]
#div content-left section-profile-stats

# -------------------------
# Gestion des modules
# -------------------------


def GetListofModules(dirname):
	ListOfDirs = os.listdir(dirname)  
	ModulesDirs = []
	for f in ListOfDirs:
		if  os.path.isdir(dirname+"/"+f):
			ModulesDirs.append(f)
	# On retire les repertoires non modules
	if ("retired" not in dirname):
		f = [x for x in ModulesDirs if x not in ExcludeDirsRetired]
	else:
		f = [x for x in ModulesDirs if x not in ExcludeDirs]
	return f

def getText(path):
	f = open(path,'r')
	text = f.read()+"\n"
	text.replace(tagAuto,"")
	f.close()
	return text

def returnSoup(path):
	f = open(path, 'r')
	RawHTML=markdown.markdown( f.read() )
	f.close()
	return [BeautifulSoup(RawHTML,"lxml"),RawHTML]

def getHs(soupH,h,hText):
	Text = BeautifulSoup("", "lxml")
	if (h in ValidH):
		allH = soupH.find_all(h)
		for H in allH:
			if hText in H:
 				nextSib = H.find_next(True)
   				while nextSib is not None and h not in nextSib.name :
 
					Text.append(nextSib)
					#print nextSib.text
               				nextSib = nextSib.nextSibling
	return Text

def returnHList(soup,h,hText):
	ListItem = []
	if (h in ValidH):
		desch3 = soup.find_all(h)
		for H in desch3:
			if hText in H.text:
			    for item in H.find_next("ul").find_all("li"):
				ListItem.append(item)
	else:
		print "H Error"
	return ListItem

def getCode(string):
	ListOfCodes = []
	for item in string.find_all("code"):
		ListOfCodes.append(item.text)
	return ListOfCodes


def MakeExperiments(ExpList,ListIfImage,FatJSON):
	ExpeJSON = {}
	ExpeSummary = ""
	for Expe in ExpList:
		ExpeJSON[Expe] = {}

		# Checks MD, ino, py, c, jupyter
		ListOfChecks = ["md","jupyter","C", "arduino", "python"]
		SourceCode = "# Experiment `"+Expe+"`\n\n## List of files"
		for keyKey in ListOfChecks:
			Files = []
			for key in FatJSON[keyKey].keys():
				tmpfile = open("."+key, "r") 
				if "`"+Expe+"`" in tmpfile.read() :
					Files.append(key)
				elif (Expe in key) and ("include" not in key) and ("gitbook" not in key):
					Files.append(key)
			Files = list(set(Files))
			if len(Files):
				SourceCode += "\n\n### "+keyKey+"\n\n"
				for fil in Files:
					SourceCode += "* ["+fil.split("/")[-1]+"]("+fil+")\n"

		fnameD = "./include/experiments/auto/Code_"+Expe+".md"
		OpenWrite(SourceCode,fnameD)


		fnameD = "./include/experiments/Desc_"+Expe+".md"
		if not (os.path.isfile(fnameD)):
			OpenWrite("# Experiment "+Expe+" description\n\n",fnameD)

		matches = [x for x in ListIfImage if Expe in x[3] ]
		ExpeJSON[Expe]["images"] = []
		setupimgs = [x for x in matches if "setup" in x[2] ]
		bscimgs = [x for x in matches if "BSC" in x[2] ]
		ascimgs = [x for x in matches if "ASC" in x[2] ]

		others = []
		ModList = []
		for item in matches:
			if((item not in setupimgs) and (item not in ascimgs) and (item not in bscimgs) ):
				others.append(item)
			ModList.append(item[1])
			ExpeJSON[Expe]["images"].append(item[5][1:])

		ExpImages = "# Images of the Experiment\n\n"
		if (len(setupimgs)):
			ExpImages += "## Setup\n\n"
			
			for img in setupimgs:
				ExpImages += "![]("+img[5][1:]+")\n\n"+img[4]+"\n\n"
		if (len(bscimgs)):
			ExpImages += "## Raw images\n\n"
			for img in bscimgs:
				ExpImages += "![]("+img[5][1:]+")\n\n"+img[4]+"\n\n"
		if (len(ascimgs)):
			ExpImages += "## Scan converted\n\n"
			for img in ascimgs:
				ExpImages += "![]("+img[5][1:]+")\n\n"+img[4]+"\n\n"
		if (len(others)):
			ExpImages += "## Others\n\n"
			for img in others:
				ExpImages += "![]("+img[5][1:]+")\n\n"+img[4]+"(category: __"+img[2]+"__)\n\n"

		OpenWrite(ExpImages,"./include/experiments/auto/Img_"+Expe+".md")

		ModulesT = "\n# Modules\n\n"

		ModF = []
		ModZ = []
		for mod in ModList:
			Modz = mod.split(",")
			for module in Modz:
				ModZ.append(module.strip())
		ModF = list(set(ModZ)) # Modules
		if "ToTag" in ModF:
			Modz.remove("ToTag")
		ExpeJSON[Expe]["modules"] = []
		for OneMod in ModF:
			if OneMod in ModulesList:
				ModulesT += "* ["+OneMod+"](/"+OneMod+"/)\n"
				ExpeJSON[Expe]["modules"].append(OneMod)
			elif OneMod in ModulesRetiredList:
				ModulesT += "* ["+OneMod+"](/retired/"+OneMod+"/)\n"
				ExpeJSON[Expe]["modules"].append(OneMod)


		fname = "./include/experiments/auto/Mod_"+Expe+".md"
		OpenWrite(ModulesT,fname)


		fname = "./include/experiments/auto/"+Expe+".md.tpl"
		PM = "@kelu include(/include/experiments/Desc_"+Expe+".md)\n\n"
		PM = "@kelu include(/include/experiments/auto/Code_"+Expe+".md)\n\n"
		PM += "@kelu include(/include/experiments/auto/Mod_"+Expe+".md)\n\n"
		PM += "@kelu include(/include/experiments/auto/Img_"+Expe+".md)\n\n"

		ExpeSummary += "  * ["+Expe+"](/include/experiments/auto/"+Expe+".md)\n"
		OpenWrite(PM,fname)
	OpenWrite(ExpeSummary,"include/AllExpes.md")
	return ModF,ExpeJSON

# -------------------------
# Processing images
# -------------------------


def ListJPGfromBMP(path):
	# Gets BMP, makes PNG
	ListBMP = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.BMP'))]
	for bmpImg in ListBMP:
		img = Image.open(bmpImg)
		ImgPath = os.path.dirname(bmpImg)
		ImgName = bmpImg.split("/")[-1].split(".")[0]
		NewPath = ImgPath+"/"+ImgName+".png"

		if not os.path.isfile(NewPath):
			if "IMAG" in bmpImg:
				new_img = img.resize( (800, 480) )
				new_img.save(NewPath, 'png')
			else:
				img.save( NewPath, 'png')

	return ListBMP


def CreateImgTags(ImgSrc):
	# Use Make, Model
	# ModulesList 
	# ModulesRetiredList
	edited = 0
	metadata = pyexiv2.ImageMetadata(ImgSrc)
	metadata.read()
	FileNameIs = ImgSrc.split("/")[-1]
	# Datetime
	try:
    		metadata['Exif.Image.DateTime']
	except KeyError:
		#edited = 1
		dt = ""
		hm = ""
		if ("201" in FileNameIs):	
			m = re.findall("([0-9]+)", FileNameIs)
			if (len(m) and len(m[0]) == 8): 
				tim = m[0]
				dt = tim[:4]+"-"+tim[4:6]+"-"+tim[6:8]

			if ( (len(m) > 1) and len(m[1]) == 6): 
				hom = m[1]
				hm = hom[:2]+":"+hom[2:4]+":"+hom[4:6]
			else:
				hm = "12:00:00" 
			if (len(dt) and len(hm)):
				DateTime = dt + " "+hm
				if (len(DateTime) == 19):
					metadata['Exif.Image.DateTime'] = DateTime
					edited = 1
					print FileNameIs + " -- " + DateTime

	# Main Module
	try:
    		metadata['Exif.Image.Software']
	except KeyError:
		edited = 1
		print 'Exif.Image.Software'
		if any(ext in ImgSrc for ext in ModulesList):
			metadata['Exif.Image.Software'] = ImgSrc.split("/")[1]
		elif any(ext in ImgSrc for ext in ModulesRetiredList):
			metadata['Exif.Image.Software'] = ImgSrc.split("/")[2]
		elif "/s3/" in ImgSrc:
			metadata['Exif.Image.Software'] = "s3"
		else:
			metadata['Exif.Image.Software'] = "ToTag"

	DefaultTag = ["A310","8.3","26.1.B","9.3.2","Adobe Photoshop","G900IDVU1CQB1"]

	if any(ext in metadata['Exif.Image.Software'].value for ext in DefaultTag):
		edited = 1
		if any(ext in ImgSrc for ext in ModulesList):
			metadata['Exif.Image.Software'] = ImgSrc.split("/")[1]
		elif any(ext in ImgSrc for ext in ModulesRetiredList):
			metadata['Exif.Image.Software'] = ImgSrc.split("/")[2]
		else:
			metadata['Exif.Image.Software'] = "ToTag"

	# Experiment
	DefaultTag = ["Apple","Sony","LG Electronics","amsung","OnePlus","Canon"]
	try:
		metadata['Exif.Image.Make'].value
	except KeyError:
		metadata['Exif.Image.Make'] = "ToTag"
	if any(ext in metadata['Exif.Image.Make'].value for ext in DefaultTag): 
		edited = 1
		metadata['Exif.Image.Make'] = "ToTag"

	# Artist
	try:
    		metadata['Exif.Image.Artist']
	except KeyError:
		edited = 1
		print 'Exif.Image.Artist'
		if ("community" in ImgSrc):
			Author = ImgSrc.replace("/include/community/","")
			AuthorName = Author.split("/")[0][1:]
			print AuthorName
		else:
			AuthorName = "kelu124"
		metadata['Exif.Image.Artist'] = AuthorName

	# Category
	try:
		metadata['Exif.Photo.MakerNote']
	except KeyError:
		edited = 1
		print 'Exif.Photo.MakerNote'
		
		if any(ext in ImgSrc for ext in ("TEK0","IMAG0")):
					metadata['Exif.Photo.MakerNote'] = "oscilloscope"
		elif ("iewme.png" in ImgSrc):
			metadata['Exif.Photo.MakerNote'] = "thumbnail"
		elif any(ext in ImgSrc for ext in ("2016","2017","2018")): 
					metadata['Exif.Photo.MakerNote'] = "picture"
		else:
			metadata['Exif.Photo.MakerNote'] = "ToTag"

	DefaultTag = ["Apple iOS","0100"]
	if any(ext in metadata['Exif.Photo.MakerNote'].value for ext in DefaultTag):
		edited = 1
		metadata['Exif.Photo.MakerNote'] = "ToTag"

	MaNo = metadata['Exif.Photo.MakerNote'].value
	try:
		MaNo.decode('utf-8',"strict")

	except UnicodeError:
		# MakerNote sometimes bugs
		print ImgSrc+" : "+str(metadata['Exif.Photo.MakerNote'])
		edited = 1
		metadata['Exif.Photo.MakerNote'] = "ToTag"

	# Image description
	try:
    		metadata['Exif.Image.ImageDescription']
	except KeyError:
		edited = 1
    		metadata['Exif.Image.ImageDescription'] = "ToTag"

	# FilePath

	try:
    		metadata['Exif.Image.DocumentName']
	except KeyError:
		edited = 1
    		metadata['Exif.Image.DocumentName'] = ImgSrc

	if not ( metadata['Exif.Image.DocumentName'].value == ImgSrc):
		edited = 1
		#print metadata['Exif.Image.DocumentName'], ImgSrc
    		metadata['Exif.Image.DocumentName'] = ImgSrc

	# Description
	try:
    		metadata['Exif.Image.ImageHistory']
	except KeyError:

		edited = 1
		metadata['Exif.Image.ImageHistory'] = "Coming from a project aiming at open-sourcing ultrasound imaging hardware - see https://kelu124.gitbooks.io/echomods/content/"

	if edited:
		print edited,ImgSrc
		metadata.write()

	return metadata


def GetTags(Tag):
	TagValue = []
	# 'Exif.Image.Artist' --> Author
	# 'Exif.Image.Software' --> Modules
	# 'Exif.Photo.MakerNote' --> category
	# 'Exif.Image.Make' --> Experiment
	# 'Exif.Image.ImageDescription' --> description

	Tag.read()
	TagValue.append( Tag['Exif.Image.Artist'].value )
	TagValue.append( Tag['Exif.Image.Software'].value )
	TagValue.append( str(Tag['Exif.Photo.MakerNote'].value) )
	TagValue.append( str(Tag['Exif.Image.Make'].value) )
	TagValue.append( str(Tag['Exif.Image.ImageDescription'].value) )
	TagValue.append( str(Tag['Exif.Image.DocumentName'].value) )
 

	return TagValue
	
# -------------------------
# Preparing gitbook
# -------------------------

def GitBookizeModule(s,module):
	t = s.split("\n## ")
	del t[1]
	titreModule = t[1]
	titreModule = titreModule.replace("\n","").replace("Title","")
	del t[1]
	del t[1]
	del t[1]
	del t[1]
	#del t[-1]
	del t[-1]
	del t[0]	
	joiner = "\n## "
	u = joiner.join(t)
	u = "## "+u.replace("![Block schema](source/blocks.png)","![Block schema](https://raw.githubusercontent.com/kelu124/echomods/master/"+module+"/source/blocks.png)")
	HeaderModule = "# "+titreModule+ "\n\n## What does it look like? \n\n <img src='https://raw.githubusercontent.com/kelu124/echomods/master/"+module+"/viewme.png' align='center' width='150'>\n\n"
	u = HeaderModule+ u
	return u


def SearchString(s, leader, trailer):
  end_of_leader = s.index(leader) + len(leader)
  start_of_trailer = s.index(trailer, end_of_leader)
  return s[end_of_leader:start_of_trailer]

def AddOneLevel(s):
	return s.replace("# ", "## ")

def AddTwoLevels(s):
	return s.replace("# ", "### ")

def WorkLogLevel(s):
	return s.replace("#### ", "## ")

def IncludeImage(s):
	return s.replace("<img src='https://github.com/kelu124/echomods/blob/master/", "<img src='https://raw.githubusercontent.com/kelu124/echomods/master/")

def AddRawHURL(s):
	BaseURL = "https://kelu124.gitbooks.io/echomods/content"
	URL = "https://raw.githubusercontent.com/kelu124/echomods/master/" 
	for o in range(len(ToBeReplaced)):
		s = s.replace("]("+ToBeReplaced[o]+")", "]("+BaseURL+Replaced[o]+")")

	for moduledeux in ModulesChaptDeux:
		s = s.replace("](/"+moduledeux+"/)", "]("+BaseURL+"/Chapter2/"+moduledeux+".md)")	
		s = s.replace("](/"+moduledeux+"/source/blocks.png)", "](https://raw.githubusercontent.com/kelu124/echomods/master/"+moduledeux+"/source/blocks.png)")	
		s = s.replace("](/"+moduledeux+"/Readme.md)", "]("+BaseURL+"/Chapter2/"+moduledeux+".md)")
	for moduledeux in ModulesChaptDeuxRT:
		s = s.replace("](/retired/"+moduledeux+"/)", "]("+BaseURL+"/Chapter2/"+moduledeux+".md)")	
		s = s.replace("](/retired/"+moduledeux+"/source/blocks.png)", "](https://raw.githubusercontent.com/kelu124/echomods/master/"+moduledeux+"/source/blocks.png)")	
		s = s.replace("](/retired/"+moduledeux+"/Readme.md)", "]("+BaseURL+"/Chapter2/"+moduledeux+".md)")

	for moduletrois in ModulesChaptTrois:
		s = s.replace("](/"+moduletrois+"/)", "]("+BaseURL+"/Chapter3/"+moduletrois+".md)")	
		s = s.replace("](/"+moduletrois+"/Readme.md)", "]("+BaseURL+"/Chapter3/"+moduletrois+".md)")
		s = s.replace("](/"+moduletrois+"/source/blocks.png)", "](https://raw.githubusercontent.com/kelu124/echomods/master/"+moduletrois+"/source/blocks.png)")	

	for moduletrois in ModulesChaptTroisRT:
		s = s.replace("](/retired/"+moduletrois+"/)", "]("+BaseURL+"/Chapter3/"+moduletrois+".md)")	
		s = s.replace("](/retired/"+moduletrois+"/Readme.md)", "]("+BaseURL+"/Chapter3/"+moduletrois+".md)")
		s = s.replace("](/retired/"+moduletrois+"/source/blocks.png)", "](https://raw.githubusercontent.com/kelu124/echomods/master/"+moduletrois+"/source/blocks.png)")


	s = s.replace("![](/", "![]("+URL)

	s = GHubToGBook(s)

	return s

def GHubToGBook(s):

	for module in ModulesChaptDeux:
		s = s.replace("](https://github.com/kelu124/echomods/tree/master/"+module+"/)", "](https://kelu124.gitbooks.io/echomods/content/Chapter2/"+module+".html)")
		s = s.replace("io/echomods/content/Chapter2/"+module+".md)","io/echomods/content/Chapter2/"+module+".html)")

	for module in ModulesChaptTrois:
		s = s.replace("](https://github.com/kelu124/echomods/tree/master/"+module+"/)", "](https://kelu124.gitbooks.io/echomods/content/Chapter3/"+module+".html)")
		s = s.replace("io/echomods/content/Chapter3/"+module+".md)","io/echomods/content/Chapter3/"+module+".html)")

	s = s.replace("](https://github.com/kelu124/bomanz/)", "](https://kelu124.gitbooks.io/echomods/content/Chapter3/bomanz.html)")	

	return s

def AddRawMurgenURL(s):
	ListOfMurgenSessions = ["Session_1.md","Session_2.md","Session_3.md","Session_4.md","Session_4b.md","Session_5.md","Session_6.md","Session_7.md","Session_8.md","Session_9_ATL.md",]
	BaseURL = "https://kelu124.gitbooks.io/echomods/content"
	URL = "https://raw.githubusercontent.com/kelu124/murgen-dev-kit/master/"
	for Session in ListOfMurgenSessions:
		s = s.replace("](/worklog/"+Session+")", "]("+BaseURL+"/Chapter4/"+Session+")")	
	s= re.sub('!\[.*\]', '![]', s)
	return s.replace("![](/", "![]("+URL)

def AddRawBomanzURL(s):
	BaseURL = "https://kelu124.gitbooks.io/echomods/content"
	URL = "https://raw.githubusercontent.com/kelu124/bomanz/master/"
	PyNb = "https://github.com/kelu124/bomanz/blob/master"
	s= re.sub('!\[.*\]', '![]', s)
	s = s.replace("![](/", "![]("+URL)
	s = s.replace("](/", "]("+PyNb+"/")
	s= GHubToGBook(s)
	return s

def OpenWrite(Write,Open):
	f = open(Open,"w+")
	Write.replace(tagAuto,"")
	f.write(Write+"\n\n"+tagAuto)
	return f.close()


def CopyFile(From,To):
	return OpenWrite(getText(From),To)

def CopyGitBookFile(From,To):
	result = []
	with open("./"+From) as FileContent:
		for line in FileContent:
			i = 0
			result.append(line)
	return OpenWrite(AddRawHURL("".join(result)),To)

def CopyGitBookMurgenFile(From,To):
	return OpenWrite(AddRawMurgenURL(getText(From)),To)

def CopyGitBookBomanzFile(From,To):
	return OpenWrite(AddRawBomanzURL(getText(From)),To)

def GraphModule(Paires,GraphThisModule,ReadMe,FullSVG):
        for eachPair in Paires:
	    eachPair = eachPair.text
	    if ("->" in eachPair):
	   	Couples = eachPair.split("->")
		for single in Couples:
		    GraphThisModule.node(single, style="rounded")
		# Add the edge		
		for k in range(len(Couples)-1):
		    GraphThisModule.edge(Couples[k], Couples[k+1])
	if FullSVG:
		GraphThisModule.render(ReadMe+'/source/blocks')
		Svg2Png(ReadMe+'/source/blocks')


# -------------------------
# Check update suppliers
# -------------------------

def GetSuppliersList(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], 'sup*.md'))]
	Text = ""
	for eachSupplier in results:
		[soup,ReadMehHtmlMarkdown] = returnSoup(eachSupplier)
		#print getParam(ReadMe,"ds")
		Infos = returnHList(soup,"h3","Info")
		NameSupplier = ""
		SiteSupplier = ""
		for info in Infos:
			if "Name:" in info.text:
				NameSupplier = info.text.replace("Name:", "").strip()
			if "Site:" in info.text:
				SiteSupplier = info.text.replace("Site:", "").strip()
		Text += "\n* ["+NameSupplier+"]("+SiteSupplier+"): "
		Status = returnHList(soup,"h3","Status")
		for status in Status:
			Text += status.text.replace("</li>", "").replace("<li>", "")+", "
	Text += "\n\n"

	return Text	


def GetLogs(path):
	d = {}

	d[20160306] = ["./gitbook/content/Chapter4/Session_1.md"]
	d[20160311] = ["./gitbook/content/Chapter4/Session_2.md"]
	d[20160315] = ["./gitbook/content/Chapter4/Session_3.md"]
	d[20160319] = ["./gitbook/content/Chapter4/Session_4.md"]
	d[20160319] += ["./gitbook/content/Chapter4/Session_4b.md"]
	d[20160320] = ["./gitbook/content/Chapter4/Session_5.md"]
	d[20160328] = ["./gitbook/content/Chapter4/Session_6.md"]
	d[20160403] = ["./gitbook/content/Chapter4/Session_7.md"]
	d[20160503] = ["./gitbook/content/Chapter4/Session_8.md"]
	d[20160703] = ["./gitbook/content/Chapter4/Session_9.md"]

	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.*'))]
	ExcludeDirs = ["tools",".git","doc"]
	f = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	for eachMd in f:
	    if ( (".ipynb_checkpoints" not in eachMd) and (".html" not in eachMd) ):
		if (eachMd.split("/")[-1].startswith("2017") or eachMd.split("/")[-1].startswith("2016") or eachMd.split("/")[-1].startswith("2015") ):
		        Date = int(eachMd.split("/")[-1].replace("-","")[:8])
			#print eachMd +"  -  " + str(Date)
			if Date in d:
				d[Date] += [eachMd]
			else:
				d[Date] = [eachMd]

	with open("include/AddPressReview.md") as FileContent:
	    for line in FileContent:  #iterate over the file one line at a time(memory efficient)
		if "*" in line:
			url = line[line.find("(")+1:line.find(")")]
			Date = int(line.replace("* ","").replace("-","")[:8])
			if Date in d:
				d[Date] += [url]
			else:
				d[Date] = [url]
	return d

def CreateWorkLog(d):
	log = "# History \n\n"
	keys = sorted(d, reverse=True)
	for key in keys:
		date = str(key)
		log += "\n * __"+date[0:4]+"-"+date[4:6]+"-"+date[6:8]+"__: "
		LogOfTheDay = []

		for item in d[key]:
			if ("/gitbook/" in item):
				link = "["+item.split("/")[-1]+"](https://kelu124.gitbooks.io/echomods"+item[17:].split(".")[0]+".html)"
				LogOfTheDay.append(link)
			elif ("http" in item):
				link = "[link from "+item.split("/")[2]+"]("+item+")"
				LogOfTheDay.append(link)
				#print link
			elif ("/gh-pages/_posts/" in item):
				url ="http://kelu124.github.io/echomods/"+item.split("/")[-1]
				link = "[worklog of the day]("+url+")"
				LogOfTheDay.append(link)
			else:
			    if (len(item)):
				url = "https://github.com/kelu124/echomods/tree/master"+item[1:]
				text = item.split("/")[-1]
				link = "["+text+"]("+url+")"
				LogOfTheDay.append(link)
				#m = 0

		log += ", ".join(LogOfTheDay)

	return AddRawHURL(log)

# -------------------------	
# Check auto-files
# Check other files
# -------------------------

def GetGeneratedFiles(path):
	ManualFiles = []
	ManualDesc = []
	ManualContent = []
	AllMDContent = []
	AllFilesList = []
	AutoFiles = []
	log = []
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.md'))]
	ExcludeDirs = ["tools",".git","gh-pages","doc"]
	f = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	for eachMd in f:
		Desc = ""
		with open(eachMd) as FileContent:
			found = False
			foundDesc= False
			FileContenu = ""
			for line in FileContent:  #iterate over the file one line at a time(memory efficient)
			    if tagAuto in line:
				found = True
			    if tagDesc in line:
				foundDesc = True
				start = '\[\]\(@description'
				end = '\)'
				Desc = re.search('%s(.*)%s' % (start, end), line).group(1).strip()
			    FileContenu += line
				#  Pitch/Intro of the project)
			if not found:
				ManualFiles.append(eachMd)
				ManualDesc.append(Desc)	
			else: 
				AutoFiles.append(eachMd)
			if (not found) and (not foundDesc):
				log.append("__[MD Files]__ "+RedMark+" `"+eachMd+"` : Missing description")

			AllFilesList.append(eachMd)
			AllMDContent.append(FileContenu)

	#AutoFiles.sort()
	#ManualFiles.sort()
	return [AutoFiles,ManualFiles,ManualDesc,log,AllMDContent,AllFilesList]


def GetIncludes (InitialText, filez, contentz,origin):
	log = []
	pattern = r'@kelu include\((.*?)\)'
	results = re.findall(pattern, InitialText, flags=0) 
	GoodResults = ["."+x for x in results]
	for item in GoodResults:
		if item in filez:
			k = filez.index(item)
			toreplace = "@kelu include("+item[1:]+")"
			InitialText = InitialText.replace(toreplace,contentz[k])
			#print toreplace
		else:
			InitialText = InitialText.replace("@kelu include("+item[1:]+")","ERROR")
			print "Include error: "+origin+" for "+item
			log += "[INCLUDE] Error with "+origin+"\n\n"
	InitialText = InitialText.replace(tagAuto,"")
	return InitialText,log

 
def CreateRefFiles(NdFiles,PathRefedFile,ContentFiles,PathRefingFile):
	InRef = []
	FileList = []
	log = []

	StringData = ""
	for k in range(NdFiles):
		if (PathRefedFile in ContentFiles[k]) and ("/include/FilesList/" not in ContentFiles[k]): 
			FileList.append(PathRefingFile[k][1:])
			InRef.append("[`"+PathRefingFile[k][1:]+"`]("+PathRefingFile[k][1:]+")")
	if len(InRef):
		StringData = ". File used in: "+", ".join(InRef)+".\n"
	
		#print InRef
	else:
		StringData = ". _File not used._\n"
		if ("/include/" in PathRefedFile):
			log.append("__[Unrefed file]__ "+WarningMark+" `"+PathRefedFile+"` : No references of this file (in _include_). ")
		else:
		    if (not ("/gitbook/" in PathRefedFile)):
			log.append("__[Unrefed file]__ "+RedMark+" `"+PathRefedFile+"` : No references of this file. ")
		    
	return StringData, log, FileList

def GetPythonFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.py'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	PythonFilesList = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	return PythonFilesList

def GetTPLFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.tpl'))]
	ExcludeDirs = ["tools",".git","gh-pages","gitbook"] 
	PythonFilesList = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	return PythonFilesList


def GetJupyFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.ipynb'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	ResJupy = [x for x in results if ".ipynb_checkpoints" not in x]
	JupyFiles = [x for x in ResJupy if x.split("/")[1] not in ExcludeDirs]
	return JupyFiles

def GetImgFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.jpg'))]
	results += [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.png'))]
	results += [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.JPG'))]
	results += [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.PNG'))]
	results += [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.JPEG'))]
	results += [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.jpeg'))]
	ExcludeDirs = ["tools",".git","gh-pages","old"] 
	ImgFiles = [x[1:] for x in results if x.split("/")[1] not in ExcludeDirs]
	
	return ImgFiles

def GetInoFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.ino'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	InoFiles = [x for x in results if x.split("/")[1] not in ExcludeDirs]
	return InoFiles

def GetCFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.c'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	InoFiles = [x for x in results if x.split("/")[1] not in ExcludeDirsRetired]
	return InoFiles

def GetPptFiles(path):
	results = [y for x in os.walk(path) for y in glob(os.path.join(x[0], 'ppt_*.md'))]
	ExcludeDirs = ["tools",".git","gh-pages"] 
	PptFiles = [x for x in results if x.split("/")[1] not in ExcludeDirs]

	return PptFiles

def CheckPythonFile(files):
	## See http://stackoverflow.com/questions/1523427/what-is-the-common-header-format-of-python-files for an idea 
	log = []
	PythonDesc = []
	JSONPython = {}
	for PythonFile in files:
		JSONPython[PythonFile] = {}
		JSONPython[PythonFile]["path"] = PythonFile
		with open(PythonFile) as f:
		    lN = 0
		    moduleDesc = ""
		    # Description, author, copyright, license
		    ErrorConditions = [True, True, True, True]
		    for line in f:
			if (lN == 0) and ("#!/usr/bin/env python" not in line):
				log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Header error ")
			if ("__author__") in line:
				ErrorConditions[1]=False
				JSONPython[PythonFile]["author"] = line
			if ("__copyright__") in line:
				ErrorConditions[2]=False
			if ("__license__") in line:
				ErrorConditions[3]=False
			if ("'''Description") in line:
				ErrorConditions[0]=False
				moduleDesc = line.replace("'''", "").replace("Description:", "").strip()
 				JSONPython[PythonFile]["description"] = moduleDesc

			line = line.rstrip('\r\n').rstrip('\n')
			lN+=1
		    if (ErrorConditions[0]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing description")
			PythonDesc.append("")
		    else:
			PythonDesc.append(moduleDesc)
		    if (ErrorConditions[1]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing Author ")
		    if (ErrorConditions[2]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing Copyright ")
		    if (ErrorConditions[3]):
			log.append("__[Python]__ "+RedMark+" `"+PythonFile+"` : Missing License")
	return log,PythonDesc,JSONPython

def CheckCFile(files):
	## See http://stackoverflow.com/questions/1523427/what-is-the-common-header-format-of-C-files for an idea 
	log = []
	CDesc = []
	JSONC = {}
	for CFile in files:
		JSONC[CFile] = {}
		JSONC[CFile]["path"] = CFile
		with open(CFile) as f:
		    lN = 0
		    moduleDesc = ""
		    # Description, author, copyright, license
		    ErrorConditions = [True, True, True, True]
		    for line in f:
			if (lN == 0) and ("#!/usr/bin/env C" not in line):
				log.append("__[C]__ "+RedMark+" `"+CFile+"` : Header error ")
			if ("__author__") in line:
				ErrorConditions[1]=False
				JSONC[CFile]["author"] = line
			if ("__copyright__") in line:
				ErrorConditions[2]=False
			if ("__license__") in line:
				ErrorConditions[3]=False
			if ("'''Description") in line:
				ErrorConditions[0]=False
				moduleDesc = line.replace("'''", "").replace("Description:", "").strip()
 				JSONC[CFile]["description"] = moduleDesc

			line = line.rstrip('\r\n').rstrip('\n')
			lN+=1
		    if (ErrorConditions[0]):
			log.append("__[C]__ "+RedMark+" `"+CFile+"` : Missing description")
			CDesc.append("")
		    else:
			CDesc.append(moduleDesc)
		    if (ErrorConditions[1]):
			log.append("__[C]__ "+RedMark+" `"+CFile+"` : Missing Author ")
		    if (ErrorConditions[2]):
			log.append("__[C]__ "+RedMark+" `"+CFile+"` : Missing Copyright ")
		    if (ErrorConditions[3]):
			log.append("__[C]__ "+RedMark+" `"+CFile+"` : Missing License")
	return log,CDesc,JSONC

def CheckInoFile(files):
	log = []
	InoDesc = []
	for InoFile in files:
		InoD = ""
		with open(InoFile) as f:
		    lN = 0
		    # Description, author, copyright, license
		    ErrorConditions = [True, True, True, True]
		    for line in f:
			if ("Description:") in line:
				ErrorConditions[1]=False
				InoD = line.replace("Description:", "").strip()
			if ("Author:") in line:
				ErrorConditions[2]=False
			if ("Licence:") in line:
				ErrorConditions[3]=False
			if ("Copyright") in line:
				ErrorConditions[0]=False
			line = line.rstrip('\r\n').rstrip('\n')
			lN+=1
		    if (ErrorConditions[0]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing description")
		    if (ErrorConditions[1]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing Author ")
		    if (ErrorConditions[2]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing Copyright ")
		    if (ErrorConditions[3]):
			log.append("__[Arduino]__ "+RedMark+" `"+InoFile+"` : Missing License")
		InoDesc.append(InoD)
	return log, InoDesc


def CheckLink(path,autogen):
	log = []
	with open(path) as f:
		if ("gitbook" not in path):
		    for line in f:
			patternCode = r"\]\((.*?)\)"
			links = re.findall(patternCode, line, flags=0)
			if len(links):
			    for link in links:
				    Error = False
				    Message = "__[Links]__ "+RedMark+" `"+path+"`"
				    if ("http" not in link) and ("www" not in link) and  (not (link =="")) and  ("@autogenerated" not in link):
					    if (not link.startswith("/") and "@description" not in link):
						Error = True
						Message += " : Error in link definition, non-absolute path in link to `"+link+"`"
				    if (link.startswith("/")) and (link.endswith("/")):
					if not (os.path.isdir("."+link)):
						Error = True
						Message += " : Link to non-existing folder `."+link+"`"
				    if (link.startswith("/")) and not (link.endswith("/")):
					if not (os.path.exists("."+link)):
						Error = True
						Message += " : Link to non-existing file `."+link+"`"
				    if autogen:
					Message = Message +" _(@autogenerated)_"
				    if Error:
					log.append(Message)
	return log
# -------------------------
# Creation of dev-kit sets
# -------------------------

def GetParams(ListOfItems):
    results = []	
    for item in ListOfItems:
	pattern = r"<li>(.*?):"
	results += re.findall(pattern, str(item), flags=0) 
    return results

def getParam(Module,Parameter):
	Param = "Missing parameter for "+Parameter
	Parameter=Parameter+":"
	soupModule = returnSoup(Module+"/Readme.md")[0]
	LIs = soupModule.find_all("li")
	for eachParam in LIs:
		if (eachParam.text.startswith(Parameter)):
			Param = eachParam.text
	Param = Param.replace(Parameter, '').strip()
	return Param

# -------------------------
# Create the kits
# -------------------------

def CreateKits(path,pathmodules,FullSVG):
	Slides = ""
	AllCosts = "# What does it cost?\n\n"
	log = []
	mJSON = []

	for file in os.listdir(path):
	    if file.endswith(".set.md"):
		CostOfSet = ""
		ListOfDirs = []
		KitModuleFile = []
		NomDuSet = file[:-7]
		log.append("__[SET]__ Added `"+NomDuSet+"`\n")
		Slides = Slides + "### "+NomDuSet+"\n\n<ul>"
		with open(path+file) as f:
		    for line in f:
			line = line.rstrip('\r\n').rstrip('\n')
			if len(line)>1 and not line.startswith("#"):
				ListOfDirs.append(line)
			if len(line)>1 and line.startswith("#"):
				KitModuleFile.append(line)
		SetName = ""
		SetDescription = ""

		for item in KitModuleFile:
			if "#Title:" in str(item):
				patternCode = r"#Title:(.*?)$"
				if (re.findall(patternCode, str(item), flags=0)):
					SetName = "## "+re.findall(patternCode, str(item), flags=0)[0]
					
			if "#Description:" in str(item):
				patternCode = r"Description:(.*?)$"
				if (re.findall(patternCode, str(item), flags=0)):
					SetDescription = re.findall(patternCode, str(item), flags=0)[0]

			item = item.replace("#", "")
			Slides += "<li>"+item+"</li>\n"

		CostOfSet += SetName+"\n\n"+SetDescription.strip()+"\n"
		CostOfSet += "\n\n"
		Slides += "</ul>" +"\n\n### "+NomDuSet+": diagram\n\n![](https://raw.githubusercontent.com/kelu124/echomods/master/include/sets/"+NomDuSet+".png)"+"\r\n\n"

		GraphModules = digraph()
		# Dans chaque sous-ensemble..
		PrixSet = 0

		for eachInput in ListOfDirs:
			ModuleCost = ""
			ModuleSourcing = ""
			GraphModules.node(eachInput, style="filled", fillcolor="blue", shape="box",fontsize="22")
			ReadMe = eachInput


			if (eachInput in ModulesChaptDeuxRT) or (eachInput in ModulesChaptTroisRT):
				pathMdl = "retired/"+eachInput
			else:
				pathMdl = eachInput

			ReadMehHtmlMarkdown = returnSoup("./"+pathMdl+"/Readme.md")[1]

			soupSet = returnSoup("./"+pathMdl+"/Readme.md")[0]

			# Getting the Desc of the Module
			ModuleTitle = getHs(soupSet,"h2","Title").text

			#print ModuleDesc

			with open("./"+pathMdl+"/Readme.md") as FileContent:
				for line in FileContent:  #iterate over the file one line at a time(memory efficient)
					if "* cost:" in line:
						patternCode = r"cost:(.*?)$"
						ModuleCost = re.findall(patternCode, line, flags=0)[0]
						PrixSet += int(''.join(c for c in ModuleCost if c.isdigit()))
					if "* sourcing:" in line:
						patternCode = r"\* sourcing:(.*?)$"
						ModuleSourcing = re.findall(patternCode, line, flags=0)[0]

			if (len(ModuleCost)  and len(ModuleSourcing)):
				CostOfSet += "* "+ModuleTitle+" (["+eachInput+"](/"+eachInput
				CostOfSet += "/)) -- get for _"+ModuleCost+"_ (Where? " + ModuleSourcing+")\n"
			if len(ModuleCost) == 0:
				log.append("__[MDL "+eachInput+"]__ "+ RedMark+" Cost missing\n")
			if len(ModuleSourcing) == 0:
				log.append("__[MDL "+eachInput+"]__ "+ RedMark+" Sourcing missing\n")

			
			# Getting the Innards of the Module // inside the block diagram
			pattern = r"block diagram</h3>([\s\S]*)<h2>About"
			results = re.findall(pattern, ReadMehHtmlMarkdown, flags=0) 
			patternCode = r"<li>(.*?)</li>"

			Pairs = []
			GraphThisModule = digraph()
			for item in results:
			    Pairs= (map(str, re.findall(patternCode, item, flags=0)))
			    for eachPair in Pairs:
				eachPair = eachPair.replace("<code>", "")
				eachPair = eachPair.replace("</code>", "")
				Couples = eachPair.split("-&gt;")		
				for single in Couples:
				    GraphThisModule.node(single, style="rounded")
				# Add the edge		
				for k in range(len(Couples)-1):
				    GraphThisModule.edge(Couples[k], Couples[k+1])
				# GraphModules.render('include/'+ReadMe)

			# OK - Getting the Inputs of the Module
			Module = []
			ItemList =  returnHList(soupSet,"h3","Inputs")
		 	for OneIO in ItemList:
				codes = getCode(OneIO)
				if len(codes) > 0:
				    for EachIO in codes:
					Module.append(EachIO)
			if len(Module)>0:
			    for item in Module:
				if "ITF-m" not in item:
				    GraphModules.node(item, style="rounded,filled", fillcolor="yellow")
				else:
				    GraphModules.node(item, style="rounded,filled", fillcolor="green")		
				GraphModules.edge(item, ReadMe, splines="line", nodesep="1")


			# Getting the Ouputs of the Module
			ItemList =  returnHList(soupSet,"h3","Outputs")
		 	for OneIO in ItemList:
				codes = getCode(OneIO)
				if len(codes) > 0:
				    for EachIO in codes:
					Module.append(EachIO)
			if len(Module)>0:
			    for item in Module:
				if "ITF-m" not in item:
				    GraphModules.node(item, style="rounded,filled", fillcolor="yellow")
				else:
				    GraphModules.node(item, style="rounded,filled", fillcolor="green")		
				GraphModules.edge(item, ReadMe, splines="line", nodesep="1")
			GraphModules.edge(ReadMe, item, splines="line", nodesep="1", fillcolor="red")


			GraphPath = path+"/sets/"+NomDuSet
			if FullSVG:
				GraphModules.render(GraphPath)	
				Svg2Png(GraphPath) 
		CostOfSet+="\n\n_Total cost of the set: "+str(PrixSet)+"$_\n\n"
		OpenWrite(CostOfSet,path+"/sets/"+NomDuSet+".cost.md")
		AllCosts += CostOfSet
	# Writing the slides
	OpenWrite(Slides,path+"sets/sets_slides.md")
	OpenWrite(AllCosts,path+"sets/KitCosts.md")





	return log

