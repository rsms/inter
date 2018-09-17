// constants
var kSVGScale  = 0.1 // how bmuch metrics are scaled in the SVGs
var kGlyphSize = 346 // at kSVGScale. In sync with CSS and SVGs
var kUPM       = 2816


function pxround(n) {
  return Math.round(n * 2) / 2
}

// forEachElement(selector, fun)
// forEachElement(parent, selector, fun)
function eachElement(parent, selector, fun) {
  if (typeof selector == 'function') {
    fun = selector
    selector = parent
    parent = document
  }
  Array.prototype.forEach.call(parent.querySelectorAll(selector), fun)
}


if (!isMac) {
  eachElement('kbd', function(e) {
    if (e.innerText == '\u2318') {
      e.innerText = 'Ctrl'
    }
  })
}

function httpget(url, cb) {
  var req = new XMLHttpRequest();
  req.addEventListener("load", function() {
    cb(this.responseText, this)
  })
  req.open("GET", url)
  req.send()
}

function fetchGlyphInfo(cb) {
  httpget("../lab/glyphinfo.json", function(res) {
    cb(JSON.parse(res).glyphs)
  })
}

function fetchMetrics(cb) {
  httpget("metrics.json", function(res) {
    cb(JSON.parse(res))
  })
}

var glyphInfo = null
var glyphMetrics = null

function initMetrics(data) {
  // metrics.json uses a compact format with numerical glyph indentifiers
  // in order to minimize file size.
  // We expand the glyph IDs to glyph names here.
  var nameIds = data.nameids
  // console.log(data)
  
  var metrics = {}
  var metrics0 = data.metrics
  Object.keys(metrics0).forEach(function (id) {
    var name = nameIds[id]
    var v = metrics0[id]
    // v : [width, advance, left, right]
    metrics[name] = {
      width: v[0],
      advance: v[1],
      left: v[2],
      right: v[3]
    }
  })

  var kerningLeft = {}  // { glyphName: {rightGlyphName: kerningValue, ...}, ... }
  var kerningRight = {}
  data.kerning.forEach(function (t) {
    // each entry looks like this:
    //  [leftGlyphId, rightGlyphId, kerningValue]
    var leftName = nameIds[t[0]]
    if (!leftName) {
      console.error('nameIds missing', t[0])
    }
    var rightName = nameIds[t[1]]
    if (!rightName) {
      console.error('nameIds missing', t[1])
    }
    var kerningValue = t[2]
    
    var lm = kerningLeft[leftName]
    if (!lm) {
      kerningLeft[leftName] = lm = {}
    }
    lm[rightName] = kerningValue

    var rm = kerningRight[rightName]
    if (!rm) {
      kerningRight[rightName] = rm = {}
    }
    rm[leftName] = kerningValue
  })

  glyphMetrics = {
    metrics: metrics,
    kerningLeft: kerningLeft,
    kerningRight: kerningRight,
  }
  // console.log('glyphMetrics', glyphMetrics)
}

function fetchAll(cb) {
  var i = 0
  var res = {}
  var decr = function(){
    if (--i == 0) {
      cb(res)
    }
  }
  i++
  fetchGlyphInfo(function(r){ glyphInfo = r; decr() })
  i++
  fetchMetrics(function(r){
    initMetrics(r)
    decr()
  })
}

fetchAll(render)


var styleSheet = document.styleSheets[document.styleSheets.length-1]
var glyphRule, lineRule, zeroWidthAdvRule
var currentScale = 0
var defaultSingleScale = 1
var currentSingleScale = 1
var defaultGridScale = 0.4
var currentGridScale = defaultGridScale
var glyphs = document.getElementById('glyphs')

function updateLayoutAfterChanges() {
  var height = parseInt(window.getComputedStyle(glyphs).height)
  var margin = height - (height * currentScale)
  // console.log('scale:', currentScale, 'height:', height, 'margin:', margin)
  if (currentScale > 1) {
    glyphs.style.marginBottom = null
  } else {
    glyphs.style.marginBottom = -margin + 'px'
  }
}

