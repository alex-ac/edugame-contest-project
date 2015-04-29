from bge import render, logic, events

import math

class Input(object):
    def __init__(self):
        self.mouse_click_s = None
        self.mouse_move_s = None
        self.keyboard_s = None
        self.joystick_s = None

        self.lock_mouse = None
        self.mouse_sensitivity = 0.001
        self.raycast_distance = 1000.0
        render.showMouse(True)

        self.keyboard_hooks = []
        self.mouse_hooks = []
        self.joystick_hooks = []

    def mouse_click(self, controller):
        if not self.mouse_click_s:
            self.mouse_click_s = controller.sensors['MouseClick']
        if self.mouse_click_s.getButtonStatus(events.LEFTMOUSE) != \
            logic.KX_INPUT_JUST_RELEASED:
            return
        scene = logic.getCurrentScene()
        camera = scene.active_camera
        width, height = render.getWindowWidth(), render.getWindowHeight()
        x = self.mouse_click_s.position[0] / width
        y = self.mouse_click_s.position[1] / height

        target = camera.getScreenRay(x, y, self.raycast_distance)
        if target == None or len(self.mouse_hooks) == 0:
            return
        for name in self.mouse_hooks[-1]:
            if name == target.name:
                self.mouse_hooks[-1][name]()
                break

    def mouse_move(self, controller):
        if not self.mouse_move_s:
            self.mouse_move_s = controller.sensors['MouseMove']
        width, height = render.getWindowWidth(), render.getWindowHeight()
        x = (width / 2 - self.mouse_move_s.position[0]) * self.mouse_sensitivity
        y = (height / 2 - self.mouse_move_s.position[1]) * self.mouse_sensitivity

        if self.lock_mouse:
            if 'rotations' not in self.lock_mouse:
                self.lock_mouse['rotations'] = [math.pi / 2, 0, 0]
            rotations = self.lock_mouse['rotations']
            if (rotations[0] + y > math.pi) or \
                (rotations[0] + y < 0):
                y = 0
            rotations[2] += x
            rotations[0] += y
            self.lock_mouse.localOrientation = (0.0, 0.0, rotations[2])
            logic.getCurrentScene().active_camera.localOrientation = (rotations[0], 0.0, 0.0)

            render.setMousePosition(int(width / 2), int(height / 2))

    def keyboard(self, controller):
        if not self.keyboard_s:
            self.keyboard_s = controller.sensors['Keyboard']
        if not len(self.keyboard_hooks):
            return
        shift = self.keyboard_s.getKeyStatus(events.LEFTSHIFTKEY) == logic.KX_INPUT_ACTIVE or \
                self.keyboard_s.getKeyStatus(events.RIGHTSHIFTKEY) == logic.KX_INPUT_ACTIVE
        for event in self.keyboard_s.events:
            if event[1] in (logic.KX_INPUT_JUST_ACTIVATED,
                            logic.KX_INPUT_JUST_RELEASED,
                            logic.KX_INPUT_ACTIVE):
                name = events.EventToCharacter(event[0], shift)
                if not name:
                    name = events.EventToString(event[0])
                if not name:
                    continue
                for hook in self.keyboard_hooks[-1]:
                    if hook == name:
                        self.keyboard_hooks[-1][hook](logic.KX_INPUT_JUST_RELEASED != event[1])
                        break

    #def joystick(self):
    #    if not len(self.joystick_hooks):
    #        return
    #    hooks = self.joystick_hooks[-1!
    #    if 'axis' in hooks:
    #        axis_values = self.joystick_s.axisValues
    #        for i in range(len(hooks['axis'])):
    #            if i == len(axis_values):
    #                break
    #            hooks['axis'][i](axis_values[i])
    #
    #    if 'hat' in hooks:
    #        hat

    def push_keyboard_hooks(self, hooks):
        self.keyboard_hooks.append(hooks)

    def pop_keyboard_hooks(self):
        self.keyboard_hooks.pop()

    def push_mouse_hooks(self, hooks):
        self.mouse_hooks.append(hooks)

    def pop_mouse_hooks(self):
        self.mouse_hooks.pop()

    def push_joystick_hooks(self, hooks):
        self.joystick_hooks.append(hooks)

    def pop_joystick_hooks(self):
        self.joystick_hooks.pop()

service = Input()

def mouse_click(controller):
    service.mouse_click(controller)

def mouse_move(controller):
    service.mouse_move(controller)

def keyboard(controller):
    service.keyboard(controller)

def joystick(controller):
    #service.joystick()
    pass

