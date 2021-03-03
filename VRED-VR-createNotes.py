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