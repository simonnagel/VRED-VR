'''
Scripted by Simon Nagel
Use this Script in a collaboration session to filter/smooth the jittering camera movement of a HMD user. The image appear less shaky for the spectators.

How to use:
Open this scene.
Change the vrPCName to the computer name of YOUR VR Computer that runs the headset.
Change the collabIP to the IP Address in your network where your collaboration session runs
Save the scene.
Open it on two computers.
Run the Script.
Adjust the value filter. (5 = almost no filtering; 100 = very smooth filtering)


General Concept of the Script:
The transformation of a node called Ref_Object is stored in a list.
The average transformation of the last x frames will be used as new transformation for a node called Filtered_Object.
Keep in mind that the filter refers to the last x frames and not seconds. If you prefer to work in seconds, set the timer = vrTimer(0.04), which refers to 25 frames per second
The nodes Ref_Object and Filtered_Object are synced in collaboration.
The timer is only executed on the VR Computer.
A Camera is parented to the Filtered_Object. Activate it on the Spectators computer to see a smooth image on another collaboration computer.

'''

vrPcName = "VR1"
collabIP = "10.146.20.100"


import socket
hostname = socket.gethostname()
vrSessionService.join(collabIP, hostname)

### Add the strength of the filter here

filter = 50

#initialize values
#the findNode("") should not be part of the timer, as is costs performance
listPos = []
del listPos[:]
listRot = []
del listRot[:]
timer = vrTimer()
count = 0
persp= findNode("Perspective")
node = findNode("Ref_Object")
filterObj = findNode("Filtered_Object")
x = 0
y = 0
z = 0
rx = 0
ry = 0
rz = 0

#syncronize nodes in collaboration
vrSessionService.addNodeSync(node)
vrSessionService.addNodeSync(filterObj)

def cameraJitterFilter():
    global count
    global listPos
    global listRot
    global node
    global persp
    global x
    global y
    global z
    global rx
    global ry
    global rz 
    global filterObj
    
    #counter to have a change in timer
    count = count+1
    
    #copying the camera transformation to the Ref_Object Transformation
    perspPos = persp.getWorldTranslation()  
    perspRot = persp.getWorldRotation()  
    node.setWorldTranslation(perspPos[0],perspPos[1],perspPos[2])
    node.setRotation(perspRot[0],perspRot[1],perspRot[2])
       
    #add new values to the list
    pos = node.getWorldTranslation()
    rot = node.getWorldRotation()    
    listPos.append(pos)
    listRot.append(rot)

    #after x frames the oldest value of the list is deleted and the average of the transformation and rotation values is calculated and set to the Filtered_Obj
    if count>filter:
        listPos.pop(0)
        for i in range(filter):
            x = x + listPos[i][0]
            y = y + listPos[i][1]
            z = z + listPos[i][2]
        x =x/(filter+1)
        y =y/(filter+1)
        z =z/(filter+1)
        setTransformNodeTranslation(filterObj,x,y,z,1)

        listRot.pop(0)
        for i in range(filter):
            rx = rx + listRot[i][0]
            ry = ry + listRot[i][1]
            rz = rz + listRot[i][2]
        rx =rx/(filter+1)
        ry =ry/(filter+1)
        rz =rz/(filter+1)
        setTransformNodeRotation(filterObj,rx,ry,rz)

timer.connect("cameraJitterFilter()") 

# runs the timer on YOUR VR Computer that runs the headset.
if hostname == vrPcName:
    timer.setActive(true)
    selectCamera("Perspective")
    setDisplayMode(VR_DISPLAY_OPEN_VR)
else:
    selectCamera("Filter_Cam")
