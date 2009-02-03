#Covered by GPL V2.0
#Coded by Carlos del Ojo Elias (deepbit@gmail.com)

from urlparse import *
import logging
import re
import copy

from xml.dom.minidom import Document


XSS_SET={
'XSS\'PWNR': "' (Single Quotes)",
'XSS"PWNR': '" (Double Quotes)',
'XS<SP>WNR': '<, > (Less than and great than symbols)',
'XS(SP)WNR': '( ) (Parenthesis)',
'XS-<SCRIPT>alert(document.cookie)</SCRIPT>-SPWNR' : 'Scripting keywords enabled'
}

CARS=['<','>',"'",'(',')']

ENCODING=[
('%hex', 'url encoding (%hex)'),
('%25hex', 'doble url encoding (%25hex)'),
('%2525hex', 'triple url encoding (%25hex)'),
('\\xhex', 'utf8 encoding (\\xhex)'),
('\\u00hex', 'utf8 encoding (\\u00Hex)')
]

STRENCODED="XSSPWNR"
for x,y in ENCODING:
	STRENCODED+="-"+x.replace("hex","41")
STRENCODED+="-XSSPWNR2"


######################################################################################################
######################################################################################################
######################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################

class crossiter:
	''' Container of request variants ''' 
	def __init__(self,req,str="gp"):
		self.req=req
		self.GET=False
		self.POST=False

		self.GETvars=self.req.getGETVars()
		self.POSTvars=self.req.getPOSTVars()

		self.posGET=0
		self.posPOST=0

		if 'g' in str.lower():
			self.GET=True
		if 'p' in str.lower():
			self.POST=True

		self.req.setTotalTimeout(15)
		self.resultSet=[]
		self.success=False

	def launch(self):
		for i in self:
			if i[0]:
				self.success=True
				self.resultSet.append(i)

	def getXMLResults(self):
		success=False

		doc=Document()
		wml = doc.createElement("GazpacioResults")
		doc.appendChild(wml)
		result=doc.createElement("XssResult")
		wml.appendChild(result)
		result.appendChild(self.req.getXML(doc))
		for i in self.resultSet:
			if i[0]:
				success=True
				var = doc.createElement("variable")
				var.setAttribute("name",i[2])
				var.setAttribute("method",i[1])
				inj = doc.createElement("InjectionsAvailable")
				inj.appendChild(doc.createTextNode("\r\n".join(i[3])))
				var.appendChild(inj)
				result.appendChild(var)

		if success:
			return doc

		return None


	def getRAWResults(self):
		if self.success:
			return self.resultSet
		else:
			return []

	def __iter__ (self):
		self.posGET=0
		self.posPOST=0
		return self

	def perform(self, pattern, searchPatt,var):
		matchPatt = False

		var.update(pattern)
	
		for i in range (5):
			try:
				self.req.perform()
				break
			except:
				pass

		var.restore()


		if self.req.response.getContent().count(searchPatt):
			matchPatt = True

		return matchPatt

	def testEncoding(self,var):
		global STRENCODED

		var.update(STRENCODED)

		for i in range (5):
			try:
				self.req.perform()
				break
			except:
				pass

		var.restore()


		res=[('','Normal Encoding')]
		encodings=re.findall("XSSPWNR(.*)XSSPWNR2",self.req.response.getContent())
		if encodings:
			encodings=encodings[0].replace("%2D","-")
			encodings=encodings.replace("%2d","-")
			encodings=re.findall("-[^-]+",encodings)

			for i in range(len(ENCODING)):
				try:
					if encodings[i][1:]=='A':
						res.append(ENCODING[i])
				except:
					print "-----------------EXCEPCION PUTA!----------------"

		return res
		

	def next(self):
		if self.GET and self.posGET < len (self.GETvars):
			var=self.GETvars[self.posGET]
			method="GET"
			self.posGET+=1

		elif self.POST and self.posPOST < len (self.POSTvars):
			var=self.POSTvars[self.posPOST]
			method="POST"
			self.posPOST+=1

		else:
			raise StopIteration

		var.update("XSSPWNR")

		for i in range(5):
			try:
				self.req.perform()
				break
			except:
				pass

		var.restore()
		
		logging.debug('\tTrying %s...' % (var.name))
		

		if self.req.response.getContent().count("XSSPWNR"):
			logging.debug('\t\t%s: Single string injectable' % (var.name))
			setout=[]

			AVAIL_ENCS=self.testEncoding(var)
	
			
			for x,y in XSS_SET.items():
				for enco, desc in AVAIL_ENCS:
					xx = ''
					if enco:
						for car in x:
							xx += enco.replace("hex",hex(ord(car))[2:])
					else:
						xx=x

					logging.debug('\t\tTrying %s (%s) (%s)...' % (var.name, y, desc))
					if self.perform(xx, x,var):
						logging.debug('\t\t%s: %s (%s)' % (var.name,y, desc))
						setout.append(XSS_SET[x] + " " + "(%s)" %(desc))

						logging.debug('\t\tIf encoding works we dont try next...')
						break;

			return (True,method,var.name,setout,var.value)
		else:
			return (False,method,var.name,[],var.value)



