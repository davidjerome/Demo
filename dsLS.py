import sys, sip, re, os, webbrowser
from PyQt4 import QtGui, QtCore, uic
import dsLight
reload(dsLight)

# for the custom Icons
import dsLSResourceUI
reload(dsLSResourceUI)

def getMayaWindow():
    'Get the maya main window as a QMainWindow instance'
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

import maya.cmds as cmds
import maya.OpenMayaUI as mui

if sys.platform == "linux2":
    uiFile = '/dsGlobal/dsCore/maya/dsLight/dsLS.ui'
    presetPath = '/dsPipe/Library/asset/3D/LightSetup/presets'
else:
    uiFile = '//vfx-data-server/dsGlobal/dsCore/maya/dsLight/dsLS.ui'
    presetPath = r'\\vfx-data-server\dsPipe\Library\asset\3D\LightSetup\presets'
    
    
form_class, base_class = uic.loadUiType(uiFile)

class Window(base_class, form_class):
    def __init__(self, parent=getMayaWindow()):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        
        self.updatePresets()
        self.updateLights()
        
        self.connect(self.actionWiki,QtCore.SIGNAL('triggered()'), lambda item=[]: self.webBrowser())
        self.load_B.clicked.connect(self.loadPreset)
        self.prefix_LW.itemSelectionChanged.connect(self.updatePrefix)
        self.prefix_LW.itemDoubleClicked.connect(self.doIt)
        self.prefix_LE.returnPressed.connect(self.doIt)
        self.nn_LE.returnPressed.connect(self.doIt)
        self.lsSelected_B.clicked.connect(self.lsSelected)
        
    def doIt(self):
        self.getRadioLight()
        preFix = str(self.prefix_LE.text())
        nn = str(self.nn_LE.text())

        if nn != "":
            name = preFix + "_" + nn
        else:
            name = preFix

        if not re.search(" ",str(self.prefix_LE.text())):
            if not re.search("[0-9]",str(self.prefix_LE.text())):
                
                light = dsLight.dsCreateLight(name,self.type)
                if light != None:
                    dsLight.createLS(preFix,light)
            else:
                self.updateClear()
        else:
            self.updateClear()
        self.updateClear()
        self.updatePrefix()
        
    def updateClear(self):
        self.updateLights()
        self.prefix_LE.clear()
        self.nn_LE.clear()
        
    def getRadioLight(self):
        if self.amb_RB.isChecked():self.type ="ambient"
        if self.are_RB.isChecked():self.type ="area"
        if self.dir_RB.isChecked():self.type ="directional" 
        if self.poi_RB.isChecked():self.type ="point" 
        if self.spo_RB.isChecked():self.type ="spot" 
        if self.voL_RB.isChecked():self.type ="volume" 
        if self.rec_RB.isChecked():self.type ="vrayRect" 
        if self.dom_RB.isChecked():self.type ="vrayDome" 
        if self.IES_RB.isChecked():self.type ="vrayIES" 
        if self.sph_RB.isChecked():self.type ="vraySphere" 

    def updatePrefix(self):
        self.prefix_LE.clear()
        prefix = str(self.prefix_LW.currentItem().text())
        self.prefix_LE.setText(prefix)  
    
    def lsSelected(self):
        tmpList = self.light_LW.selectedItems()
        lightTypeList = ["VRayLightRectShape","VRayLightDomeShape","VRayLightIESShape","VRayLightSphereShape","directionalLight","ambientLight","pointLight","spotLight","areaLight","volumeLight"]

        for t in tmpList:
            shapeList = cmds.listRelatives(str(t.text()))
            for s in shapeList:
                if cmds.nodeType(s) in lightTypeList:
                    tmpSplit = str(t.text()).split("_")
                    prefix = tmpSplit[0]
                    dsLight.createLS(prefix,str(t.text()))
            
    def updateLights(self):
        self.light_LW.clear()
        lightList = cmds.ls(lt=True) + cmds.ls(type='VRayLightRectShape') + cmds.ls(type='VRayLightDomeShape') + cmds.ls(type='VRayLightIESShape') + cmds.ls(type='VRayLightSphereShape')
        try:
            lightNames = cmds.listRelatives(lightList, parent=True)
            
            for light in lightNames:
                self.light_LW.addItem(light)
        except:
            print "no lights in mayaScene"
        
    def updatePresets(self):
        self.presetDict = {}
        for (path,dirs,files) in os.walk(presetPath):
            for file in files:
                if re.search("_preset",file):
                    self.preset_CB.addItem(file)
                    fPath = path + "/" + file
                    self.presetDict[file] = fPath

    def loadPreset(self):
        "loads maya scene from preset combo box"
        mayaScene = self.presetDict[str(self.preset_CB.currentText())]
        print "importing " + mayaScene
        cmds.file(str(mayaScene), i=True)
        self.updateLights()
        
    def webBrowser(self):
        new = 2 # open in a new tab, if possible
        # open a public URL, in this case, the webbrowser docs
        url = "http://vfx.duckling.dk/?page_id=1543"
        webbrowser.open(url,new=new)
        
def dsLS():
    global myWindow
    myWindow = Window()
    myWindow.show()
