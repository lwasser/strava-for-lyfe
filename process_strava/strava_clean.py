"""A module with helper functions to process data."""

from shapely.geometry import LineString, Point

def swap(x):
    coords = list(x.coords)
    # Swap each coordinate using list comprehension and create Points
    coords = [Point(t[1], t[0]) for t in coords]
    return LineString(coords)