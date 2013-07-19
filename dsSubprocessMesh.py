import itertools as it
import sys,time,subprocess


def rfMeshMe(scene,startGlobal,endGlobal,proc,rfRange):
    if sys.platform == "linux":
        rf = "/usr/local/realflow/bin/realflow"
    else:
        rf = "C:\\Program Files\\Next Limit\\RealFlow 2012\\realflow.exe"
        
    max_load = proc
    sleep_interval = .5
    pid_list = []
    rangeList = []
    
    for i in range(startGlobal,endGlobal,rfRange):
        start = i
        end = i + rfRange - 1
        rangeList.append(str(start) +"-"+ str(end))
    tmpGrp = rangeList[-1].split("-")
    
    if int(tmpGrp[-1]) != endGlobal:
        newStart = tmpGrp[0]
        newEnd = endGlobal
        rangeList.remove(rangeList[-1])
        rangeList.append(str(newStart)+"-"+str(newEnd))

    for tmp in rangeList:
        tmpGrp = tmp.split("-")
        start = int(tmpGrp[0])
        end = int(tmpGrp[-1])
        pid = action(rf,start,end,scene)  
        pid_list.append(pid)
        while len(filter(lambda x: x.poll() is None, pid_list)) >= max_load:
            time.sleep(sleep_interval)
    #clearTmp()

def clearTmp():
    if sys.platform == "linux":
        tmpDir = "/media/fat/_rfcmd"
    else:
        tmpDir = "C:/temp"
    tmpList = os.listdir(tmpDir)
    for tmp in tmpList:
        if re.search("rfcmd_",tmp):
            tmpFile = tmpDir + "/" + tmp
            print tmpFile
            os.remove(tmpFile)

def action(rf,start,end,scene):
    if sys.platform == "linux":
        shPath = "/media/fat/_rfcmd/rfcmd_"+ str(start)+ "_" + str(end) +".sh"
    else:
        shPath = "C:/temp/rfcmd_"+ str(start)+ "_" + str(end) +".bat"
        
    f = open(shPath, 'w')
    f.write('"%s" -nogui -threads 1 -mesh -range %s %s "%s"' % (rf, start, end, scene))
    f.close()
    if sys.platform == "linux2":
        p = subprocess.Popen(shPath, shell=True)
    else:
        p = subprocess.Popen(shPath, creationflags = subprocess.CREATE_NEW_CONSOLE)
    return p    
    

rfScene = "/media/fat/Realflow/q0370/q0370_s0010_Jetski_Grid_v003.flw"
startGlobal = 0
endGlobal = 85
proc = 5
rfRange = int(endGlobal/proc)

rfMeshMe(rfScene,startGlobal,endGlobal,proc,rfRange)

