from magiccube import Cube
from pyTwistyScrambler import scrambler333

cube = Cube(3)
cube.rotate("Z2")
print(scram := scrambler333.get_WCA_scramble())
cube.rotate(scram)
print(cube)