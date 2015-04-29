import math

from mathutils import Vector

from panel import panel
from character import character

from bge import logic

def vector_length(v):
    return math.sqrt(math.pow(v.x, 2) + math.pow(v.y, 2) + math.pow(v.z, 2))

class Robot(object):
    def __init__(self, controller):
        self.controller = controller
        self.owner = controller.owner
        self.motion = controller.actuators['Motion']
        scene = logic.getCurrentScene()
        self.arm = scene.objects['RobotArmature']
        self.state = 0
        self.owner['Robot'] = True
        self.front = scene.objects['RobotFront']

    def act(self):
        if not character:
            return;

        will_move = character.move_forward or character.move_back or \
            character.move_left or character.move_right
        frame = self.arm.getActionFrame()

        if self.state == 0 and will_move:
            self.arm.stopAction()
            self.arm.playAction('ArmatureAction', 0, 30,
                play_mode = logic.KX_ACTION_MODE_PLAY,
                speed = 2.0)
            self.state = 1
        if self.state == 1 and will_move and frame == 30:
            self.arm.stopAction()
            self.arm.playAction('ArmatureAction', 30, 90,
                play_mode = logic.KX_ACTION_MODE_LOOP,
                speed = 2.0)
            self.state = 2
        if self.state in (1, 2) and not will_move:
            self.arm.stopAction()
            self.arm.playAction('ArmatureAction', 90, 120,
                play_mode = logic.KX_ACTION_MODE_PLAY,
                speed = 2.0)
            self.state = 3
        if (self.state == 0 and frame < 120) or (self.state == 3 and frame == 120):
            self.arm.stopAction()
            self.arm.playAction('ArmatureAction', 120, 250,
                play_mode = logic.KX_ACTION_MODE_LOOP,
                speed = 2.0)
            self.state = 0

        velocity = list(character.global_velocity[:])
        if panel.reverse_x:
            velocity[0] *= -1
        if panel.reverse_y:
            velocity[1] *= -1

        self.motion.linV = velocity[0], velocity[1], self.owner.worldLinearVelocity.z
        self.motion.useLocalLinV = False
        direction = Vector((velocity[0], velocity[1], 0.0)).normalized()
        if vector_length(direction):
            self.front.worldPosition = self.owner.worldPosition + direction 
        self.controller.activate(self.motion)
    instance = None

def act(controller):
    if not Robot.instance:
        Robot.instance = Robot(controller)

    Robot.instance.act()
