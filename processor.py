import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Literal
from shapely.geometry import Polygon
from shapely.validation import make_valid
from shapesimilarity import shape_similarity
from math import sqrt

class Sound:
    def __init__(self, label: str, f1: int, f2: int):
        self.label = label
        self.f1 = f1
        self.f2 = f2

class FormantPolygon:
    def __init__(self, speaker: str, vowels: list[Sound]):
        self.speaker = speaker
        self.vowels = []

        for vwl in vowels:
            if vwl.f1 == 0 or vwl.f2 == 0:
                pass
            else:
                self.vowels.append(vwl)

    def __str__(self):
        output = f"{self.speaker}\nVowel\tF1\tF2\n"
        for vwl in self.vowels:
            output += f"{vwl.label}\t{vwl.f1}\t{vwl.f2}\n"

        return output

    def __len__(self):
        return len(self.vowels)

    def get_x_y(self):
        xpoints = []
        ypoints = []
        
        for sound in self.vowels:
            xpoints.append(sound.f1)
            ypoints.append(sound.f2)

        xpoints = np.array(xpoints)
        ypoints = np.array(ypoints)

        return xpoints, ypoints

    def get_centroid(self, method):
        xpoints, ypoints = NormalizedPolygon(self, method=method).get_x_y()
        coords = list(zip(xpoints, ypoints))
        coords.append(coords[0])

        centroid = Polygon(coords).centroid

        centroid_x, centroid_y = centroid.x, centroid.y
        
        return [centroid_x, centroid_y]

    def get_area(self, method):
        xpoints, ypoints = NormalizedPolygon(self, method=method).get_x_y()
        coords = list(zip(xpoints, ypoints))
        coords.append(coords[0])

        poly = Polygon(coords)

        if poly.is_valid:
            return poly.area
        else:
            poly = make_valid(poly)
            return poly.area
    
    def save_to_json(self):
        polygon_dict = {
            "speaker": self.speaker,
            "vowels": [
                {
                    "label": vwl.label,
                    "f1": vwl.f1,
                    "f2": vwl.f2
                } for vwl in self.vowels
            ]
        }

        return polygon_dict
    
    def filter_vowels(self, target_vowels):
        self.vowels = [vwl for vwl in self.vowels if vwl.label in target_vowels]

    @staticmethod
    def from_dict(data):
        vowels = [Sound(vwl["label"], vwl["f1"], vwl["f2"]) for vwl in data["vowels"]]

        return FormantPolygon(data["speaker"], vowels)

class NormalizedPolygon(FormantPolygon):
    def __init__(
            self,
            polygon: FormantPolygon,
            method: Literal["Z-score", "Bark"]="Z-score"
    ):
        self.speaker = polygon.speaker

        normalized = []
        if method == "Z-score":
            self.method = "Z-score"

            f1, f2 = polygon.get_x_y()
            f1_mean, f2_mean = np.mean(f1), np.mean(f2)
            f1_std, f2_std = np.std(f1), np.std(f2)

            for vwl in polygon.vowels:
                z_f1 = (vwl.f1 - f1_mean) / f1_std
                z_f2 = (vwl.f2 - f2_mean) / f2_std
                
                normalized.append(Sound(vwl.label, z_f1, z_f2))

            self.vowels = normalized
        elif method == "Bark":
            self.method = "Bark"
            
            for vwl in polygon.vowels:
                bark_f1 = (26.81 * vwl.f1) / (1960 + vwl.f1) - 0.53
                bark_f2 = (26.81 * vwl.f2) / (1960 + vwl.f2) - 0.53

                normalized.append(Sound(vwl.label, bark_f1, bark_f2))
            
            self.vowels = normalized
        else:
            self.vowels = polygon.vowels

def get_deviation(polygon1: FormantPolygon, polygon2: FormantPolygon = None, method: Literal["Z-score, Bark"] = "Z-score"):
    if polygon2 is None:
        
        polygon2 = FormantPolygon(speaker="За Іщенком", vowels=[Sound("а", 750, 1200),
                                                                Sound("е", 520, 1630),
                                                                Sound("и", 350, 2100),
                                                                Sound("і", 280, 2270),
                                                                Sound("у", 350, 600),
                                                                Sound("о", 450, 750)])
    
    polygon1, polygon2 = NormalizedPolygon(polygon1, method), NormalizedPolygon(polygon2, method)

    x1, y1 = polygon1.get_x_y()
    x2, y2 = polygon2.get_x_y()

    bark_polygon1_np = np.column_stack((x1, y1))
    bark_polygon2_np = np.column_stack((x2, y2))

    deviation = 1 - shape_similarity(bark_polygon1_np, bark_polygon2_np)
    
    return deviation

def centroid_distance(c1, c2):
    x1, y1, x2, y2 = *c1, *c2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

if __name__ == "__main__":
    ish = FormantPolygon(speaker="За Іщенком",
                         vowels=[
                            Sound("а", 750, 1200),
                            Sound("е", 520, 1630),
                            Sound("и", 350, 2100),
                            Sound("і", 280, 2270),
                            Sound("у", 350, 600),
                            Sound("о", 450, 750)
                         ])
    with open("arsenii.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    test_poly = FormantPolygon.from_dict(data)
    print(test_poly)
    s = test_poly.get_area("Bark")
    print(f"Площа (shapely): {s}")
    s = test_poly.get_centroid("Bark")
    print(f"Центроїд: {s}")

    print(f"\nІщенко deviation from Іщенко: {get_deviation(ish)}")
    print(f"Test deviation from Іщенко: {get_deviation(test_poly)}")