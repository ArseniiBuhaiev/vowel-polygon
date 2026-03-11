import matplotlib.pyplot as plt
import numpy as np

class Sound():
    def __init__(self, name: str, f1: int, f2: int):
        self.name = name
        self.f1 = f1
        self.f2 = f2

class FormantPolygon():
    def __init__(self, speaker: str, vowels: list[Sound]):
        self.speaker = speaker
        self.vowels = vowels

    def get_x_y(self):
        xpoints = []
        ypoints = []
        
        for sound in self.vowels:
            xpoints.append(sound.f1)
            ypoints.append(sound.f2)

        xpoints = np.array(xpoints)
        ypoints = np.array(ypoints)

        return xpoints, ypoints