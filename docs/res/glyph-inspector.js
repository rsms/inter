import fontkit from "./fontkit-2.0.2.js"

const { min, max, ceil, floor } = Math
const $  = (q, el) => (el || document).querySelector(q)
const $$ = (q, el) => [].slice.call((el || document).querySelectorAll(q))

const rootElement = document.getElementById("glyphs")
const inspectorElement = rootElement.querySelector(".inspector")

const LABEL_X_OFFS = 16
const HMETRICS_LABEL_Y_OFFS = 5

// console.log("rootElement", rootElement)
// console.log("inspectorElement", inspectorElement)
// console.log("fontkit", fontkit)

// for (let el of $$(".popup-menu", rootElement)) {
//   let select = $('select', el)
//   let label = $('.label', el)
//   label.innerText = select.selectedOptions[0].label
//   select.onchange = () => label.innerText = select.selectedOptions[0].label
// }

let pixelRatio = window.devicePixelRatio || 1
function pxround(px) {
  return ((px * pixelRatio) >>> 0) / pixelRatio
}

const monotime = performance.now.bind(performance)
const WGHT_MIN = 14, WGHT_MAX = 32

class GlyphInspector {
  constructor() {
    this.font = null
    this.glyph = null
    this.glyphUnicode = 0
    this.defaultGlyphUnicode = 0x0041
    this.selectedGlyphGridCell = null
    this.defaultAxisValues = {wght: 400, opsz: WGHT_MAX}
    this.axisValues = {wght: 0, opsz: 0}
    this.idNameElement = $(".identification .name", rootElement)
    this.idUnicodeElement = $(".identification .unicode", rootElement)
    this.previewElement = $(".preview", rootElement)
    this.bgcolor = getComputedStyle(rootElement).getPropertyValue('--background-color')
    this.drawScheduled = false
    this.fontInstanceCache = new Map()
    this.draggedWghtStartTime = 0
    this.hasDraggedWght = false
    this.drawTime = monotime()

    this.tmpcanvas = document.createElement("CANVAS")
    this.tmpcanvas.width = 32
    this.tmpcanvas.height = 32
    this.canvas = document.createElement("CANVAS")
    let canvasWrapper = $(".canvas", inspectorElement)
    const onresize = (ev) => {
      let w = canvasWrapper.clientWidth
      let h = canvasWrapper.clientHeight
      pixelRatio = window.devicePixelRatio || 1 // update global var
      this.resize(w, h)
    }
    canvasWrapper.innerText = ''
    canvasWrapper.appendChild(this.canvas)
    onresize()
    window.addEventListener('resize', onresize, {passive: true})
    this.canvas.ondblclick = () => this.setFontInstance(this.defaultAxisValues)

    this.initCursor()

    const urlAnchor = document.location.hash
    const urlAnchorPrefix = '#glyphs/'
    let urlAnchorGlyphName = ''
    if (urlAnchor.startsWith(urlAnchorPrefix) &&
      urlAnchor.length > urlAnchorPrefix.length)
    {
      urlAnchorGlyphName = urlAnchor.substr(urlAnchorPrefix.length)
    }

    this.opszSlider = $('input[name="opsz"]')
    this.defaultAxisValues.opsz = this.opszSlider.valueAsNumber
    this.opszSlider.oninput = (ev) => {
      this.setFontInstance({opsz: this.opszSlider.valueAsNumber})
    }
    // enable clicking on label to toggle
    this.opszSlider.onclick = (ev) => ev.stopPropagation()
    this.opszSlider.parentElement.onclick = (ev) => {
      this.setFontInstance({opsz: this.axisValues.opsz > WGHT_MIN ? WGHT_MIN : WGHT_MAX})
    }

    this.opszCheckbox = $('input[name="opsz-switch"]')
    this.defaultAxisValues.opsz = this.opszCheckbox.checked ? WGHT_MIN : WGHT_MAX
    this.opszCheckbox.onchange = (ev) => {
      this.setFontInstance({opsz: this.opszCheckbox.checked ? WGHT_MIN : WGHT_MAX})
    }

    let showDetailsCheckbox = $('input[name="show-details"]')
    this.showDetails = showDetailsCheckbox.checked
    showDetailsCheckbox.onchange = (ev) => {
      this.showDetails = showDetailsCheckbox.checked
      this.scheduleDraw()
      if (this.showDetails)
        console.log(`details of glyph "/${this.glyph.name}"`, this.glyph)
      if (!this.hasDraggedWght) {
        const autoHideHelpTimeout = 2000
        clearTimeout(this.autoHideHelpTimer)
        if (this.showDetails) {
          this.draggedWghtStartTime = 0
          this.autoHideHelpTimer = setTimeout(() => {
            this.draggedWghtStartTime = monotime()
            this.scheduleDraw()
          }, autoHideHelpTimeout)
        }
      }
    }

    this.glyphGridCells = {} // uc => Element
    let glyphsGrid = $(".glyph-list .content", rootElement)
    let removeAnchors = document.body.clientWidth <= 500
    for (let i = 0; i < glyphsGrid.children.length; i++) {
      let el = glyphsGrid.children[i]
      if (removeAnchors)
        el.removeAttribute("name")
      if (!el.dataset.cp) {
        console.warn('no data-cp for glyphsGrid', el)
        continue
      }
      let unicode = parseInt(el.dataset.cp, 16)
      el.onclick = ev => {
        this.setGlyphByUnicode(unicode)
        history.replaceState({}, null, '#glyphs/' + el.dataset.name)
        ev.stopPropagation()
        ev.preventDefault()
      }
      this.glyphGridCells[unicode] = el
      if (urlAnchorGlyphName === el.dataset.name) {
        if (this.selectedGlyphGridCell)
          this.selectedGlyphGridCell.classList.toggle('selected', false)
        el.classList.toggle('selected', true)
        this.selectedGlyphGridCell = el
        this.defaultGlyphUnicode = unicode
        rootElement.scrollIntoView(/*alignToTop*/true)
        el.scrollIntoViewIfNeeded()
      }
    }
    // if (removeAnchors && urlAnchorGlyphName)
    //   rootElement.focus()
  }

