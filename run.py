#TODO: maintenant que l'on peut ajouter des items dans la liste, il faut pouvoir les ajouter à l'ontologie à merger.

import sys
import subprocess
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import QObject, SIGNAL,SLOT, Qt, QCoreApplication, QThread
from saturation_thread import *
from fusion_thread import *
from fusion_adv_thread import *
from mainwindow import Ui_OntologyTool
from listdiff import Ui_ListDiff

mode = 1
ontology = ""
rules = ""
ontologies = []
output = ""

class MyWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_OntologyTool()
		self.ui.setupUi(self)
		self.ui.stopButton.setVisible(False)
		self.ui.stopButton.setEnabled(False)
		self.ui.goButton.setEnabled(False)
		self.list = QtGui.QWidget()
		self.ui2 = Ui_ListDiff()
		self.ui2.setupUi(self.list)
		self.ui2.delButton.setEnabled(False)
		self.ui2.addButton.setEnabled(False)
		self.diff = []
		self.toDel = []
		qApp = QCoreApplication.instance()
		# connect signals with slots

		# closing action
		self.connect(self.ui.actionExit, SIGNAL("triggered()"),qApp, SLOT("quit()"))
		self.connect(QtGui.QShortcut(self.ui.actionExit.shortcut(), self), SIGNAL("activated()"), qApp, SLOT("quit()"))

		# browsing ontologies
		self.connect(self.ui.browseOntologies, SIGNAL("clicked()"), self.ontologies_dialog)
		self.connect(self.ui.ontologyFiles, SIGNAL("textChanged(const QString &)"), self.check_launch)

		# output name
		self.connect(self.ui.browseOutput, SIGNAL("clicked()"), self.ouput_dialog)
		self.connect(self.ui.outputName, SIGNAL("textChanged(const QString &)"), self.check_launch)

		# rules file
		self.connect(self.ui.browseRules_2, SIGNAL("clicked()"), self.rules_dialog)
		self.connect(self.ui.rulesFile, SIGNAL("textChanged(const QString &)"), self.check_launch)

		# radio buttons
		self.connect(self.ui.radioSaturation, SIGNAL("toggled(bool)"), self.modeSaturation)
		self.connect(self.ui.radioFusion, SIGNAL("toggled(bool)"), self.modeFusion)
		self.connect(self.ui.radioFusionAdv, SIGNAL("toggled(bool)"), self.modeFusionAdv)

		# go button
		self.connect(self.ui.goButton, SIGNAL("clicked()"), self.launch_tool)

	# our own slots
	def ontologies_dialog(self):
		global mode, ontology, ontologies, output
		from os.path import isfile
		fd = QtGui.QFileDialog(self)
		# Saturation
		if(mode == 1):
			self.filename = fd.getOpenFileName(self, "Input ontologies", "./", "Ontology Files (*.rdf *.ttl *.owl)")
			if(isfile(self.filename)):
				self.ui.ontologyFiles.setText(self.filename)
				ontology = self.filename
				n = len(ontology)
				output = ontology[:n-4]
				output = output + "_sat.rdf"
				self.ui.outputName.setText(output)
		# Fusion
		else:
			self.filenames = fd.getOpenFileNames(self, "Input ontologies", "./", "Ontology Files (*.rdf *.ttl *.owl)")
			text = ""
			ontologies = []
			for filename in self.filenames:
				if isfile(filename):
					text = text + filename + ";"
					ontologies.append(filename)
			self.ui.ontologyFiles.setText(text)

	def ouput_dialog(self):
		global output
		fd = QtGui.QFileDialog(self)
		if(output == ""):
			pathOutput = "./"
		else: pathOutput = output
		self.filename = fd.getSaveFileName(self, "Output name", pathOutput, "Ontology Files (*.rdf *.ttl *.owl)")
		if(self.filename != ""):
			self.ui.outputName.setText(self.filename)
			output = self.filename

	def rules_dialog(self):
		global rules
		fd = QtGui.QFileDialog(self)
		self.filename = fd.getOpenFileName(self, "Rules file", "./")
		from os.path import isfile
		if isfile(self.filename):
			self.ui.rulesFile.setText(self.filename)
			rules = self.filename

	def check_launch(self):
		global mode
		if(mode == 1):
			if(self.ui.ontologyFiles.text() != "" and self.ui.outputName.text() != "" and self.ui.rulesFile.text() != ""):
				self.ui.goButton.setEnabled(True)
			else:
				self.ui.goButton.setEnabled(False)
		else:
			if(self.ui.ontologyFiles.text() != "" and self.ui.outputName.text() != ""):
				self.ui.goButton.setEnabled(True)
			else:
				self.ui.goButton.setEnabled(False)

	def modeSaturation(self):
		global mode
		mode = 1
		self.ui.modeSelectedLabel.setText("Saturation")
		self.ui.browseRules_2.setEnabled(True)
		self.ui.browseRules_2.setVisible(True)
		self.ui.rulesFile.setEnabled(True)
		self.ui.rulesFile.setVisible(True)
		self.ui.outputName.clear()

	def modeFusion(self):
		global mode
		mode = 2
		self.ui.modeSelectedLabel.setText("Fusion")
		self.ui.browseRules_2.setEnabled(False)
		self.ui.browseRules_2.setVisible(False)
		self.ui.rulesFile.setEnabled(False)
		self.ui.rulesFile.setVisible(False)
		self.ui.outputName.clear()

	def modeFusionAdv(self):
		global mode
		mode = 3
		self.ui.modeSelectedLabel.setText("Fusion advanced")
		self.ui.browseRules_2.setEnabled(False)
		self.ui.browseRules_2.setVisible(False)
		self.ui.rulesFile.setEnabled(False)
		self.ui.rulesFile.setVisible(False)
		self.ui.outputName.clear()

	# running selected tool
	def launch_tool(self):
		global mode, ontology, rules, ontologies
		self.ui.tableWidget.clear()
		self.ui.sortieConsole.clear()
		self.ui2.listWidget.clear()
		if(mode == 1):
			# SATURATION
			self.sat_thread = Saturation(ontology, rules, output)
			self.connect(self.sat_thread,SIGNAL("finished()"), self.sat_done)
			self.connect(self.sat_thread,SIGNAL("add_text(QString)"), self.add_text)
			self.connect(self.sat_thread, SIGNAL("update_table(PyQt_PyObject)"), self.update_table)
			self.ui.stopButton.setEnabled(True)
			self.ui.stopButton.setVisible(True)
			self.ui.goButton.setEnabled(False)
			self.sat_thread.start()
		elif(mode == 2):
			# FUSION
			self.fus_thread = Fusion(ontologies, output)
			self.connect(self.fus_thread, SIGNAL("finished()"), self.fus_done)
			self.connect(self.fus_thread, SIGNAL("warn_ontology()"), self.warn_ontology)
			self.connect(self.fus_thread,SIGNAL("add_text(QString)"), self.add_text)
			self.connect(self.fus_thread, SIGNAL("update_table(PyQt_PyObject)"), self.update_table)
			self.ui.stopButton.setEnabled(True)
			self.ui.stopButton.setVisible(True)
			self.ui.goButton.setEnabled(False)
			self.fus_thread.start()
		elif(mode == 3):
			# FUSION ADVANCED

			# Differences list
			self.list.show()
			self.setEnabled(False)

			# Checking list thread
			self.fusAdv_thread = Diff(ontologies)
			self.connect(self.fusAdv_thread, SIGNAL("finished()"), self.fusAdv_done)
			self.connect(self.fusAdv_thread, SIGNAL("addListItem(QString)"), self.addListItem)
			self.ui.goButton.setEnabled(False)
			self.ui2.listWidget.itemClicked.connect(self.itemChoice)
			self.connect(self.ui2.delButton, SIGNAL("clicked()"), self.delItem)
			self.connect(self.ui2.addButton, SIGNAL("clicked()"), self.addItem)
			self.connect(self.ui2.cancelButton, SIGNAL("clicked()"), self.cancel)
			self.connect(self.ui2.okButton, SIGNAL("clicked()"), self.confirm)
			self.connect(self.fusAdv_thread, SIGNAL("update_table(PyQt_PyObject)"), self.update_table)
			self.fusAdv_thread.start()


			# Confirm et send to fusion thread
		else:
			# ERREUR
			mode = 1

	def add_text(self, msg):
		self.ui.sortieConsole.append(msg)

	def warn_ontology(self):
		QtGui.QMessageBox.warning(self, "Warning!", "You have selected only one ontology. The fusion will still process but the merged ontology will contain the same triples than the input one")

	def update_table(self, dict):
		global mode
		self.ui.tableWidget.setColumnCount(2)
		if(mode == 1):
			self.ui.tableWidget.setRowCount(2)
		else:
			self.ui.tableWidget.setRowCount(len(ontologies)+1)
		forHeaders = []
		for n, key in enumerate(sorted(dict.keys())):
			forHeaders.append(key)
			for m, item in enumerate(dict[key]):
				newItem = QTableWidgetItem(item)
				self.ui.tableWidget.setItem(m,n,newItem)
		self.ui.tableWidget.setHorizontalHeaderLabels(forHeaders)
		self.ui.tableWidget.resizeColumnToContents(1)
		self.ui.tableWidget.resizeColumnToContents(2)

	def addListItem(self, item):
		self.ui2.listWidget.addItem(item)

	def itemChoice(self, item):
		self.ui2.delButton.setEnabled(True)
		self.itemSelected = item

	def delItem(self):
		self.toDel.append(self.itemSelected.text())
		self.ui2.listWidget.takeItem(self.ui2.listWidget.row(self.itemSelected))


	def addItem(self):
		item = QtGui.QInputDialog.getText(self.list, "New triple", "Add a new triple (subject, predicate, object) :")
		if(item != ""):
			triple = item[0].split(", ")
			newTriple = triple[0]+" || "+triple[1]+" || "+triple[2]
			self.ui2.listWidget.addItem(newTriple)

	def cancel(self):
		self.list.close()
		self.setEnabled(True)

	def confirm(self):
		# FUSION

		for index in range(self.ui2.listWidget.count()):
			self.diff.append(self.ui2.listWidget.item(index).text())

		self.setEnabled(True)
		self.list.close()

		self.fusAdv_thread = FusionAdv(ontologies, output, self.diff, self.toDel)
		self.connect(self.fusAdv_thread, SIGNAL("finished()"), self.fusAdv_done)
		self.connect(self.fusAdv_thread,SIGNAL("add_text(QString)"), self.add_text)
		self.connect(self.fusAdv_thread, SIGNAL("update_table(PyQt_PyObject)"), self.update_table)
		self.ui.stopButton.setEnabled(True)
		self.ui.stopButton.setVisible(True)
		self.ui.goButton.setEnabled(False)
		self.fusAdv_thread.start()

	def sat_done(self):
		QtGui.QMessageBox.information(self, "Done!", "Saturation complete !")
		self.ui.stopButton.setEnabled(False)
		self.ui.stopButton.setVisible(False)
		self.ui.goButton.setEnabled(True)

	def fus_done(self):
		QtGui.QMessageBox.information(self, "Done!", "Fusion complete !")
		self.ui.stopButton.setEnabled(False)
		self.ui.stopButton.setVisible(False)
		self.ui.goButton.setEnabled(True)

	def fusAdv_done(self):
		self.ui2.addButton.setEnabled(True)
		self.ui.goButton.setEnabled(True)
		self.ui.stopButton.setEnabled(False)
		self.ui.stopButton.setVisible(False)

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	myApp = MyWindow()
	myApp.show()
	sys.exit(app.exec_())
