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


'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.
Scripted by Simon Nagel, supported by Rutvik Bhatt
First download and copy two osb files "VRControllerNotes_Notes" and "VRControllerNotes" provided in GitHub repository into "C:\Users\USERNAME\Documents\Autodesk\Automotive\VRED" path in order to use the dedicated Notes controller.
If you do not wish to use the dedicated controller you can skip this part. 
Just paste the Scene in the Script Editor of VRED and press run.
Turn on the OpenVR and press the menu button on the controller. 
Press the 'Notes' tools menu in the menu. 
    You will see a Note on the top of the right controller.
    Press the right trigger on the controller to put your note anywhere you desire. 
    
Press Center Touch Pad button on the right controller to change the view of the notes
    1. The default mode where you see the Note on top of the right controller
    2. The second mode where the Note is on the end of the Ray, You can put note on any Geometry in the scene
Press the Down Touch Pad button to enable the delete mode, You can delete the notes that you have put by pointing at the note and press the trigger
Press the Left or Right Touch Pad button to increase and decrease the size of the Notes
Press the Up Touch Pad button to change the note from 'Good Note' to 'Bad Note'
    
This script works in VRED Collaboration.
Please make sure that, the Script is executed on each computer of each participant.
'''





from math import sqrt
import random
from PySide2 import QtCore, QtGui
notesControllerFound = False
mainCustomFuncGroup = False

notesController = 0
goodBadNotes = 0
allNotesNodes = getAllNodes()
for node in allNotesNodes:
    allNotesNodeName = node.getName()
    if allNotesNodeName == "VRController_Notes":
        notesController+=1
    elif allNotesNodeName == "Notes":
        goodBadNotes += 1
    elif allNotesNodeName == 'VRED-VR-Custom-Fucntion':
        print("group node found in Notes")
        mainCustomFuncGroup = True
        customFunctionsGroup = node
        
if notesController == 0:
    import os
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename = "\VRControllerNotes"
    if os.path.exists(filepath+str(filename)+".osb"):
        node = loadGeometry(filepath +str(filename)+".osb")
        node.setName("VRControllerNotes")
        notesControllerFound = True
    else:
        print("file doesnt exist")
        notesControllerFound = False
else:
    notesControllerFound = True
    
if goodBadNotes == 0:
    import os
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename = "\VRControllerNotes_Notes"
    node = loadGeometry(filepath +str(filename)+".osb")
    node.setName("VRControllerNotes_Notes")
    createNode("Group", "Cloned_ref_obj")
    
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

refObject = findNode("Notes").getChild(0)
switch = findNode("Notes")
count = 0
Cloned_ref_obj = findNode("Cloned_ref_obj")
menuOpened = False

class Notes():
    def __init__(self):

        self.isEnabled = False
        self.activeNode = None
        self.upbuttonIsActive = False
        self.timer = vrTimer()
        self.createMenu()
        
        
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")

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
        padCenter = vrdVirtualTouchpadButton('padcenter', 0.0, 0.5, 0.0, 360.0)
        padLeft = vrdVirtualTouchpadButton('padleft', 0.5, 1.0, 225.0, 315.0)
        padUp = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 315.0, 45.0)
        padRight = vrdVirtualTouchpadButton('padright', 0.5, 1.0, 45.0, 135.0)
        padDown = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 135.0, 225.0)

        # right controller
        self.rightController.addVirtualButton(padCenter, 'touchpad')
        self.rightController.addVirtualButton(padLeft, 'touchpad')
        self.rightController.addVirtualButton(padUp, 'touchpad')
        self.rightController.addVirtualButton(padRight, 'touchpad')
        self.rightController.addVirtualButton(padDown, 'touchpad')
        '''
        
        multiButtonPadNotes = vrDeviceService.createInteraction("MultiButtonPadNotes")
        multiButtonPadNotes.setSupportedInteractionGroups(["NotesGroup"])
        toolsMenuNotes = vrDeviceService.getInteraction("Tools Menu")
        toolsMenuNotes.addSupportedInteractionGroup("NotesGroup")  
        #setting control action for right controller Pad
        '''
        self.leftAction = multiButtonPad.createControllerAction("right-padleft-pressed")
        self.upAction = multiButtonPad.createControllerAction("right-padup-pressed")
        self.downAction = multiButtonPad.createControllerAction("right-paddown-pressed")
        self.rightAction = multiButtonPad.createControllerAction("right-padright-pressed")
        self.centerAction = multiButtonPad.createControllerAction("right-padcenter-pressed")
        '''
        self.leftUpperActionNotes = multiButtonPadNotes.createControllerAction("right-padupleft-pressed")
        self.leftDownActionNotes = multiButtonPadNotes.createControllerAction("right-paddownleft-pressed")
        self.upActionNotes = multiButtonPadNotes.createControllerAction("right-padup-pressed")
        self.downActionNotes = multiButtonPadNotes.createControllerAction("right-paddown-pressed")
        self.rightUpperActionNotes = multiButtonPadNotes.createControllerAction("right-padupright-pressed")
        self.rightDownActionNotes = multiButtonPadNotes.createControllerAction("right-paddownright-pressed")
        self.centerActionNotes = multiButtonPadNotes.createControllerAction("right-padcenter-pressed") 
           
        
        teleport = vrDeviceService.getInteraction("Teleport")
        teleport.addSupportedInteractionGroup("NotesGroup") 
        teleport.setControllerActionMapping("prepare" , "left-touchpad-touched")
        teleport.setControllerActionMapping("abort" , "left-touchpad-untouched")
        teleport.setControllerActionMapping("execute" , "left-touchpad-pressed")
        
        #controllerInteraction = vrDeviceService.createInteraction("new")
        
        self.pointer = vrDeviceService.getInteraction("Pointer")
        self.pointer.addSupportedInteractionGroup("NotesGroup")
        
        # right trigger events
        self.triggerRightPressed = multiButtonPadNotes.createControllerAction("right-trigger-pressed")
        #triggerRightPressed = controllerInteraction.createControllerAction("right-trigger-released")                
        self.deleteNoteIsActive = False
        self.changeView = False
        

        
    def distanceFunc(self):
    
        global refObject
        global menuOpened
        controllerRot = getTransformNodeRotation(self.rightController.getNode())    
        handPos = getTransformNodeTranslation(self.rightController.getNode(),1)
        handMat = self.rightController.getNode().getWorldTransform()
        rayOrigin = Pnt3f(handPos.x(),handPos.y(),handPos.z())
        refObject.setActive(0)
        intersectionRay = self.rightController.pick()
        hitpoint = intersectionRay.getPoint()
        hitNode = intersectionRay.getNode()
        hitNode = toNode(hitNode.getObjectId())
        interPosRay = Pnt3f(hitpoint.x(),hitpoint.y(),hitpoint.z())
        refObject.setActive(1)

        self.activeNode = hitNode
        if self.activeNode.getName() == "VRMenuPanel" and menuOpened == False:
            self.neutralNotes()
            menuOpened = True
        elif hitNode.getName() != "VRMenuPanel" and menuOpened == True:
            self.defaultNotesMappings()
            menuOpened = False    
            
        
        vrConstraintService.createOrientationConstraint([self.rightController.getNode()], refObject)           
        if not self.changeView:            
            setTransformNodeTranslation(refObject, handPos.x(), handPos.y(), handPos.z(),1)   
             
        else:
            setTransformNodeTranslation(refObject, interPosRay.x(), interPosRay.y(), interPosRay.z(),1)
                 
    def createMenu(self):
        
        myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath =  myDocuments +"\Autodesk\Automotive\VRED"
        filename = "\objectNotesOn.png"
        icon = QtGui.QIcon()
        icon.addFile(filepath+filename,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.On)
        myDocuments_second = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath_second =  myDocuments_second +"\Autodesk\Automotive\VRED"
        filename_second = "\objectNotesOff.png"
        icon.addFile(filepath_second+filename_second,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
        self.tool = vrImmersiveUiService.createTool("Tool_Notes")
        self.tool.setText("Notes")
        self.tool.setCheckable(True)
        self.tool.setIcon(icon)
        self.tool.signal().checked.connect(self.notesEnable)
        self.tool.signal().unchecked.connect(self.notesDisable)
    
    def notesEnable(self):
        
        global refObject
        global camera_perspective
        global ray_c_node
        global switch
        global all_Icons_nodes
        global notesControllerFound
        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName() and tool.getName()[:5] == 'Tool_':
                tool.setChecked(False)
                tool.signal().unchecked.emit(None)
        print("Notes Enabled")
        self.isEnabled = True
                
        vrDeviceService.setActiveInteractionGroup("NotesGroup")   
        
        self.leftUpperActionNotes.signal().triggered.connect(self.sizeDown)
        #self.leftDownActionNotes.signal().triggered.connect()
        self.upActionNotes.signal().triggered.connect(self.ChangeNote)
        self.downActionNotes.signal().triggered.connect(self.deleteNote)
        self.rightUpperActionNotes.signal().triggered.connect(self.sizeUp)
        #self.rightDownActionNotes.signal().triggered.connect()
        self.centerActionNotes.signal().triggered.connect(self.changeNoteView)
        
        '''                                                                              
        self.leftAction.signal().triggered.connect(self.sizeDown)
        self.upAction.signal().triggered.connect(self.ChangeNote)
        self.downAction.signal().triggered.connect(self.deleteNote)
        self.rightAction.signal().triggered.connect(self.sizeUp)
        self.centerAction.signal().triggered.connect(self.changeNoteView)
        '''
        #all_Icons_nodes.setVisibilityFlag(True)
        
        refObject_node = vrNodeService.getNodeFromId(refObject.getID())
        refObject_node.getChild(0).setVisibilityFlag(True)
        
        refObject = switch.getChild(0)
        switch.fields().setInt32("choice",0)
        
        if notesControllerFound == True:
            self.newRightCon = findNode("VRController_Notes")
            self.rightController.setVisible(0)
            self.newRightCon.setActive(1)
            controllerPos = getTransformNodeTranslation(self.rightController.getNode(),1)
            setTransformNodeTranslation(self.newRightCon, controllerPos.x(), controllerPos.y(), controllerPos.z(), True)
            self.NoteControllerConstraint = vrConstraintService.createParentConstraint([self.rightController.getNode()], self.newRightCon, False)
        else:
            self.rightController.setVisible(1)
            
        self.deleteNoteIsActive = False
        self.changeView = False
        self.iconsNotesTrashOff()
        self.triggerRightPressed.signal().triggered.connect(self.trigger_right_pressed)       
        self.timer.setActive(1)
        self.timer.connect(self.distanceFunc)
        
        if self.changeView == False:
            self.iconsNotesConstraint()
            refObject_node.getParent().setVisibilityFlag(True)
            self.onControllerNotesMapping()
            
        else:
            self.iconsNotesRay()
            self.onRayNotesMapping()
             
        
    def notesDisable(self):
        global notesControllerFound
        
        if self.isEnabled == False:
            print("Notes was not enabled before " )
            return
        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName():
                tool.setCheckable(True)
                #tool.setChecked(False)
        print("Notes Disabled")
        self.isEnabled = False
        
        self.deleteNoteIsActive = False
        
        self.leftUpperActionNotes.signal().triggered.disconnect(self.sizeDown)
        #self.leftDownActionNotes.signal().triggered.disconnect()
        self.upActionNotes.signal().triggered.disconnect(self.ChangeNote)
        self.downActionNotes.signal().triggered.disconnect(self.deleteNote)
        self.rightUpperActionNotes.signal().triggered.disconnect(self.sizeUp)
        #self.rightDownActionNotes.signal().triggered.disconnect()
        self.centerActionNotes.signal().triggered.disconnect(self.changeNoteView)
        
        '''
        self.leftAction.signal().triggered.disconnect(self.sizeDown)
        self.upAction.signal().triggered.disconnect(self.ChangeNote)
        self.downAction.signal().triggered.disconnect(self.deleteNote)
        self.rightAction.signal().triggered.disconnect(self.sizeUp)
        self.centerAction.signal().triggered.disconnect(self.changeNoteView)
        self.triggerRightPressed.signal().triggered.disconnect(self.trigger_right_pressed)
        '''
        vrDeviceService.setActiveInteractionGroup("Locomotion")
                
        global refObject
        global all_Icons_nodes
        
        #all_Icons_nodes.setVisibilityFlag(False)
        refObject_node = vrNodeService.getNodeFromId(refObject.getID())
        refObject_node.getChild(0).setVisibilityFlag(False)
        
        self.rightController.setVisible(1)
        if notesControllerFound == True:
            self.newRightCon.setActive(0)
            vrConstraintService.deleteConstraint(self.NoteControllerConstraint)
        
        self.timer.setActive(0)
        self.neutralNotes()
        
        constraints = vrConstraintService.getConstraints()
        
        for constraint in constraints:
            vrConstraintService.deleteConstraint(constraint)
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
    
    def trigger_right_pressed(self):
        
        global refObject
        global Cloned_ref_obj
        nodeNum = random.randint(0,1000000)
        if not self.activeNode.getName() == "VRMenuPanel":
            if self.deleteNoteIsActive:
                node = self.activeNode.getParent().getParent()
                nodeName = "%s" %node.getName()
                if hasNodeTag(node.getParent(), 'Cloned Note'):
                    vrSessionService.sendPython('deleteNode(findNode("'+nodeName+'"),True)')       
            else:
                nameRefObject = refObject.getName()
                current_position = getTransformNodeTranslation(refObject, True)
                current_rotation = getTransformNodeRotation(refObject)
                current_scale = getTransformNodeScale(refObject)
                
                nameString = "%s" % nameRefObject
                posString = "%f,%f,%f" %(current_position.x(),current_position.y(),current_position.z())
                rotString = "%f,%f,%f" %(current_rotation.x(),current_rotation.y(),current_rotation.z())
                scaleString= "%f,%f,%f" %(current_scale.x(),current_scale.y(),current_scale.z())
                
                vrSessionService.sendPython('clonedRef = cloneNode(findNode("'+nameString+'"), False)')
                
                clonedNewName  = nameString + '_' + str(nodeNum)

                vrSessionService.sendPython('clonedRef.setName("'+clonedNewName+'")')
                vrSessionService.sendPython('moveNode(clonedRef, refObject, Cloned_ref_obj)')
                vrSessionService.sendPython('setTransformNodeRotation(clonedRef, '+rotString+')')
                vrSessionService.sendPython('setTransformNodeTranslation(clonedRef, '+posString+', True)')
                vrSessionService.sendPython('setTransformNodeScale(clonedRef, '+scaleString+')')
                vrSessionService.sendPython('addNodeTag(Cloned_ref_obj, "Cloned Note")')
 
    def deleteNote(self):
        
        global refObject
        global all_Icons
        refObject_node = vrNodeService.getNodeFromId(refObject.getID())
        #all_Icons_node = vrNodeService.getNodeFromId(all_Icons.getID())    #Converting all_icons from vrNodePtr to vrdNode
        if not self.deleteNoteIsActive:
            self.iconsNotesTrashOn()
            refObject_node.getParent().setVisibilityFlag(False)
            self.deleteNoteIsActive = True
            self.onRayNotesMapping()
            

            
        else:
            self.deleteNoteIsActive = False
            self.iconsNotesTrashOff()
            refObject_node.getParent().setVisibilityFlag(True)
            self.defaultNotesMappings()

                
    def sizeUp(self):
        
        global refObject 
        currentsize = getTransformNodeScale(refObject)
        ref_Parent = vrNodeService.getNodeFromId(refObject.getParent().getID())
        switch_child = ref_Parent.getChildren()
        for current_note in switch_child:
            setTransformNodeScale(current_note, currentsize.x() * 1.2, currentsize.y() * 1.2, currentsize.z() * 1.2)

        
    def sizeDown(self):
        
        global refObject 
        
        currentsize = getTransformNodeScale(refObject)
        ref_Parent = vrNodeService.getNodeFromId(refObject.getParent().getID())
        switch_child = ref_Parent.getChildren()
        for current_note in switch_child:
            setTransformNodeScale(current_note, currentsize.x() / 1.2, currentsize.y() / 1.2, currentsize.z() / 1.2)
        
        
    def changeNoteView(self):
        
        global rightControllerOld
        global refObject
        if not self.deleteNoteIsActive:
            if not self.changeView:
                self.iconsNotesRay()
                self.changeView = True
                
                self.onRayNotesMapping()
                
            else:
                self.changeView = False
                self.iconsNotesConstraint()
                
                self.onControllerNotesMapping()
 
                           
    def ChangeNote(self):
        
        global refObject
        global count
        global switch
        
        refObject.getParent()
        hello = vrNodeService.getNodeFromId(refObject.getParent().getID())
        all_child = hello.getChildren()
        
        if not self.upbuttonIsActive:
            index = count%len(all_child)
            count += 1
            refObject = switch.getChild(index)
            switch.fields().setInt32("choice",index)
           
        else:
            self.upbuttonIsActive = False 

    def iconsNotesTrashOn(self):
        global notesControllerFound
        if notesControllerFound == True:
            setSwitchMaterialChoice("C_N_Icon_Minus", 0)
            setSwitchMaterialChoice("C_N_Icon_Next", 0)
            setSwitchMaterialChoice("C_N_Icon_Plus", 0)
            setSwitchMaterialChoice("C_N_Icon_Trash", 2)

    def iconsNotesTrashOff(self):
        global notesControllerFound
        if notesControllerFound == True:
            setSwitchMaterialChoice("C_N_Icon_Minus", 1)
            setSwitchMaterialChoice("C_N_Icon_Next", 1)
            setSwitchMaterialChoice("C_N_Icon_Plus", 1)
            setSwitchMaterialChoice("C_N_Icon_Trash", 1)

    def iconsNotesConstraint(self):
        global notesControllerFound
        if notesControllerFound == True:
            setSwitchMaterialChoice("C_N_Icon_Notes", 2)
        
    def iconsNotesRay(self):
        global notesControllerFound
        if notesControllerFound == True:
            setSwitchMaterialChoice("C_N_Icon_Notes", 1) 
        
    def neutralNotes(self):
        
        self.pointer.setControllerActionMapping("prepare" , "any-customtrigger-touched")
        self.pointer.setControllerActionMapping("abort" , "any-customtrigger-untouched")
        self.pointer.setControllerActionMapping("start" , "any-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "any-customtrigger-released")   
                         
    def onControllerNotesMapping(self):
        
        self.pointer.setControllerActionMapping("prepare" , "disable")
        self.pointer.setControllerActionMapping("abort" , "any-customtrigger-untouched")
        self.pointer.setControllerActionMapping("start" , "any-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "any-customtrigger-released") 
    
    def onRayNotesMapping(self):
        
        self.pointer.setControllerActionMapping("prepare" , "right-customtrigger-touched")
        self.pointer.setControllerActionMapping("abort" , "disable") # Hack: Override the input with an unknown input
        self.pointer.setControllerActionMapping("start" , "right-customtrigger-pressed")
        self.pointer.setControllerActionMapping("execute" , "right-customtrigger-released")
            
    def defaultNotesMappings(self):
        
        if self.changeView == False :
            self.onControllerNotesMapping()
        else:
            self.onRayNotesMapping()   
                                                                                                                                
notes = Notes()
print ("executed")

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
from PySide2 import QtCore, QtGui
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
mainCustomFuncGroup = False
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
    elif nodeName == 'VRED-VR-Custom-Fucntion':
        print("group node found in Draw")
        mainCustomFuncGroup = True
        customFunctionsGroup = i


        
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
else:
    drawControllerFound = True
    
if drawControllerFound == True:
    drawControllerTool = findNode("VRController_Draw")
    drawControllerTool.setActive(0)
else:
    drawControllerTool = rightController.getNode()
    drawControllerTool = toNode(drawControllerTool.getObjectId())
    
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
        if drawControllerFound == True:
            setSwitchMaterialChoice("C_D_Icon_Visible", 1)
        
    else:
        linesVisible = False
        vrSessionService.sendPython('lineGrp.setActive(1)')
        if drawControllerFound == True:
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
                if vrSessionService.isConnected():
                    localUser = vrSessionService.getUser()
                    localUserID = vrdSessionUser.getUserId(localUser)
                    newMatName = "_d_line_material_"+str(localUserID)
                else:
                    newMatName = "_d_line_material_"+str(1000)
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
                if vrSessionService.isConnected():
                    vrSessionService.sendPython('clnode.setMaterial(findMaterial("'+valueLocalId+'"))')
                else:
                    vrSessionService.sendPython('clnode.setMaterial(findMaterial("_d_line_material"))')
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
        
        self.isEnabled = False
        self.isPointingRayActive = True
        self.createMenu()         
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")
        self.leftController.setVisualizationMode(Visualization_ControllerAndHand)
        self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        vrImmersiveInteractionService.setDefaultInteractionsActive(1)
        
        # six button config
        padCenterDraw = vrdVirtualTouchpadButton('padcenter', 0.0, 0.5, 0.0, 360.0)
        padUpperLeftDraw = vrdVirtualTouchpadButton('padupleft', 0.5, 1.0, 270.0, 330.0)
        padLowerLeftDraw = vrdVirtualTouchpadButton('paddownleft', 0.5, 1.0, 210.0, 270.0)
        padUpDraw = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 330.0, 30.0)
        padUpperRightDraw = vrdVirtualTouchpadButton('padupright', 0.5, 1.0, 30.0, 90.0)
        padLowerRightDraw = vrdVirtualTouchpadButton('paddownright', 0.5, 1.0, 90.0, 150.0)
        padDownDraw = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 150.0, 210.0)
        
        # Right controller
        self.rightController.addVirtualButton(padCenterDraw, 'touchpad')
        self.rightController.addVirtualButton(padUpperLeftDraw, 'touchpad')
        self.rightController.addVirtualButton(padLowerLeftDraw, 'touchpad')
        self.rightController.addVirtualButton(padUpDraw, 'touchpad')
        self.rightController.addVirtualButton(padUpperRightDraw, 'touchpad')
        self.rightController.addVirtualButton(padLowerRightDraw, 'touchpad')
        self.rightController.addVirtualButton(padDownDraw, 'touchpad')        
        
        
        '''
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
        '''
        
        multiButtonPadDraw = vrDeviceService.createInteraction("MultiButtonPadDraw")
        multiButtonPadDraw.setSupportedInteractionGroups(["DrawGroup"])
        toolsMenuDraw = vrDeviceService.getInteraction("Tools Menu")
        toolsMenuDraw.addSupportedInteractionGroup("DrawGroup")   
        #setting control action for right controller Pad
        
        '''
        self.leftActionDraw = multiButtonPadDraw.createControllerAction("right-padleft-pressed")
        self.upActionDraw = multiButtonPadDraw.createControllerAction("right-padup-pressed")
        self.downActionDraw = multiButtonPadDraw.createControllerAction("right-paddown-pressed")
        self.rightActionDraw = multiButtonPadDraw.createControllerAction("right-padright-pressed")
        self.centerActionDraw = multiButtonPadDraw.createControllerAction("right-padcenter-pressed")
        '''
        self.leftUpperActionDraw = multiButtonPadDraw.createControllerAction("right-padupleft-pressed")
        self.leftDownActionDraw = multiButtonPadDraw.createControllerAction("right-paddownleft-pressed")
        self.upActionDraw = multiButtonPadDraw.createControllerAction("right-padup-pressed")
        self.downActionDraw = multiButtonPadDraw.createControllerAction("right-paddown-pressed")
        self.rightUpperActionDraw = multiButtonPadDraw.createControllerAction("right-padupright-pressed")
        self.rightDownActionDraw = multiButtonPadDraw.createControllerAction("right-paddownright-pressed")
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
        
        myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath =  myDocuments +"\Autodesk\Automotive\VRED"
        filename = "\objectDrawOn.png"
        icon = QtGui.QIcon()
        icon.addFile(filepath+filename,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.On)
        myDocuments_second = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
        filepath_second =  myDocuments_second +"\Autodesk\Automotive\VRED"
        filename_second = "\objectDrawOff.png"
        icon.addFile(filepath_second+filename_second,QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
        self.tool = vrImmersiveUiService.createTool("Tool_Draw")
        self.tool.setText("Draw")
        self.tool.setCheckable(True)
        self.tool.setIcon(icon)
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
        
        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName() and tool.getName()[:5] == 'Tool_':
                tool.setChecked(False)
                tool.signal().unchecked.emit(None)
        print("Draw Enabled")
        self.isEnabled = True
        
        desktopMode = False
        drawVREnable = True
        
        vrDeviceService.setActiveInteractionGroup("DrawGroup")
        
        self.leftUpperActionDraw.signal().triggered.connect(lastLine)
        #self.leftDownAction.signal().triggered.connect()
        #self.upAction.signal().triggered.connect()
        self.downActionDraw.signal().triggered.connect(toggleLines)
        #self.rightUpperAction.signal().triggered.connect()
        #self.rightDownAction.signal().triggered.connect()
        self.centerActionDraw.signal().triggered.connect(self.changeViewDraw)
        
        '''
        self.leftActionDraw.signal().triggered.connect(lastLine)
        #self.upActionDraw.signal().triggered.connect(self.)
        self.downActionDraw.signal().triggered.connect(toggleLines)
        #self.rightActionDraw.signal().triggered.connect(toggleLines)
        self.centerActionDraw.signal().triggered.connect(self.changeViewDraw)
        '''
        
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
        
        if self.isEnabled == False:
            print("Draw was not enabled before " )
            return
        
        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName():
                tool.setCheckable(True)
                #tool.setChecked(False)
        print("Draw Disabled")
        self.isEnabled = False
        
        d_child = drawTool.getChild(0)
        d_child.setActive(True)
        desktopMode = True
        drawVREnable = False
        timer.setActive(0)
        
        self.leftUpperActionDraw.signal().triggered.disconnect(lastLine)
        #self.leftDownAction.signal().triggered.disconnect()
        #self.upAction.signal().triggered.disconnect()
        self.downActionDraw.signal().triggered.disconnect(toggleLines)
        #self.rightUpperAction.signal().triggered.disconnect()
        #self.rightDownAction.signal().triggered.disconnect()
        self.centerActionDraw.signal().triggered.disconnect(self.changeViewDraw)
        
        '''
        self.leftActionDraw.signal().triggered.disconnect(lastLine)
        #self.upActionDraw.signal().triggered.disconnect(self.)
        self.downActionDraw.signal().triggered.disconnect(toggleLines)
        #self.rightActionDraw.signal().triggered.disconnect(toggleLines)
        self.centerActionDraw.signal().triggered.disconnect(self.changeViewDraw)
        '''      
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