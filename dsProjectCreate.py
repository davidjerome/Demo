from xml.etree import ElementTree as ET
from xml.dom import minidom
import sys, os, re, shutil, imp

if sys.platform == "linux2":
    uiFile = '/mounts/vfxstorage/dsGlobal/dsCore/tools/dsProjectCreate/dsSgProjectCreate.ui'
    sys.path.append('/mounts/vfxstorage/dsGlobal/dsCore/maya/dsCommon/')
    sys.path.append('/mounts/vfxstorage/dsGlobal/dsCore/shotgun/')
    
else:
    uiFile = '//vfx-data-server/dsGlobal/dsCore/tools/dsProjectCreate/dsSgProjectCreate.ui'
    sys.path.append('//vfx-data-server/dsGlobal/dsCore/maya/dsCommon/')
    sys.path.append('//vfx-data-server/dsGlobal/dsCore/shotgun/')

from PyQt4 import QtGui, QtCore, uic
import sgTools
reload(sgTools)
import dsFolderStruct as dsFS

print 'Loading ui file:', os.path.normpath(uiFile)
form_class, base_class = uic.loadUiType(uiFile)

class MyForm(base_class, form_class):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName('dsProjectCreate')
        self.setWindowTitle("dsProjectCreate")
        
        if sys.platform == "linux2":
            self.dsPipe = "/dsPipe/"
        else:
            self.dsPipe = "//vfx-data-server/dsPipe/"
        
        self.dsProjectList = []
        self.getProjectList()
        self.updateProjects()

        QtCore.QObject.connect(self.CB_Projects, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateUI)
        QtCore.QObject.connect(self.EpiListWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.updateSeq)
        QtCore.QObject.connect(self.SeqListWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.updateShot)
        QtCore.QObject.connect(self.action_NP, QtCore.SIGNAL("triggered()"), self.addProject)
        QtCore.QObject.connect(self.B_Cancel, QtCore.SIGNAL("clicked()"), self.popUpOff)
        QtCore.QObject.connect(self.B_Cancel_2, QtCore.SIGNAL("clicked()"), self.popUpOff_2)
        QtCore.QObject.connect(self.B_Episode, QtCore.SIGNAL("clicked()"), self.addEpisode)
        QtCore.QObject.connect(self.B_Sequence, QtCore.SIGNAL("clicked()"), self.addSeq)
        QtCore.QObject.connect(self.B_Shot, QtCore.SIGNAL("clicked()"), self.addShot)
        QtCore.QObject.connect(self.SB_StartAt, QtCore.SIGNAL("valueChanged(int)"), self.updatePreview)
        QtCore.QObject.connect(self.SB_Amount, QtCore.SIGNAL("valueChanged(int)"), self.updatePreview)
        QtCore.QObject.connect(self.SB_StepBy, QtCore.SIGNAL("valueChanged(int)"), self.updatePreview)
        QtCore.QObject.connect(self.B_Enter, QtCore.SIGNAL("clicked()"), self.userInput)
        QtCore.QObject.connect(self.LE_ProjectName, QtCore.SIGNAL("returnPressed()"), self.userInput)        
        
    def userInput(self):
        reload(sgTools)
        
        ''' works with popup PTE_Preview. Taking the text value and using it accordingly'''
        ''' On new Project this run's dsCreateFs and send's PROJECT for folder creation'''
        self.dsProjectList = []
        projdata = self.CB_Projects.currentText()
        
        if self.toggle == "Project":
            projectName = self.LE_ProjectName.text()
            fullPath = self.dsPipe + "/" + projectName
            if not os.path.isdir(fullPath):
                dsFS.dsCreateFs("PROJECT",self.dsPipe,projectName)
                self.popUpOff_2()
                self.getProjectList()
                print self.dsProjectList
                self.updateProjects()
                print "updating Projects"
                ##Creates project in SG
                sgTools.sgTestProject(projectName)
            
        ''' On new Episode this creates a new Folder named the episode'''
        if self.toggle == "Epi":
            epiName = self.LE_ProjectName.text()
            if re.search("(_[0-9][0-9][0-9][0-9][0-9][0-9])",epiName):
                epiNSplit = epiName.split("_")
                if epiNSplit != []:
                    if len(epiNSplit[-1]) == 6:
                        fullPath = self.dsPipe + self.dsPrj + "/film/"
                        if not os.path.isdir(fullPath):
                            os.mkdir(fullPath)
                        sgTools.sgTestEpisode(self.dsPrj,epiName)
                        dsFS.dsCreateFs("EPISODE",fullPath,epiName)
                        self.popUpOff_2()
                        self.updateUI()
            
        ''' On new Sequence this run's dsCreateFs and send's SEQUENCE for folder creation'''
        if self.toggle == "Seq":
            row = self.EpiListWidget.currentRow()
            data = self.EpiListWidget.item(row).text()
            fullPath = self.dsPipe + self.dsPrj + "/film/" + str(data) + "/"      
            for Seq in self.qsList:
                if not os.path.isdir(fullPath + "/" + Seq):
                    if self.seqWF_CB.checkState() == 2:
                        dsFS.dsCreateFs("3D",fullPath,Seq)
                        sgTools.sgTestSeq("SEQUENCE",str(self.dsPrj),str(data),str(Seq))             
                    if self.shotWF_CB.checkState() == 2:
                        os.mkdir(fullPath + Seq)
                        sgTools.sgTestSeq("SHOT",str(self.dsPrj),str(data),str(Seq))
                self.popUpOff()
                self.updateUI()
            self.EpiListWidget.setCurrentRow(row)
            
        ''' On new Shot this run's dsCreateFs and send's SHOT for folder creation'''
        if self.toggle == "Shot":
            rowEpi = self.EpiListWidget.currentRow()
            Episode = self.EpiListWidget.item(rowEpi).text()
            rowSeq = self.SeqListWidget.currentRow()
            seq = self.SeqListWidget.item(rowSeq).text()
            fullPath = self.dsPipe + self.dsPrj + "/film/" + str(Episode) + "/" + str(seq) + "/"
            for Shot in self.qsList:
                if not os.path.isdir(fullPath + "/" + Shot):
                    if self.seqWF_CB.checkState() == 2:
                        dsFS.dsCreateFs("COMP",fullPath,Shot)
                        sgTools.sgTestShot("SEQUENCE",str(self.dsPrj),str(Episode),str(seq),str(Shot))
                    if self.shotWF_CB.checkState() == 2:
                        dsFS.dsCreateFs("3D",fullPath,Shot)
                        dsFS.dsCreateFs("COMP",fullPath ,Shot)
                        sgTools.sgTestShot("SHOT",str(self.dsPrj),str(Episode),str(seq),str(Shot))
                self.popUpOff()
                self.updateUI()
            self.EpiListWidget.setCurrentRow(rowEpi)
            self.SeqListWidget.setCurrentRow(rowSeq)
            
    def updatePreview(self):
        self.LW_Preview.clear()
        startAt = int(self.SB_StartAt.text())
        stepBy = int(self.SB_StepBy.text())
        amount = int(self.SB_Amount.text())
        end = startAt + amount * stepBy
        self.qsList = []
        
        for i in range(startAt,end,stepBy):
            if self.toggle == "Seq":
                self.LW_Preview.addItem('q%04d' %int(i))
                self.qsList.append('q%04d' %int(i))
            if self.toggle == "Shot":
                self.LW_Preview.addItem('s%04d' %int(i))
                self.qsList.append('s%04d' %int(i))
        
    def addEpisode(self):
        ''' Set's up gui for adding episode'''
        self.toggle = "Epi"
        self.popDownFrame.setGeometry(QtCore.QRect(30, 110, 241, 61))
        self.LE_ProjectName.setFocus()

    def addSeq(self):
        ''' Set's up gui for adding a sequence'''
        if self.EpiListWidget.currentRow() > -1:
            self.toggle = "Seq"
            self.popUpOn()
            self.seqWF_CB.setEnabled(1)
            self.shotWF_CB.setEnabled(1)
        
    def addShot(self):
        ''' Set's up gui for adding a shot'''
        if self.SeqListWidget.currentRow() > -1:
            self.toggle = "Shot"
            self.popUpOn()
        rowEpi = self.EpiListWidget.currentRow()
        Episode = self.EpiListWidget.item(rowEpi).text()
        rowSeq = self.SeqListWidget.currentRow()
        seq = self.SeqListWidget.item(rowSeq).text()
        fullPath = self.dsPipe + self.dsPrj + "/film/" + str(Episode) + "/" + str(seq) + "/"
        wf = sgTools.sgTestSeqWF(str(self.dsPrj),str(Episode),str(seq))
        WF = wf['sg_sequence_type']
        if WF == 'Shot':
            self.seqWF_CB.setCheckState(0)
            self.shotWF_CB.setCheckState(2)
            self.seqWF_CB.setEnabled(0)
            self.shotWF_CB.setEnabled(0)
        if WF == 'Sequence':
            self.seqWF_CB.setCheckState(2)
            self.shotWF_CB.setCheckState(0)
            self.seqWF_CB.setEnabled(0)
            self.shotWF_CB.setEnabled(0)
                
    def popUpOff_2(self):
        ''' moves popup off screen '''
        self.popDownFrame.setGeometry(QtCore.QRect(-341, 0, 241, 61))
        self.LE_ProjectName.clear()
        
    def popUpOff(self):
        ''' moves popup off screen '''
        self.popupFrame.setGeometry(QtCore.QRect(610, 30, 210, 101))
        self.LW_Preview.clear()
        
    def popUpOn(self):
        ''' moves popup into a center position '''
        self.popupFrame.setGeometry(QtCore.QRect(40, 0, 210, 101))
        self.SB_StartAt.setValue(10)
        self.SB_StepBy.setValue(10)
        self.SB_Amount.setValue(1)
        self.LW_Preview.clear()
        self.updatePreview()

    def addProject(self):
        ''' Set's up gui for adding project'''
        self.toggle = "Project"
        self.popDownFrame.setGeometry(QtCore.QRect(0, 0, 241, 61))
        self.LE_ProjectName.setFocus()

    def updateEpi(self):
        ''' Updates gui bye folder searching'''
        epiList = os.listdir(self.dsPipe + self.dsPrj + "/film/")
        epiList.sort()
        for epi in epiList:
            if os.path.isdir(self.dsPipe + self.dsPrj + "/film/" + epi):
                self.EpiListWidget.addItem(epi)
        
    def updateSeq(self):
        ''' Updates gui bye folder searching'''
        self.SeqListWidget.clear()
        row = self.EpiListWidget.currentRow()
        data = self.EpiListWidget.item(row).text()
        seqList = os.listdir(self.dsPipe + self.dsPrj + "/film/" + str(data) + "/")
        seqList.sort()
        for seq in seqList:
            if re.match("(Q[0-9][0-9][0-9][0-9])",seq) or re.match("(q[0-9][0-9][0-9][0-9])",seq):
                self.SeqListWidget.addItem(seq)
        
    def updateShot(self):
        ''' Updates gui bye folder searching'''
        self.ShotListWidget.clear()
        rowEpi = self.EpiListWidget.currentRow()
        Episode = self.EpiListWidget.item(rowEpi).text()

        rowSeq = self.SeqListWidget.currentRow()
        shot = self.SeqListWidget.item(rowSeq).text()
        shotList = os.listdir(self.dsPipe + self.dsPrj + "/film/" + str(Episode) + "/" + str(shot) + "/")
        shotList.sort()
        for shot in shotList:
            if re.match("(S[0-9][0-9][0-9][0-9])",shot) or re.match ("(s[0-9][0-9][0-9][0-9])",shot):  
                self.ShotListWidget.addItem(shot)
                
    def clearUI(self):
        ''' Init gui'''
        #self.CB_Projects.clear()
        self.EpiListWidget.clear()
        self.SeqListWidget.clear()
        self.ShotListWidget.clear()

    def updateUI(self):
        ''' Updates gui'''
        self.clearUI()
        dsObj = {}
        self.dsPrj = self.CB_Projects.currentText()
        if self.dsPrj != "":
            self.updateEpi()

    def updateProjects(self):
        ''' Updates gui bye folder searching'''
        self.CB_Projects.clear()
        self.CB_Projects.addItem("")
        self.dsProjectList.sort()
        for project in self.dsProjectList:
            self.CB_Projects.addItem(project)
                  
    def getProjectList(self):
        ''' Updates Project drop down '''
        self.allList = []

        tmpProjectList = os.listdir(self.dsPipe)
        for folder in tmpProjectList:
            if os.path.isdir(self.dsPipe + folder + "/Local"):
                self.dsProjectList.append(folder)
                localConfig = "/Local/config.xml"
            if os.path.isdir(self.dsPipe + folder + "/.local"):
                self.dsProjectList.append(folder)
                localConfig = "/.local/config.xml"
        self.allList = self.dsProjectList
        
        self.dsProjectList = []
        self.dsProjectList = self.allList
        self.updateProjects()
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
