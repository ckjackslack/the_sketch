import math
import random


# Helper function to map a value from one range to another
def map_value(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))


# Helper function to generate a random color
def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# Helper function to convert degrees to radians
def degrees_to_radians(degrees):
    return degrees * (math.pi / 180)


# Helper function to convert radians to degrees
def radians_to_degrees(radians):
    return radians * (180 / math.pi)


# Helper function to limit a value within a given range
def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)