function setScale(scale) {
  if (queryString.iframe !== undefined) {
    scale = 0.11
  } else if (queryString.g) {
    scale = Math.min(Math.max(1, scale), 3)
  } else {
    scale = Math.min(Math.max(0.05, scale), 3)
  }

  if (currentScale == scale) {
    return
  }

  currentScale = scale
  if (queryString.g) {
    currentSingleScale = scale
  } else {
    currentGridScale = scale
  }

  var hairline = Math.ceil(1 / window.devicePixelRatio / scale)
  var spacing = Math.ceil(6 / scale)

  var s = glyphs.style
  if (queryString.g || queryString.iframe !== undefined) {
    s.paddingLeft = null
  } else {
    s.paddingLeft = spacing + 'px'
  }
  s.width = (100 / scale) + '%'
  s.transform = 'scale(' + scale + ')'

  if (!glyphRule) {
    glyphRule = styleSheet.cssRules[styleSheet.insertRule('#glyphs .glyph {}', styleSheet.cssRules.length)]
    lineRule = styleSheet.cssRules[styleSheet.insertRule('#glyphs .glyph .line {}', styleSheet.cssRules.length)]
    zeroWidthAdvRule = styleSheet.cssRules[styleSheet.insertRule('#glyphs .glyph.zero-width .advance {}', styleSheet.cssRules.length)]
  }

  if (queryString.g) {
    glyphRule.style.marginRight = null
    glyphRule.style.marginBottom = null
  } else {
    glyphRule.style.marginRight = Math.ceil(6 / scale) + 'px';
    glyphRule.style.marginBottom = Math.ceil(6 / scale) + 'px';
    if (queryString.iframe !== undefined) {
      glyphRule.style.marginBottom = Math.ceil(16 / scale) + 'px';
    }
  }
  lineRule.style.height = hairline + 'px'
  zeroWidthAdvRule.style.borderWidth = (hairline) + 'px'

  updateLayoutAfterChanges()
  requestAnimationFrame(updateLayoutAfterChanges)
}


function encodeQueryString(q) {
  return Object.keys(q).map(function(k) {
    if (k) {
      var v = q[k]
      return encodeURIComponent(k) + (v ? '=' + encodeURIComponent(v) : '')
    }
  }).filter(function(s) { return !!s }).join('&')
}

function parseQueryString(qs) {
  var q = {}
  qs.replace(/^\?/,'').split('&').forEach(function(c) {
    var kv = c.split('=')
    var k = decodeURIComponent(kv[0])
    if (k) {
      q[k] = kv[1] ? decodeURIComponent(kv[1]) : null
    }
  })
  return q
}


var queryString = parseQueryString(location.search)
var glyphNameEl = null
var baseTitle = document.title
var flippedLocationHash = false

var singleInfo = document.querySelector('#single-info')
singleInfo.parentElement.removeChild(singleInfo)
singleInfo.style.display = 'block'

function updateLocation() {
  queryString = parseQueryString(location.search)

  // var glyphs = document.getElementById('glyphs')
  var h1 = document.querySelector('h1')
  if (queryString.g) {
    if (!glyphNameEl) {
      glyphNameEl = document.createElement('a')
      glyphNameEl.href = '?g=' + encodeURIComponent(queryString.g)
      wrapIntLink(glyphNameEl)
      glyphNameEl.className = 'glyph-name'
    }
    document.title = queryString.g + ' – ' + baseTitle
    glyphNameEl.innerText = queryString.g
    h1.appendChild(glyphNameEl)
    document.body.classList.add('single')
    setScale(currentSingleScale)
  } else {
    document.title = baseTitle
    if (glyphNameEl) {
      h1.removeChild(glyphNameEl)
    }
    document.body.classList.remove('single')
    setScale(currentGridScale)
  }

  document.querySelector('.row.intro').style.display = (
    queryString.iframe !== undefined ? 'none' : null
  )
  if (queryString.iframe !== undefined) {
    document.body.classList.add('iframe')
  } else {
    document.body.classList.remove('iframe')
  }

  render()
}

window.onpopstate = function(ev) {
  updateLocation()
}

function navto(url) {
  if (location.href != url) {
    history.pushState({}, "Glyphs", url)
    updateLocation()
  }
  window.scrollTo(0,0)
}

function wrapIntLink(a) {
  a.addEventListener('click', function(ev) {
    if (!ev.metaKey && !ev.ctrlKey && !ev.shiftKey) {
      ev.preventDefault()
      navto(a.href)
    }
  })
}