  loadImage(filename) { // -> Promise<Image>
    let selfDirname = (new URL(import.meta.url)).pathname
    selfDirname = selfDirname.substr(0, selfDirname.lastIndexOf('/'))
    let img = new Image()
    img.src = filename[0] == '/' ? filename : selfDirname + '/' + filename
    return new Promise((res, rej) => {
      img.onload = () => { res(img) }
      img.onerror = err => { rej(err) }
    })
  }

  initCursor() {
    this.cursor = {
      x: 0,
      y: 0,
      dragOriginAxisValues: {...this.axisValues},
      dragOriginX: 0,
      dragOriginY: 0,
      dtime: 0,
      active: false,
      dragging: false,
    }
    // this.cursorImage = null
    // this.loadImage('cursor-glyph-inspector.svg').then(im => {
    //   this.cursorImage = im
    //   this.scheduleDraw()
    // })

    this.canvas.addEventListener('pointerover', ev => {
      // Fired when a pointer is moved into an element's hit test boundaries
      //console.log(ev.type, ev.pointerType, ev)
      this.cursorActivate(ev)
    })
    // this.canvas.addEventListener('pointerenter', ev => {
    //   // Fired when a pointer is moved into the hit test boundaries of an element
    //   // or one of its descendants, including as a result of a pointerdown event
    //   // from a device that does not support hover
    //   console.log(ev.type, ev.pointerType, ev)
    // })
    this.canvas.addEventListener('pointerdown', ev => {
      // Fired when a pointer becomes "active buttons state"
      //console.log(ev.type, ev.pointerType, ev)
      this.cursorDragBegin(ev)
    })
    // this.canvas.addEventListener('gotpointercapture', ev => {
    //   console.log(ev.type, ev.pointerType, ev)
    // })
    this.canvas.addEventListener('pointermove', ev => {
      // Fired when a pointer changes coordinates.
      // This event is also used if the change in pointer state cannot be reported
      // by other events
      //console.log(ev.type, ev.pointerType, ev)
      this.cursorMoved(ev)
    })
    this.canvas.addEventListener('pointerup', ev => {
      // Fired when a pointer is no longer "active buttons state"
      //console.log(ev.type, ev.pointerType, ev)
      this.cursorDragEnd(ev)
    })
    this.canvas.addEventListener('pointercancel', ev => {
      // A browser fires this event if it concludes the pointer will no longer be
      // able to generate events (for example the related device is deactivated)
      //console.log(ev.type, ev.pointerType, ev)
      if (this.cursor.dragging)
        this.cursorDragEnd(ev)
      if (this.cursor.active)
        this.cursorDeactivate(ev)
    })
    this.canvas.addEventListener('pointerout', ev => {
      // Fired for several reasons, including:
      // - pointer is moved out of the hit test boundaries of an element
      // - firing the pointerup event for a device that does not support hover
      // - after firing the pointercancel event
      // - when a pen stylus leaves the hover range detectable by the digitizer
      //console.log(ev.type, ev.pointerType, ev)
      if (this.cursor.active)
        this.cursorDeactivate(ev)
    })
    // this.canvas.addEventListener('pointerleave', ev => {
    //   // Fired when a pointer is moved out of the hit test boundaries of an element.
    //   // For pen devices, this event is fired when the stylus leaves the hover range
    //   // detectable by the digitizer
    //   console.log(ev.type, ev.pointerType, ev)
    // })
  }

