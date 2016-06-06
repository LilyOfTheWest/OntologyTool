#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Saturation tool for ontologies in rdf
# Version for PyQt4
# Written by Line POUVARET
# Intern at Inria Grenoble-Alpes in team IMAGINE
# Supervised by François FAURE and Olivier Palombi
# The program will save the saturated ontology in an output file


from PyQt4.QtCore import QThread, SIGNAL
import sys
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
from rdflib.plugins.sparql import prepareQuery

log = ""
tab = {}

class Saturation(QThread):

	def __init__(self, ontology, rules, output):
		QThread.__init__(self)
		self.ontology = ontology
		self.rules = rules
		self.output = output

	def __del__(self):
		self.wait()

	# Converts seconds in hour, min, s, ms (String format)
	def prettyTime(self, t):
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

	# Saturation
	def run(self):
		ontology = self.ontology
		rules = self.rules
		output = self.output
		global log
		today = datetime.now()
		log = open("./logs/saturator_"+str(today.month)+"_"+str(today.day)+"_"+str(today.year)+"_"+str(today.hour)+"_"+str(today.minute)+"_"+str(today.second)+".log", "w")
		tps0 = time.clock()
		self.myPrint("Saturation begins...\n...\n")

		#Definition of namespaces
		owl =  Namespace("http://www.w3.org/2002/07/owl#")
		rdfs =  Namespace("http://www.w3.org/2000/01/rdf-schema#")
		xsd =  Namespace("http://www.w3.org/2001/XMLSchema#")
		rdf =  Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		mcf =  Namespace("http://www.mycorporisfabrica.org/ontology/mcf.owl#")

		# Rules parsing
		rules = open(rules, "r")
		rules_list = []
		for line in rules:
			rules_list.append(line)

		# Ontology parsing
		g = ConjunctiveGraph()
		self.myPrint ("Parsing ontology : "+ontology+"...\n...")
		g.parse(ontology, format=guess_format(ontology))
		self.myPrint ("\nParsing done !\n")
		self.myPrint ("\nOntology's size before saturating process : "+(str(len(g)))+" triples\n")

		listNames = []
		listSizes = []
		ontologySplit = ontology.split('/')
		ontologyName = ontologySplit[len(ontologySplit)-1]
		listNames.append(ontologyName)
		listSizes.append(str(len(g)))
		tab["Ontology"] = listNames
		tab["Size"] = listSizes
		self.emit(SIGNAL('update_table(PyQt_PyObject)'), tab)

		sizeBegin = len(g)
		# Preparing the loop
		size = len(g)
		ok=True
		count = 0

		while ok:
			self.myPrint('\tLoop '+ str(count+1) +' in progress...\n')
			self.myPrint('\tSize at beginning of loop: '+str(size)+'\n')
			nR = 0
			# For each rule
			for r in rules_list:
				self.myPrint("\t\tRule "+str(nR+1)+" in progress...\n")
				q = ''+r.rstrip()+''
				q = prepareQuery(q, initNs={ 'mcf': mcf })
				# Adding new triples to the graph
				s = len(g)
				for row in g.query(q,):
					g.add(row)
				nTriples = len(g)-s
				self.myPrint("\t\tRule "+str(nR+1)+" added "+str(nTriples)+" triples !\n\n")
				nR+=1
			if(size == len(g)):
				ok = False
			else:
				size = len(g)

			count+=1
			self.myPrint("\tLoop "+str(count)+" done !\n\n")

		self.myPrint("New size of saturated ontology : "+str(len(g))+" triples \n")
		self.myPrint(str(len(g)-sizeBegin)+" triples added to the ontology\n")
		self.myPrint("Number of loops : "+str(count)+"\n")


		ontologySplit = output.split('/')
		ontologyName = ontologySplit[len(ontologySplit)-1]
		listNames.append(ontologyName)
		listSizes.append(str(len(g)))
		tab["Ontology"] = listNames
		tab["Size"] = listSizes
		self.emit(SIGNAL("update_table(PyQt_PyObject)"), tab)

		self.myPrint("Saving the ontology...\n")
		# Saving the ontology
		extension = output[len(output)-4:]
		f = ""
		if(extension == ".ttl"):
			f = "turtle"
		elif(extension == ".rdf"):
			f = "xml"
		else:
			f="xml"
			output = output + ".rdf"
		g.serialize(output, format=f)
		self.myPrint("Saving done !\n")

		tps1 = time.clock()

		self.myPrint("Saturation complete.\n")
		execTime = self.prettyTime(tps1-tps0)
		self.myPrint("\nExecuting time : "+execTime+"\n")

		# Closing open files
		log.close()
