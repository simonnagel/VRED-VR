'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.

Scripted by Rutvik Bhatt, supported by Simon Nagel

First download and copy the osb file "VRController_Select" provided in the GitHub repository into "C:\Users\USERNAME\Documents\Autodesk\Automotive\VRED" path in order to use the dedicated select controller.
If you do not wish to use the dedicated controller you can skip this part. Additionally, download the "Text_to_html.html" file from the GitHub repository and keep it in the folder where your vpb file is opened. 


Just paste the script in the Script Editor of VRED and press run.
Turn on the OpenVR and press the menu button on the controller.
Press the 'Select Object' tools menu in the menu. 
    Press the trigger and point it to the object that you want to select and look at the terminal that floats along with the right controller
    Read the data of the selected node on the terminal 
    Press left, right, up, down to select the corresponding nodes 
    Press the middle menu to open new tools of functionalities

This script works in VRED Collaboration.
Please make sure that, the Script is executed on each computer of each participant.
     
'''


#-------------------------------------------------Select controller---------------------------------------------
import math
import os
import PySide2.QtGui
from PySide2 import QtCore, QtGui
QColor = PySide2.QtGui.QColor
QVector3D = PySide2.QtGui.QVector3D

selectController = 0
selectControllerFound = False
mainCustomFuncGroup = False
allselectNodes = getAllNodes()
for node in allselectNodes:
    allselectNodesName = node.getName()
    if allselectNodesName == "VRController_Select":
        selectController+=1
    elif allselectNodesName == 'VRED-VR-Custom-Fucntion':
        print("group node found in select")
        mainCustomFuncGroup = True
        customFunctionsGroup = node
        
if selectController == 0:
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename = "\VRControllerSelect"
    if os.path.exists(filepath+str(filename)+".osb"):
        node = loadGeometry(filepath +str(filename)+".osb")
        node.setName("VRControllerSelect")
        selectControllerFound = True
    else:
        print("file doesnt exist")
        selectControllerFound = False
else:
    selectControllerFound = True
    
#-----------------------------------------------Select HTML Terminal-------------------------------------
import os
terminal = 0
html_init_line = 25
myArray = []
allNodes = getAllNodes()
htmlNodeExists = False
filename_html = 'Text_to_html.html'
plane = None
htmlGroupNode = False
for node in allNodes:
    nodeName = node.getName()
    if nodeName == 'Select_HTML':
        htmlNodeExists = True
        plane = node
    elif nodeName == 'Group_html':
        htmlGroupNode = True
   
if not htmlNodeExists:

    plane = createPlane(1000, 1000, 2, 2, 1, 1, 1)
    setTransformNodeScale(plane, 0.20, 0.15, 0.075)
    setTransformNodeRotation(plane,-59,0,0)
    setTransformNodeTranslation(plane, 132, 36, -89, 0)
    plane.setName('Select_HTML')
    if htmlGroupNode == True:
        addChilds(findNode('Group_html'),[plane])

if not htmlGroupNode:
    htmlGroup = createNode('Transform3D', 'Group_html')
    addChilds(htmlGroup,[plane])

    
if not vrWebEngineService.getWebEngine("select_html").getName() == 'select_html':
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename_html = "\Text_to_html.html"
    #filename_html = os.getcwd()+'\Text_to_html.html'
    print('engine not exist')
    if os.path.exists(filepath+filename_html):
        webEngine = vrWebEngineService.createWebEngine("select_html")
        webEngine.setUrl(filepath+filename_html)
        webEngine.setMaterial(plane.getMaterial())
        webEngine.setHeight(800)
        webEngine.setWidth(1000)
        filename_html = filepath+'\Text_to_html.html'
    else:
        print('File not found')
else:
    webEngine = vrWebEngineService.getWebEngine("select_html")
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename_html = "\Text_to_html.html"
    #filename_html = os.getcwd()+'\Text_to_html.html'
    webEngine.setUrl(filepath+filename_html)
    webEngine.setMaterial(plane.getMaterial())
    webEngine.setHeight(800)
    webEngine.setWidth(1000)
    filename_html = filepath+'\Text_to_html.html'        

if not mainCustomFuncGroup:
    customFunctionsGroup = createNode('Group', 'VRED-VR-Custom-Fucntion')
    
allFucnNames = ["VRControllerMove", "VRControllerSelect", "VRControllerNotes", 
                "VRControllerDraw", "VRControllerNotes_Notes", "Cloned_ref_obj",
                "D_Tool", "D_Lines", "D_tempLine", "Group_html"]

allNodeFuncname = getAllNodes()
for node in allNodeFuncname:
    nodeName = node.getName()
    if nodeName in allFucnNames:
        addChilds(customFunctionsGroup, [node])
#-----------------------------------------Select Class-----------------------------------------------
class SelectObject():
    
    def __init__(self):
        inpectText = ""
        self.isEnabled =False
        self.createMenu()
        self.timer = vrTimer()
        self.init_html()
        self.parentList = []
        self.multipleSelected = False
        self.tag = None
        self.hitNode = None
        #self.middleMenuFlag = False
        self.extraFucntions = False

        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")
        #tracker = vrDeviceService.getVRDevice("tracker")

        self.leftController.setVisualizationMode(Visualization_ControllerAndHand)
        self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        vrImmersiveInteractionService.setDefaultInteractionsActive(1)

        # six button config
        padCenter = vrdVirtualTouchpadButton('padcenter', 0.0, 0.5, 0.0, 360.0)
        padUpperLeft = vrdVirtualTouchpadButton('padupleft', 0.5, 1.0, 270.0, 330.0)
        padLowerLeft = vrdVirtualTouchpadButton('paddownleft', 0.5, 1.0, 210.0, 270.0)
        padUp = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 330.0, 30.0)
        padUpperRight = vrdVirtualTouchpadButton('padupright', 0.5, 1.0, 30.0, 90.0)
        padLowerRight = vrdVirtualTouchpadButton('paddownright', 0.5, 1.0, 90.0, 150.0)
        padDown = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 150.0, 210.0)
        
        # Right controller
        self.rightController.addVirtualButton(padCenter, 'touchpad')
        self.rightController.addVirtualButton(padUpperLeft, 'touchpad')
        self.rightController.addVirtualButton(padLowerLeft, 'touchpad')
        self.rightController.addVirtualButton(padUp, 'touchpad')
        self.rightController.addVirtualButton(padUpperRight, 'touchpad')
        self.rightController.addVirtualButton(padLowerRight, 'touchpad')
        self.rightController.addVirtualButton(padDown, 'touchpad')
        
        '''
        padCenterSelect = vrdVirtualTouchpadButton('padcenter', 0.0, 0.5, 0.0, 360.0)
        padLeftSelect = vrdVirtualTouchpadButton('padleft', 0.5, 1.0, 225.0, 315.0)
        padUpSelect = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 315.0, 45.0)
        padRightSelect = vrdVirtualTouchpadButton('padright', 0.5, 1.0, 45.0, 135.0)
        padDownSelect = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 135.0, 225.0)

        # right controller
        self.rightController.addVirtualButton(padCenterSelect, 'touchpad')
        self.rightController.addVirtualButton(padLeftSelect, 'touchpad')
        self.rightController.addVirtualButton(padUpSelect, 'touchpad')
        self.rightController.addVirtualButton(padRightSelect, 'touchpad')
        self.rightController.addVirtualButton(padDownSelect, 'touchpad')
        '''
        
        multiButtonPadSelect = vrDeviceService.createInteraction("multiButtonPadSelect")
        multiButtonPadSelect.setSupportedInteractionGroups(["SelectGroup"])
        toolsMenuSelect = vrDeviceService.getInteraction("Tools Menu")
        toolsMenuSelect.addSupportedInteractionGroup("SelectGroup")
        
        #setting control action for right controller Pad
        '''
        self.leftActionSelect = multiButtonPadSelect.createControllerAction("right-padleft-pressed")
        self.upActionSelect = multiButtonPadSelect.createControllerAction("right-padup-pressed")
        self.downActionSelect = multiButtonPadSelect.createControllerAction("right-paddown-pressed")
        self.rightActionSelect = multiButtonPadSelect.createControllerAction("right-padright-pressed")
        self.centerActionSelect = multiButtonPadSelect.createControllerAction("right-padcenter-pressed")
        '''
        self.leftUpperAction = multiButtonPadSelect.createControllerAction("right-padupleft-pressed")
        self.leftDownAction = multiButtonPadSelect.createControllerAction("right-paddownleft-pressed")
        self.upAction = multiButtonPadSelect.createControllerAction("right-padup-pressed")
        self.downAction = multiButtonPadSelect.createControllerAction("right-paddown-pressed")
        self.rightUpperAction = multiButtonPadSelect.createControllerAction("right-padupright-pressed")
        self.rightDownAction = multiButtonPadSelect.createControllerAction("right-paddownright-pressed")
        self.centerAction = multiButtonPadSelect.createControllerAction("right-padcenter-pressed")    
                                   
        teleport = vrDeviceService.getInteraction("Teleport")
        teleport.addSupportedInteractionGroup("SelectGroup")
        teleport.setControllerActionMapping("prepare" , "left-touchpad-touched")
        teleport.setControllerActionMapping("abort" , "left-touchpad-untouched")
        teleport.setControllerActionMapping("execute" , "left-touchpad-pressed")
        
        self.pointer = vrDeviceService.getInteraction("Pointer")
        self.pointer.addSupportedInteractionGroup("SelectGroup")
        
        self.triggerRightPressedSelect = multiButtonPadSelect.createControllerAction("right-trigger-pressed")
        self.triggerRightReleasedSelect = multiButtonPadSelect.createControllerAction("right-trigger-released")
        
   
    def createMenu(self):
        
        myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath =  myDocuments +"\Autodesk\Automotive\VRED"
        filename = "\objectSelectOn.png"
        icon = QtGui.QIcon()
        icon.addFile(filepath+filename,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.On)
        myDocuments_second = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath_second =  myDocuments_second +"\Autodesk\Automotive\VRED"
        filename_second = "\objectSelectOff.png"
        icon.addFile(filepath_second+filename_second,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
        self.tool = vrImmersiveUiService.createTool("Tool_select")
        self.tool.setText("Select Object")
        self.tool.setCheckable(True)
        self.tool.setIcon(icon)
        self.tool.signal().checked.connect(self.selectEnable)
        self.tool.signal().unchecked.connect(self.selectDisable)
    
    def selectEnable(self):
        global selectControllerFound
        global plane
        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName() and tool.getName()[:5] == 'Tool_':
                tool.setChecked(False)
                tool.signal().unchecked.emit(None)
        self.isEnabled = True
        print("Select Enabled")
        
        vrDeviceService.setActiveInteractionGroup("SelectGroup")
        self.triggerRightPressedSelect.signal().triggered.connect(self.triggerPressedSelect)
        self.triggerRightReleasedSelect.signal().triggered.connect(self.triggerreleasedSelect) 

        self.leftUpperAction.signal().triggered.connect(self.selectButtonLeft)
        self.leftDownAction.signal().triggered.connect(self.leftdown)
        self.upAction.signal().triggered.connect(self.selectButtonUp)
        self.downAction.signal().triggered.connect(self.selectButtonDown)
        self.rightUpperAction.signal().triggered.connect(self.selectButtonRight)
        self.rightDownAction.signal().triggered.connect(self.rightdown)
        self.centerAction.signal().triggered.connect(self.middleMenu)


        '''
        self.leftActionSelect.signal().triggered.connect(self.selectButtonLeft)
        self.upActionSelect.signal().triggered.connect(self.selectButtonUp)
        self.downActionSelect.signal().triggered.connect(self.selectButtonDown)
        self.rightActionSelect.signal().triggered.connect(self.selectButtonRight)
        self.centerActionSelect.signal().triggered.connect(self.middleMenu)
        '''
        
        if selectControllerFound == True:
            self.newRightCon = findNode("VRController_Select")
            self.rightController.setVisible(0)
            self.newRightCon.setActive(1)
            controllerPos = getTransformNodeTranslation(self.rightController.getNode(),1)
            setTransformNodeTranslation(self.newRightCon, controllerPos.x(), controllerPos.y(), controllerPos.z(), True)
            self.SelectControllerConstraint = vrConstraintService.createParentConstraint([self.rightController.getNode()], self.newRightCon, False)
            menuSwitchingNode = findNode('Icons_Select_Switch_Menu')
            if not self.extraFucntions:
                menuSwitchingNode.fields().setInt32("choice",0)
            else:
                menuSwitchingNode.fields().setInt32("choice",1)
        else:
            self.rightController.setVisible(1)
   
        self.selectObjectRayMode()    
        self.timer.setActive(1)
        self.timer.connect(self.htmlPos)
        plane.setActive(1)
        

        
    def selectDisable(self):
        global inpectText
        global selectControllerFound
        if self.isEnabled == False:
            print("select was not enabled before " )
            return
        
        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName():
                tool.setCheckable(True)
        print("Select Disabled")
        self.isEnabled = False
        
        inpectText = ""
        self.tag = None
        self.ourPrintFunction(inpectText)
        self.timer.setActive(0)
        
        self.leftUpperAction.signal().triggered.disconnect(self.selectButtonLeft)
        self.leftDownAction.signal().triggered.disconnect(self.leftdown)
        self.upAction.signal().triggered.disconnect(self.selectButtonUp)
        self.downAction.signal().triggered.disconnect(self.selectButtonDown)
        self.rightUpperAction.signal().triggered.disconnect(self.selectButtonRight)
        self.rightDownAction.signal().triggered.disconnect(self.rightdown)
        self.centerAction.signal().triggered.disconnect(self.middleMenu)
        
        '''
        self.leftActionSelect.signal().triggered.disconnect(self.selectButtonLeft)
        self.upActionSelect.signal().triggered.disconnect(self.selectButtonUp)
        self.downActionSelect.signal().triggered.disconnect(self.selectButtonDown)
        self.rightActionSelect.signal().triggered.disconnect(self.selectButtonRight)
        self.centerActionSelect.signal().triggered.disconnect(self.middleMenu)
        '''
        
        self.triggerRightPressedSelect.signal().triggered.disconnect(self.triggerPressedSelect)
        self.triggerRightReleasedSelect.signal().triggered.disconnect(self.triggerreleasedSelect)
        vrDeviceService.setActiveInteractionGroup("Locomotion")
        self.neutralRayMode()

        deselectAll()
        setWireframeSelection(0)
        vrSessionService.sendPython('deselectAll()')
        vrSessionService.sendPython('setWireframeSelection(0)')
        plane.setActive(0)
        self.rightController.setVisible(1)
        if selectControllerFound == True: 
            self.newRightCon.setActive(0)
            vrConstraintService.deleteConstraint(self.SelectControllerConstraint)
        constraints = vrConstraintService.getConstraints()
        for constraint in constraints:
            vrConstraintService.deleteConstraint(constraint)   
    def leftdown(self):
        print("left down pressed")
    
    def rightdown(self):
        print("rightdown pressed")
                
    def htmlPos(self):
        
        controllerRot = getTransformNodeRotation(self.rightController.getNode())
        controllerTrans = getTransformNodeTranslation(self.rightController.getNode(),1)
        group = findNode("Group_html")
        setTransformNodeTranslation(group, 0, 0, 1, 0)
        self.groupConst = vrConstraintService.createParentConstraint([self.rightController.getNode()], group, False)
        
        
    def triggerPressedSelect(self):
        
        self.intersectionRay = self.rightController.pick()
        self.hitNode = self.intersectionRay.getNode()
        
        if self.hitNode.getName() != "VRMenuPanel":
            if type(self.hitNode) == 'vrdNode':
                self.hitNode = toNode(self.hitNode.getObjectId())
                selectNode(self.hitNode,1)
                setWireframeSelection(1)
                
                #nameString = "%s" % self.hitNode.getName()
                #vrSessionService.sendPython('selectNode("'+nameString+'",1)')
                #vrSessionService.sendPython('setWireframeSelection(1)')
                
            else:
                #self.hitNodeID = getNodeID(self.hitNode.getName())
                #self.hitNode = vrNodeService.getNodeFromId(self.hitNode.getID())
                
                selectNode(self.hitNode,1)
                setWireframeSelection(1)
                
                mypath = getUniquePath(getSelectedNode())
                nameString = "%s" %mypath
                vrSessionService.sendPython('"'+nameString+'"')
                vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                
                #nameString = "%s" % self.hitNode.getName()
                #vrSessionService.sendPython('selectNode("'+nameString+'",1)')
                vrSessionService.sendPython('setWireframeSelection(1)')
                
        self.updateHTMLText()       
 
    def triggerreleasedSelect(self):
        
        if self.hitNode.getName() != "VRMenuPanel" or self.hitNode != None:
            print(self.hitNode.getName())
    
    
    def middleMenu(self):
        
        menuSwitchingNode = findNode('Icons_Select_Switch_Menu')
        
        if not self.extraFucntions:
            menuSwitchingNode.fields().setInt32("choice",1)
            self.extraFucntions = True
            
        else:
            menuSwitchingNode.fields().setInt32("choice",0)
            self.extraFucntions = False
            #make new flag here for new controller allocations
      
        
    def addNodeTag(self):
        
        
        if hasNodeTag(getSelectedNode(), 'Movable'):
            removeNodeTag(getSelectedNode(), 'Movable')
            #self.tag = "Selected Object is NOT 'Movable':  "+getSelectedNode().getName()
        else:
            addNodeTag(getSelectedNode(), 'Movable')
            #self.tag = "Selected Object is 'Movable' :"+getSelectedNode().getName()
        self.updateHTMLText()  

    def selectButtonUp(self):
        print("up pressed")
        if not self.extraFucntions == True:
            currentNode = getSelectedNode()
            parentnode = currentNode.getParent()
            parentnodeName = parentnode.getName()
            if not parentnodeName == "Root":
                selectParent()
                #vrSessionService.sendPython('selectParent()')

                #selectNode(parentnode,1)
                #print(getSelectedNode.getName())
                mypath = getUniquePath(getSelectedNode())
                nameString = "%s" %mypath
                vrSessionService.sendPython('"'+nameString+'"')
                vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                
                #currentnode = getSelectedNode()
                #nameString = "%s" % currentnode.getName()
                #vrSessionService.sendPython('selectNode("'+nameString+'",1)')

                self.multipleSelected = True
        else:
            self.addNodeTag()
        
        self.updateHTMLText()  
            
    def selectButtonDown(self):
        print('Down button pressed')
        if not self.extraFucntions == True:
            checkChildren = getSelectedNode().getNChildren()
            if checkChildren >=1:
                child = getSelectedNode().getChild(0)
                selectNode(child)
                
                mypath = getUniquePath(getSelectedNode())
                nameString = "%s" %mypath
                vrSessionService.sendPython('"'+nameString+'"')
                vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                #nameString = "%s" % child.getName()
                #vrSessionService.sendPython('selectNode("'+nameString+'",1)')
            else:
                child = getSelectedNode()
                selectNode(child)
                
                mypath = getUniquePath(getSelectedNode())
                nameString = "%s" %mypath
                vrSessionService.sendPython('"'+nameString+'"')
                vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                #nameString = "%s" % child.getName()
                #vrSessionService.sendPython('selectNode("'+nameString+'",1)')

        else:
            self.toggleVisibility()
            
        self.updateHTMLText()   
       
    def selectButtonLeft(self):
        print('Left pressed')
        if not self.extraFucntions == True:
            currentNode = getSelectedNode()
            currentNodename = currentNode.getName()
            parent = currentNode.getParent()
            
            
            for i in range(parent.getNChildren()):
                newNodeName = parent.getChild(i).getName()
                if newNodeName == currentNodename:
                    if i == 0:
                        selectNode(getSelectedNode())
                        mypath = getUniquePath(getSelectedNode())
                        nameString = "%s" %mypath
                        vrSessionService.sendPython('"'+nameString+'"')
                        vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                        #vrSessionService.sendPython('selectNode(getSelectedNode())')
                    else:                
                        brother = parent.getChild(i-1)
                        selectNode(brother)
                        
                        mypath = getUniquePath(getSelectedNode())
                        nameString = "%s" %mypath
                        vrSessionService.sendPython('"'+nameString+'"')
                        vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                        #nameString = "%s" % brother.getName()
                        #vrSessionService.sendPython('selectNode("'+nameString+'",1)')
                        
                    break
        
        self.updateHTMLText()  
        
    def selectButtonRight(self):
        print('Right pressed')
        if not self.extraFucntions == True:
            currentNode = getSelectedNode()
            currentNodename = currentNode.getName()
            parent = currentNode.getParent()
            
            lst = list(range(parent.getNChildren()))
            #print(lst)
            for i in range(parent.getNChildren()):
                newNodeName = parent.getChild(i).getName()
                if newNodeName == currentNodename:
                    if i+1 == len(lst):
                        selectNode(getSelectedNode())
                        
                        mypath = getUniquePath(getSelectedNode())
                        nameString = "%s" %mypath
                        vrSessionService.sendPython('"'+nameString+'"')
                        vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                        #vrSessionService.sendPython('selectNode(getSelectedNode())')
                    else:            
                        sister = parent.getChild(i+1)
                        selectNode(sister)
                        
                        mypath = getUniquePath(getSelectedNode())
                        nameString = "%s" %mypath
                        vrSessionService.sendPython('"'+nameString+'"')
                        vrSessionService.sendPython('selectNode(findUniquePath("'+nameString+'"))')
                        #nameString = "%s" % sister.getName()
                        #vrSessionService.sendPython('selectNode("'+nameString+'",1)')                        
                        
                    break    
        
        self.updateHTMLText()  
             
    def toggleVisibility(self):
   
        checkVisibility = getSelectedNode().getActive()
        if checkVisibility == True:
            getSelectedNode().setActive(0)
            mypath = getUniquePath(getSelectedNode())
            nameString = "%s" %mypath
            vrSessionService.sendPython('"'+nameString+'"')
            vrSessionService.sendPython('findUniquePath("'+nameString+'").setActive(0)')
            setSwitchMaterialChoice("C_S_Icon_Visible", 1)
        else:
            getSelectedNode().setActive(1)
            mypath = getUniquePath(getSelectedNode())
            nameString = "%s" %mypath
            vrSessionService.sendPython('"'+nameString+'"')
            vrSessionService.sendPython('findUniquePath("'+nameString+'").setActive(1)')
            setSwitchMaterialChoice("C_S_Icon_Visible", 0)
    def selectObjectRayMode(self):
        
        print("selectObjectRayMode")
        self.pointer.setControllerActionMapping("prepare" , "right-customtrigger-touched")
        self.pointer.setControllerActionMapping("abort" , "disable") # Hack: Override the input with an unknown input
        self.pointer.setControllerActionMapping("start" , "right-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "right-customtrigger-released")
        
    def neutralRayMode(self):
        
        self.pointer.setControllerActionMapping("prepare" , "any-customtrigger-touched")
        self.pointer.setControllerActionMapping("abort" , "any-customtrigger-untouched")
        self.pointer.setControllerActionMapping("start" , "any-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "any-customtrigger-released") 
    
    def updateHTMLText(self):
        global inpectText

        del self.parentList[:]
        interPos = getTransformNodeTranslation(self.rightController.getNode(),1)
        if self.multipleSelected == True:
            interObj = getSelectedNode()

        else:
            interObj = getSelectedNode()
            
        if interObj.isValid(): 
            nodename = interObj.getName()
            parentnode = interObj.getParent()
            parentnodeName = parentnode.getName()
            inpectText = ""
            firstParentName = parentnodeName
            
            while parentnodeName != "Root":
                parentnode =  parentnode.getParent()
                parentnodeName = parentnode.getName()
                self.parentList.append(parentnodeName)
            
            for i in range(len(self.parentList)-1,-1,-1):
                inpectText = inpectText +str(self.parentList[i])+"<br>"
            inpectText = "Nodename: "+"<br>"+nodename+"<br><br>"+"Parent Nodes: "+"<br>"+inpectText
            inpectText = inpectText+firstParentName+ "<br><br>"
            if hasNodeTag(getSelectedNode(), 'Movable'):
                tagStatus = "Selected Object is 'Movable'"
                inpectText = inpectText+ "<br><br>"+"Tag Status: "+"<br>"+tagStatus
            else:
                tagStatus = "Selected Object is NOT 'Movable'"
                inpectText = inpectText+ "<br><br>"+"Tag Status: "+"<br>"+tagStatus
                    
            if self.tag != None:
                inpectText = inpectText+ "<br><br>"+"Tag: "+"<br>"+self.tag
                
            self.ourPrintFunction(inpectText)
    
#--------------------------------------------------------------HTML declaration----------------------------------------------------------------------------
    '''
    # The HTML declaration section 
    The HTML file indexes it's lines starting from 1. But, python starts it's indexing from 0.
    The function replace_line() accesses the HTML file and reads all of the lines into a list. 
    For ex. line number 5 in HTML would be index number 4 in the list. 
    html_init_line specifies the line number from where all of the Voice recognition terminal outputs are saved.
    We print total of 4 concurrent outputs together hence 4 lines after html_init_line are reserved for this purpose.
    '''
                        
    def init_html(self):
        global filename_html
        global html_init_line
        init_text = ["<h2> <font color='#AAAAAA'> Welcome to your python based <br> VRED-AUTO-Terminal <br> We provide terminal outputs in VR <br> to improve your VR Experience <br> </font></h2>"]
                     
        self.replace_line(filename_html, html_init_line, init_text)
    
    def replace_line(self,file_name, line_num, text): 
    
        f = open(file_name, 'r')
        lines = f.readlines()
        f.close()
        start = line_num
        end = line_num+len(text)
        lines[start:end] = text
        out = open(file_name, 'w')
        out.close()
        out = open(file_name, 'a')
        for line in lines:
            out.writelines(line)
        out.close()

    def ourPrintFunction(self,text):
        global myArray
        global html_init_line
        global filename_html
        
        buildLine2 = "<h2> <font color='#AAAAAA'>" +str(text)+   "</font></h2> \n"
        myArray = [buildLine2]
        self.replace_line(filename_html, html_init_line, myArray)
             
       
select = SelectObject()
vrDeviceService.setActiveInteractionGroup("Locomotion")
