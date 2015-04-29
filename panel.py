import input

import math

from bge import logic

class Panel(object):
    def __init__(self):
        self.scene = logic.getCurrentScene()
        self.reverse_x_button = self.scene.objects['ReverseXButton']
        self.reverse_y_button = self.scene.objects['ReverseYButton']
        self.camera = self.scene.objects['CommandPanelCamera']
        self.restore = None
        self.reverse_x = False
        self.reverse_y = False

    def enable(self):
        self.scene.active_camera = self.camera
        input.service.push_mouse_hooks({
            'ReverseXButton': lambda : self.toggle_x(),
            'ReverseYButton': lambda : self.toggle_y(),
            'CommandPanelExitButton': lambda : self.exit(),
        })
        input.service.push_keyboard_hooks({})

    def toggle_x(self):
        self.reverse_x = not self.reverse_x
        if self.reverse_x:
            self.reverse_x_button.playAction('ReverseXButtonAction', 0, 30,
                play_mode = logic.KX_ACTION_MODE_PLAY,
                layer = 0,
                speed = 5.0)
        else:
            self.reverse_x_button.playAction('ReverseXButtonAction', 30, 60,
                play_mode = logic.KX_ACTION_MODE_PLAY,
                layer = 1,
                speed = 5.0)

    def toggle_y(self):
        self.reverse_y = not self.reverse_y
        if self.reverse_y:
            self.reverse_y_button.playAction('ReverseYButtonAction', 0, 30,
                play_mode = logic.KX_ACTION_MODE_PLAY,
                layer = 0,
                speed = 5.0)
        else:
            self.reverse_y_button.playAction('ReverseYButtonAction', 30, 60,
                play_mode = logic.KX_ACTION_MODE_PLAY,
                layer = 0,
                speed = 5.0)

    def exit(self):
        input.service.pop_mouse_hooks()
        input.service.pop_keyboard_hooks()
        self.restore()

panel = Panel()

