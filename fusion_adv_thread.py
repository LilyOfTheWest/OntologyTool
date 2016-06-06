#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Advanced Fusion tool for ontologies in rdf
# Version for PyQt4
# Written by Line POUVARET
# Intern at Inria Grenoble-Alpes in team IMAGINE
# Supervised by François FAURE and Olivier Palombi
# The program will save the merged ontology in an output file


from PyQt4.QtCore import QThread, SIGNAL
import sys
import os
import glob
import time
from datetime import datetime
from math import *
from random import *
from rdflib import Graph, ConjunctiveGraph, URIRef, Literal, BNode, plugin
from rdflib.namespace import RDF, FOAF, RDFS, OWL, Namespace
from rdflib.plugin import register, Serializer, Parser
from rdflib.util import guess_format
from rdflib.query import ResultParser, ResultSerializer, \
    Processor, Result, UpdateProcessor

log = ""
tab = {}
listNames = []
listSizes = []
class Diff(QThread):
	def __init__(self, ontologies):
		QThread.__init__(self)
		self.ontologies = ontologies

	def __del__(self):
		self.wait()

	def run(self):
		ontologies = self.ontologies

		# Definition of namespaces
		# Uncomment if needed
		NS_owl =  Namespace("http://www.w3.org/2002/07/owl#")
		NS_rdfs =  Namespace("http://www.w3.org/2000/01/rdf-schema#")
		NS_xsd =  Namespace("http://www.w3.org/2001/XMLSchema#")
		NS_rdf =  Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		NS_mcf =  Namespace("http://www.mycorporisfabrica.org/ontology/mcf.owl#")

		g1 = ConjunctiveGraph()
		g2 = ConjunctiveGraph()
		g1.parse(ontologies[0], format=guess_format(ontologies[0]))
		g2.parse(ontologies[1], format=guess_format(ontologies[1]))
		listDiff = ConjunctiveGraph()
		listDiff = g1 ^ g2

		global listNames, listSizes

		for s,p,o in g1.triples((None, None, None)):
			item = ""
			#item += "[[ "+str(s)+" ]]\t[[ "+str(p)+" ]]\t[[ "+str(o)+" ]]"
			item +=str(s)+" || "+str(p)+" || "+str(o)
			self.emit(SIGNAL('addListItem(QString)'), item)

		ontologySplit = ontologies[0].split('/')
		ontologyName=ontologySplit[len(ontologySplit)-1]
		listNames.append(ontologyName)
		listSizes.append(str(len(g1)))
		tab["Ontology"] = listNames
		tab["Size"] = listSizes

		self.emit(SIGNAL('update_table(PyQt_PyObject)'), tab)

		ontologySplit = ontologies[1].split('/')
		ontologyName=ontologySplit[len(ontologySplit)-1]
		listNames.append(ontologyName)
		listSizes.append(str(len(g2)))
		tab["Ontology"] = listNames
		tab["Size"] = listSizes

		self.emit(SIGNAL('update_table(PyQt_PyObject)'), tab)



class FusionAdv(QThread):
	def __init__(self, ontologies, output, diff, toDel):
		QThread.__init__(self)
		self.ontologies = ontologies
		self.diff = diff
		self.toDel = toDel
		self.output = output

	def __del__(self):
		self.wait()

	# Converts seconds in hour, min, s, ms (String format)
	def prettyTime(self,t):
		m = 0
		s = int(t)
		h = 0
		ms = int(round((t-int(t))*1000))
		if t >= 1:
			if t >= 60:
				m = s/60
				s = s%60
				if m >= 60:
					h = m/60
					m = m%60

		t = ""+str(h)+" hours, "+str(m)+" minutes, " + str(s)+" seconds, "+str(ms)+" milliseconds."
		return t

	# Printing function
	def myPrint(self, msg):
		global log
		log.write(msg)
		self.emit(SIGNAL('add_text(QString)'), msg)

	def run(self):
		global log
		today = datetime.now()
		log = open("./logs/fusionAdv_"+str(today.month)+"_"+str(today.day)+"_"+str(today.year)+"_"+str(today.hour)+"_"+str(today.minute)+"_"+str(today.second)+".log", "w")
		ontologies = self.ontologies
		output = self.output
		tps0 = time.clock()

		self.myPrint("Fusion process begins...\n...\n")

		owl =  Namespace("http://www.w3.org/2002/07/owl#")
		rdfs =  Namespace("http://www.w3.org/2000/01/rdf-schema#")
		xsd =  Namespace("http://www.w3.org/2001/XMLSchema#")
		rdf =  Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		mcf =  Namespace("http://www.mycorporisfabrica.org/ontology/mcf.owl#")

		self.myPrint("Parsing the first graph...\n")
		g1 = ConjunctiveGraph()
		g1.parse(ontologies[0], format=guess_format(ontologies[0]))
		diff = ConjunctiveGraph()
		toDel = ConjunctiveGraph()
		self.myPrint("Parsing done !\n\n")

		self.myPrint("Parsing differences list...\n")
		listDiff = self.diff
		for item in listDiff:
			itemSplit = item.split(" || ")
			s = itemSplit[0]
			p = itemSplit[1]
			o = itemSplit[2]

			msg="Adding triple : "
			msg=msg+s+" || "+p+" || "+o+"\n"
			self.myPrint(msg)
			diff.add((URIRef(s),URIRef(p),URIRef(o)))
		self.myPrint("Parsing done !\n\n")

		self.myPrint("Parsing triples to remove from the final graph...\n")
		listToDel = self.toDel
		for item in listToDel:
			itemSplit = item.split(" || ")
			s = itemSplit[0]
			p = itemSplit[1]
			o = itemSplit[2]

			msg = "Removing triple : "
			msg = msg + s+" || "+p+" || "+o+"\n"
			self.myPrint(msg)
			toDel.add((URIRef(s),URIRef(p),URIRef(o)))
		self.myPrint("Parsing done !\n\n")

		self.myPrint("Final merge processing...\n")
		gMerge = ConjunctiveGraph()

		gMerge = g1 + diff
		gMerge = gMerge - toDel
		self.myPrint("Merge process complete !\n\n")

		global listNames, listSizes
		ontologySplit = output.split('/')
		ontologyName=ontologySplit[len(ontologySplit)-1]
		listNames.append(ontologyName)
		listSizes.append(str(len(gMerge)))
		tab["Ontology"] = listNames
		tab["Size"] = listSizes

		self.emit(SIGNAL('update_table(PyQt_PyObject)'), tab)

		self.myPrint("Saving the ontology...\n")
		# Saving the merged ontology
		extension = output[len(output)-4:]
		f = ""
		if(extension == ".ttl"):
			f = "turtle"
		elif(extension == ".rdf"):
			f = "xml"
		else:
			f="xml"
			output = output + ".rdf"
		gMerge.serialize(output, format=f)

		self.myPrint("Saving done !\n\n")

		tps1 = time.clock()

		self.myPrint("Fusion advanced complete.\n")
		execTime = self.prettyTime(tps1-tps0)
		self.myPrint("\nFusion advanced executing time : "+execTime+"\n")

		log.close()
