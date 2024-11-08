"""
Copied the required parts from https://github.com/LuPro/SlabelFish.

@LuPro

Thank you very much for sharing your work!
However, you have not licensed your code, nor did you provide a way to dynamically import the
library.
Please file an issue in GitHub if you wish for me to remove this code from this repository and I
will gladly write my own encoder/decoder.
"""

from ._encoder import encode
from ._decoder import decode
from ._model import Slab, AssetData, AssetTransform
