'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.

Scripted by Simon Nagel, supported by Rutvik Bhatt

First download and copy paste the "VRControllerDraw.osb" file provided in the GitHub repository into "C:\Users\USERNAME\Documents\Autodesk\Automotive\VRED" path in order to use the dedicated draw controller.
If you do not wish to use the dedicated controller you can skip this part. 

Just paste the Scene in the Script Editor of VRED and press run.
Press D to enable drawing 
    You will see a pencil, as an indicator, that drawing is active.
    Draw while keeping the left mouse button pressed and move your mouse cursor.
    You will draw directly on the geometry and create a "line" geometry per stroke.
Press D again to disable drawing 
Press L to remove the last line 
Press G to remove all the lines

VR Instructions:
    
Turn on OpenVR and press the menu button.
Press the 'Draw' tools menu in the menu. 
    You will see a pointy edge on the top of the right controller.
    Press the right trigger on the controller to draw anywhere you desire.
Press Center Touch Pad button on the right controller to change the mode of drawing
    1. First draw mode is the default mode where you can draw from the top edge of the controller 
    2. Second draw mode is the draw on ray mode, The ray will be visible constantly and by pressing the right trigger you can draw at the end of the ray on any Geometry
Press the Down Touch Pad button to hide all the drawing that you have made 
Press the Left Touch Pad button to delete the last line  


This script works in VRED Collaboration.
Please make sure that, the Script is executed on each computer of each participant.

