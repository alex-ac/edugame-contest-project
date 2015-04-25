#########################################################
##                                                     ##
##     Shaft's fps character script for Blender 2.6x   ##
##                                                     ##
#########################################################


################## input vzriables ######################
#                                                       #
# obj['allowRun'] - allows player to run                #
#    0 - only walking allowed                           #
#    1 - running allowed                                #
#                                                       #
# obj['allowMove'] - denies any movement                #
#   0 - any movement denied                             #
#   1 - movenet allowed(if not denied by other input    #           <<<All this is not currently in use
#       var's)                                          #
#                                                       #
# obj['allowMouseLook'] - enables built-in mouse look   #
#   0 - mouse look disabled                             #
#   1 - mouse look enabled                              #
#                                                       #
# obj['allowJump'] - allows jumping                     #
#   0 - jumping allowed                                 #
#   1 - no jumping allowed                              #
#                                                       #
#########################################################


################## output explonation ###################
#                                                       #
# obj['walkingSpd'] - the current state of walking      #
#    0 - not moving                                     #
#    1 - walking                                        #
#    2 - running                                        #
#                                                       #
# obj['jumped'] the jump state                          #           <<<All this is not currently in use
#       var's)                                          #
#    0 - not performing a jump                          #
#    1 - is in air                                      #
#    2 - just jumped                                    #
#    3 - just landed                                    #
#                                                       #
# obj['crouched'] is the player crouching               #
#    0 - is not crouching                               #
#    1 - is crouching                                   #
#                                                       #
#########################################################



##################### conrtols ##########################

#world gravity (the one setten up in physics settings)
grav = 9.8
#mouse sensitivity, x/y
scale = 0.001, 0.001
#movement speed, walk/run/jump height/in air movement/max fall speed per frame
Mspeed = 2, 4, 4, 1, 0.2
#controls, see http://www.blender.org/documentation/blender_python_api_2_64a_release/bge.events.html for keys.
forward=    bge.events.WKEY
backward=   bge.events.SKEY
left=       bge.events.AKEY
right=      bge.events.DKEY
jump=       bge.events.SPACEKEY
crouch=     bge.events.LEFTCTRLKEY
run=        bge.events.LEFTSHIFTKEY
interact=   bge.events.EKEY
#character height (blender units), stand(+0.2 = eye height)/crouch(must be a bit bigger than physics sphere radius)
height = 0.6 , 0.2



###### init ######
co = bge.logic.getCurrentController()
obj = co.owner

if not obj['init']:
    obj['inAir'] = 0
    obj['init'] = 1
    obj['xOnJump'] = 0
    obj['yOnJump'] = 0
    obj['Mz'] = 0.0
    obj['spdOnJump'] = 0
    ray = co.sensors['ray']
    obj['x'],obj['y'],obj['z'] = ray.hitObject.localPosition
    obj['surf'] = ray.hitObject.name
    obj['standing'] = 1
    obj['rePhysNextFrame'] = 1  



     
###### Mouse Look ######


    
import bge
mouse = co.sensors["Mouse"]
lmotion = co.actuators["LMove"]
wmotion = co.actuators["WMove"]
cam = wmotion.owner
pos = [0,0]



def mousePos():#calculates the mouse position comparint to the screen centre.
   x = (int)(bge.render.getWindowWidth() / 2 - mouse.position[0]) * scale[0]
   y = (int)(bge.render.getWindowHeight() / 2 - mouse.position[1]) * scale[1]
   return (x, y)

pos[0],pos[1] = mousePos()

ori = cam.localOrientation[1][1]
if ori < -0.98:
    if pos[1] > 0:
        pos[1] = 0
if ori > 0.98:
    if pos[1] < 0:
        pos[1] = 0
if obj['allowMouseLook']:  
    wmotion.dRot = ((pos[1],0,0))                    
    lmotion.dRot = ((0,0,pos[0]))
    co.activate(lmotion)
    co.activate(wmotion)




bge.render.setMousePosition(int(bge.render.getWindowWidth() / 2), int(bge.render.getWindowHeight() / 2))




##### Keys ######
keyboard = bge.logic.keyboard
active = bge.logic.KX_SENSOR_ACTIVE
w=0
a=0
s=0
d=0
running=0
jumped=0
crouched = 0
if keyboard.events[forward] == active:
        w = 1
if keyboard.events[backward] == active:
        s = 1      
if keyboard.events[left] == active:
        a = 1
if keyboard.events[right] == active:
        d = 1 
if keyboard.events[run] == active:
        running = 1*obj['allowRun']
if keyboard.events[jump] == active:
        jumped = 1   
if keyboard.events[crouch] == active:
        crouched = 1    
                                          
obj['jumped'] = jumped#for output


        
##### Movement #####

import mathutils
ray = co.sensors['ray']
rayUp = co.sensors['rayUp']
head = co.sensors['activator'].owner
spaceAbove = co.sensors['crouch_sns']
fall = co.sensors['fall_sens']



