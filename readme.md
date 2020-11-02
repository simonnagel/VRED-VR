# Python VR functions for VRED
### Improve your VRED VR experience with custom python functions
### Just copy and paste the python code to your VRED Sript Editor and press run

![](images/VRED-VR-drawLines.gif)

<br>



### Before you start:
To customized your VR Controller, please copy all the files from the folder [OSB](https://github.com/simonnagel/VRED-VR/tree/master/OSB) to your user\Documents\Autodesk\Automotive\VRED folder
<br>
This is highly recommended, otherwise you will __not__ see icons on the controller.
<br>
![](images/VRED-VR-ScreenshotOsbFiles.png)

<br>

### VRED-VR-drawLines.py - you can draw in VRED
You can use this script in VR or in Desktop Mode to Sketch on your High Quality Model in VRED.
The Color of your drawing line will automatically adapt to your Collaboration color.
Works ootb in Collaboration.

Just paste the script [VRED-VR-drawLines.py](https://github.com/simonnagel/VRED-VR/tree/master/VRED-VR-drawLines.py) in your VRED Script Editor and press run.

In Desktop Mode: 
- Press D to draw
- Press L to delete the last line 
- Press G to hide/toggle all the lines 

In VR: 
- Go to your VR Menu and choose Draw. 
- Use the Trigger to draw.
- Press the middle of the touchpad to change the draw mode.
- Press the left of the touchpad to delete the last line.
- Press the bototm of the touchpad to hide all lines.

VRED-drawLines:

![](images/VRED-VR-drawLines2.gif)


### VRED-VR-createNotes.py - you can create notes in VRED
You can use this script in VR to create Notes in your Scene. 
Customize the file VRControllerNotes_Notes.osb to change the shape of your Notes. You can add as many Notes as you want. Just place them below the Switch Node "Notes".

Works ootb in Collaboration.
Just paste the script [ VRED-VR-createNotes.py](https://github.com/simonnagel/VRED-VR/tree/master/ VRED-VR-createNotes.py) in your VRED Script Editor and press run.


In VR: 
- Go to your VR Menu and choose Notes.
- Use the Trigger to create a note.
- Press the middle of the touchpad to change the create mode.
- Press the left of the touchpad scale the active note smaller.
- Press the right of the touchpad scale the active note bigger.
- Press the top of the touchpad to toggle to the next note type.
- Press the bottom of the touchpad to active delete mode. Once deleted, you can hover with the ray over any note and press the trigger to delete

VRED-VR-createNotes:
![](images/VRED-VR-createNotes.gif)
