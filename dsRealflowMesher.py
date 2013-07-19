import re,os,sys,subprocess,shutil,time
import itertools as it
from PyQt4 import QtGui, QtCore, uic

if sys.platform == "linux2":
    uiFile = '/dsGlobal/dsCore/tools/dsRealflowMesher/dsRealflowMesher.ui'
else:
    uiFile = '//vfx-data-server/dsGlobal/dsCore/tools/dsRealflowMesher/dsRealflowMesher.ui'
    

print 'Loading ui file:', os.path.normpath(uiFile)
form_class, base_class = uic.loadUiType(uiFile)

class MyForm(base_class, form_class):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName('dsRFMesher')
        self.setWindowTitle("dsRFMesher")
        
        if sys.platform == "linux2":
            self.rf = "'/usr/local/realflow/bin/realflow'"
            self.ply2vrmesh = "'/usr/ChaosGroup/V-Ray/Maya2012-x64/bin/ply2vrmesh'"
        else:
            self.rf = "C:/Program Files/Next Limit/RealFlow 2012/realflow.exe"
            self.ply2vrmesh = "C:/Program Files/Chaos Group/V-Ray/Maya 2012 for x64/bin/ply2vrmesh.exe"
            
        self.PB_loadRF.clicked.connect(self.loadRF)
        self.PB_MeshPath.clicked.connect(self.loadMeshPath)
        self.PB_Update.clicked.connect(self.UpdateRF)
        self.PB_Destination.clicked.connect(self.loadDestPath)
        self.PB_Mesh.clicked.connect(self.MeshMe)
        self.PB_VrayProxy.clicked.connect(self.VrayProxy)
     
    def loadMeshPath(self):
        #load realflow file
        self.testSettings()
        self.LE_MeshPath.setEnabled(1)
        self.meshPath = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "Realflow Mesh (*.bin)")
        self.LE_MeshPath.setText(self.meshPath)
        tmpSplit = str(self.meshPath).split("/")
        destPath = str(self.meshPath).replace(tmpSplit[-1] + "/","vrmesh")
        self.LE_DestPath.setText(destPath)
        self.generateVrayPath()
        
        
    def loadDestPath(self):
        #load realflow file
        self.testSettings()
        self.LE_DestPath.setEnabled(1)
        self.destPath = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
        self.LE_DestPath.setText(self.destPath + "/")     
   
    def loadRF(self):
        #load realflow file
        self.testSettings()
        self.rfFile = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "Realflow Files (*.flw)")
        self.path_LE.setText(self.rfFile)

    def UpdateRF(self):
        self.testSettings()
        if not self.LE_MeshPath.isEnabled():
            self.generateMeshPath()
        if not self.LE_DestPath.isEnabled():
            self.generateVrayPath()
    
    def testSettings(self):
        #get interface info and test if all values are int 
        val = 0
        try:
            self.startGlobal = int(self.LE_start.text())
            self.endGlobal = int(self.LE_end.text())
            self.proc = int(self.LE_split.text())
            self.seqOffset = int(self.LE_offset.text())
            self.rfRange = int(self.LE_range.text())
            self.meshName = str(self.LE_MeshName.text())
            val = 1
        except:
            val = 0
            print "Values need to be int"
    
    def generateMeshPath(self):
        tmp = str(self.rfFile).split("/")
        root = self.rfFile.replace(tmp[-1],"")
        self.meshPath = root + "meshes/" + self.meshName
        self.LE_MeshPath.setText(self.meshPath)
        
    def generateVrayPath(self):
        tmp = str(self.meshPath).split("/")
        root = self.meshPath.replace(tmp[-1],"")
        self.vrayProxPath = root + "vrMesh/" + self.meshName
        self.LE_DestPath.setText(self.vrayProxPath)     
        
    def MeshMe(self):
        self.testSettings()
        max_load = self.proc
        sleep_interval = .5
        pid_list = []
        rangeList = []
        
        for i in range(self.startGlobal,self.endGlobal,self.rfRange):
            start = i
            end = i + self.rfRange - 1
            rangeList.append(str(start) +"-"+ str(end))
        tmpGrp = rangeList[-1].split("-")
        
        if int(tmpGrp[-1]) != self.endGlobal:
            newStart = tmpGrp[0]
            newEnd = self.endGlobal
            rangeList.remove(rangeList[-1])
            rangeList.append(str(newStart)+"-"+str(newEnd))
    
        for tmp in rangeList:
            tmpGrp = tmp.split("-")
            start = int(tmpGrp[0])
            end = int(tmpGrp[-1])
            print tmp
            pid = action(rf,start,end,scene)  
            pid_list.append(pid)
            while len(filter(lambda x: x.poll() is None, pid_list)) >= max_load:
                time.sleep(sleep_interval)
        
    def VrayProxy(self):
        self.testSettings()
        # max_load is your amount of process at one time
        max_load = self.proc
        sleep_interval = 0.5
        pid_list = []
        
        tmpSplit = str(self.meshPath).split("/")
        
        tmpList = os.listdir(self.meshPath.replace(tmpSplit[-1],""))
        tmpList.sort()
        
        frameNum = int(self.seqOffset)

        dstvrMesh = str(self.LE_DestPath.text())

        if not os.path.exists(dstvrMesh):os.makedirs(dstvrMesh)
        
        for file in tmpList:
            #if not re.search("Realwave",file):
            if re.search(".bin",file):
                inPath = self.meshPath + file
                val = "%05d" %(frameNum)
                fileNew = re.sub("_[0-9][0-9][0-9][0-9][0-9].","_" + str(val) + ".",file)
                fileNew = fileNew.replace(".bin",".vrmesh")
                outPath = dstvrMesh + fileNew

                pid = self.vrmeshMe(inPath,outPath)
                pid_list.append(pid)
                
                while len(filter(lambda x: x.poll() is None, pid_list)) >= max_load:
                    time.sleep(sleep_interval)
                    
                frameNum = frameNum + 1
                    
        outSplit = outPath.split("/")
        fileSplit = outSplit[-1].split("_")
        rootPath = outPath.replace(fileSplit[-1],"%05d")
        rootPath = rootPath + ".vrmesh"
        
    def vrmeshMe(self,inPath,outPath):
        #command line to subprocess
        fps = self.SB_FPS.value()
        if self.CB_MapChannel.isChecked():
            MP = "0"
        else:
            MP = "1"
        
        if self.CB_FlipNormals.isChecked():         
            cmd = "%s %s %s -flipNormals -mapChannel %s -fps %s" %(self.ply2vrmesh,inPath,outPath,MP,fps)
        else:      
            cmd = "%s %s %s -mapChannel %s -fps %s" %(self.ply2vrmesh,inPath,outPath,MP,fps)
        
        if sys.platform == "linux2":
            proc = subprocess.Popen(cmd,shell=False)
        else:
            p = subprocess.Popen(cmd, creationflags = subprocess.CREATE_NEW_CONSOLE)
        return p     

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
