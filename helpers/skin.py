from random import shuffle


SKIN = list(range(1, 15))
shuffle(SKIN)

def get_skin():
    return SKIN[:]

def reset_skin():
    global SKIN
    shuffle(SKIN)

def set_skin(skin):
    global SKIN
    SKIN = list(skin)