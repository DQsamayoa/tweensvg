
from TweenSVG.Tweener import Tweener

def tween_svgs_from_filenames(filenames, duration='5s', group_matching=False, fadeout_early=False, fadein_late=False):
    tween = Tweener(duration=duration, group_matching=group_matching, fadein_late=fadein_late, fadeout_early=fadeout_early)
    for filename in filenames:
        tween.add_keyframe_from_file(filename)
    return tween.tweens()