wrapIntLink(document.querySelector('h1 > a'))


// keep refs to svgs so we don't have to refcount while using
var svgRepository = {}
;(function(){
  var svgs = document.getElementById('svgs'), svg, name
  for (var i = 0; i < svgs.children.length; ++i) {
    svg = svgs.children[i]
    name = svg.id.substr(4) // strip "svg-" prefix
    svgRepository[name] = svg
  }
})()


// Maps glyphname to glyphInfo. Only links to first found entry for a flyph.
var glyphInfoMap = {}
var needsUpdateGlyphInfoMap = true


function render() {
  if (!glyphInfo) {
    return
  }

  var rootEl = document.getElementById('glyphs')
  rootEl.style.display = 'none'
  rootEl.innerText = ''

  // glyphInfo: {
  //   "glyphs": [
  //     // <=v2.5:
  //     [name :string, unicode? :int|null, unicodeName? :string, color? :string|null],
  //     // >=v2.6: (has mtime)
  //     [name :string, unicode? :int|null, unicodeName? :string, mtime? :string, color? :string|null],
  //     ["A", 65, "LATIN CAPITAL LETTER A", "#dbeaf7"],
  //     ...
  //   ],
  // }
  //
  // Note: Glyph names might appear multiple times (always adjacent) when a glyph is
  // represented by multiple Unicode code points. For example:
  //
  //   ["Delta", 916, "GREEK CAPITAL LETTER DELTA"],
  //   ["Delta", 8710, "INCREMENT"],
  //

  var glyphs = glyphInfo
  var singleGlyph = null
  var lastGlyphEl = null
  var lastGlyphName = ''

  glyphInfo.forEach(function(g, i) {
    var name = g[0]

    if (needsUpdateGlyphInfoMap && !glyphInfoMap[name]) {
      glyphInfoMap[name] = g
    }

    if (queryString.g && name != queryString.g) {
      // ignore
      return
    }

    var glyph = renderGlyphGraphicG(g, lastGlyphName, lastGlyphEl, singleGlyph)

    if (glyph) {
      rootEl.appendChild(glyph.element)
      lastGlyphEl = glyph.element
      lastGlyphName = name
      if (queryString.g) {
        singleGlyph = glyph
      }
    }
  })

  needsUpdateGlyphInfoMap = false

  if (singleGlyph) {
    renderSingleInfo(singleGlyph)
    rootEl.appendChild(singleInfo)
  }

  rootEl.style.display = null
  updateLayoutAfterChanges()
}


function renderGlyphGraphic(glyphName) {
  var g = glyphInfoMap[glyphName]
  return g ? renderGlyphGraphicG(g) : null
}


