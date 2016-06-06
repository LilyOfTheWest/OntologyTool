#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fusion tool for ontologies in rdf
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

class Fusion(QThread):
	def __init__(self, ontologies, output):
		QThread.__init__(self)
		self.ontologies = ontologies
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
		log = open("./logs/fusion_"+str(today.month)+"_"+str(today.day)+"_"+str(today.year)+"_"+str(today.hour)+"_"+str(today.minute)+"_"+str(today.second)+".log", "w")
		ontologies = self.ontologies
		output = self.output
		tps0 = time.clock()
		n = 0
		self.myPrint("Fusion process begins...\n...\n")

		# Definition of namespaces
		# Uncomment if needed
		# NS_owl =  Namespace("http://www.w3.org/2002/07/owl#")
		# NS_rdfs =  Namespace("http://www.w3.org/2000/01/rdf-schema#")
		# NS_xsd =  Namespace("http://www.w3.org/2001/XMLSchema#")
		# NS_rdf =  Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		# NS_mcf =  Namespace("http://www.mycorporisfabrica.org/ontology/mcf.owl#")

		# Final graph creation
		gMerge = ConjunctiveGraph()
		n = len(ontologies)
		if(n == 1):
			self.emit(SIGNAL('warn_ontology()'))

		listNames = []
		listSizes = []
		self.myPrint("Beginning additions...\n\n")
		for ontology in ontologies:
			ontologySplit = ontology.split('/')
			ontologyName=ontologySplit[len(ontologySplit)-1]
			listNames.append(ontologyName)
			gAdd = ConjunctiveGraph()
			self.myPrint("\tParsing ontology "+ontology+"...\n")
			gAdd.parse(ontology, format=guess_format(ontology))
			self.myPrint("\tAdding ontology "+ontology+", "+str(len(gAdd))+ " triples...\n")
			listSizes.append(str(len(gAdd)))
			tab["Ontology"] = listNames
			tab["Size"] = listSizes
			self.emit(SIGNAL('update_table(PyQt_PyObject)'), tab)
			gMerge = gMerge + gAdd
			self.myPrint("\tOntology "+ontology+" added !\n")
			self.myPrint("\tNew size of merged ontology : "+str(len(gMerge))+" triples\n\n")

		self.myPrint("Additions complete !\n")
		self.myPrint("Final size of merged ontology : "+str(len(gMerge))+" triples\n\n")
		ontologySplit = output.split('/')
		ontologyName = ontologySplit[len(ontologySplit)-1]
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

		self.myPrint("Fusion complete.\n")
		execTime = self.prettyTime(tps1-tps0)
		self.myPrint("\nFusion executing time : "+execTime+"\n")

		# Closing open files
		log.close()
