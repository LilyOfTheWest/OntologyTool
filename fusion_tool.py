#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Saturation tool for ontologies in rdf
# Written by Line POUVARET
# Intern at Inria Grenoble-Alpes in team IMAGINE
# Supervised by François FAURE and Olivier Palombi
# The program will save the merged ontology in an output file (in turtle format) with "_sat" added to its name

import sys
import os
import glob
import commands
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

today = datetime.now()
log = file("fusion_"+str(today.month)+"_"+str(today.day)+"_"+str(today.year)+"_"+str(today.hour)+"_"+str(today.minute)+".log", "w")
mode = 1

# Converts seconds in hour, min, s, ms (String format)
def prettyTime(t):
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
def myPrint(msg):
	global mode
	if mode == 0 or mode == 3:
		log.write(msg)
	else:
		print msg
		log.write(msg)

def fusion(ontologies, output):
	global mode

	# Definition of namespaces
	# Uncomment if needed
	# NS_owl =  Namespace("http://www.w3.org/2002/07/owl#")
	# NS_rdfs =  Namespace("http://www.w3.org/2000/01/rdf-schema#")
	# NS_xsd =  Namespace("http://www.w3.org/2001/XMLSchema#")
	# NS_rdf =  Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
	# NS_mcf =  Namespace("http://www.mycorporisfabrica.org/ontology/mcf.owl#")

	# Final graph creation
	gMerge = ConjunctiveGraph()

	myPrint("Beginning additions...\n\n")
	for ontology in ontologies:
		gAdd = ConjunctiveGraph()
		if mode == 2 or mode == 3:
			myPrint("\tParsing ontology "+ontology+"...\n")
		gAdd.parse(ontology, format=guess_format(ontology))
		if mode == 2 or mode == 3:
			myPrint("\tAdding ontology "+ontology+", "+str(len(gAdd))+ " triples...\n")
		gMerge = gMerge + gAdd
		if mode == 2 or mode == 3:
			myPrint("\tOntology "+ontology+" added !\n")
			myPrint("\tNew size of merged ontology : "+str(len(gMerge))+" triples\n\n")

	myPrint("Additions complete !\n")
	myPrint("Final size of merged ontology : "+str(len(gMerge))+" triples\n\n")

	myPrint("Saving the ontology in turtle format...\n")
	# Saving the merged ontology in turtle
	gMerge.serialize(output, format="turtle")
	myPrint("Saving done !\n\n")

# Help function
def usage():
	print("\nUSAGE: python fusion_tool.py [options] output [ontologies]\n")
	print("[options] : \n")
	print("\t-h, --help : Display informations about how to use the program\n")
	print("\t-v, --verbose : Activate verbose mode for the output in the shell\n")
	print("\t-q, --quiet : Enable quiet mode for the ouput in the shell\n")
	print("\t-a, --all: Use all rdf files in current folder\n")
	print("\t Enabling both quiet and verbose mode will just write everything in the log file (in verbose mode)\n")
	print("output : name of the output file")
	print("[ontologies] : list of input files separated by a space\n")


def main(argv=None):
	if argv is None:
		argv = sys.argv

    # Options
	import getopt
	try:
		options, argv = getopt.getopt(argv[1:], "hvqa", ["help","verbose","quiet","all"])
	except getopt.GetoptError as message:
		sys.stderr.write("%s\n" % message)
		sys.exit(1)

	global mode
	inputAll = 0

	for option, value in options:
		if option in ["-h", "--help"]:
			usage()
		elif option in ["-v", "--verbose"]:
			if mode == 0:
				mode = 3
			else:
				mode = 2
		elif option in ["-q", "--quiet"]:
			if mode == 2:
				mode = 3
			else:
				mode = 0
		elif option in ["-a", "--all"]:
			inputAll = 1
		else:
			assert False, "unhandled option"

	if inputAll == 1:
		if len(argv) != 1:
			usage()
			sys.exit(1)
		# Nom du fichier de sortie
		output = argv[0]
		output += "_merged.rdf"
		ontologies = glob.glob("./*.rdf")
	else:
		if len(argv) < 3:
			usage()
			sys.exit(1)
		# Nom du fichier de sortie
		output = argv[0]
		output += "_merged.rdf"
		ontologies = [];
		for arg in argv:
			if arg != argv[0]:
				ontologies.append(arg)

	myPrint("Fusion process begins...\n...\n")
	tps0 = time.clock()
	fusion(ontologies, output)
	tps1 = time.clock()

	myPrint("Fusion complete.\n")
	execTime = prettyTime(tps1-tps0)
	myPrint("\nFusion executing time : "+execTime+"\n")

	# Closing the open files
	log.close()

if __name__ == "__main__":
	sys.exit(main())
