var CtxEdit = (function(){


function getLocalObject(key) {
  let s = sessionStorage.getItem(key)
  if (s) {
    try {
      return JSON.parse(s)
    } catch (e) {
      console.error(
        `failed to parse sessionStorage value "${s}" for key ${key}`,
        err.stack || String(err)
      )
    }
  }
  return null
}


function setLocalObject(key, value) {
  let json = JSON.stringify(value)
  sessionStorage.setItem(key, json)
}


function rmLocalObject(key) {
  sessionStorage.removeItem(key)
}


class FloatProp {
  constructor(cssProp, unitSuffix) {
    this.cssProp = cssProp
    this.unitSuffix = unitSuffix
  }

  valueInStyle(s) {
    let v = s[this.cssProp]
    return v !== undefined ? parseFloat(v) : v
  }

  applyStyle(el, value) {
    el.style[this.cssProp] = value + this.unitSuffix
  }
}

class FontStyleProp {

  valueInStyle(s) {
    let italic = s['font-style'] == 'italic' || s['font-style'].indexOf('oblique') != -1
    let weight = parseFloat(s['font-weight'])
    if (isNaN(weight)) {
      weight = s['font-weight']
      if (weight == 'thin') {       return italic ? 'thin-italic' :       'thin' }
      if (weight == 'extra-light') {return italic ? 'extra-light-italic' :'extra-light' }
      if (weight == 'light') {      return italic ? 'light-italic' :      'light' }
      if (weight == 'normal') {     return italic ? 'italic' :            'regular' }
      if (weight == 'medium') {     return italic ? 'medium-italic' :     'medium' }
      if (weight == 'semi-bold') {  return italic ? 'semi-bold-italic' :  'semi-bold' }
      if (weight == 'bold') {       return italic ? 'bold-italic' :       'bold' }
      if (weight == 'extra-bold') { return italic ? 'extra-bold-italic' : 'extra-bold' }
    } else {
      if (weight <= 150) { return italic ? 'thin-italic' :       'thin' }
      if (weight <= 250) { return italic ? 'extra-light-italic' :'extra-light' }
      if (weight <= 350) { return italic ? 'light-italic' :      'light' }
      if (weight <= 450) { return italic ? 'italic' :            'regular' }
      if (weight <= 550) { return italic ? 'medium-italic' :     'medium' }
      if (weight <= 650) { return italic ? 'semi-bold-italic' :  'semi-bold' }
      if (weight <= 750) { return italic ? 'bold-italic' :       'bold' }
      if (weight <= 850) { return italic ? 'extra-bold-italic' : 'extra-bold' }
    }
    return italic ? 'black-italic' : 'black'
  }

  applyStyle(el, value) {
    let cl = el.classList
    for (let k of Array.from(cl.values())) {
      if (k.indexOf('font-style-') == 0) {
        cl.remove(k)
      }
    }
    cl.add('font-style-' + value)
  }
}

class LineHeightProp {
  valueInStyle(s) {
    let v = s['line-height']
    if (v === undefined) {
      return 1.0
    }
    if (v.lastIndexOf('px') == v.length - 2) {
      // compute
      return parseFloat(
        (parseFloat(v) / parseFloat(s['font-size'])).toFixed(3)
      )
    }
    v = parseFloat(v)
    return isNaN(v) ? 1.0 : v
  }

  applyStyle(el, value) {
    el.style['line-height'] = String(value)
  }
}

class TrackingProp {
  valueInStyle(s) {
    let v = s['letter-spacing']
    if (v === undefined) {
      return 0
    }
    if (v.lastIndexOf('px') == v.length - 2) {
      // compute
      return parseFloat(
        (parseFloat(v) / parseFloat(s['font-size'])).toFixed(3)
      )
    }
    v = parseFloat(v)
    return isNaN(v) ? 0 : v
  }

  applyStyle(el, value) {
    el.style['letter-spacing'] = value.toFixed(3) + 'em'
  }
}

const Props = {
  size:       new FloatProp('font-size', 'px'),
  tracking:   new TrackingProp(),
  lineHeight: new LineHeightProp(),
  style:      new FontStyleProp(),
}

function valuesFromStyle(s) {
  let values = {}
  for (let name in Props) {
    let p = Props[name]
    values[name] = p.valueInStyle(s)
  }
  return values
}


class Editable {
  constructor(el, key) {
    this.el = el
    this.key = key
    this.defaultValues = valuesFromStyle(getComputedStyle(this.el))
    this.values = Object.assign({}, this.defaultValues)
    this.defaultExplicitTracking = this.defaultValues['tracking'] != 0
    this.explicitTracking = this.defaultExplicitTracking
    this.explicitTrackingKey = this.key + ":etracking"
    this.loadValues()
    this.updateSizeDependantProps()
  }

  resetValues() {
    this.values = Object.assign({}, this.defaultValues)
    let style = this.el.style
    for (let name in this.values) {
      Props[name].applyStyle(this.el, this.values[name])
    }
    rmLocalObject(this.key)
    rmLocalObject(this.explicitTrackingKey)
    this.explicitTracking = this.defaultExplicitTracking
    this.updateSizeDependantProps()
  }

  setExplicitTracking(explicitTracking) {
    if (this.explicitTracking !== explicitTracking) {
      this.explicitTracking = explicitTracking
      if (!this.explicitTracking) {
        this.updateSizeDependantProps()
      }
    }
  }

  setValue(name, value) {
    this.values[name] = value
    Props[name].applyStyle(this.el, value)
    if (name == 'size') {
      this.updateSizeDependantProps()
    }
  }

  updateSizeDependantProps() {
    let size = this.values.size

    // dynamic tracking
    if (!this.explicitTracking) {
      this.setValue('tracking', InterDynamicTracking(size))
    }

    // left indent
    // TODO: Consider making this part of dynamic metrics.
    let leftMargin = size / -16
    if (leftMargin == 0) {
      this.el.style.marginLeft = null
    } else {
      this.el.style.marginLeft = leftMargin.toFixed(1) + 'px'
    }
  }

  loadValues() {
    let values = getLocalObject(this.key)
    if (values && typeof values == 'object') {
      for (let name in values) {
        if (name in this.values) {
          let value = values[name]
          this.values[name] = value
          Props[name].applyStyle(this.el, value)
        } else if (console.warn) {
          console.warn(`Editable.loadValues ignoring unknown "${name}"`)
        }
      }
      // console.log(`loaded values for ${this}:`, values)
    }
    let etr = getLocalObject(this.explicitTrackingKey)
    this.explicitTracking = this.defaultExplicitTracking || etr
  }

  isDefaultValues() {
    for (let k in this.values) {
      if (this.values[k] !== this.defaultValues[k]) {
        return false
      }
    }
    return true
  }

  saveValues() {
    if (this.isDefaultValues()) {
      rmLocalObject(this.key)
      rmLocalObject(this.explicitTrackingKey)
    } else {
      setLocalObject(this.key, this.values)
      setLocalObject(this.explicitTrackingKey, this.explicitTracking ? "1" : "0")
    }
    // console.log(`saved values for ${this}`)
  }

  toString() {
    return `Editable(${this.key})`
  }
}


var supportsFocusTrick = (u =>
  u.indexOf('Firefox/') == -1
)(navigator.userAgent)


class CtxEdit {
  constructor() {
    this.bindings = new Bindings()
    this.keyPrefix = 'ctxedit:' + document.location.pathname + ':'
    this.editables = new Map()
    this.ui = $('#ctxedit-ui')
    this.currEditable = null
    this._saveValuesTimer = null
    this.isChangingBindings = true
    this.bindings = new Bindings()
    this.initBindings()
    this.initUI()
    this.addAllEditables()
    this.isChangingBindings = false
    this.preloadFonts()

    if (supportsFocusTrick) {
      this.ui.addEventListener('focus', ev => {
        if (this.currEditable) {
          ev.preventDefault()
          ev.stopImmediatePropagation()
          this.currEditable.el.focus()  // breaks Firefox
        }
      }, {capture:true, passive:false})
    }
  }

  initUI() {
    $('.reset-button', this.ui).addEventListener('click', ev => this.reset())
    $('.dismiss-button', this.ui).addEventListener('click', ev => this.stopEditing())
    this.initRangeSliders()
  }

  initRangeSliders() {
    this._sliderTimers = new Map()
    $$('input[type="range"]', this.ui).forEach(input => {
      var binding = this.bindings.getBinding(input.dataset.binding)

      // create and hook up value tip
      let valtip = document.createElement('div')
      let valtipval = document.createElement('div')
      let valtipcallout = document.createElement('div')
      valtip.className = 'slider-value-tip'
      valtipval.className = 'value'
      valtipcallout.className = 'callout'
      valtipval.innerText = '0'
      valtip.appendChild(valtipval)
      valtip.appendChild(valtipcallout)
      binding.addOutput(valtipval)
      document.body.appendChild(valtip)

      let inputBounds = {}
      let min = parseFloat(input.getAttribute('min'))
      let max = parseFloat(input.getAttribute('max'))
      if (isNaN(min)) {
        min = 0
      }
      if (isNaN(max)) {
        max = 1
      }
      const sliderThumbWidth = 12
      const valtipYOffset = 14

      let updateValTipXPos = () => {
        let r = (binding.value - min) / (max - min)
        let sliderWidth = inputBounds.width - sliderThumbWidth
        let x = ((inputBounds.x + (sliderThumbWidth / 2)) + (sliderWidth * r)) - (valtip.clientWidth / 2)
        valtip.style.left = x + 'px'
      }

      binding.addListener(updateValTipXPos)

      let shownCounter = 0
      let showValTip = () => {
        if (++shownCounter == 1) {
          valtip.classList.add('visible')
          inputBounds = input.getBoundingClientRect()
          valtip.style.top = (inputBounds.y - valtip.clientHeight + valtipYOffset) + 'px'
          updateValTipXPos()
        }
      }
      let hideValTip = () => {
        if (--shownCounter == 0) {
          valtip.classList.remove('visible')
        }
      }

      input.addEventListener('pointerdown', showValTip)
      input.addEventListener('pointerup', hideValTip)
      input.addEventListener('pointercancel', hideValTip)

      let timer = null
      input.addEventListener('input', ev => {
        if (timer === null) {
          showValTip()
        } else {
          clearTimeout(timer)
        }
        timer = setTimeout(() => {
          timer = null
          hideValTip()
        }, 400)
      })
    })
  }

  initBindings() {
    let b = this.bindings

    // let updateTracking = fontSize => {
    //   if (!this.currEditable.explicitTracking) {
    //     var tracking = InterDynamicTracking(fontSize)
    //     this.isChangingBindings = true
    //     b.setValue('tracking', tracking)
    //     this.isChangingBindings = false
    //   }
    // }

    b.configure('tracking', 0, 'float', tracking => {
      if (!this.isChangingBindings && !this.currEditable.explicitTracking) {
        // console.log('enabled explicit tracking')
        this.currEditable.setExplicitTracking(true)
        this.setNeedsSaveValues()
      }
    })
    b.setFormatter('tracking', v => v.toFixed(3))

    b.configure('size', 0, 'float', size => {
      let ed = this.currEditable
      if (ed) {
        setTimeout(() => {
          // HERE BE DRAGONS! Feedback loop from Editable
          if (!ed.explicitTracking) {
            this.isChangingBindings = true
            b.setValue('tracking', ed.values.tracking)
            this.isChangingBindings = false
          }
        }, 10)
      }
    })

    b.configure('lineHeight', 1, 'float')

    b.bindAllInputs($$('.control input', this.ui))
    b.bindAllInputs($$('.control select', this.ui))

    $('.control input[data-binding="tracking"]').addEventListener("dblclick", ev => {
      let ed = this.currEditable
      setTimeout(() => {
        ed.setExplicitTracking(false)
        this.setNeedsSaveValues()
        this.isChangingBindings = true
        b.setValue('tracking', ed.values.tracking)
        this.isChangingBindings = false
      }, 50)
    })

    for (let binding of b.allBindings()) {
      binding.addListener(() => this.bindingChanged(binding))
    }
  }

  preloadFonts() {
    // Note: This has no effect on systems supporting variable fonts.
    [
      "regular",
      "italic",
      "medium",
      "medium-italic",
      "semi-bold",
      "semi-bold-italic",
      "bold",
      "bold-italic",
      "extra-bold",
      "extra-bold-italic",
      "black",
      "black-italic",
    ].forEach(style => {
      let e = document.createElement('div')
      e.className = 'font-preload font-style-' + style
      e.innerText = 'a'
      document.body.appendChild(e)
    })
  }

  bindingChanged(binding) {
    if (this.isChangingBindings) {
      // Note: this.isChangingBindings is true when binding values are
      // changed internally, in which case we do nothing here.
      return
    }
    if (this.currEditable) {
      this.currEditable.setValue(binding.name, binding.value)
    }
    this.setNeedsSaveValues()
  }

  reset() {
    for (let ed of this.editables.values()) {
      ed.resetValues()
    }
    this.updateBindingValues()
  }

  updateBindingValues() {
    if (this.currEditable) {
      this.isChangingBindings = true
      this.bindings.setValues(this.currEditable.values)
      this.isChangingBindings = false
    }
  }

  saveValues() {
    if (this._saveValuesTimer !== null) {
      clearTimeout(this._saveValuesTimer)
      this._saveValuesTimer = null
    }
    if (this.currEditable) {
      this.currEditable.saveValues()
    }
  }

  setNeedsSaveValues() {
    if (this._saveValuesTimer !== null) {
      clearTimeout(this._saveValuesTimer)
    }
    this._saveValuesTimer = setTimeout(() => this.saveValues(), 300)
  }

  setCurrEditable(ed) {
    if (this._saveValuesTimer !== null &&
        this.currEditable &&
        !this.isChangingBindings)
    {
      this.saveValues()
    }
    this.currEditable = ed
    this.updateBindingValues()
    if (this.currEditable) {
      this.showUI()
    } else {
      this.hideUI()
    }
  }

  onEditableReceivedFocus(ed) {
    // console.log(`onEditableReceivedFocus ${ed}`)
    clearTimeout(this._deselectTimer)
    this.setCurrEditable(ed)
  }

  onEditableLostFocus(ed) {
    // console.log(`onEditableLostFocus ${ed}`)
    // this.setCurrEditable(null)
    if (supportsFocusTrick) {
      this._deselectTimer = setTimeout(() => this.setCurrEditable(null), 10)
    }
  }

  showUI() {
    this.ui.classList.add('visible')
  }

  hideUI() {
    this.ui.classList.remove('visible')
  }

  stopEditing() {
    if (this.currEditable) {
      this.currEditable.el.blur()
      this.setCurrEditable(null)
    }
  }

  addAllEditables() {
    for (let el of $$('[data-ctxedit]')) {
      this.addEditable(el)
    }
  }

  addEditable(el) {
    let key = this.keyPrefix + el.dataset.ctxedit
    let existing = this.editables.get(key)
    if (existing) {
      throw new Error(`duplicate editable ${key}`)
    }
    let ed = new Editable(el, key)
    this.editables.set(key, ed)
    this.initEditable(ed)
    // this.showUI() // XXX
  }

  initEditable(ed) {
    // filter paste
    ed.el.addEventListener('paste', ev => {
      ev.preventDefault()
      let text = ev.clipboardData.getData("text/plain")
      document.execCommand("insertHTML", false, text)
    }, {capture:true,passive:false})

    ed.el.addEventListener('focus', ev => this.onEditableReceivedFocus(ed))
    ed.el.addEventListener('blur', ev => this.onEditableLostFocus(ed))
  }
}

return CtxEdit
})();