  cursorActivate(ev) {
    this.cursor.active = true
    this.scheduleDraw()
  }

  cursorDeactivate(ev) {
    this.cursor.active = false
    this.scheduleDraw()
  }

  cursorMoved(ev) {
    this.cursor.x = ev.offsetX
    this.cursor.y = ev.offsetY

    // // if we draw our own cursor:
    // if (!this.cursor.active)
    //   return
    // this.scheduleDraw()
    if (!this.cursor.dragging)
      return

    let w = this.canvas.width / pixelRatio
    //let h = this.canvas.height / pixelRatio

    let dx_dp = this.cursor.x - this.cursor.dragOriginX
    //let dy_dp = this.cursor.y - this.cursor.dragOriginY

    // ratio of half canvas
    // movement from center to edge = 1.0
    // movement from edge to edge = 2.0
    let dx = dx_dp / (w/2)
    //let dy = dy_dp / (h/2)
    //let d = Math.sqrt(dx*dx + dy*dy)
    //let d = (dx + dy) / 2
    let d = dx

    let {wght, opsz} = this.cursor.dragOriginAxisValues
    wght = wght + d*800
    if (ev.shiftKey)
      wght = Math.round(wght / 100) * 100
    wght = max(100, min(900, wght))
    // opsz = max(WGHT_MIN, min(WGHT_MAX, opsz))
    this.hasDraggedWght = true
    if (this.draggedWghtStartTime == 0)
      this.draggedWghtStartTime = monotime()
    clearTimeout(this.autoHideHelpTimer)
    this.setFontInstance({wght, opsz})
  }

  cursorDragBegin(ev) {
    if (!this.cursor.active)
      console.warn("pointerdown without a prior pointerover")
    this.canvas.setPointerCapture(ev.pointerId)
    this.cursor.dragOriginX = ev.offsetX
    this.cursor.dragOriginY = ev.offsetY
    this.cursor.dragOriginAxisValues = {...this.axisValues}
    this.cursor.dragging = true
    this.scheduleDraw()

    this.cancelEvent = ev => {
      ev.preventDefault()
      ev.stopPropagation()
      return false
    }

    //document.addEventListener('touchstart', this.cancelEvent, {passive:false,capture:true})
    //document.addEventListener('touchbegin', this.cancelEvent, {passive:false,capture:true})
    //document.addEventListener('scroll', this.cancelEvent, {passive:false,capture:true})
    //document.style.overflow = 'hidden'
  }

  cursorDragEnd(ev) {
    //document.removeEventListener('touchstart', this.cancelEvent, {passive:false,capture:true})
    //document.removeEventListener('touchbegin', this.cancelEvent, {passive:false,capture:true})
    //document.removeEventListener('scroll', this.cancelEvent, {passive:false,capture:true})
    //document.style.overflow = null
    this.cursor.dragging = false
    this.scheduleDraw()
  }

  drawCursor(g, w, h) {
    if (!this.cursor.active)
      return
    let {x, y} = this.cursor

    // if (this.cursorImage) {
    //   let im = this.cursorImage
    //   g.drawImage(im, x - im.width/2, y - im.width/2)
    // }

    // g.beginPath()
    // g.moveTo(x, y-8)
    // g.lineTo(x, y+8)
    // g.moveTo(x-8, y)
    // g.lineTo(x+8, y)
    // g.strokeStyle = 'red'
    // g.lineWidth = 1.0
    // g.stroke()

    if (this.cursor.dragging) {
      g.fillStyle = 'white'
      g.strokeStyle = 'rgba(0,0,0,0.4)'
      g.lineWidth = 1.5

      // let label = `${this.axisValues.opsz}`
      // g.textAlign = 'left'
      // g.strokeText(label, x+10, y+4)
      // g.fillText(label, x+10, y+4)

      let label = `${this.axisValues.wght.toFixed(1)}`
      g.textAlign = 'center'
      g.strokeText(label, x, y+22)
      g.lineWidth = 2.0
      g.strokeStyle = 'rgba(0,0,0,0.1)'
      g.strokeText(label, x, y+23)
      g.fillText(label, x, y+22)
    }
  }

