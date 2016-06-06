bash generateUi.sh
pyrcc4 -o Images_rc.py ./Images/Images.qrc
pyinstaller --clean -n OntologyTool run.py