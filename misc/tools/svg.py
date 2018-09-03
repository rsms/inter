# encoding: utf8
#
# The MIT License
#
# Copyright (c) 2010 Type Supply LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# https://github.com/typesupply/ufo2svg
#
from __future__ import absolute_import
from fontTools.pens.basePen import BasePen


def valueToString(v):
    """
    >>> valueToString(0)
    '0'
    >>> valueToString(10)
    '10'
    >>> valueToString(-10)
    '-10'
    >>> valueToString(0.1)
    '0.1'
    >>> valueToString(0.0001)
    '0.0001'
    >>> valueToString(0.00001)
    '0'
    >>> valueToString(10.0001)
    '10.0001'
    >>> valueToString(10.00001)
    '10'
    """
    if int(v) == v:
        v = "%d" % (int(v))
    else:
        v = "%.4f" % v
        # strip unnecessary zeros
        # there is probably an easier way to do this
        compiled = []
        for c in reversed(v):
            if not compiled and c == "0":
                continue
            compiled.append(c)
        v = "".join(reversed(compiled))
        if v.endswith("."):
            v = v[:-1]
        if not v:
            v = "0"
    return v


def pointToString(pt):
    # return " ".join([valueToString(i) for i in pt])
    return valueToString(pt[0]) + " " + valueToString(pt[1])


class SVGPathPen(BasePen):

    def __init__(self, glyphSet, yMul):
        BasePen.__init__(self, glyphSet)
        self._commands = []
        self._lastCommand = None
        self._lastX = None
        self._lastY = None
        self._yMul = yMul

    # def pointToString(self, pt):
    #     pts = []
    #     n = 0
    #     for i in pt:
    #         if n == 1:
    #             i = i * self._yMul
    #         pts.append(valueToString(i))
    #         n = n + 1
    #     return " ".join(pts)


    def pt(self, pt1):
        return (pt1[0], pt1[1] * self._yMul)


    def _handleAnchor(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen.moveTo((10, 10))
        >>> pen._commands
        ['M10 10']
        """
        if self._lastCommand == "M":
            self._commands.pop(-1)

    def _moveTo(self, pt):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen._commands
        ['M0 0']

        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 0))
        >>> pen._commands
        ['M10 0']

        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 10))
        >>> pen._commands
        ['M0 10']
        """
        pt = self.pt(pt)
        self._handleAnchor()
        t = "M%s" % (pointToString(pt))
        self._commands.append(t)
        self._lastCommand = "M"
        self._lastX, self._lastY = pt

    def _lineTo(self, pt):
        """
        # duplicate point
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((10, 10))
        >>> pen._commands
        ['M10 10']

        # vertical line
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((10, 0))
        >>> pen._commands
        ['M10 10', 'V0']

        # horizontal line
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((0, 10))
        >>> pen._commands
        ['M10 10', 'H0']

        # basic
        >>> pen = SVGPathPen(None)
        >>> pen.lineTo((70, 80))
        >>> pen._commands
        ['L70 80']

        # basic following a moveto
        >>> pen = SVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen.lineTo((10, 10))
        >>> pen._commands
        ['M0 0', ' 10 10']
        """
        pt = self.pt(pt)
        x, y = pt
        # duplicate point
        if x == self._lastX and y == self._lastY:
            return
        # vertical line
        elif x == self._lastX:
            cmd = "V"
            pts = valueToString(y)
        # horizontal line
        elif y == self._lastY:
            cmd = "H"
            pts = valueToString(x)
        # previous was a moveto
        elif self._lastCommand == "M":
            cmd = None
            pts = " " + pointToString(pt)
        # basic
        else:
            cmd = "L"
            pts = pointToString(pt)
        # write the string
        t = ""
        if cmd:
            t += cmd
            self._lastCommand = cmd
        t += pts
        self._commands.append(t)
        # store for future reference
        self._lastX, self._lastY = pt

    def _curveToOne(self, pt1, pt2, pt3):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.curveTo((10, 20), (30, 40), (50, 60))
        >>> pen._commands
        ['C10 20 30 40 50 60']
        """
        pt1 = self.pt(pt1)
        pt2 = self.pt(pt2)
        pt3 = self.pt(pt3)
        t = "C"
        t += pointToString(pt1) + " "
        t += pointToString(pt2) + " "
        t += pointToString(pt3)
        self._commands.append(t)
        self._lastCommand = "C"
        self._lastX, self._lastY = pt3

    def _qCurveToOne(self, pt1, pt2):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.qCurveTo((10, 20), (30, 40))
        >>> pen._commands
        ['Q10 20 30 40']
        """
        assert pt2 is not None
        pt1 = self.pt(pt1)
        pt2 = self.pt(pt2)
        t = "Q"
        t += pointToString(pt1) + " "
        t += pointToString(pt2)
        self._commands.append(t)
        self._lastCommand = "Q"
        self._lastX, self._lastY = pt2

    def _closePath(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.closePath()
        >>> pen._commands
        ['Z']
        """
        self._commands.append("Z")
        self._lastCommand = "Z"
        self._lastX = self._lastY = None

    def _endPath(self):
        """
        >>> pen = SVGPathPen(None)
        >>> pen.endPath()
        >>> pen._commands
        ['Z']
        """
        self._closePath()
        self._lastCommand = None
        self._lastX = self._lastY = None

    def getCommands(self):
        return "".join(self._commands)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