  snapToGrid(value) {
    const gridSize = 16
    return value - (value % gridSize)
  }

  drawHMetricLine(g, w, h, y, label) {
    g.beginPath()
    g.moveTo(0, y)
    g.lineTo(w, y)
    g.strokeStyle = 'white'
    g.lineWidth = 1.0
    g.stroke()

    g.fillStyle = 'white'
    g.strokeStyle = this.bgcolor
    g.lineWidth = 3.0

    g.textAlign = 'left'
    if (this.showDetails)
      g.strokeText(label, LABEL_X_OFFS, y - HMETRICS_LABEL_Y_OFFS)
    g.fillText(label, LABEL_X_OFFS, y - HMETRICS_LABEL_Y_OFFS)
  }

  drawPathDetails(glyph, g, w, h, scale) {
    let anchors = []
    let handles = []
    let x1, y1, startX, startY
    let commands = glyph.path.commands
    let cmd2

    // g.fillStyle = 'blue'

    // TODO: consider converting quadratic to cubic bezier paths to display
    // actual design-time paths

    g.save()
    g.beginPath()

    for (let i = 0; i < commands.length; i++) {
      let { command, args } = commands[i]
      //console.log(command, ...args)
      //g.fillText(`${i}`, args[0] * scale, -args[1] * scale)
      switch (command) {
        case "closePath":
          if (anchors.length > 0)
            anchors[anchors.length-1].push(/*isStartingPoint*/true)
          //g.closePath()
          break
        case "moveTo":
          x1 = args[0] * scale
          y1 = args[1] * -scale
          anchors.push([x1, y1])
          startX = x1
          startY = y1
          g.moveTo(x1, y1)
          break
        case "lineTo":
          x1 = args[0] * scale
          y1 = args[1] * -scale
          anchors.push([x1, y1])
          g.moveTo(x1, y1)
          break
        case "quadraticCurveTo":
          x1 = args[2] * scale
          y1 = args[3] * -scale
          anchors.push([x1, y1])
          handles.push([args[0] * scale, args[1] * -scale])
          g.lineTo(args[0] * scale, args[1] * -scale)
          g.lineTo(x1, y1)
          break
        case "bezierCurveTo":
          x1 = args[4] * scale
          y1 = -args[5] * scale
          anchors.push([x1, y1])
          handles.push([args[0] * scale, -args[1] * scale])
          handles.push([args[2] * scale, -args[3] * scale])
          break
        default:
          console.warning("unhandled draw command:", command)
      }
    }

    g.lineWidth = 1
    g.strokeStyle = 'rgba(0,0,0,0.3)'
    //g.strokeStyle = 'red'
    g.stroke()

    let radius = 3

    g.strokeStyle = 'black'
    g.fillStyle = 'white'
    for (let [x, y, isStartingPoint] of anchors) {
      g.beginPath()
      g.ellipse(x, y, radius, radius, 0, 0, 360)
      if (isStartingPoint) {
        g.fillStyle = 'black'
        g.fill()
        g.fillStyle = 'white'
      } else {
        g.fill()
        g.stroke()
      }
    }

    g.strokeStyle = 'black'
    g.fillStyle = 'black'
    for (let [x, y] of handles) {
      g.beginPath()
      g.ellipse(x, y, 2, 2, 0, 0, 360)
      g.fill()
    }

    g.restore()
  }

  makePixelDrawing(w, h, f) { // -> Promise<ImageBitmap>
    let canvas = this.tmpcanvas
    canvas.width = w
    canvas.height = h
    let g = canvas.getContext('2d')
    g.clearRect(0,0,w,h)
    let imageData = g.getImageData(0, 0, w, h)
    f(g, w, h, imageData)
    g.putImageData(imageData, 0, 0)
    if (navigator.userAgent.indexOf('Safari') != -1) {
      // TODO FIXME: g.createPattern errors in Safari when we pass ImageBitmap
      return Promise.resolve(this.tmpcanvas)
    }
    return createImageBitmap(this.tmpcanvas, 0, 0, w, h)
  }

