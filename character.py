from bge import logic, render
from mathutils import Vector

import input
from panel import panel

import math

import bge

class Character(object):
    def __init__(self):
        self.controller = None
        self.owner = None
        self.ray_s = None
        self.motion = None
        self.velocity = (0.0, 0.0, 0.0)
        self.global_velocity = (0.0, 0.0, 0.0)
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
        self.move_forward = 0
        self.move_back = 0
        self.move_left = 0
        self.move_right = 0
        
    def init(self, controller):
        self.controller = controller
        self.owner = controller.owner
        self.ray_s = controller.sensors['Ray']
        self.motion = controller.actuators['Motion']
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
        vector = Vector((self.move_right - self.move_left, self.move_forward - self.move_back, 0)).normalized()
        if self.ray_s.positive:
            self.velocity = vector * 3
        else:
            self.velocity = self.velocity
        self.global_velocity = self.owner.worldLinearVelocity
  
    def pool(self, controller):
        if not self.controller:
            return
        self.motion.linV = (self.velocity[0],
                            self.velocity[1],
                            self.owner.worldLinearVelocity.z)
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

character = Character()

def init(controller):
    character.init(controller)

def pool(controller):
    character.pool(controller)