'''

import math
import ctypes
from math import sqrt
import random
from random import randint
import PySide2.QtGui
from datetime import datetime
QColor = PySide2.QtGui.QColor

#------Defining Controller------
leftController = vrDeviceService.getVRDevice("left-controller")
rightController = vrDeviceService.getVRDevice("right-controller")
leftController.setVisualizationMode(Visualization_ControllerAndHand)
rightController.setVisualizationMode(Visualization_ControllerAndHand)

#---------Global variables and Flags---------
drawVREnable = False
triggerisPressed = False
desktopMode = True
drawOnController = True
linesVisible = False
menuOpened = False
drawControllerFound = False
timer = vrTimer()

global lefclick, rightclick

leftclick = 0x01
rightclick = 0x02

class RenderAction(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
    def loop(self):
        if self.isActive():
            drawDesktop()
render = RenderAction()


count = 0 
mouse = getMousePosition(-1)
cam = getActiveCameraNode()
cam = findNode("Perspective")
root = findNode("Root")

#----------------------------------Checking and Loading Nodes and Controllers------------------------------

all_nodes = getAllNodes()
dTool_count = 0
dLine_count = 0
dTemp_count = 0
drawController = 0
for i in all_nodes:
    nodeName = i.getName()
    if nodeName == "D_Tool":
        dTool_count+=1
        drawTool = i
    elif nodeName == "D_Lines":
        dLine_count+=1
        lineGrp = i
    elif nodeName == "D_tempLine":
        dTemp_count+=1
    elif nodeName == "VRController_Draw":
        drawController+=1

        
if dTool_count ==0:
    drawTool = createNode("Transform3D", "D_Tool")
    d_child = createCone(50.0, 10.0, 16, 1, 1, 1.0, 0.0, 0.0)
    d_child2 = createCylinder(150.0, 10.0, 16, 1, 1,1, 0.5, 0.5, 0.5)
    d_child.setRotation(-90,0,0)
    d_child2.setRotation(-90,0,0)
    d_child.setTranslation(0,0,25)
    d_child2.setTranslation(0,0,125)
    d_child.setName("D_PencipTop")
    drawTool.addChild(d_child)
    drawTool.addChild(d_child2)

if dLine_count == 0:
    lineGrp = createNode("Group","D_Lines")

if dTemp_count == 0:
    dTemp_line = createLine(0,0,0,0,0,1,1,0,0)
    dTemp_line.setName("D_tempLine")
    mat = createMaterial("UPlasticMaterial")
    mat.setName("_d_line_material")
    pChunk = createChunk("LineChunk")
    mat.addChunk(pChunk)
    #mat.fields().setReal32("tubeRadius", 5)
    mat.fields().setVec4f("incandescenceColor",1, 0, 0,1)
    mat.fields().setVec3f("diffuseColor",0, 0, 0)
    mat.fields().setVec3f("specularColor",0, 0, 0)
    pChunk.fields().setReal32("width",5)
    pChunk.fields().setBool("smooth",True)
    container1 = vrFieldAccess(mat.fields().getFieldContainer("colorComponentData"))
    container1.setReal32("tubeRadius", 2)   
    dTemp_line.setMaterial(mat)
    
if drawController == 0:
    #vrFileIO.loadOSB(["C:\Users\Rutvi\Documents\Autodesk\Automotive\VRED\VRControllerDraw.osb"])
    import os
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents')
    filepath = myDocuments +"\Autodesk\Automotive\VRED"
    filename = "\VRControllerDraw"
    if os.path.exists(filepath+str(filename)+".osb"):
        node = loadGeometry(filepath+str(filename)+".osb")
        node.setName("VRControllerDraw") 
        drawControllerFound = True
    else:
        print("file doesnt exist")
        drawControllerFound = False

if drawControllerFound == True:
    drawControllerTool = findNode("VRController_Draw")
    drawControllerTool.setActive(0)
else:
    drawControllerTool = rightController.getNode()
    drawControllerTool = toNode(drawControllerTool.getObjectId())
    

#-------------------Synchronizing the materials----------------------     
def syncCollabDrawMaterials():
    allUsers = vrSessionService.getUsers()
    amountAllUsers = len(allUsers)
    localUser = vrSessionService.getUser()
    localUserID = vrdSessionUser.getUserId(localUser)
    localUserColor = vrdSessionUser.getUserColor(localUser)
    
    lineMats = findMaterials("_d_line_material_",1)
    amountLineMats = len(lineMats)
    
    for i in range(0,amountAllUsers):
        userID = vrdSessionUser.getUserId(allUsers[i])
        userColor = vrdSessionUser.getUserColor(allUsers[i])
        matExists = 0
        
        for i in range(0,amountLineMats):
            lineMat = lineMats[i].getName() 
            
            #extract number from string
            matID = int(''.join(filter(str.isdigit, lineMat))) 
            if matID == userID:
                matExists = 1
        if matExists == 0:    

            newMat = createMaterial("UPlasticMaterial")
            newMat.setName("_d_line_material_"+str(userID))
            newChunk = createChunk("LineChunk")
            newMat.addChunk(newChunk)            
            newMat.fields().setVec3f("diffuseColor",0, 0, 0)
            newMat.fields().setVec3f("specularColor",0, 0, 0)
            newChunk.fields().setReal32("width",5)
            newChunk.fields().setBool("smooth",True)
            newContainer1 = vrFieldAccess(newMat.fields().getFieldContainer("colorComponentData"))
            newContainer1.setReal32("tubeRadius", 2)   
        findMaterial("_d_line_material_"+str(userID)).fields().setVec4f("incandescenceColor",userColor.redF(), userColor.greenF(), userColor.blueF(),1)
    findMaterial("_d_line_material").fields().setVec4f("incandescenceColor",localUserColor.redF(), localUserColor.greenF(), localUserColor.blueF(),1)
            
    del allUsers[:]
    del lineMats[:]
    
    #updateMaterials()

#-----------------Defining all the key pressed events-------------
Dkey_count = 0
key_D = vrKey(Key_D)
key_D.connect("keypressed()")


def keypressed():
    global Dkey_count
    global drawVREnable
    global rightController
    global d_child
    global d_childConstr
    global timer
    if Dkey_count == 0:
        count = 0
        enableScenegraph(0)
        render.setActive(1)
        drawTool.setActive(1)
        setAllNavigationsEnabled(0)
        Dkey_count +=1
    else:
        Dkey_count = 0
        enableScenegraph(1)
        updateScenegraph(True)
        render.setActive(0)
        drawTool.setActive(0)
        setAllNavigationsEnabled(1)
       
        
key_L = vrKey(Key_L)
key_L.connect("lastLine()")

def lastLine():
    
    print("Last line deleted")
    #deleteNode(list[-1],1)
    vrSessionService.sendPython('lineGrp = findNode("D_Lines")')
    vrSessionService.sendPython('linegrp_VRDObject = vrNodeService.getNodeFromId(lineGrp.getID())')
    vrSessionService.sendPython('amountChildren = linegrp_VRDObject.getChildren()')
    vrSessionService.sendPython('deleteNode(amountChildren[-1],1)')
    #deleteNode(amountChildren[-1],1)

key_G = vrKey(Key_G)
key_G.connect("toggleLines()")

def toggleLines():
    global lineGrp
    global linesVisible
    print("Pressed G and Toggled Visibiltiy of All Lines")
    vrSessionService.sendPython('lineGrp = findNode("D_Lines")')
    if linesVisible == False:
        linesVisible = True
        vrSessionService.sendPython('lineGrp.setActive(0)')
        setSwitchMaterialChoice("C_D_Icon_Visible", 1)
        
    else:
        linesVisible = False
        vrSessionService.sendPython('lineGrp.setActive(1)')
        setSwitchMaterialChoice("C_D_Icon_Visible", 0)
        
l_child = findNode("D_tempLine")  
choiceState = 0

oldX = 0
oldY = 0
oldZ = 0

listPos = []
del listPos[:]

leftclickpressed = False

timerMatCollabDrawUpdate = vrTimer()
timerMatCollabDrawUpdate.connect(syncCollabDrawMaterials)
localUser = vrSessionService.getUser()
localUserID = vrdSessionUser.getUserId(localUser)
timerMatCollabDrawUpdate.setActive(1)

#----------------------The main function used in both the modes 'Desktop Draw' and 'VR Draw'------------------------
def drawDesktop():

    global oldX
    global oldY
    global oldZ
    global listPos
    global cam
    global drawTool
    global count
    global Dkey_count
    global node
    global root
    global lineGrp
    global l_child
    global leftclickpressed
    global localUserID
    global drawVREnable
    global triggerisPressed
    global rightController
    global desktopMode
    global drawOnController
    global drawToolConstr
    global drawControllerTool
    global hitNode
    global draw
    global menuOpened
    global drawControllerFound
    mousePos = getMousePosition(-1)
    

    if desktopMode == True:
        
        drawTool.setActive(0)
        lineGrp.setActive(0)
        l_child.setActive(0)
        intersection =getSceneIntersection(-1,mousePos[0],mousePos[1])
        drawTool.setActive(1)
        lineGrp.setActive(1)
        l_child.setActive(1)
        interPos = intersection[1]
        interObj = intersection[0]
        interDir = intersection[2]
        camPos = cam.getTranslation()
        mat = interObj.getMaterial()
        drawTool.setTranslation(interPos.x(),interPos.y(),interPos.z())

    if drawVREnable == True:
        intersectionRay = rightController.pick()
        hitNode = intersectionRay.getNode()
        if hitNode.getName() == "VRMenuPanel" and menuOpened == False:
            draw.neutral()
            menuOpened = True
        elif hitNode.getName() != "VRMenuPanel" and menuOpened == True:
            draw.defaultMappings()
            menuOpened = False
            
        if drawOnController == False:
            intersection = rightController.pick()
            hitpoint = intersection.getPoint()
            interPos = Pnt3f(hitpoint.x(),hitpoint.y(),hitpoint.z())    
        else:
            contPos = getTransformNodeTranslation(drawControllerTool, 1)
            interPos = contPos
         
    x = interPos.x()
    y = interPos.y()
    z = interPos.z()
    pos = [interPos.x(),interPos.y(),interPos.z()]
    listPos.append(pos)


    oldPos = [oldX,oldY,oldZ]
    distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(oldPos, pos)]))
    oldX = x
    oldY = y
    oldZ = z
        
    count = count +1
    if (mousePos[0] !=-1 and desktopMode == True)  or (drawVREnable == True):
        if (ctypes.windll.user32.GetKeyState(leftclick) > 1 and desktopMode == True)  or (triggerisPressed == True and hitNode.getName() !="VRMenuPanel"):              #ctypes.windll.user32.GetKeyState(leftclick) > 1:     # D button is presse
            leftclickpressed = True
            if count ==1:
                node = l_child
                leContain = vrFieldAccess(node.fields().getFieldContainer("lengths")) 
                leContain.setMUInt32("lengths",[1])
                inContain = vrFieldAccess(node.fields().getFieldContainer("indices")) 
                inContain.setMUInt32("indices",[0,1])
                positions = []
                positions.append(x)
                positions.append(y)
                positions.append(z)
                positions.append(x)
                positions.append(y)
                positions.append(z)
                node.setPositions(positions)
            else:
                if distance < 100:

                    leContain = vrFieldAccess(node.fields().getFieldContainer("lengths"))    
                    lengthsList = leContain.getMUInt32("lengths")
                    lengths = lengthsList[0]
                
                    inContain = vrFieldAccess(node.fields().getFieldContainer("indices"))   
                    indicesList = inContain.getMUInt32("indices")
                    indices0 = indicesList[-2]
                    indices1 = indicesList[-1]
                
                    positions = node.getPositions()
                    newLengths = lengths + 2 
                    newIndices0 = indices1
                    newIndices1 = indices1+1
                    indicesList.append(newIndices0)
                    indicesList.append(newIndices1)
                    
                    positions.append(x)
                    positions.append(y)
                    positions.append(z)
            
                    leContain.setMUInt32("lengths",[newLengths])                
                    inContain.setMUInt32("indices",indicesList)
                    node.setPositions(positions)

        else:
            if leftclickpressed == True:
                leftclickpressed = False
                leContain = vrFieldAccess(node.fields().getFieldContainer("lengths"))    
                lengthsList = leContain.getMUInt32("lengths")
                lengths = lengthsList[0]
                
                inContain = vrFieldAccess(node.fields().getFieldContainer("indices"))   
                indicesList = inContain.getMUInt32("indices")
                
                positions = node.getPositions()
                
                valueNewLength = "%d" %lengths
                valueIndicesList = "%s" %indicesList
                valuePosition = "%s" %positions
                if vrSessionService.isConnected() == 1:
                    localUser = vrSessionService.getUser()
                    localUserID = vrdSessionUser.getUserId(localUser)
                    newMatName = "_d_line_material_"+str(localUserID)
                else:
                    newMatName = "_d_line_material_"
                valueLocalId = "%s" %newMatName
                

                localUser = vrSessionService.getUser()
                userName = vrdSessionUser.getUserName(localUser)
                #randomNumber = randint(10000,100000)
                now = datetime.now()
                dt_string = now.strftime("%y%m%d_%H%M%S")
                
                newRandomNumber = "%s" %dt_string
                newName = userName
                newNodeName = "%s" %newName
                #vrSessionService.sendPython('print("starting clonning")')
                #clnode = cloneNode(node, 1)
                vrSessionService.sendPython('clnode = cloneNode(l_child, 1)')
                vrSessionService.sendPython('clnode.setName("'+newRandomNumber+'_Line_by_'+newNodeName+'")')
                #moveNode(clnode, root, lineGrp)
                vrSessionService.sendPython('deselectAll()')
                vrSessionService.sendPython('moveNode(clnode, root ,lineGrp)')
                vrSessionService.sendPython('vrFieldAccess(clnode.fields().getFieldContainer("lengths")).setMUInt32("lengths",['+valueNewLength+'])')               
                vrSessionService.sendPython('vrFieldAccess(clnode.fields().getFieldContainer("indices")).setMUInt32("indices",'+valueIndicesList+')')
                vrSessionService.sendPython('clnode.setPositions('+valuePosition+')')
                if vrSessionService.isConnected() == 1:
                    vrSessionService.sendPython('clnode.setMaterial(findMaterial("'+valueLocalId+'"))')
                
                leContain = vrFieldAccess(node.fields().getFieldContainer("lengths")) 
                leContain.setMUInt32("lengths",[1])
                inContain = vrFieldAccess(node.fields().getFieldContainer("indices")) 
                inContain.setMUInt32("indices",[0,1])
                node.setPositions([0,0,0,0,0,1])

            count = 0
vrLogInfo("Hello Welcome to Drawing\n Press D to enable drawing \n Press D again to disable drawing \n Press L to remove the last line \n Press G to remove all the lines")

findNode("D_PencipTop").setMaterial(findMaterial("_d_line_material"))
findNode("D_tempLine").setMaterial(findMaterial("_d_line_material"))

#vrSessionService.join("localhost")

#------------------------------Defining a Class for drawing in VR--------------------------------------------

class DrawinVR():
    def __init__(self):
        global drawVREnable
        global drawTriggerEnable
        global timer
        global triggerisPressed
        global drawTool
        
        self.isPointingRayActive = True
        self.createMenu()         
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")
        self.leftController.setVisualizationMode(Visualization_ControllerAndHand)
        self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        vrImmersiveInteractionService.setDefaultInteractionsActive(1)
        
        padCenterDraw = vrdVirtualTouchpadButton('padcenter', 0.0, 0.6, 0.0, 360.0)
        padLeftDraw = vrdVirtualTouchpadButton('padleft', 0.5, 1.0, 225.0, 315.0)
        padUpDraw = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 315.0, 45.0)
        padRightDraw = vrdVirtualTouchpadButton('padright', 0.5, 1.0, 45.0, 135.0)
        padDownDraw = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 135.0, 225.0)

        # right controller
        self.rightController.addVirtualButton(padCenterDraw, 'touchpad')
        self.rightController.addVirtualButton(padLeftDraw, 'touchpad')
        self.rightController.addVirtualButton(padUpDraw, 'touchpad')
        self.rightController.addVirtualButton(padRightDraw, 'touchpad')
        self.rightController.addVirtualButton(padDownDraw, 'touchpad')
        
        multiButtonPadDraw = vrDeviceService.createInteraction("MultiButtonPadDraw")
        multiButtonPadDraw.setSupportedInteractionGroups(["DrawGroup"])
        toolsMenuDraw = vrDeviceService.getInteraction("Tools Menu")
        toolsMenuDraw.addSupportedInteractionGroup("DrawGroup")   
        #setting control action for right controller Pad
        
        self.leftActionDraw = multiButtonPadDraw.createControllerAction("right-padleft-pressed")
        self.upActionDraw = multiButtonPadDraw.createControllerAction("right-padup-pressed")
        self.downActionDraw = multiButtonPadDraw.createControllerAction("right-paddown-pressed")
        self.rightActionDraw = multiButtonPadDraw.createControllerAction("right-padright-pressed")
        self.centerActionDraw = multiButtonPadDraw.createControllerAction("right-padcenter-pressed")
        

            
        teleportDraw = vrDeviceService.getInteraction("Teleport")
        teleportDraw.addSupportedInteractionGroup("DrawGroup") 
        teleportDraw.setControllerActionMapping("prepare" , "left-touchpad-touched")
        teleportDraw.setControllerActionMapping("abort" , "left-touchpad-untouched")
        teleportDraw.setControllerActionMapping("execute" , "left-touchpad-pressed")
        
        self.pointer = vrDeviceService.getInteraction("Pointer")
        self.pointer.addSupportedInteractionGroup("DrawGroup")
        
        self.triggerRightPressedDraw = multiButtonPadDraw.createControllerAction("right-trigger-pressed")
        self.triggerRightReleasedDraw = multiButtonPadDraw.createControllerAction("right-trigger-released")


           
    def createMenu(self):
        
        self.tool = vrImmersiveUiService.createTool("Draw")
        self.tool.setText("Draw")
        self.tool.setCheckable(True)
        #self.tool.setIcon(icon)
        self.tool.signal().checked.connect(self.drawEnable)
        self.tool.signal().unchecked.connect(self.drawDisable)
    
    def drawEnable(self):
        global drawVREnable
        global drawTriggerEnable
        global drawTool
        global drawControllerTool
        global desktopMode
        global drawOnController
        global drawControllerFound
        
        desktopMode = False
        drawVREnable = True
        
        vrDeviceService.setActiveInteractionGroup("DrawGroup")
        
        self.leftActionDraw.signal().triggered.connect(lastLine)
        #self.upActionDraw.signal().triggered.connect(self.)
        self.downActionDraw.signal().triggered.connect(toggleLines)
        #self.rightActionDraw.signal().triggered.connect(toggleLines)
        self.centerActionDraw.signal().triggered.connect(self.changeViewDraw)
        
        
        if drawControllerFound == True:
            self.rightController.setVisible(0)
            self.controllerConstr = vrConstraintService.createParentConstraint([self.rightController.getNode()], drawControllerTool, False)
            drawControllerTool.setActive(1)
        else:
            self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        self.triggerRightPressedDraw.signal().triggered.connect(self.triggerPressedDraw)
        self.triggerRightReleasedDraw.signal().triggered.connect(self.triggerreleasedDraw) 
        
        if drawControllerFound == True: 
            if drawOnController == True:
                self.onControllerDrawMapping()
                setSwitchMaterialChoice("C_D_Icon_Draw", 0)
            else:
                self.onRayDrawMapping()
                setSwitchMaterialChoice("C_D_Icon_Draw", 1)
            
           
        timer.setActive(1)
        timer.connect(drawDesktop)
    
    def triggerPressedDraw(self):
        global triggerisPressed
        triggerisPressed = True
     
    def triggerreleasedDraw(self):
        global triggerisPressed
        triggerisPressed = False   

    def drawDisable(self):
        global drawTool
        global drawVREnable
        global desktopMode
        global drawControllerFound
        
        d_child = drawTool.getChild(0)
        d_child.setActive(True)
        desktopMode = True
        drawVREnable = False
        timer.setActive(0)
        
        self.leftActionDraw.signal().triggered.disconnect(lastLine)
        #self.upActionDraw.signal().triggered.disconnect(self.)
        self.downActionDraw.signal().triggered.disconnect(toggleLines)
        #self.rightActionDraw.signal().triggered.disconnect(toggleLines)
        self.centerActionDraw.signal().triggered.disconnect(self.changeViewDraw)
                
        vrDeviceService.setActiveInteractionGroup("Locomotion")                         
        
        self.triggerRightPressedDraw.signal().triggered.disconnect(self.triggerPressedDraw)
        self.triggerRightReleasedDraw.signal().triggered.disconnect(self.triggerreleasedDraw) 
        
        
        if drawControllerFound == True:
            vrConstraintService.deleteConstraint(self.controllerConstr)
            drawControllerTool.setActive(0)

        self.rightController.setVisible(1)
        self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        
        self.neutral()
        
        constraints = vrConstraintService.getConstraints()
        for constraint in constraints:
            vrConstraintService.deleteConstraint(constraint)
            
    def changeViewDraw(self):
        global drawOnController
        global drawTool
        global drawControllerFound
            
        if drawOnController == False:
            drawOnController = True
            if drawControllerFound == True:
                setSwitchMaterialChoice("C_D_Icon_Draw", 0)
            self.onControllerDrawMapping()

        else:
            drawOnController = False
            if drawControllerFound == True:
                setSwitchMaterialChoice("C_D_Icon_Draw", 1)
            self.onRayDrawMapping()
              
                
    def neutral(self):
        
        self.pointer.setControllerActionMapping("prepare" , "any-customtrigger-touched")
        self.pointer.setControllerActionMapping("abort" , "any-customtrigger-untouched")
        self.pointer.setControllerActionMapping("start" , "any-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "any-customtrigger-released")  

    def onControllerDrawMapping(self):
        
        self.pointer.setControllerActionMapping("prepare" , "disable")
        self.pointer.setControllerActionMapping("abort" , "any-customtrigger-untouched")
        self.pointer.setControllerActionMapping("start" , "any-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "any-customtrigger-released") 
    
    def onRayDrawMapping(self):
        
        self.pointer.setControllerActionMapping("prepare" , "right-customtrigger-touched")
        self.pointer.setControllerActionMapping("abort" , "disable") # Hack: Override the input with an unknown input
        self.pointer.setControllerActionMapping("start" , "right-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "right-customtrigger-released")
            
    def defaultMappings(self):
        
        if drawOnController == True :
            self.onControllerDrawMapping()
        else:
            self.onRayDrawMapping()
                                                       
    def onPointerInteractionAbort(self):
        self.rightController.enableRay("controllerhandle") 
                    
draw = DrawinVR()       
print("Executed")        
