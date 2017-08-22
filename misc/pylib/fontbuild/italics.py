# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import math

from fontTools.misc.transform import Transform
import numpy as np
from numpy.linalg import norm
from scipy.sparse.linalg import cg
from scipy.ndimage.filters import gaussian_filter1d as gaussian
from scipy.cluster.vq import vq, whiten

from fontbuild.alignpoints import alignCorners
from fontbuild.curveFitPen import fitGlyph, segmentGlyph


def italicizeGlyph(f, g, angle=10, stemWidth=185, meanYCenter=-825, narrowAmount=1):
    unic = g.unicode #save unicode

    glyph = f[g.name]
    slope = np.tanh(math.pi * angle / 180)

    # determine how far on the x axis the glyph should slide
    # to compensate for the slant.
    # meanYCenter:
    #   -600 is a magic number that assumes a 2048 unit em square,
    #   and -825 for a 2816 unit em square. (UPM*0.29296875)
    m = Transform(1, 0, slope, 1, 0, 0)
    xoffset, junk = m.transformPoint((0, meanYCenter))
    m = Transform(narrowAmount, 0, slope, 1, xoffset, 0)

    if len(glyph) > 0:
        g2 = italicize(f[g.name], angle, xoffset=xoffset, stemWidth=stemWidth)
        f.insertGlyph(g2, g.name)

    transformFLGlyphMembers(f[g.name], m)

    if unic > 0xFFFF: #restore unicode
        g.unicode = unic


def italicize(glyph, angle=12, stemWidth=180, xoffset=-50):
    CURVE_CORRECTION_WEIGHT = .03
    CORNER_WEIGHT = 10

    # decompose the glyph into smaller segments
    ga, subsegments = segmentGlyph(glyph,25)
    va, e  = glyphToMesh(ga)
    n = len(va)
    grad = mapEdges(lambda a,(p,n): normalize(p-a), va, e)
    cornerWeights = mapEdges(lambda a,(p,n): normalize(p-a).dot(normalize(a-n)), grad, e)[:,0].reshape((-1,1))
    smooth = np.ones((n,1)) * CURVE_CORRECTION_WEIGHT

    controlPoints = findControlPointsInMesh(glyph, va, subsegments)
    smooth[controlPoints > 0] = 1
    smooth[cornerWeights < .6] = CORNER_WEIGHT
    # smooth[cornerWeights >= .9999] = 1

    out = va.copy()
    hascurves = False
    for c in glyph.contours:
        for s in c.segments:
            if s.type == "curve":
                hascurves = True
                break
        if hascurves:
            break
    if stemWidth > 100:
        outCorrected = skewMesh(recompose(skewMesh(out, angle * 1.6), grad, e, smooth=smooth), -angle * 1.6)
        # out = copyMeshDetails(va, out, e, 6)
    else:
        outCorrected = out

    # create a transform for italicizing
    normals = edgeNormals(out, e)
    center = va + normals * stemWidth * .4
    if stemWidth > 130:
        center[:, 0] = va[:, 0] * .7 + center[:,0] * .3
    centerSkew = skewMesh(center.dot(np.array([[.97,0],[0,1]])), angle * .9)

    # apply the transform
    out = outCorrected + (centerSkew - center)
    out[:,1] = outCorrected[:,1]

    # make some corrections
    smooth = np.ones((n,1)) * .1
    out = alignCorners(glyph, out, subsegments)
    out = copyMeshDetails(skewMesh(va, angle), out, e, 7, smooth=smooth)
    # grad = mapEdges(lambda a,(p,n): normalize(p-a), skewMesh(outCorrected, angle*.9), e)
    # out = recompose(out, grad, e, smooth=smooth)

    out = skewMesh(out, angle * .1)
    out[:,0] += xoffset
    # out[:,1] = outCorrected[:,1]
    out[va[:,1] == 0, 1] = 0
    gOut = meshToGlyph(out, ga)
    # gOut.width *= .97
    # gOut.width += 10
    # return gOut

    # recompose the glyph into original segments
    return fitGlyph(glyph, gOut, subsegments)


def transformFLGlyphMembers(g, m, transformAnchors = True):
    # g.transform(m)
    g.width = g.width * m[0]
    p = m.transformPoint((0,0))
    for c in g.components:
        d = m.transformPoint(c.offset)
        c.offset = (d[0] - p[0], d[1] - p[1])
    if transformAnchors:
        for a in g.anchors:
                aa = m.transformPoint((a.x,a.y))
                a.x  = aa[0]
                # a.x,a.y = (aa[0] - p[0], aa[1] - p[1])
                # a.x = a.x - m[4]


def glyphToMesh(g):
    points = []
    edges = {}
    offset = 0
    for c in g.contours:
        if len(c) < 2:
            continue
        for i,prev,next in rangePrevNext(len(c)):
            points.append((c[i].points[0].x, c[i].points[0].y))
            edges[i + offset] = np.array([prev + offset, next + offset], dtype=int)
        offset += len(c)
    return np.array(points), edges


def meshToGlyph(points, g):
    g1 = g.copy()
    j = 0
    for c in g1.contours:
        if len(c) < 2:
            continue
        for i in range(len(c)):
            c[i].points[0].x = points[j][0]
            c[i].points[0].y = points[j][1]
            j += 1
    return g1


