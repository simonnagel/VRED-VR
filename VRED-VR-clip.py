'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.
Scripted by Simon Nagel, supported by Rutvik Bhatt

First download and copy paste the "VRControllerClip.osb" file provided in the GitHub repository into "C:\Users\USERNAME\Documents\Autodesk\Automotive\VRED" path in order to use the dedicated draw controller.

If you do not wish to use the dedicated controller you can skip this part. 
Just paste the Scene in the Script Editor of VRED and press run.

This script works in VRED Collaboration.
Please make sure that, the Script is executed on each computer of each participant.
'''


import os
from PySide2 import QtCore, QtGui

clippingController = 0
clippingControllerFound = False
mainCustomFuncGroup = False
allClipNodes = getAllNodes()
for node in allClipNodes:
    allClipNodesName = node.getName()
    if allClipNodesName == "VRController_Clip":
        clippingController+=1
    elif allClipNodesName == 'VRED-VR-Custom-Fucntion':
        mainCustomFuncGroup = True
        customFunctionsGroup = node
        
if clippingController == 0:
    myDocuments = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents')
    filepath =  myDocuments +"\Autodesk\Automotive\VRED"
    filename = "\VRControllerClip"
    if os.path.exists(filepath+str(filename)+".osb"):
        node = loadGeometry(filepath +str(filename)+".osb")
        node.setName("VRControllerClip")
        clippingControllerFound = True
    else:
        print("file doesnt exist")
        clippingControllerFound = False
else:
    clippingControllerFound = True

if not mainCustomFuncGroup:
    customFunctionsGroup = createNode('Group', 'VRED-VR-Custom-Fucntion')
    
allFucnNames = ["VRControllerMove", "VRControllerSelect", "VRControllerNotes", 
                "VRControllerDraw", "VRControllerNotes_Notes", "Cloned_ref_obj",
                "D_Tool", "D_Lines", "D_tempLine", "Group_html","VRControllerClip"]

allNodeFuncname = getAllNodes()
for node in allNodeFuncname:
    nodeName = node.getName()
    if nodeName in allFucnNames:
        addChilds(customFunctionsGroup, [node])
'''        
class RenderActionMove(vrInteraction):
    
    def __init__(self):
        vrInteraction.__init__(self)
        #ObjectMover.__init__(self)
        
        self.addRender()
    def preRender(self):
        
        move.constraintCheckFunction()
