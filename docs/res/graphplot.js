
function GraphPlot(canvas) {
  this.canvas = canvas
  const g = canvas.getContext('2d')
  if (g == null) {
    throw new Error('failed to acquire 2d context')
  }

  this.width    = 0  // dp
  this.height   = 0  // dp
  this.widthPx  = 0  // px
  this.heightPx = 0  // px
  this.pixelRatio = 1
  this.g = g
  this.dataSegments = []
  this.axes = {
    x0: .5,          // % from left to x=0
    y0: .5,          // % from top to y=0
    scalex: 40,      // pixels from x=0 to x=1
    scaley: 40,      // pixels from y=0 to y=1
    negativeX: true,
  }

  if (!this.autosize()) {
    this.setSize(256, 256)
  }
}

GraphPlot.prototype.autosize = function() {
  try {
    this.canvas.width = null
    this.canvas.height = null
    this.canvas.style.width = null
    this.canvas.style.height = null
    var cs = window.getComputedStyle(this.canvas)
    var width = parseFloat(cs.width)
    var height = parseFloat(cs.height)
    this.setSize(width, height)
    return true
  } catch (err) {
    if (typeof console != 'undefined' && console.warn) {
      console.warn('GraphPlot.autosize failed: ' + err)
    }
  }
  return false
}

// setOrigin sets the origin of axis x and y
// The values should be in the range [0-1] and maps to the extremes
// of the canvas.
//
GraphPlot.prototype.setOrigin = function(x, y) {
  var p = this
  p.axes.x0 = x
  p.axes.y0 = y
}

// setScale sets the value scale for x and y axis.
// The values should be provided as display points.
//
GraphPlot.prototype.setScale = function(x, y) {
  var p = this
  if (y === undefined) {
    y = x
  }
  p.axes.scalex = x
  p.axes.scaley = y
}

// setSize sets the size of canvas in display points
//
GraphPlot.prototype.setSize = function(width, height) {
  var p = this
  p.width = width
  p.height = height
  const el = p.canvas, g = p.g
  p.pixelRatio = window.devicePixelRatio || 1
  if (p.pixelRatio != 1) {
    el.width = p.widthPx = width * p.pixelRatio
    el.height = p.heightPx = height * p.pixelRatio
    g.scale(p.pixelRatio, p.pixelRatio)
  } else {
    el.width = p.widthPx = width
    el.height = p.heightPx = height
    g.scale(1, 1)
  }
  el.style.width = `${width}px`
  el.style.height = `${height}px`
}


GraphPlot.prototype.renderAxes = function() {
  var p = this
    , g = p.g
    , x0 = Math.round(p.axes.x0 * p.widthPx) / p.pixelRatio
    , y0 = Math.round(p.axes.y0 * p.heightPx) / p.pixelRatio

  g.beginPath()
  g.strokeStyle = "rgb(0, 0, 0, 0.2)"
  if (y0 > 0 && y0 < p.width) {
    g.moveTo(0, y0); g.lineTo(p.width, y0)  // X axis
  }
  if (x0 > 0 && x0 < p.height) {
    g.moveTo(x0, 0); g.lineTo(x0, p.height)  // Y axis
  }
  g.stroke()
}


// plotf plots an arbitrary function on the graph
//
GraphPlot.prototype.plotf = function(f, color) {
  var p = this
    , g = p.g
    , w = p.width
    , h = p.height
    , x0 = p.axes.x0 * p.width
    , y0 = p.axes.y0 * p.height
    , x = 0
    , y = 0
    , dx = 4 / p.pixelRatio // smaller means finer curves and more CPU
    , scalex = p.axes.scalex * w
    , scaley = p.axes.scaley * h
    , iMax = Math.round((w - x0) / dx)
    , iMin = p.axes.negativeX ? Math.round(-x0 / dx) : 0

  g.beginPath()
  g.lineWidth = 1
  g.strokeStyle = color || "rgb(0, 0, 0, 0.8)"

  for (var i = iMin; i <= iMax; i++) {
    x = dx * i
    y = f(x / scalex) * scaley
    if (i == iMin) {
      g.moveTo(x0 + x, y0 - y)
    } else {
      g.lineTo(x0 + x, y0 - y)
    }
  }
  
  g.stroke()
}


// plotLines draws straight lines between a collection of points
//
GraphPlot.prototype.plotLine = function(points, color) {
  var p = this
    , g = p.g
    , x0 = p.axes.x0 * p.width
    , y0 = p.axes.y0 * p.height
    , x = 0
    , y = 0
    , scalex = p.axes.scalex * p.width
    , scaley = p.axes.scaley * p.height
    , pt

  g.beginPath()
  g.lineWidth = 1
  g.strokeStyle = color || "rgb(0, 0, 0, 0.8)"

  var i = 0
  for (; i < points.length; i++) {
    pt = points[i]
    x = pt[0] * scalex
    y = pt[1] * scaley
    if (i == 0) {
      g.moveTo(x0 + x, y0 - y)
    } else {
      g.lineTo(x0 + x, y0 - y)
    }
  }

  g.stroke()
}


// plotPoints draws points
//
GraphPlot.prototype.plotPoints = function(points, color) {
  var p = this
    , g = p.g
    , x0 = p.axes.x0 * p.width
    , y0 = p.axes.y0 * p.height
    , x = 0
    , y = 0
    , scalex = p.axes.scalex * p.width
    , scaley = p.axes.scaley * p.height
    , pt
    , i = 0

  g.fillStyle = color || "rgb(0, 0, 0, 0.8)"

  for (; i < points.length; i++) {
    pt = points[i]
    x = x0 + pt[0] * scalex
    y = y0 - pt[1] * scaley
    g.beginPath()
    g.arc(x, y, 3, 0, Math.PI + (Math.PI * 2) / 2, false)
    g.fill()
  }
}


GraphPlot.prototype.clear = function() {
  var p = this
  p.g.clearRect(0, 0, p.width, p.height)
  p.renderAxes()
}


GraphPlot.prototype.renderDemo = function() {
  var p = this
    , g = p.g
    , dpscale = p.pixelRatio
    , w = p.widthPx
    , h = p.heightPx

  p.clear()

  p.plotf(
    function(x) { return Math.sin(x) },
    'blue'
  )

  p.plotf(
    function(x) { return Math.cos(3*x) },
    'hotpink'
  )

  // var scale = p.height / 4
  // g.moveTo(0, scale)
  // var i, sine, lines = 200, frag = p.width / lines
  // for (i = 0; i < lines; i++) {
  //   sine = Math.sin(i / scale * 2) * scale
  //   g.lineTo(i * frag, -sine + scale)
  // }
  // g.stroke()
}