def crouch():#changes the object dimensions and updates its phys mesh when crouching. returns the CORRECT crouched status
    if obj['rePhysNextFrame'] != 0:
        obj.reinstancePhysicsMesh()
        obj['rePhysNextFrame'] -= 1
                
    if not obj['standing'] and not crouched:
        if spaceAbove.positive:    
            obj.playAction('crouch(0-10)', 5, 10, 0, 0, 0, bge.logic.KX_ACTION_MODE_PLAY, 0, 0, 10)#this is a frame by frame pre-animated sequence changing the phys mesh dimensions
            head.playAction('crouch_head', 5, 10, 0, 0, 0, bge.logic.KX_ACTION_MODE_PLAY, 0, 0, 0.5)
            obj['standing'] = 1
            obj['rePhysNextFrame'] = 2
            return 0
        else:
            return 1
    
    if crouched and obj['standing']:
        obj.playAction('crouch(0-10)', 0, 5, 0, 0, 0, bge.logic.KX_ACTION_MODE_PLAY, 0, 0, 10)
        head.playAction('crouch_head', 0, 5, 0, 0, 0, bge.logic.KX_ACTION_MODE_PLAY, 0, 0, 0.5)
        obj['standing'] = 0
        obj['rePhysNextFrame'] = 2
        return 1
    
    return crouched


                      
def allignToSurface():#keeps the object staying on the moving surface
    surface = ray.hitObject
    if surface != None:
        xPos,yPos,zPos = surface.localPosition.x,surface.localPosition.y,surface.localPosition.z    
        movementOfSurface = mathutils.Vector((xPos-obj['x'],yPos-obj['y'],zPos-obj['z']))
        if surface.name == obj['surf']:
            obj.localPosition += movementOfSurface
        obj['x'],obj['y'],obj['z'] = xPos,yPos,zPos
        obj['surf'] = surface.name

        
        
def ungrav():#gets the gravitation for 1 frame(60fps)
    return grav/60


    
def zPos():#custom gravity and ground level allignement. returns the final z axis speed
    Mz = obj['Mz']
    ground = ray.hitPosition[2]
    ground = ground + height[crouched]
    if onGround() and not obj['inAir']:
        obj['Mz'] = 0
        obj.localPosition.z = ground
        return ungrav()
    else:
        if fall.positive:
            obj['Mz'] -= ungrav()
            return obj['Mz']
        else:           
            Mz = Mz - ungrav()
            obj.localPosition.z += Mz/60
            obj['Mz'] = Mz
            return ungrav()

        
        
def wasdMove():#returns the moving speed for x and y axes depending on is the ob running or walking.
    My = w-s
    Mx = d-a
    coefficent = 1 - 0.29*(Mx*My)*(Mx*My)
    Mx = Mx*coefficent*Mspeed[running*(1-crouched)] 
    My = My*coefficent*Mspeed[running*(1-crouched)]       
    return(Mx,My)



def onGround():#calculates if the object is standing on ground.
    selfHeight = obj.localPosition.z - ray.hitPosition[2]
    if selfHeight > height[crouched]-height[0] and selfHeight<height[crouched]+0.05:
        return(1)
    else:
        return(0)

    

def airMove():#returns the in air speed for x and y axes (if the ob is in air)
    if (obj.localLinearVelocity.y*obj.localLinearVelocity.y) < (Mspeed[obj['spdOnJump']]*Mspeed[obj['spdOnJump']]):
        My = (w-s)*Mspeed[3] + obj['yOnJump']
    else:
        My = obj['yOnJump']   
    if (obj.localLinearVelocity.x*obj.localLinearVelocity.x)  < (Mspeed[obj['spdOnJump']]*Mspeed[obj['spdOnJump']]):
        Mx = (d-a)*Mspeed[3] + obj['xOnJump']
    else:
        Mx = obj['xOnJump']    
    return (Mx,My)

crouched = crouch()
        
if onGround():
    Mx,My = wasdMove()
    if obj['inAir'] == 1:
        obj['inAir'] = 0
        obj['xOnJump'] = 0
        obj['yOnJump'] = 0
        obj['spdOnJump'] = 0
        obj['jumped'] = 3#for output
else:
        Mx,My = airMove()
    
if jumped and onGround() and not crouched and obj['allowJump']:
    obj['Mz'] = Mspeed[2]
    obj['xOnJump'] = obj.localLinearVelocity.x
    obj['yOnJump'] = obj.localLinearVelocity.y
    obj['inAir'] = 1
    obj['spdOnJump'] = running*(1-crouched)

if not obj['inAir'] and not onGround():
    obj['xOnJump'] = obj.localLinearVelocity.x
    obj['yOnJump'] = obj.localLinearVelocity.y
    obj['inAir'] = 1
    obj['spdOnJump'] = running*(1-crouched)
    Mx,My = airMove()
    obj['jumped'] = 2#for output
    
if obj['allowMove']:    
    obj.localLinearVelocity = [Mx,My,zPos()] 
    
allignToSurface() 
   
running *= obj['allowRun']


### Output ###
if (w-s)*(w-s) or (a-d)*(a-d):
    obj['walkingSpd'] = 1+running*obj['allowMove']
else:
    obj['walkingSpd'] = 0
#obj['jumped'] = obj['jumped'] #defined in code
obj['crouched'] = crouched 
obj['jumped'] = obj['jumped']*obj['allowJump']*obj['allowMove']  