  getPattern() { // -> ImageBitmap|null
    if (this.pattern1)
      return this.pattern1
    if (this.pattern1Promise)
      return null
    this.pattern1Promise = this.makePixelDrawing(8, 8, (g, w, h, imageData) => {
      const setpx = (x,y) => {
        let n = (y*w + x) * 4
        imageData.data[n]   = 255 // r
        imageData.data[n+1] = 255 // g
        imageData.data[n+2] = 255 // b
        imageData.data[n+3] = 160 // a
      }
      setpx(0, 0) // patch line intersecting at corner (when 2px wide, only)
      for (let x = w-1, y = 0; y < h; x--, y++) {
        setpx(x, y)
        setpx(x, y+1) // 2px wide
      }
    }).then(image => {
      this.pattern1 = image
      this.scheduleDraw()
    })
    return null
  }

  drawGlyphBounds(glyph, g, w, h, x, xmax, ascender, descender, scale) {
    // g.beginPath()
    // g.moveTo(x, ascender)
    // g.lineTo(x, descender)
    // g.moveTo(xmax, ascender)
    // g.lineTo(xmax, descender)
    // g.strokeStyle = 'white'
    // g.lineWidth = 1
    // g.stroke()

    //let pattern = g.createPattern(image, "repeat")

    let patternImage = this.getPattern()
    if (patternImage) {
      const px = pixelRatio
      g.save()
      let pattern = g.createPattern(patternImage, "repeat")
      g.scale(1/px, 1/px)
      g.fillStyle = pattern
      g.fillRect(0, ascender*px, x*px, (descender - ascender)*px)
      g.fillRect(xmax*px, ascender*px, (w - xmax)*px, (descender - ascender)*px)
      g.restore()
    }

    let { maxX, minX } = glyph.bbox
    maxX = maxX >> 0 // should always be integer, but floor just in case
    minX = minX >> 0 // should always be integer, but floor just in case
    let advanceWidth = glyph.advanceWidth >>> 0
    let lsb = minX
    let rsb = advanceWidth - (maxX - minX) - minX
    let y = descender + 4

    g.fillStyle = 'black'
    g.strokeStyle = 'black'
    g.lineWidth = 1

    // advance width
    g.textAlign = 'center'
    g.fillText(`${advanceWidth}`, pxround(w/2), y + 24)

    if (advanceWidth == 0) {
      x = w/2
      g.beginPath()
      g.moveTo(x, y)
      g.lineTo(x, y+8)
      g.stroke()
    } else {
      // LSB
      let x2 = lsb * scale
      g.beginPath()
      g.moveTo(x, y)
      g.lineTo(x, y+8)
      g.moveTo(pxround(x + x2), y)
      g.lineTo(pxround(x + x2), y+8)
      g.stroke()
      g.textAlign = 'center'
      g.fillText(`${lsb}`, pxround(x + x2/2), y + 24)

      // RSB
      x2 = rsb * scale
      g.beginPath()
      g.moveTo(xmax, y)
      g.lineTo(xmax, y+8)
      g.moveTo(pxround(xmax - x2), y)
      g.lineTo(pxround(xmax - x2), y+8)
      g.stroke()
      g.textAlign = 'center'
      g.fillText(`${rsb}`, pxround(xmax - x2/2), y + 24)
    }
  }

