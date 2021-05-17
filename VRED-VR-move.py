'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.

Scripted by Rutvik Bhatt, supported by Simon Nagel

First download and copy the osb file "VRControllerMove" provided in the GitHub repository into "C:\Users\USERNAME\Documents\Autodesk\Automotive\VRED" path in order to use the dedicated Move controller.
If you do not wish to use the dedicated controller you can skip this part. 

Add all the nodes that you want to move in a tag named "Movable".

Just paste the Scene in the Script Editor of VRED and press run.
Turn on the OpenVR and press the menu button on the controller.
Press the 'Move' tools menu in the menu. 
    Press the trigger and point it to the object that you want to move freely, keep the trigger pressed and move the object
    Release the trigger to put the object to the desired place

Press the Left Touch pad button to undo
Press the Right Touch pad button to redo 
Press the Up Touch pad button to reset the scene (Note: The objects will be placed at their original positon) 

This script works in VRED Collaboration.
Please make sure that, the Script is executed on each computer of each participant.
     
'''

import os
import math
from PySide2 import QtCore, QtGui
def roundup(x):
    return int(math.ceil(x / 15.0)) * 15

moveController = 0
moveControllerFound = False
mainCustomFuncGroup = False
allMoveNodes = getAllNodes()
for node in allMoveNodes:
    allMoveNodesName = node.getName()
    if allMoveNodesName == "VRController_Move":
        moveController+=1
    elif allMoveNodesName == 'VRED-VR-Custom-Fucntion':
        mainCustomFuncGroup = True
        customFunctionsGroup = node
        
if moveController == 0:
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename = "\VRControllerMove"
    if os.path.exists(filepath+str(filename)+".osb"):
        node = loadGeometry(filepath +str(filename)+".osb")
        node.setName("VRControllerMove")
        moveControllerFound = True
    else:
        print("file doesnt exist")
        moveControllerFound = False
else:
    moveControllerFound = True

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

class RenderActionMove(vrInteraction):
    
    def __init__(self):
        vrInteraction.__init__(self)
        #ObjectMover.__init__(self)
        
        self.addRender()
    def preRender(self):
        
        move.constraintCheckFunction()
        

class ObjectMover():
    def __init__(self):
        self.isEnabled = False
        #RenderAction.__init__(self)
        self.moverEnabled = False
        self.createMenu()
        self.node = None
        self.undo_list = []
        self.position_list = []
        self.redo_list = []
        self.all_nodes = []
        self.resetflag = False
        nodes = getAllNodes()
        self.last_pos_node = []
        self.startMoveFlag = False
        self.snapping = False
        
        
        self.timer = vrTimer()
        for node in nodes:
            if hasNodeTag(node, 'Movable'):
                node_translation = getTransformNodeTranslation(node, True)
                node_rotation = getTransformNodeRotation(node)
                self.all_nodes.append([node, node_translation, node_rotation])
             
        
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")
        self.leftController.setVisualizationMode(Visualization_ControllerAndHand)
        self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        vrImmersiveInteractionService.setDefaultInteractionsActive(1)

        
        padCenter = vrdVirtualTouchpadButton('padcenter', 0.0, 0.5, 0.0, 360.0)
        padUpperLeft = vrdVirtualTouchpadButton('padupleft', 0.5, 1.0, 270.0, 330.0)
        padLowerLeft = vrdVirtualTouchpadButton('paddownleft', 0.5, 1.0, 210.0, 270.0)
        padUp = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 330.0, 30.0)
        padUpperRight = vrdVirtualTouchpadButton('padupright', 0.5, 1.0, 30.0, 90.0)
        padLowerRight = vrdVirtualTouchpadButton('paddownright', 0.5, 1.0, 90.0, 150.0)
        padDown = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 150.0, 210.0)

        # right controller
        self.rightController.addVirtualButton(padCenter, 'touchpad')
        self.rightController.addVirtualButton(padUpperLeft, 'touchpad')
        self.rightController.addVirtualButton(padLowerLeft, 'touchpad')
        self.rightController.addVirtualButton(padUp, 'touchpad')
        self.rightController.addVirtualButton(padUpperRight, 'touchpad')
        self.rightController.addVirtualButton(padLowerRight, 'touchpad')
        self.rightController.addVirtualButton(padDown, 'touchpad')
        
        multiButtonPadMove = vrDeviceService.createInteraction("MultiButtonPadMove")
        multiButtonPadMove.setSupportedInteractionGroups(["MoveGroup"])
        toolsMenuNotes = vrDeviceService.getInteraction("Tools Menu")
        toolsMenuNotes.addSupportedInteractionGroup("MoveGroup")
        
        #setting control action for right controller Pad
        
        self.leftUpperActionMove = multiButtonPadMove.createControllerAction("right-padupleft-pressed")
        self.leftDownActionMove = multiButtonPadMove.createControllerAction("right-paddownleft-pressed")
        self.upActionMove = multiButtonPadMove.createControllerAction("right-padup-pressed")
        self.downActionMove = multiButtonPadMove.createControllerAction("right-paddown-pressed")
        self.rightUpperActionMove = multiButtonPadMove.createControllerAction("right-padupright-pressed")
        self.rightDownActionMove = multiButtonPadMove.createControllerAction("right-paddownright-pressed")
        self.centerActionMove = multiButtonPadMove.createControllerAction("right-padcenter-pressed")
         
        teleport = vrDeviceService.getInteraction("Teleport")
        teleport.addSupportedInteractionGroup("MoveGroup")
        teleport.setControllerActionMapping("prepare" , "left-touchpad-touched")
        teleport.setControllerActionMapping("abort" , "left-touchpad-untouched")
        teleport.setControllerActionMapping("execute" , "left-touchpad-pressed")
        
        self.pointer = vrDeviceService.getInteraction("Pointer")
        self.pointer.addSupportedInteractionGroup("MoveGroup")
        
    def constraintCheckFunction(self):
        global constXPressed
        global constYPressed
        global constZPressed
        #global startMoveFlag
        global device
        if self.startMoveFlag == True and not self.node == None:
            self.currentNodePos = getTransformNodeTranslation(self.node,1)
            self.currentNodeRot = getTransformNodeRotation(self.node)
            
            if constXPressed == True and constYPressed == True:
                
                x_y_translation = "%f,%f,%f" %(self.currentNodePos.x(), self.currentNodePos.y(),self.originalNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+x_y_translation+', True)')
                
                x_y_rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+x_y_rotation+')')
                
                
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.currentNodePos.x(), self.currentNodePos.y(),self.originalNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constYPressed == True and constZPressed == True:
                
                y_z_translation = "%f,%f,%f" %(self.originalNodePos.x(), self.currentNodePos.y(),self.currentNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+y_z_translation+', True)')

                y_z_rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+y_z_rotation+')')

                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.originalNodePos.x(), self.currentNodePos.y(),self.currentNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constXPressed == True and constZPressed == True:
                
                x_z_translation = "%f,%f,%f" %(self.currentNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+x_z_translation+', True)')
                
                x_z_rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+x_z_rotation+')')

                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.currentNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constXPressed == True:
                
                x_translation = "%f,%f,%f" %(self.currentNodePos.x(), self.originalNodePos.y(),self.originalNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+x_translation+', True)')
                
                x_rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+x_rotation+')')
                

                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.currentNodePos.x(), self.originalNodePos.y(),self.originalNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constYPressed == True:
                
                y_translation = "%f,%f,%f" %(self.originalNodePos.x(), self.currentNodePos.y(),self.originalNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+y_translation+', True)')
                
                y_rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+y_rotation+')')
                
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.originalNodePos.x(), self.currentNodePos.y(),self.originalNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constZPressed == True:
                

                z_translation = "%f,%f,%f" %(self.originalNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+z_translation+', True)')
                
                z_rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+z_rotation+')')
                
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.originalNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif self.snapping == True:

                self.currentNodeRot = getTransformNodeRotation(self.node) 
                self.x = roundup(self.currentNodeRot.x()) 
                self.y = roundup(self.currentNodeRot.y()) 
                self.z = roundup(self.currentNodeRot.z()) 
                snap_rotation = "%f,%f,%f" %(self.x,self.y,self.z)
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+snap_rotation+')')
                self.newRot = setTransformNodeRotation(self.node,self.x,self.y,self.z)  
                translation = "%f,%f,%f" %(self.currentNodePos.x(), self.currentNodePos.y(),self.currentNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+translation+', True)')
                
            else:
                translation = "%f,%f,%f" %(self.currentNodePos.x(), self.currentNodePos.y(),self.currentNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+translation+', True)')
                
                rotation = "%f,%f,%f" %(self.currentNodeRot.x(),self.currentNodeRot.y(),self.currentNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+rotation+')')
                                
        
    def startMove(self,action,device):
        global constXPressed
        global constYPressed
        global constZPressed
        #global startMove
        self.node = self.getMovable(device.pick().getNode())

        if not self.node.isNull():
            self.originalNodeRot = getTransformNodeRotation(self.node)
            if constXPressed == True or constYPressed == True or constZPressed == True:
                #self.snapping = True
                self.constraint = vrConstraintService.createParentConstraint([device.getNode()],self.node,True)
                
                mypath = getUniquePath(self.node)
                nameString = "%s" %mypath
                vrSessionService.sendPython('"'+nameString+'"')
                vrSessionService.sendPython('nodeRef = findUniquePath("'+nameString+'")')
                
                #nameString = "%s" % self.node.getName()
                #vrSessionService.sendPython('nodeRef = findNode("'+nameString+'")')
                
                
            else:  
                self.constraint = vrConstraintService.createParentConstraint([device.getNode()],self.node,True)
                #vrSessionService.addNodeSync(self.node)
                
                
                
            self.originalNodePos = getTransformNodeTranslation(self.node,1)
            self.startMoveFlag = True
            
            mypath = getUniquePath(self.node)
            nameString = "%s" %mypath
            vrSessionService.sendPython('"'+nameString+'"')
            vrSessionService.sendPython('nodeRef = findUniquePath("'+nameString+'")')
            
            #nameString = "%s" % self.node.getName()
            #vrSessionService.sendPython('nodeRef = findNode("'+nameString+'")')
                    
    def stopMove(self,action,device):
        #global startMoveFlag
        global constXPressed
        global constYPressed
        global constZPressed

        if not self.node == None and not self.node.isNull():
            self.finalNodePos = getTransformNodeTranslation(self.node,1)
            self.finalNodeRot = getTransformNodeRotation(self.node)
            

            print("outsside")

            
            
            if constXPressed == True and constYPressed == True:
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.currentNodePos.x(), self.currentNodePos.y(),self.originalNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constYPressed == True and constZPressed == True:
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.originalNodePos.x(), self.currentNodePos.y(),self.currentNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                
            elif constXPressed == True and constZPressed == True:
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.currentNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 

            elif constXPressed == True:
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.currentNodePos.x(), self.originalNodePos.y(),self.originalNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 

            elif constYPressed == True:
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.originalNodePos.x(), self.currentNodePos.y(),self.originalNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 

            elif constZPressed == True:
                self.afterconstraintPos = setTransformNodeTranslation(self.node,self.originalNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z(),1)
                self.afterconstraintRot = setTransformNodeRotation(self.node,self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z()) 
                print("insidie z ")
                
            elif self.snapping == True:
                self.currentNodeRot = getTransformNodeRotation(self.node) 
                self.x = roundup(self.currentNodeRot.x()) 
                self.y = roundup(self.currentNodeRot.y()) 
                self.z = roundup(self.currentNodeRot.z()) 
                snap_rotation = "%f,%f,%f" %(self.x,self.y,self.z)
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+snap_rotation+')')
                self.newRot = setTransformNodeRotation(self.node,self.x,self.y,self.z)  
                print("insside snapping true")
                
            else:
                finalTranslation = "%f,%f,%f" %(self.finalNodePos.x(), self.finalNodePos.y(),self.finalNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+finalTranslation+', True)')
                finalRotation = "%f,%f,%f" %(self.finalNodeRot.x(),self.finalNodeRot.y(),self.finalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+finalRotation+')')
                
            vrConstraintService.deleteConstraint(self.constraint)
            self.startMoveFlag = False
            '''
            elif self.snapping == True:
                self.newRot = setTransformNodeRotation(self.node,self.x,self.y,self.z)  
            
            #vrSessionService.removeNodeSync(self.node)
            
            
            else:
                translation = "%f,%f,%f" %(self.originalNodePos.x(), self.originalNodePos.y(),self.currentNodePos.z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+translation+', True)')
                
                rotation = "%f,%f,%f" %(self.originalNodeRot.x(),self.originalNodeRot.y(),self.originalNodeRot.z())
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+rotation+')')
            '''

            
            
    def createMenu(self):
        myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath =  myDocuments +"\Autodesk\Automotive\VRED"
        filename = "\objectMoveOn.png"
        icon = QtGui.QIcon()
        icon.addFile(filepath+filename,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.On)
        myDocuments_second = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath_second =  myDocuments_second +"\Autodesk\Automotive\VRED"
        filename_second = "\objectMoveOff.png"
        icon.addFile(filepath_second+filename_second,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
        self.tool = vrImmersiveUiService.createTool("Tool_move")
        self.tool.setText("Move")
        self.tool.setCheckable(True)
        self.tool.setIcon(icon)
        self.tool.signal().checked.connect(self.moveEnable)
        self.tool.signal().unchecked.connect(self.moveDisable)
        
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
        
    def moveEnable(self):
        global constXPressed
        global constYPressed
        global constZPressed
        global moveControllerFound
        
        constXPressed = False
        constYPressed = False
        constZPressed = False
        allTools = vrImmersiveUiService.getTools()
         
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName() and tool.getName()[:5] == 'Tool_':
                tool.setChecked(False)
                tool.signal().unchecked.emit(None)
        print("Entering Move Enabled")
        self.isEnabled = True
        
        
        vrDeviceService.setActiveInteractionGroup("MoveGroup")
        self.leftUpperActionMove.signal().triggered.connect(self.undo)
        self.leftDownActionMove.signal().triggered.connect(self.constX)
        self.upActionMove.signal().triggered.connect(self.reset)
        self.downActionMove.signal().triggered.connect(self.constY)
        self.rightUpperActionMove.signal().triggered.connect(self.redo)
        self.rightDownActionMove.signal().triggered.connect(self.constZ)
        self.centerActionMove.signal().triggered.connect(self.constDeactive)
        

        nodes = getAllNodes()
        for node in nodes:
            if hasNodeTag(node, 'Movable'):
                if node.getName() not in [element[0].getName() for element in self.all_nodes]:
                    #print('For node inside', node.getName(), [element[0].getName() for element in self.all_nodes])
                    #print('Before appending, ', len(self.all_nodes), [element[0].getName() for element in self.all_nodes])
                    #print('new node made movable', node.getName())
                    node_translation = getTransformNodeTranslation(node, True)
                    node_rotation = getTransformNodeRotation(node)
                    self.all_nodes.append([node, node_translation, node_rotation])
                    #print('After appending', len(self.all_nodes), [element[0].getName() for element in self.all_nodes])
        
        if not self.moverEnabled:
            start = self.pointer.getControllerAction("start")
            start.signal().triggered.connect(self.startMove)
            execute = self.pointer.getControllerAction("execute")
            execute.signal().triggered.connect(self.stopMove)
            self.moverEnabled = True
        if moveControllerFound == True:
            self.newRightCon = findNode("VRController_Move")
            self.rightController.setVisible(0)
            self.newRightCon.setActive(1)
            controllerPos = getTransformNodeTranslation(self.rightController.getNode(),1)
            setTransformNodeTranslation(self.newRightCon, controllerPos.x(), controllerPos.y(), controllerPos.z(), True)
            self.MoveControllerConstraint = vrConstraintService.createParentConstraint([self.rightController.getNode()], self.newRightCon, False)
        else:
            self.rightController.setVisible(1)
        self.timer.setActive(0)
                
    def moveDisable(self):
        global moveControllerFound
        global constXPressed
        global constYPressed
        global constZPressed
        if self.isEnabled == False:
            print("move was not enabled before " )
            return
        

        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName():
                tool.setCheckable(True) 
                #tool.setChecked(False)
        print("Move Disabled")
        self.isEnabled = False
        vrDeviceService.setActiveInteractionGroup("Locomotion")
        self.leftUpperActionMove.signal().triggered.disconnect(self.undo)
        self.leftDownActionMove.signal().triggered.disconnect(self.constX)
        self.upActionMove.signal().triggered.disconnect(self.reset)
        self.downActionMove.signal().triggered.disconnect(self.constY)
        self.rightUpperActionMove.signal().triggered.disconnect(self.redo)
        self.rightDownActionMove.signal().triggered.disconnect(self.constZ)
        self.centerActionMove.signal().triggered.disconnect(self.constDeactive)
        
        if self.moverEnabled:
            start = self.pointer.getControllerAction("start")
            start.signal().triggered.disconnect(self.startMove)
            execute = self.pointer.getControllerAction("execute")
            execute.signal().triggered.disconnect(self.stopMove)
            self.moverEnabled = False
            
        self.rightController.setVisible(1)
        if moveControllerFound == True: 
            self.newRightCon.setActive(0)
            vrConstraintService.deleteConstraint(self.MoveControllerConstraint)
            setSwitchMaterialChoice("C_M_Icon_X", 0)
            setSwitchMaterialChoice("C_M_Icon_Y", 0)
            setSwitchMaterialChoice("C_M_Icon_Z", 0)

            print("Constraint deactivated")
            constXPressed = False
            constYPressed = False
            constZPressed = False
            
            
        self.timer.setActive(0)
    
        constraints = vrConstraintService.getConstraints()
        for constraint in constraints:
            vrConstraintService.deleteConstraint(constraint)
        
        #for node in self.all_nodes:
            #print('Node inside all_nodes: ', node[0].getName())
            #print('length of all_nodes: ', len(self.all_nodes))
            
            
    def getMovable(self,node):
        while not node.isNull():
            x = node.getName()
            if hasNodeTag(node, 'Movable'):
                current_position = getTransformNodeTranslation(node, True)
                current_rotation = getTransformNodeRotation(node)
                self.undo_list.append([node, current_position, current_rotation])
                return node
            if(node.getName() == "Group" or node.getName() =="Transform"):
                break
            node = node.getParent()
        return node
        
    
    def undo(self):
        for i in self.undo_list:
            print(i[0].getName())                 
            print(i[1])
        
    
        if self.resetflag is True:
            for i in self.last_pos_node:
                
                mypath = getUniquePath(i[0])
                nameString = "%s" %mypath
                vrSessionService.sendPython('"'+nameString+'"')
                vrSessionService.sendPython('nodeRef = findUniquePath("'+nameString+'")')
                
                #nameString = "%s" % i[0].getName()
                #vrSessionService.sendPython('nodeRef = findNode("'+nameString+'")')
                
                i_translation = "%f,%f,%f" %(i[1].x(), i[1].y(), i[1].z())
                i_rotation = "%f,%f,%f" %(i[2].x(), i[2].y(), i[2].z())
                vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+i_translation+', True)')
                vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+i_rotation+')')
            self.resetflag = False
            del(self.last_pos_node[:])
            return
                
        if not len(self.undo_list) == 0:
            x = self.undo_list[-1]
            
            mypath = getUniquePath(x[0])
            nameString = "%s" %mypath
            vrSessionService.sendPython('"'+nameString+'"')
            vrSessionService.sendPython('nodeRef = findUniquePath("'+nameString+'")')
            
            #nameString = "%s" % x[0].getName()
            #vrSessionService.sendPython('nodeRef = findNode("'+nameString+'")')
            
            x_translation = "%f,%f,%f" %(x[1].x(), x[1].y(), x[1].z())
            x_rotation = "%f,%f,%f" %(x[2].x(), x[2].y(), x[2].z())
            current_position = getTransformNodeTranslation(x[0], True)
            current_rotation = getTransformNodeRotation(x[0])
            vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+x_translation+', True)')
            vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+x_rotation+')')
            self.redo_list.append([x[0], current_position, current_rotation])
            del(self.undo_list[-1])
                
        
        print("UNDO")
    
    def redo(self):
        for i in self.redo_list:
            print(i[0].getName())
            print(i[1])
        if not len(self.redo_list) == 0:
            x = self.redo_list[-1]
            #print(x)
            
            mypath = getUniquePath(x[0])
            nameString = "%s" %mypath
            vrSessionService.sendPython('"'+nameString+'"')
            vrSessionService.sendPython('nodeRef = findUniquePath("'+nameString+'")')
            
            #nameString = "%s" % x[0].getName()
            #vrSessionService.sendPython('nodeRef = findNode("'+nameString+'")')
            
            x_translation = "%f,%f,%f" %(x[1].x(), x[1].y(), x[1].z())
            x_rotation = "%f,%f,%f" %(x[2].x(), x[2].y(), x[2].z())
            
            current_position = getTransformNodeTranslation(x[0], True)
            current_rotation = getTransformNodeRotation(x[0])
            vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+x_translation+', True)')
            vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+x_rotation+')')
            self.undo_list.append([x[0], current_position, current_rotation])
            del(self.redo_list[-1])
        print("REDO")
        
    def reset(self):
        
        last_pos = getAllNodes()
        for node in last_pos:
            if hasNodeTag(node, 'Movable'):
                node_last_pos = getTransformNodeTranslation(node, True)
                node_last_rot = getTransformNodeRotation(node)
                self.last_pos_node.append([node, node_last_pos, node_last_rot])
                print('recording the last pos of ', node.getName())
        for i in self.all_nodes:
            mypath = getUniquePath(i[0])
            nameString = "%s" %mypath
            vrSessionService.sendPython('"'+nameString+'"')
            vrSessionService.sendPython('nodeRef = findUniquePath("'+nameString+'")')
            
            #nameString = "%s" % i[0].getName()
            #vrSessionService.sendPython('nodeRef = findNode("'+nameString+'")')
            
            i_translation = "%f,%f,%f" %(i[1].x(), i[1].y(), i[1].z())
            i_rotation = "%f,%f,%f" %(i[2].x(), i[2].y(), i[2].z())
            vrSessionService.sendPython('setTransformNodeTranslation(nodeRef, '+i_translation+', True)')
            vrSessionService.sendPython('setTransformNodeRotation(nodeRef, '+i_rotation+')')
            #print('this node is in all node list ', i[0].getName())
            
        #del(self.undo_list[:])
        #del(self.redo_list[:])
        self.resetflag = True
        print('Reset button down touchpad pressed')

    def constX(self):
        print("Constraint in X direction Active")
        global constXPressed
        
        if constXPressed == False:
            constXPressed = True
            print("flag X pressed is: ", constXPressed)
            self.moveXConstraintON()

        else:
            constXPressed = False
            print("flag X pressed is: ", constXPressed)
            self.moveXConstraintOFF()
            
                   
    def constY(self):
        global constYPressed
        print("Constraint in Y direction Active")
        if constYPressed == False:
            constYPressed = True
            print("flag Y pressed is: ", constYPressed)
            self.moveYConstraintON()

        else:
            constYPressed = False
            print("flag Y pressed is: ", constYPressed)
            self.moveYConstraintOFF()
    
    def constZ(self):
        global constZPressed
        print("Constraint in Z direction Active")
        if constZPressed == False:
            constZPressed = True
            print("flag Z pressed is: ", constZPressed)
            self.moveZConstraintON()

        else:
            constZPressed = False
            print("flag Z pressed is: ", constZPressed) 
            self.moveZConstraintOFF()
        
    def constDeactive(self):
        
        if self.snapping == True:
            self.snapping = False
            self.moveIconFree()
        else:
            self.snapping = True
            self.moveIconSnap()

            
    def moveXConstraintON(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_X", 1)

    def moveXConstraintOFF(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_X", 0)
                
    def moveYConstraintON(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_Y", 1)
    
    def moveYConstraintOFF(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_Y", 0)
     
    def moveZConstraintON(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_Z", 1)
    
    def moveZConstraintOFF(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_Z", 0)

    def moveIconFree(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_Move", 0)
    
    def moveIconSnap(self):
        if moveControllerFound == True: 
            setSwitchMaterialChoice("C_M_Icon_Move", 1)
                         
        
move = ObjectMover()
render_move = RenderActionMove()
