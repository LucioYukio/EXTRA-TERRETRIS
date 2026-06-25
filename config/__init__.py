import sys


if sys.platform == "emscripten":
    import pplay.sound

    class _DummySound:
        loop = False
        def __init__(self, *_):
            self.volume = 50
        def set_volume(self, v):
            self.volume = min(v, 100)
        def increase_volume(self, v):
            self.set_volume(self.volume + v)
        def decrease_volume(self, v):
            self.set_volume(self.volume - v)
        def is_playing(self):
            return False
        def pause(self):
            pass
        def unpause(self):
            pass
        def play(self):
            pass
        def stop(self):
            pass
        def set_repeat(self, r):
            self.loop = r
        def fadeout(self, _):
            pass

    pplay.sound.Sound = _DummySound