  drawAxisValues(g, w, h, ascender) {
    let {wght, opsz} = this.axisValues
    g.save()

    let x = w - LABEL_X_OFFS
    let y = ascender/2 + 4

    g.font = '400 14px InterVariable, sans-serif'
    g.fillStyle = 'black'
    g.textAlign = 'right'
    g.fillText(`wght ${wght.toFixed(1)}`, x, y)
    x -= w/4
    g.fillText(`opsz ${opsz.toFixed(1)}`, x, y)

    let helpOpacity = 1
    if (this.draggedWghtStartTime > 0) {
      let age = this.drawTime - this.draggedWghtStartTime
      helpOpacity = 1.0 - age/200
      if (helpOpacity > 0)
        this.scheduleDraw()
    }
    if (helpOpacity > 0) {
      let label = `⟷ drag to adjust weight`
      g.font = '500 18px InterVariable, sans-serif'
      g.textAlign = 'center'
      let textMetrics = g.measureText(label)
      g.fillStyle = `rgba(255,255,255,${helpOpacity})`
      const bgpadding_x = 8, bgpadding_y = 6
      const cornerRadius = 4
      g.beginPath()
      g.roundRect(
        w/2 - textMetrics.actualBoundingBoxLeft - bgpadding_x,
        h/2 - textMetrics.actualBoundingBoxAscent - bgpadding_y - 1,
        textMetrics.width + bgpadding_x*2,
        textMetrics.actualBoundingBoxAscent
        + textMetrics.actualBoundingBoxDescent + bgpadding_y*2,
        cornerRadius)
      g.fill()
      g.fillStyle = `rgba(0,0,0,${helpOpacity})`
      g.fillText(label, w/2, h/2)
    }

    g.restore()
  }

  drawDebugXLine(g, w, h, x, name) {
    g.save()

    g.beginPath()
    g.moveTo(x, 0)
    g.lineTo(x, h)

    g.strokeStyle = 'red'
    g.lineWidth = 1
    g.stroke()

    g.textAlign = 'center'
    g.fillStyle = 'red'
    g.strokeStyle = this.bgcolor
    g.lineWidth = 3.0
    g.strokeText(`${name}=${x}`, x, h/2)
    g.fillText(`${name}=${x}`, x, h/2)

    g.restore()
  }

  drawDebugYLine(g, w, h, y, name) {
    g.save()

    g.beginPath()
    g.moveTo(0, y)
    g.lineTo(w, y)

    g.strokeStyle = 'red'
    g.lineWidth = 1
    g.stroke()

    g.textAlign = 'center'
    g.fillStyle = 'red'
    g.strokeStyle = this.bgcolor
    g.lineWidth = 3.0
    g.strokeText(`${name}=${y}`, w/2, y+4)
    g.fillText(`${name}=${y}`, w/2, y+4)

    g.restore()
  }

  drawGlyph(glyph, g, w, h) {
    const margin = 16
    // for debugging margin:
    //const margin = performance.now()/30 % 32; requestAnimationFrame(() => this.draw())

    // for debugging scalable layout:
    //h -= performance.now()/30 % 100; requestAnimationFrame(() => this.draw())

    const fontInstance = glyph._font
    const upm = fontInstance.unitsPerEm

    const { maxX, maxY, minX, minY } = fontInstance.bbox

    let maxGlyphHeight = maxY - minY
    let maxGlyphWidth = max(upm, glyph.advanceWidth * 1.1) // maxX-minX is very large

    let boundsW = w - margin*2
    let boundsH = h - margin*2

    let scale = min(boundsW/maxGlyphWidth, boundsH/maxGlyphHeight)

    let glyphWidth = glyph.advanceWidth * scale
    let x = pxround((boundsW - glyphWidth) / 2 + margin)
    let xmax = pxround((boundsW + glyphWidth) / 2 + margin)

    let baseline  = pxround(upm * scale)
    let capHeight = pxround((upm - fontInstance.capHeight) * scale)
    let xHeight   = pxround((upm - fontInstance.xHeight) * scale)
    let ascender  = pxround((upm - fontInstance.ascent) * scale)
    let descender = pxround((upm - fontInstance.descent) * scale)

    g.save()

    let verticalOffset = pxround( (h - margin)*maxY/maxGlyphHeight - baseline - margin)
    g.translate(0, verticalOffset)

    // this.drawDebugXLine(g, w, h, x, 'x')
    // this.drawDebugXLine(g, w, h, xmax, 'xmax')

    // draw bounds (side bearings)
    if (this.showDetails) {
      this.drawGlyphBounds(
        glyph, g, w, h, x, xmax, ascender, descender, scale)
    }

    // draw horizontal metrics
    if (this.showDetails) {
      this.drawHMetricLine(g, w, h, baseline, "Baseline")
      this.drawHMetricLine(g, w, h, capHeight, "Cap height")
      this.drawHMetricLine(g, w, h, xHeight, "x-height")
      this.drawHMetricLine(g, w, h, ascender, "Ascender")
      this.drawHMetricLine(g, w, h, descender, "Descender")
    } else {
      const yoffs = 1.0 - (1.0 / pixelRatio)
      this.drawHMetricLine(g, w, h, baseline - yoffs, "Baseline")
      this.drawHMetricLine(g, w, h, capHeight + yoffs, "Cap height")
      this.drawHMetricLine(g, w, h, xHeight + yoffs, "x-height")
    }

    // draw glyph
    g.translate(x, baseline)
    if (glyph.advanceWidth >>> 0 == 0) {
      // center zero-width glyphs, regardless of LSB
      let maxX = glyph.bbox.maxX >> 0
      let minX = glyph.bbox.minX >> 0
      g.translate((-minX - (maxX-minX)/2) * scale, 0)
    }
    g.beginPath()
    for (let i = 0, len = glyph.path.commands.length; i < len; i++) {
      let cmd = glyph.path.commands[i]
      let x1 = cmd.args[0] * scale
      let y1 = -cmd.args[1] * scale
      let x2, y2, x3, y3
      if (cmd.args.length > 2) {
        x2 = cmd.args[2] * scale
        y2 = -cmd.args[3] * scale
        if (cmd.args.length > 4) {
          x3 = cmd.args[4] * scale
          y3 = -cmd.args[5] * scale
        }
      }
      g[cmd.command](x1, y1, x2, y2, x3, y3)
    }

    if (this.showDetails) {
      g.fillStyle = 'rgba(0,0,0,0.1)'
      g.fill()
      g.strokeStyle = 'black'
      g.lineWidth = 1
      g.stroke()
    } else {
      g.fillStyle = 'black'
      g.fill()
    }

    if (this.showDetails)
      this.drawPathDetails(glyph, g, w, h, scale)

    g.restore()

    if (this.showDetails)
      this.drawAxisValues(g, w, h, ascender + verticalOffset)
  }

