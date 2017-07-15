
from TweenSVG.Tweener import Tweener

def tween_svgs_from_filenames(filenames, duration='5s', group_matching=False):
    tween = Tweener(duration=duration, group_matching=group_matching)
    for filename in filenames:
        tween.add_keyframe_from_file(filename)
    return tween.tweens()
