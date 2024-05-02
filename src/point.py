# A class of a point that has latitude and longitude
class Point():
    lat=""
    lon=""
    def __init__(self, latitude, longitude):
        setattr(self, "lat", latitude)
        setattr(self, "lon", longitude)