  drawGrid(g, w, h, size) {
    const upm = this.fontInstance.unitsPerEm

    let rows = ceil(h / size)
    let cols = ceil(w / size)

    g.beginPath()
    for (let row = 0; row < rows; row++) {
      g.moveTo(0, row*size)
      g.lineTo(w, row*size)
    }
    for (let col = 0; col < cols; col++) {
      g.moveTo(col*size, 0)
      g.lineTo(col*size, h)
    }
    g.strokeStyle = 'rgba(0,0,0,0.3)'
    g.lineWidth = 1.0
    g.stroke()
  }

  draw(time) {
    const g = this.canvas.getContext('2d')
    const w = this.canvas.width / pixelRatio
    const h = this.canvas.height / pixelRatio
    this.drawTime = monotime() // in case monotime() != time
    this.drawScheduled = false
    g.resetTransform()
    g.font = '500 12px InterVariable'
    g.textRendering = "geometricPrecision"
    g.scale(pixelRatio, pixelRatio)
    g.clearRect(0, 0, w, h)
    if (!this.glyph)
      return

    // g.fillStyle = '#ccc'; g.fillRect(0, 0, w, h) // debug
    // this.drawGrid(g, w, h, 8)
    this.drawGlyph(this.glyph, g, w, h)
    // this.drawCursor(g, w, h)
  }

  scheduleDraw() {
    if (this.drawScheduled)
      return
    this.drawScheduled = true
    requestAnimationFrame(time => this.draw(time))
  }

  resize(w, h) {
    this.canvas.width = w * pixelRatio
    this.canvas.height = h * pixelRatio
    this.canvas.style.width = `${w}px`
    this.canvas.style.height = `${h}px`

    // w = this.tmpcanvas.width
    // h = this.tmpcanvas.height
    // this.tmpcanvas.width = w * pixelRatio
    // this.tmpcanvas.height = h * pixelRatio
    // this.tmpcanvas.style.width = `${w}px`
    // this.tmpcanvas.style.height = `${h}px`
    // this.tmpcanvas.getContext('2d').scale(1/pixelRatio, 1/pixelRatio)

    this.scheduleDraw()
  }

  glyphByUnicode(unicode) {
    return this.fontInstance.glyphForCodePoint(unicode)
  }

