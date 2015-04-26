from bge import logic, render

import input
from panel import panel

import math

import bge

class Character(object):
    def __init__(self, controller):
        self.controller = controller
        self.owner = controller.owner
        self.ray_s = controller.sensors['Ray']
        self.motion = controller.actuators['Motion']
        self.velocity = (0.0, 0.0, 0.0)
        self.will_jump = False
        input.service.push_mouse_hooks({
            'Robot': lambda : self.robot_action(),
        })
        input.service.push_keyboard_hooks({
            'w': lambda x: self.forward(x),
            'a': lambda x: self.left(x),
            'd': lambda x: self.right(x),
            's': lambda x: self.back(x),
            ' ': lambda x: self.jump(x),
        })
        self.restore()

    def robot_action(self):
        panel.restore = lambda : self.restore()
        render.showMouse(True)
        input.service.lock_mouse = None
        self.move_forward = 0
        self.move_back = 0
        self.move_left = 0
        self.move_right = 0
        panel.enable()
    
    def restore(self):
        scene = logic.getCurrentScene()
        scene.active_camera = scene.objects['CharacterCamera']
        input.service.lock_mouse = self.owner
        render.showMouse(False)
        self.move_forward = 0
        self.move_back = 0
        self.move_left = 0
        self.move_right = 0

    def update_velocity(self):
        vector = (self.move_right - self.move_left, self.move_forward - self.move_back, 0)
        length = math.sqrt(math.pow(vector[0], 2) +
                           math.pow(vector[1], 2) +
                           math.pow(vector[2], 2))
        k = 2 if self.ray_s.positive else 1
        if (length):
            self.velocity = (vector[0] / length * k, vector[1] / length * k, 0.0)
        else:
            self.velocity = (0.0, 0.0, 0.0)
  
    def pool(self, controller):
        self.motion.linV = (self.velocity[0], self.velocity[1], 0.0)
        self.motion.useLocalLinV = True
        self.motion.force = (0.0, 0.0, 10000.0 if self.will_jump else 0.0)
        self.will_jump = False
        self.motion.useLocalForce = True
        controller.activate(self.motion)
    
    def forward(self, pressed):
        self.move_forward = int(pressed)
        self.update_velocity()
    def left(self, pressed):
        self.move_left = int(pressed)
        self.update_velocity()
    def right(self, pressed):
        self.move_right = int(pressed)
        self.update_velocity()
    def back(self, pressed):
        self.move_back = int(pressed)
        self.update_velocity()
    def jump(self, pressed):
        if self.ray_s.positive and pressed:
            self.will_jump = True

character = Character(logic.getCurrentController())

def init(controller):
    pass

def pool(controller):
    character.pool(controller)