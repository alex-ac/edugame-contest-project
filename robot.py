import math

from panel import panel
from character import character

class Robot(object):
    def __init__(self, controller):
        self.controller = controller
        self.owner = controller.owner
        self.motion = controller.actuators['Motion']
    
    def act(self):
        velocity = list(character.global_velocity[:])
        if panel.reverse_x:
            velocity[0] *= -1
        if panel.reverse_y:
            velocity[1] *= -1
        self.motion.linV = velocity[:]
        self.motion.useLocalLinV = False
        length = math.sqrt(math.pow(velocity[0], 2) +
                           math.pow(velocity[1], 2) +
                           math.pow(velocity[2], 2))
        if length:
            direction = (velocity[0]/length,
                         velocity[1]/length,
                         velocity[2]/length)
            self.owner.alignAxisToVect(direction, 1)
        self.controller.activate(self.motion)
    instance = None
     
def act(controller):
    if not Robot.instance:
        Robot.instance = Robot(controller)
    
    Robot.instance.act()