function renderGlyphGraphicG(g, lastGlyphName, lastGlyphEl, singleGlyph) {
  let name = g[0], uc = g[1], ucName = g[2], mtime = g[3], color = g[4]
  var names, glyph
  var svg = svgRepository[name]

    // XXX compatibility with v2.5 (remove when moving to v2.6)
    // glyphinfo for 2.5 doesn't contain mtime.
    if (mtime && typeof mtime == 'string' &&
        (mtime.indexOf('rgba') != -1 || mtime.indexOf('#') != -1)) {
      color = mtime
      mtime = null
    }

  if (!svg) {
    // ignore
    return null
  }

  var metrics = glyphMetrics.metrics[name]
  if (!metrics) {
    console.error('missing metrics for', name)
  }

  var info = {
    name: name,
    unicode: uc,
    unicodeName: ucName,
    // mtime: mtime,
    color: color,

    // These are all in 1:1 UPM (not scaled)
    advance: metrics.advance,
    left: metrics.left,
    right: metrics.right,
    width: metrics.width,

    element: null,
  }

  if (name == lastGlyphName) {
    // additional Unicode code point for same glyph
    glyph = lastGlyphEl
    names = glyph.querySelector('.names')
    names.innerText += ','
    if (info.unicode) {
      var ucid = ' U+' + fmthex(info.unicode)
      names.innerText += ' U+' + fmthex(info.unicode)
      if (!queryString.g) {
        glyph.title += ucid
      }
    }
    if (info.unicodeName) {
      names.innerText += ' ' + info.unicodeName
      if (!queryString.g) {
        glyph.title += ' (' + info.unicodeName + ')'
      }
    }

    if (queryString.g) {
      if (singleGlyph) {
        if (!singleGlyph.alternates) {
          singleGlyph.alternates = []
        }
        singleGlyph.alternates.push(info)
      } else {
        throw new Error('alternate glyph UC, but appears first in glyphinfo data')
      }
    }

    return
  }

  // console.log('svg for', name, svg.width.baseVal.value, '->', svg, '\n', info)

  glyph = document.createElement('a')
  glyph.className = 'glyph'
  glyph.href = '?g=' + encodeURIComponent(name)
  wrapIntLink(glyph)

  info.element = glyph

  if (!queryString.g) {
    glyph.title = name
  }

  var line = document.createElement('div')
  line.className = 'line baseline'
  line.title = "Baseline"
  glyph.appendChild(line)

  line = document.createElement('div')
  line.className = 'line x-height'
  line.title = "x-height"
  glyph.appendChild(line)

  line = document.createElement('div')
  line.className = 'line cap-height'
  line.title = "Cap height"
  glyph.appendChild(line)

  names = document.createElement('div')
  names.className = 'names'
  names.innerText = name
  if (info.unicode) {
    var ucid = ' U+' + fmthex(info.unicode)
    names.innerText += ' U+' + fmthex(info.unicode, 4)
    if (!queryString.g) {
      glyph.title += ucid
    }
  }
  if (info.unicodeName) {
    names.innerText += ' ' + info.unicodeName
    if (!queryString.g) {
      glyph.title += ' (' + info.unicodeName + ')'
    }
  }
  glyph.appendChild(names)

  var scaledAdvance = info.advance * kSVGScale

  if (scaledAdvance > kGlyphSize) {
    glyph.style.width = scaledAdvance.toFixed(2) + 'px'
  }

  var adv = document.createElement('div')
  adv.className = 'advance'
  glyph.appendChild(adv)

  adv.appendChild(svg)
  svg.style.left = (info.left * kSVGScale).toFixed(2) + 'px'

  if (info.advance <= 0) {
    glyph.className += ' zero-width'
  } else {
    adv.style.width = scaledAdvance.toFixed(2) + 'px'
  }

  return info
}


function renderSingleInfo(g) {
  var e = singleInfo
  e.querySelector('.name').innerText = g.name

  function setv(el, name, textValue) {
    el.querySelector('.' + name).innerText = textValue
  }

  var unicode = e.querySelector('.unicode')

  function configureUnicodeView(el, g) {
    var a = el.querySelector('a')
    if (g.unicode) {
      a.href = "https://codepoints.net/U+" + fmthex(g.unicode, 4)
    } else {
      a.href = ''
    }
    setv(el, 'unicodeCodePoint', g.unicode ? 'U+' + fmthex(g.unicode, 4) : '–')
    setv(el, 'unicodeName', g.unicodeName || '')
  }

  // remove any previous alternate unicode list items
  var rmli = unicode
  while ((rmli = rmli.nextSibling)) {
    if (rmli.nodeType == Node.ELEMENT_NODE) {
      if (!rmli.parentElement || !rmli.classList.contains('unicode')) {
        break
      }
      rmli.parentElement.removeChild(rmli)
    }
  }

  configureUnicodeView(unicode, g)

  if (g.alternates) {
    var refnode = unicode.nextSibling
    g.alternates.forEach(function(g) {
      var li = unicode.cloneNode(true)
      configureUnicodeView(li, g)
      if (refnode) {
        unicode.parentElement.insertBefore(li, unicode.nextSibling)
      } else {
        unicode.parentElement.appendChild(li)
      }
    })
  }

  e.querySelector('.advanceWidth').innerText = g.advance
  e.querySelector('.marginLeft').innerText = g.left
  e.querySelector('.marginRight').innerText = g.right

  var colorMark = e.querySelector('.colorMark')
  if (g.color) {
    colorMark.title = g.color.toUpperCase()
    colorMark.style.background = g.color
    colorMark.classList.remove('none')
  } else {
    colorMark.title = '(None)'
    colorMark.style.background = null
    colorMark.classList.add('none')
  }

  var svg = svgRepository[g.name]
  var svgFile = e.querySelector('.svgFile')
  svgFile.download = g.name + '.svg'
  svgFile.href = getSvgDataURI(svg)

  renderSingleKerning(g)
}


