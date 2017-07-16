#!/usr/bin/env python
from TweenSVG.SVGUtils import SVGUtils as SVU

t1 = list(SVU.path_parts("M71.3496,-72.7646C75.7115,-64.2831 81.1469,-53.7144 86.0413,-44.1974"))
t2 = list(SVU.path_parts("M57.6538,-143.908C59.6758,-133.569 61.9808,-120.09 63,-108 64.3441,-92.0566 64.3441,-87.9434 63,-72 62.2834,-63.4991 60.9311,-54.3119 59.4884,-46.0122"))

print(t1)
print(t2)

paths1, paths2, pos1, pos2 = SVU.split_paths_for_tweening(t1, t2)

print(paths1)
print(paths2)
print(pos1)
print(pos2)

print(list(SVU.path_string(p) for p in paths1))
print(list(SVU.path_string(p) for p in paths2))

print("=============================")


SVU.normalize_path_splits(paths1, paths2, pos1, pos2)