  setGlyphByUnicode(unicode) {
    this.glyph = this.glyphByUnicode(unicode)
    this.scheduleDraw()
    if (this.glyphUnicode == unicode) {
      // same logical glyph, just for a different instance
      return
    }
    this.glyphUnicode = unicode
    //console.log("this.glyph", this.glyph)

    if (this.selectedGlyphGridCell)
      this.selectedGlyphGridCell.classList.toggle('selected', false)
    this.selectedGlyphGridCell = this.glyphGridCells[unicode]
    if (this.selectedGlyphGridCell)
      this.selectedGlyphGridCell.classList.toggle('selected', true)

    // update info
    this.idNameElement.innerHTML = (
      this.selectedGlyphGridCell ? this.selectedGlyphGridCell.dataset.name :
      this.glyph.name
    ) //+ '&nbsp;' + String.fromCodePoint(unicode)
    this.idUnicodeElement.innerText = 'U+' + '0'.repeat(
      unicode < 0x10 ? 3 :
      unicode < 0x100 ? 2 :
      unicode < 0x1000 ? 1 :
      0
    ) + unicode.toString(16).toUpperCase()
    this.previewElement.innerText = String.fromCodePoint(unicode)
  }

  updateIdentificationInfo() {
    let wght = this.axisValues.wght >>> 0
    let opsz = this.axisValues.opsz >>> 0
    if (!this.previewAxisValues ||
        this.previewAxisValues.wght != wght ||
        this.previewAxisValues.opsz != opsz)
    {
      this.previewAxisValues = {wght, opsz}
      clearTimeout(this.previewUpdateTimer)
      this.previewUpdateTimer = setTimeout(() => {
        rootElement.style.setProperty('--inspector-wght', wght)
        rootElement.style.setProperty('--inspector-opsz', opsz)
      },10)
    }
  }

  getFontInstance(axisValues) {
    // note: there's no perf/memory benefit to caching instances here
    try {
      let fontInstance = this.font.getVariation(axisValues)
      // [BUG] workaround for bug in fontkit 2.0.2 where xHeight is
      // not correctly loaded for the instance
      const xHeightOpszMax = 1056 // "display"
      const xHeightOpszMin = 1118 // "text"
      // get opsz as range [0-1]
      const opszMin = this.font.variationAxes.opsz.min
      const opszMax = this.font.variationAxes.opsz.max
      let opsz = max(opszMin, min(opszMax, axisValues.opsz))
      opsz = (opsz - opszMin) / (opszMax - opszMin) // 0.0=min, 1.0=max
      // set correct xHeight
      Object.defineProperty(fontInstance, 'xHeight', {
        value: xHeightOpszMin + opsz*(xHeightOpszMax - xHeightOpszMin),
      })
      //console.log("fontInstance:", fontInstance)
      return fontInstance
    } catch (err) {
      console.warn('font.getVariation failed:', err)
      return this.font
    }
  }

  setFontInstance(axisValues) {
    axisValues = {...this.axisValues, ...axisValues}
    if (this.axisValues.wght == axisValues.wght &&
        this.axisValues.opsz == axisValues.opsz)
    {
      //console.debug("this.axisValues unchanged", axisValues, this.axisValues)
      return
    }

    this.axisValues = axisValues
    this.fontInstance = this.getFontInstance(this.axisValues)
    this.setGlyphByUnicode(this.glyphUnicode ? this.glyphUnicode : this.defaultGlyphUnicode)

    const opszMin = this.font.variationAxes.opsz.min
    const opszMax = this.font.variationAxes.opsz.max
    this.opszCheckbox.checked = this.axisValues.opsz < opszMin+(opszMax-opszMin)/2
    this.opszSlider.valueAsNumber = this.axisValues.opsz

    this.updateIdentificationInfo()
  }

  setFont(font) {
    this.font = font
    this.setFontInstance(this.defaultAxisValues)
  }

  async loadFont(url) {
    let data = await fetch(url).then(r => r.arrayBuffer())
    let font = fontkit.create(new Uint8Array(data))
    //console.log(`loadFont(${url}) =>`, font)
    this.setFont(font)

    // let wght = 100
    // let inc = true
    // setInterval(x => {
    //   this.setFontInstance({wght, opsz: WGHT_MAX})
    //   if (inc) {
    //     wght += 10
    //     if (wght > 900) {
    //       wght = 900
    //       inc = false
    //     }
    //   } else {
    //     wght -= 10
    //     if (wght < 100) {
    //       wght = 100
    //       inc = true
    //     }
    //   }
    // }, 20)
  }
}

let inspector = new GlyphInspector()
await inspector.loadFont('font-files/InterVariable.ttf')
// await inspector.loadFont('font-files/InterDisplay-Regular.otf')
