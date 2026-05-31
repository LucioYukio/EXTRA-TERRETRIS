from pplay import mouse as m

class Mouse(m.Mouse):
    def __init__(self):
        super().__init__()
        self._ticks_pressed : int = 0

    def update(self):
        if self.is_button_pressed(1) or self.is_button_pressed(2) or self.is_button_pressed(3):
            self._ticks_pressed += 1
        else:
            self._ticks_pressed = 0

    def is_button_just_pressed(self, button: int):
        self.update()
        return (self._ticks_pressed == 1) and self.is_button_pressed(button)