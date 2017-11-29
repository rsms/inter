from ufoLib import fontInfoAttributesVersion3, validateFontInfoVersion3ValueForAttribute


class RelaxedInfo(object):

    """
    This object that sets only valid info values
    into the given info object.
    """

    def __init__(self, info):
        self._object = info

    def __getattr__(self, attr):
        if attr in fontInfoAttributesVersion3:
            return getattr(self._object, attr)
        else:
            return super(RelaxedInfo, self).__getattr__(attr)

    def __setattr__(self, attr, value):
        if attr in fontInfoAttributesVersion3:
            if validateFontInfoVersion3ValueForAttribute(attr, value):
                setattr(self._object, attr, value)
        else:
            super(RelaxedInfo, self).__setattr__(attr, value)


def copyAttr(src, srcAttr, dest, destAttr):
    if not hasattr(src, srcAttr):
        return
    value = getattr(src, srcAttr)
    setattr(dest, destAttr, value)