var cachedSVGDataURIs = {}

function getSvgDataURI(svg, fill) {
  if (!fill) {
    fill = ''
  }
  var cached = cachedSVGDataURIs[svg.id + '-' + fill]
  if (!cached) {
    var src = svg.outerHTML.replace(/[\r\n]+/g, '')
    if (fill) {
      src = src.replace(/<path /g, '<path fill="' + fill + '" ')
    }
    cached = 'data:image/svg+xml,' + src
    cachedSVGDataURIs[svg.id + '-' + fill] = cached
  }
  return cached
}



function selectKerningPair(id, directly) {
  // deselect existing
  eachElement('.kernpair.selected', function(kernpair) {
    eachElement(kernpair, '.g', function (glyph) {
      var svgURI = getSvgDataURI(svgRepository[glyph.dataset.name])
      glyph.style.backgroundImage = "url('" + svgURI + "')"
    })
    kernpair.classList.remove('selected')
  })

  var el = document.getElementById(id)
  
  if (!el) {
    history.replaceState({}, '', location.search)
    return
  }
  
  el.classList.add('selected')
  eachElement(el, '.g', function (glyph) {
    var svgURI = getSvgDataURI(svgRepository[glyph.dataset.name], 'white')
    glyph.style.backgroundImage = "url('" + svgURI + "')"
  })

  if (!directly) {
    el.scrollIntoViewIfNeeded()
  }
  
  history.replaceState({}, '', location.search + '#' + id)
}