'''        

class ObjectClipping():
    def __init__(self):
        self.isEnabled = False
        self.createMenu()
        self.clipping = False
        self.gridVis = False
        self.contourVis = False
        self.planeVis = False
        self.timer = vrTimer()
        
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")
        self.leftController.setVisualizationMode(Visualization_ControllerAndHand)
        self.rightController.setVisualizationMode(Visualization_ControllerAndHand)
        #vrImmersiveInteractionService.setDefaultInteractionsActive(1)

        
        padCenterClip = vrdVirtualTouchpadButton('padcenter', 0.0, 0.5, 0.0, 360.0)
        padUpperLeftClip = vrdVirtualTouchpadButton('padupleft', 0.5, 1.0, 270.0, 330.0)
        padLowerLeftClip = vrdVirtualTouchpadButton('paddownleft', 0.5, 1.0, 210.0, 270.0)
        padUpClip = vrdVirtualTouchpadButton('padup', 0.5, 1.0, 330.0, 30.0)
        padUpperRightClip = vrdVirtualTouchpadButton('padupright', 0.5, 1.0, 30.0, 90.0)
        padLowerRightClip = vrdVirtualTouchpadButton('paddownright', 0.5, 1.0, 90.0, 150.0)
        padDownClip = vrdVirtualTouchpadButton('paddown', 0.5, 1.0, 150.0, 210.0)

        # right controller
        self.rightController.addVirtualButton(padCenterClip, 'touchpad')
        self.rightController.addVirtualButton(padUpperLeftClip, 'touchpad')
        self.rightController.addVirtualButton(padLowerLeftClip, 'touchpad')
        self.rightController.addVirtualButton(padUpClip, 'touchpad')
        self.rightController.addVirtualButton(padUpperRightClip, 'touchpad')
        self.rightController.addVirtualButton(padLowerRightClip, 'touchpad')
        self.rightController.addVirtualButton(padDownClip, 'touchpad')
        
        multiButtonPadClip = vrDeviceService.createInteraction("MultiButtonPadClip")
        multiButtonPadClip.setSupportedInteractionGroups(["ClipGroup"])
        toolsMenuClip = vrDeviceService.getInteraction("Tools Menu")
        toolsMenuClip.addSupportedInteractionGroup("ClipGroup")
        
        #setting control action for right controller Pad
        
        self.leftUpperActionClip = multiButtonPadClip.createControllerAction("right-padupleft-pressed")
        self.leftDownActionClip = multiButtonPadClip.createControllerAction("right-paddownleft-pressed")
        self.upActionClip = multiButtonPadClip.createControllerAction("right-padup-pressed")
        self.downActionClip = multiButtonPadClip.createControllerAction("right-paddown-pressed")
        self.rightUpperActionClip = multiButtonPadClip.createControllerAction("right-padupright-pressed")
        self.rightDownActionClip = multiButtonPadClip.createControllerAction("right-paddownright-pressed")
        self.centerActionClip = multiButtonPadClip.createControllerAction("right-padcenter-pressed")
         
        teleport = vrDeviceService.getInteraction("Teleport")
        teleport.addSupportedInteractionGroup("ClipGroup")
        teleport.setControllerActionMapping("prepare" , "left-touchpad-touched")
        teleport.setControllerActionMapping("abort" , "left-touchpad-untouched")
        teleport.setControllerActionMapping("execute" , "left-touchpad-pressed")
        
        self.pointer = vrDeviceService.getInteraction("Pointer")
        self.pointer.addSupportedInteractionGroup("ClipGroup")        
        
        self.triggerRightPressed = multiButtonPadClip.createControllerAction("right-trigger-pressed")
        self.triggerRightReleased = multiButtonPadClip.createControllerAction("right-trigger-released")

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
        self.tool = vrImmersiveUiService.createTool("Tool_clip")
        self.tool.setText("Clip")
        self.tool.setCheckable(True)
        self.tool.setIcon(icon)
        self.tool.signal().checked.connect(self.clipEnable)
        self.tool.signal().unchecked.connect(self.clipDisable)
        
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
        
    def clipEnable(self):
        #global constXPressed
        #global constYPressed
        #global constZPressed
        global clippingControllerFound
        
        self.constXPressed = False
        self.constYPressed = False
        self.constZPressed = False
        allTools = vrImmersiveUiService.getTools()
         
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName() and tool.getName()[:5] == 'Tool_':
                tool.setChecked(False)
                tool.signal().unchecked.emit(None)
        print("Entering Clip Enabled")
        self.isEnabled = True
        setClippingShowManipulator(0) 
        
        
        vrDeviceService.setActiveInteractionGroup("ClipGroup")
        self.leftUpperActionClip.signal().triggered.connect(self.GridVis)
        self.leftDownActionClip.signal().triggered.connect(self.constX)
        self.upActionClip.signal().triggered.connect(self.PlaneVis)
        self.downActionClip.signal().triggered.connect(self.constY)
        self.rightUpperActionClip.signal().triggered.connect(self.ContourVis)
        self.rightDownActionClip.signal().triggered.connect(self.constZ)
        self.centerActionClip.signal().triggered.connect(self.ClippingState)
        
        self.triggerRightPressed.signal().triggered.connect(self.trigger_right_pressed)
        self.triggerRightReleased.signal().triggered.connect(self.trigger_right_released)

        if clippingControllerFound == True:
            self.newRightCon = findNode("VRController_Clip")
            self.rightController.setVisible(0)
            self.newRightCon.setActive(1)
            controllerPos = getTransformNodeTranslation(self.rightController.getNode(),1)
            setTransformNodeTranslation(self.newRightCon, controllerPos.x(), controllerPos.y(), controllerPos.z(), True)
            self.ClipControllerConstraint = vrConstraintService.createParentConstraint([self.rightController.getNode()], self.newRightCon, False)

        else:
            self.rightController.setVisible(1)
            
        self.originalPos = getTransformNodeTranslation(self.rightController.getNode(),1)

                
    def clipDisable(self):
        global clippingControllerFound
        #global constXPressed
        #global constYPressed
        #global constZPressed
        if self.isEnabled == False:
            print("Clip was not enabled before " )
            return
        

        allTools = vrImmersiveUiService.getTools()
        for tool in allTools:
            if tool.getIsInternal() == False and tool.getName() != self.tool.getName():
                tool.setCheckable(True) 
                #tool.setChecked(False)
        print("Clipping Disabled")
        self.isEnabled = False
        vrDeviceService.setActiveInteractionGroup("Locomotion")
        self.leftUpperActionClip.signal().triggered.disconnect(self.GridVis)
        self.leftDownActionClip.signal().triggered.disconnect(self.constX)
        self.upActionClip.signal().triggered.disconnect(self.PlaneVis)
        self.downActionClip.signal().triggered.disconnect(self.constY)
        self.rightUpperActionClip.signal().triggered.disconnect(self.ContourVis)
        self.rightDownActionClip.signal().triggered.disconnect(self.constZ)
        self.centerActionClip.signal().triggered.disconnect(self.ClippingState)
        
        self.triggerRightPressed.signal().triggered.disconnect(self.trigger_right_pressed)
        self.triggerRightReleased.signal().triggered.disconnect(self.trigger_right_released)    
                
        self.rightController.setVisible(1)
        if clippingControllerFound == True: 
            self.newRightCon.setActive(0)
            vrConstraintService.deleteConstraint(self.ClipControllerConstraint)
            setSwitchMaterialChoice("C_C_Icon_X", 0)
            setSwitchMaterialChoice("C_C_Icon_Y", 0)
            setSwitchMaterialChoice("C_C_Icon_Z", 0)

            print("Constraint deactivated")
            self.constXPressed = False
            self.constYPressed = False
            self.constZPressed = False
            
            
        self.timer.setActive(0)
    
        constraints = vrConstraintService.getConstraints()
        for constraint in constraints:
            vrConstraintService.deleteConstraint(constraint)

            
    def trigger_right_pressed(self):
        if self.clipping == True:
            self.timer.setActive(1)
            self.timer.connect(self.trigger_right_pressed)
            self.currentPos = getTransformNodeTranslation(self.newRightCon,1)
            #getClippingPlanePosition()
            #vrSessionService.sendPython("enableClippingPlane(1)")
            '''
            if self.constXPressed == True and self.constYPressed == True:
                
                x_y_clip_position = "%f,%f,%f" %(self.currentPos.x(), self.currentPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+x_y_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                
                
            elif self.constYPressed == True and self.constZPressed == True:
                
                y_z_clip_position = "%f,%f,%f" %(self.originalPos.x(), self.currentPos.y(),self.currentPos.z())
                vrSessionService.sendPython("point = Pnt3f("+y_z_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                        
            elif self.constXPressed == True and self.constZPressed == True:
                
                x_z_clip_position = "%f,%f,%f" %(self.currentPos.x(), self.originalPos.y(),self.currentPos.z())
                vrSessionService.sendPython("point = Pnt3f("+x_z_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
            '''        
            if self.constXPressed == True:
                
                x_clip_position = "%f,%f,%f" %(self.currentPos.x(), self.originalPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+x_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                #vrSessionService.sendPython("setClippingPlaneRotation(0,0,0)")
                    
            elif self.constYPressed == True:
                
                y_clip_position = "%f,%f,%f" %(self.originalPos.x(), self.currentPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+y_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                #vrSessionService.sendPython("setClippingPlaneRotation(0,0,0)")
                
            elif self.constZPressed == True:
    
                z_clip_position = "%f,%f,%f" %(self.originalPos.x(), self.originalPos.y(),self.currentPos.z())
                vrSessionService.sendPython("point = Pnt3f("+z_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                #vrSessionService.sendPython("setClippingPlaneRotation(0,90,0)")
    
            else:
                self.originalPos = getTransformNodeTranslation(self.newRightCon,1)
                
                #getClippingPlanePosition()
                clip_position = "%f,%f,%f" %(self.originalPos.x(), self.originalPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+str(clip_position)+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                
                self.originalRot = getTransformNodeRotation(self.newRightCon)
                #self.originalRot = self.newRightCon.getRotation()
                #print(self.originalRot)
                clip_rotation = "%f,%f,%f" %(self.originalRot.x()+90, self.originalRot.y(),self.originalRot.z())
                #vrSessionService.sendPython("point = Pnt3f("+str(clip_position)+")")
                vrSessionService.sendPython("setClippingPlaneRotation("+clip_rotation+")")

            
    def trigger_right_released(self):
        
        if self.clipping == True:
            self.timer.setActive(0)
            
            if self.constXPressed == True and self.constYPressed == True:
                
                x_y_clip_position = "%f,%f,%f" %(self.currentPos.x(), self.currentPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+x_y_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                
            elif self.constYPressed == True and self.constZPressed == True:
                
                y_z_clip_position = "%f,%f,%f" %(self.originalPos.x(), self.currentPos.y(),self.currentPos.z())
                vrSessionService.sendPython("point = Pnt3f("+y_z_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                        
            elif self.constXPressed == True and self.constZPressed == True:
                
                x_z_clip_position = "%f,%f,%f" %(self.currentPos.x(), self.originalPos.y(),self.currentPos.z())
                vrSessionService.sendPython("point = Pnt3f("+x_z_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                    
            elif self.constXPressed == True:
                
                x_clip_position = "%f,%f,%f" %(self.currentPos.x(), self.originalPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+x_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                    
            elif self.constYPressed == True:
                
                y_clip_position = "%f,%f,%f" %(self.originalPos.x(), self.currentPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+y_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                
            elif self.constZPressed == True:
    
                z_clip_position = "%f,%f,%f" %(self.originalPos.x(), self.originalPos.y(),self.currentPos.z())
                vrSessionService.sendPython("point = Pnt3f("+z_clip_position+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
            else:
                self.originalPos = getTransformNodeTranslation(self.newRightCon,1)
                #getClippingPlanePosition()
                clip_position = "%f,%f,%f" %(self.originalPos.x(), self.originalPos.y(),self.originalPos.z())
                vrSessionService.sendPython("point = Pnt3f("+str(clip_position)+")")
                vrSessionService.sendPython("setClippingPlanePosition(point)")
                
                self.originalRot = getTransformNodeRotation(self.newRightCon)
                #clip_rotation = "%f,%f,%f" %(self.originalRot.x(), self.originalRot.y(),self.originalRot.z())
                #vrSessionService.sendPython("point = Pnt3f("+str(clip_position)+")")
                #vrSessionService.sendPython("setClippingPlaneRotation("+clip_rotation+")")
            
    def constX(self):
        print("Constraint in X direction Active")
        #global constXPressed
        
        if self.constXPressed == False:
            self.constXPressed = True
            print("flag X pressed is: ", self.constXPressed)
            self.clipXConstraintON()
            vrSessionService.sendPython("setClippingPlaneRotation(0,0,90)")

        else:
            self.constXPressed = False
            self.clipXConstraintOFF()
            print("flag X pressed is: ", self.constXPressed)
                 
    def constY(self):
        #global constYPressed
        print("Constraint in Y direction Active")
        if self.constYPressed == False:
            self.constYPressed = True
            print("flag Y pressed is: ", self.constYPressed)
            self.clipYConstraintON()
            vrSessionService.sendPython("setClippingPlaneRotation(0,90,0)")

        else:
            self.constYPressed = False
            print("flag Y pressed is: ", self.constYPressed)
            self.clipYConstraintOFF()
            
   
    def constZ(self):
        #global constZPressed
        print("Constraint in Z direction Active")
        if self.constZPressed == False:
            self.constZPressed = True
            print("flag Z pressed is: ", self.constZPressed)
            self.clipZConstraintOFF()
            vrSessionService.sendPython("setClippingPlaneRotation(90,0,0)")


        else:
            self.constZPressed = False
            print("flag Z pressed is: ", self.constZPressed)
            self.clipZConstraintON() 
        
    def ClippingState(self):
        
        if self.clipping == False:
            enableClippingPlane(1)
            vrSessionService.sendPython("enableClippingPlane(1)")
            self.clipping = True
            setSwitchMaterialChoice("C_C_Clip", 1)
        else:
            enableClippingPlane(0)
            vrSessionService.sendPython("enableClippingPlane(0)")
            self.clipping = False
            setSwitchMaterialChoice("C_C_Clip", 0)
    
    def GridVis(self):
        if self.gridVis == False:
            setClippingGridVisualization(1, Vec3f(1,1,1))
            vrSessionService.sendPython("setClippingGridVisualization(1, Vec3f(1,1,1))")
            self.gridVis = True
            setSwitchMaterialChoice("C_C_Grid", 1)
        else:
            self.gridVis = False
            setClippingGridVisualization(0, Vec3f(1,1,1))
            vrSessionService.sendPython("setClippingGridVisualization(0, Vec3f(1,1,1))")
            setSwitchMaterialChoice("C_C_Grid", 0)
            
    
    def ContourVis(self):
        if self.contourVis == False:
            setClippingContourVisualization(1, Vec3f(0,0,0),5)
            vrSessionService.sendPython("setClippingContourVisualization(1, Vec3f(0,0,0),5)")
            self.contourVis = True
            setSwitchMaterialChoice("C_C_Contour", 1)
        else:
            self.contourVis = False
            vrSessionService.sendPython("setClippingContourVisualization(0, Vec3f(0,0,0),5)")
            setClippingContourVisualization(0, Vec3f(0,0,0),5)
            setSwitchMaterialChoice("C_C_Contour", 0)
            
    def PlaneVis(self):
        if self.planeVis == False:
            setClippingPlaneVisualization(1, Vec3f(0.16,0.16,0.28))
            vrSessionService.sendPython("setClippingPlaneVisualization(1, Vec3f(0.16,0.16,0.28))")
            self.planeVis = True
            setSwitchMaterialChoice("C_C_Plane", 1)
        else:
            self.planeVis = False
            vrSessionService.sendPython("setClippingPlaneVisualization(0, Vec3f(0.16,0.16,0.28))")
            setClippingPlaneVisualization(0, Vec3f(0.16,0.16,0.28))
            setSwitchMaterialChoice("C_C_Plane", 0)

    def clipXConstraintON(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_X", 1)
            setSwitchMaterialChoice("C_C_Icon_Y", 0)
            setSwitchMaterialChoice("C_C_Icon_Z", 0)

    def clipXConstraintOFF(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_X", 0)
                
    def clipYConstraintON(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_X", 0)
            setSwitchMaterialChoice("C_C_Icon_Y", 1)
            setSwitchMaterialChoice("C_C_Icon_Z", 0)
    
    def clipYConstraintOFF(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_Y", 0)
     
    def clipZConstraintON(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_X", 0)
            setSwitchMaterialChoice("C_C_Icon_Y", 0)
            setSwitchMaterialChoice("C_C_Icon_Z", 1)
    
    def clipZConstraintOFF(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_Z", 0)

    def clippingOFF(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_Clip", 0)
    
    def clippingON(self):
        if clippingControllerFound == True: 
            setSwitchMaterialChoice("C_C_Icon_Clip", 1)

clip = ObjectClipping()
