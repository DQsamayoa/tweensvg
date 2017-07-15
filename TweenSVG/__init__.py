
from TweenSVG.Tweener import Tweener

def tween_svgs_from_filenames(filenames):
    tween = Tweener()
    for filename in filenames:
        tween.add_keyframe_from_file(filename)
    return tween.tweens()