def quantizeGradient(grad, book=None):
    if book == None:
        book = np.array([(1,0),(0,1),(0,-1),(-1,0)])
    indexArray = vq(whiten(grad), book)[0]
    out = book[indexArray]
    for i,v in enumerate(out):
        out[i] = normalize(v)
    return out


def findControlPointsInMesh(glyph, va, subsegments):
    controlPointIndices = np.zeros((len(va),1))
    index = 0
    for i,c in enumerate(subsegments):
        segmentCount = len(glyph.contours[i].segments) - 1
        for j,s in enumerate(c):
            if j < segmentCount:
                if glyph.contours[i].segments[j].type == "line":
                    controlPointIndices[index] = 1
            index += s[1]
    return controlPointIndices


def recompose(v, grad, e, smooth=1, P=None, distance=None):
    n = len(v)
    if distance == None:
        distance = mapEdges(lambda a,(p,n): norm(p - a), v, e)
    if (P == None):
        P = mP(v,e)
        P += np.identity(n) * smooth
    f = v.copy()
    for i,(prev,next) in e.iteritems():
        f[i] = (grad[next] * distance[next] - grad[i] * distance[i])
    out = v.copy()
    f += v * smooth
    for i in range(len(out[0,:])):
        out[:,i] = cg(P, f[:,i])[0]
    return out


def mP(v,e):
    n = len(v)
    M = np.zeros((n,n))
    for i, edges in e.iteritems():
        w = -2 / float(len(edges))
        for index in edges:
            M[i,index] = w
        M[i,i] = 2
    return M


def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v/n


def mapEdges(func,v,e,*args):
    b = v.copy()
    for i, edges in e.iteritems():
        b[i] = func(v[i], [v[j] for j in edges], *args)
    return b


def getNormal(a,b,c):
    "Assumes TT winding direction"
    p = np.roll(normalize(b - a), 1)
    n = -np.roll(normalize(c - a), 1)
    p[1] *= -1
    n[1] *= -1
    # print p, n, normalize((p + n) * .5)
    return normalize((p + n) * .5)


def edgeNormals(v,e):
    "Assumes a mesh where each vertex has exactly least two edges"
    return mapEdges(lambda a,(p,n) : getNormal(a,p,n),v,e)


def rangePrevNext(count):
    c = np.arange(count,dtype=int)
    r = np.vstack((c, np.roll(c, 1), np.roll(c, -1)))
    return r.T


def skewMesh(v,angle):
    slope = np.tanh([math.pi * angle / 180])
    return v.dot(np.array([[1,0],[slope,1]]))


def labelConnected(e):
    label = 0
    labels = np.zeros((len(e),1))
    for i,(prev,next) in e.iteritems():
        labels[i] = label
        if next <= i:
            label += 1
    return labels


def copyGradDetails(a,b,e,scale=15):
    n = len(a)
    labels = labelConnected(e)
    out = a.astype(float).copy()
    for i in range(labels[-1]+1):
        mask = (labels==i).flatten()
        out[mask,:] = gaussian(b[mask,:], scale, mode="wrap", axis=0) + a[mask,:] - gaussian(a[mask,:], scale, mode="wrap", axis=0)
    return out


def copyMeshDetails(va,vb,e,scale=5,smooth=.01):
    gradA = mapEdges(lambda a,(p,n): normalize(p-a), va, e)
    gradB = mapEdges(lambda a,(p,n): normalize(p-a), vb, e)
    grad = copyGradDetails(gradA, gradB, e, scale)
    grad = mapEdges(lambda a,(p,n): normalize(a), grad, e)
    return recompose(vb, grad, e, smooth=smooth)


def condenseGlyph(glyph, scale=.8, stemWidth=185):
    ga, subsegments = segmentGlyph(glyph, 25)
    va, e  = glyphToMesh(ga)
    n = len(va)

    normals = edgeNormals(va,e)
    cn = va.dot(np.array([[scale, 0],[0,1]]))
    grad = mapEdges(lambda a,(p,n): normalize(p-a), cn, e)
    # ograd = mapEdges(lambda a,(p,n): normalize(p-a), va, e)

    cn[:,0] -= normals[:,0] * stemWidth * .5 * (1 - scale)
    out = recompose(cn, grad, e, smooth=.5)
    # out = recompose(out, grad, e, smooth=.1)
    out = recompose(out, grad, e, smooth=.01)

    # cornerWeights = mapEdges(lambda a,(p,n): normalize(p-a).dot(normalize(a-n)), grad, e)[:,0].reshape((-1,1))
    #     smooth = np.ones((n,1)) * .1
    #     smooth[cornerWeights < .6] = 10
    #
    #     grad2 = quantizeGradient(grad).astype(float)
    #     grad2 = copyGradDetails(grad, grad2, e, scale=10)
    #     grad2 = mapEdges(lambda a,e: normalize(a), grad2, e)
    #     out = recompose(out, grad2, e, smooth=smooth)
    out[:,0] += 15
    out[:,1] = va[:,1]
    # out = recompose(out, grad, e, smooth=.5)
    gOut = meshToGlyph(out, ga)
    gOut = fitGlyph(glyph, gOut, subsegments)
    for i,seg in enumerate(gOut):
        gOut[i].points[0].y = glyph[i].points[0].y
    return gOut
