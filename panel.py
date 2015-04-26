import input

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
        print('toggle_x')
        self.reverse_x = not self.reverse_x
        self.reverse_x_button.applyMovement(
            (0, 0, -0.5 if self.reverse_x else 0.5), True)
    
    def toggle_y(self):
        print('toggle_y')
        self.reverse_y = not self.reverse_y
        self.reverse_y_button.applyMovement(
            (0, 0, -0.5 if self.reverse_y else 0.5), True)
    
    def exit(self):
        input.service.pop_mouse_hooks()
        input.service.pop_keyboard_hooks()
        self.restore()

panel = Panel()