// return true if some kerning was rendered
function renderSingleKerning(g) {
  var kerningList = document.getElementById('kerning-list')
  kerningList.style.display = 'none'
  kerningList.innerText = ''
  var thisSvg = svgRepository[g.name]
  var thisSvgURI = getSvgDataURI(thisSvg)

  if (!thisSvg) {
    kerningList.style.display = null
    return false
  }

  var kerningAsLeft = glyphMetrics.kerningLeft[g.name] || {}
  var kerningAsRight = glyphMetrics.kerningRight[g.name] || {}

  var kerningAsLeftKeys = Object.keys(kerningAsLeft)
  var kerningAsRightKeys = Object.keys(kerningAsRight)

  if (kerningAsLeftKeys.length == 0 && kerningAsRightKeys.length == 0) {
    var p = document.createElement('p')
    p.className = 'empty'
    p.innerText = 'No kerning'
    kerningList.appendChild(p)
    kerningList.style.display = null
    return false
  }

  var lilGlyphSize = 128
  var lilScale = lilGlyphSize / kGlyphSize

  function mkpairGlyph(glyphName, side, kerningValue, svgURI) {
    var metrics = glyphMetrics.metrics[glyphName]
    var svgWidth = pxround(metrics.width * kSVGScale * lilScale)
    var el = document.createElement('div')

    var leftMargin = metrics.left
    var rightMargin = metrics.right
    if (side == 'left') {
      rightMargin += kerningValue
    } else {
      leftMargin += kerningValue
    }
    leftMargin = leftMargin * kSVGScale * lilScale
    rightMargin = rightMargin * kSVGScale * lilScale

    el.dataset.name = glyphName
    el.className = 'g ' + side
    el.style.backgroundImage = "url('" + svgURI + "')"
    el.style.backgroundSize = svgWidth + 'px ' + lilGlyphSize + 'px'
    el.style.width = svgWidth + 'px'
    el.style.height = lilGlyphSize + 'px'
    el.style.marginLeft = pxround(leftMargin) + 'px'
    el.style.marginRight = pxround(rightMargin) + 'px'
    return el
  }

  function mkpairs(kerningInfo, selfName, self, side) {
    var asLeftSide = side == 'left'
    var idPrefix = asLeftSide ? 'kernl-' : 'kernr-'
    var keys = Object.keys(kerningInfo)
    var otherSide = asLeftSide ? 'right' : 'left'

    keys.forEach(function(glyphName) {
      var kerningValue = kerningInfo[glyphName]
      var otherSvg = svgRepository[glyphName]

      var pair = document.createElement('a')
      pair.className = 'kernpair ' + side
      pair.title = (
        asLeftSide ? selfName + '/' + glyphName + '  ' + kerningValue :
        glyphName + '/' + selfName + '  ' + kerningValue
      )
      pair.id = idPrefix + glyphName
      pair.href = '#' + pair.id
      pair.onclick = function(ev) {
        selectKerningPair(pair.id)
        ev.preventDefault()
        ev.stopPropagation()
      }

      var otherEl = mkpairGlyph(glyphName, otherSide, kerningValue, getSvgDataURI(otherSvg))

      if (asLeftSide) {
        if (self.parentNode) {
          pair.appendChild(self.cloneNode(true))
        } else {
          pair.appendChild(self)
        }
        pair.appendChild(otherEl)
      } else {
        pair.appendChild(otherEl)
        if (self.parentNode) {
          pair.appendChild(self.cloneNode(true))
        } else {
          pair.appendChild(self)
        }
      }

      var kern = document.createElement('div')
      kern.className = 'kern ' + (kerningValue < 0 ? 'neg' : 'pos')

      var absKernVal = Math.abs(kerningValue)
      var kernWidth = Math.max(1, pxround(absKernVal * kSVGScale * lilScale))
      kern.style.width = kernWidth + 'px'

      var leftMetrics = glyphMetrics.metrics[asLeftSide ? selfName : glyphName]
      var leftAdvance = leftMetrics.advance
      kern.style.left = pxround((leftAdvance - absKernVal) * kSVGScale * lilScale) + 'px'
      pair.appendChild(kern)

      var label = document.createElement('div')
      label.className = 'label'
      label.innerText = kerningValue
      kern.appendChild(label)

      if (glyphName != selfName) {
        var link = document.createElement('div')
        link.className = 'link'
        var linkA = document.createElement('a')
        linkA.href = '?g=' + encodeURIComponent(glyphName)
        linkA.title = 'View ' + glyphName
        linkA.innerText = '\u2197'
        linkA.tabIndex = -1
        wrapIntLink(linkA)
        link.appendChild(linkA)

        var kLinkAWidth = 16 // sync with CSS .kernpair .link a

        if (asLeftSide) {
          var rightMetrics = glyphMetrics.metrics[asLeftSide ? glyphName : selfName]
          linkA.style.marginRight = pxround(
            ((rightMetrics.advance / 2) * kSVGScale * lilScale) - (kLinkAWidth / 2)
          ) + 'px'
        } else {
          linkA.style.marginLeft = pxround(
            ((leftMetrics.advance / 2) * kSVGScale * lilScale) - (kLinkAWidth / 2)
          ) + 'px'
        }

        pair.appendChild(link)
      }
      

      kerningList.appendChild(pair)
    })

    return keys.length != 0
  }

  var selfLeft = mkpairGlyph(g.name, 'left', 0, thisSvgURI)
  var selfRight = mkpairGlyph(g.name, 'right', 0, thisSvgURI)

  if (mkpairs(kerningAsLeft, g.name, selfLeft, 'left') &&
      kerningAsRightKeys.length != 0)
  {
    var div = document.createElement('div')
    div.className = 'divider'
    kerningList.appendChild(div)
  }

  mkpairs(kerningAsRight, g.name, selfRight, 'right')

  if (location.hash && location.hash.indexOf('#kern') == 0) {
    var id = location.hash.substr(1)
    setTimeout(function(){
      selectKerningPair(id)
    },1)
  }

  kerningList.style.display = null
  return true
}


function fmthex(cp, minWidth) {
  let s = cp.toString(16).toUpperCase()
  while (s.length < minWidth) {
    s = '0' + s
  }
  return s
}


document.addEventListener('keydown', function(ev) {
  if (!queryString.g && (ev.metaKey || ev.ctrlKey)) {
    if (ev.keyCode == 187 || ev.key == '+') {
      setScale(parseFloat((currentScale + 0.1).toFixed(2)))
      ev.preventDefault()
    } else if (ev.keyCode == 189 || ev.key == '-') {
      setScale(parseFloat((currentScale - 0.1).toFixed(2)))
      ev.preventDefault()
    } else if (ev.keyCode == 48 || ev.key == '0') {
      setScale(queryString.g ? defaultSingleScale : defaultGridScale)
      ev.preventDefault()
    }
  }
})

updateLocation()