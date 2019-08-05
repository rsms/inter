(function(){

var root = document.querySelector('div.variable')
var sample = document.querySelector('.variable-sample')
var animateCheckbox = document.querySelector('[name="animate"]')


var ui = {
  state: {
    weight:        0,
    slant:         0,
    size:          0, // px
    letterSpacing: 0, // em
    lineHeight:    0,
  },

  variable: {
    weight: true,
    slant: true,
  },

  formatters: {
    size(v) { return `${v}px` },
    letterSpacing(v) { return `${v}em` },
  },

  inputs: {
    // populated by init()
  },

  init() {
    let s = getComputedStyle(sample)

    // We test for variable-font support by, in CSS, conditionally using
    // a different font family name when VF is supported. Then we test for
    // what font family name is in effect. If it's the "var" one, we can be
    // fairly certain that variable fonts are supported by the user agent.
    let supportsVF = s.fontFamily.indexOf('Inter var') != -1

    // hook up input controls
    for (let k in this.state) {
      let value = parseFloat(s.getPropertyValue(`--var-${k}`))
      this.state[k] = value
      let input = root.querySelector(`[name="${k}"]`)
      if (input) {
        this.inputs[k] = input
        input.value = value
        if (!supportsVF && this.variable[k]) {
          input.disabled = true
          input.parentElement.classList.add('disabled')
        } else if (input.type == 'range') {
          this.bindRangeControl(input, v => {
            this.state[k] = v
            this.update()
          })
        }
      }
    }

    if (!supportsVF) {
      animateCheckbox.disabled = true
      animateCheckbox.parentElement.classList.add('disabled')
      let unsupportedMessage = root.querySelector(`.unsupported-message`)
      if (unsupportedMessage) {
        unsupportedMessage.classList.add('active')
      }
    } else {
      this.state.size = window.innerWidth / 10
      root.querySelector(`[name="size"]`).value = this.state.size
      this.update()
    }
  },

  bindRangeControl(rangeInput, handler) {
    rangeInput.addEventListener('input',
      rangeInput.valueAsNumber !== undefined ? ev => {
        handler(rangeInput.valueAsNumber)
      } : ev => {
        handler(parseFloat(rangeInput.value))
      }
    )
  },

  setState(props) {
    for (let k in props) {
      if (k in this.state) {
        this.state[k] = props[k]
      }
    }
    this.update()
  },

  update() {
    let s = sample.style
    for (let k in this.state) {
      let f = this.formatters[k]
      let v = this.state[k]
      if (k == "slant") {
        // negate slant value (negative values causes positive grades)
        v = -v
      }
      s.setProperty(`--var-${k}`, f ? f(v) : v)
    }
  },
}


// monotime() :float  milliseconds
//
var monotime = (
  window.performance !== undefined && window.performance.now ? function() {
    return window.performance.now()
  } : Date.now ? function() {
    return Date.now()
  } : function() {
    return (new Date()).getTime()
  }
)


var isAnimating = false
function startAnimation() {
  if (isAnimating) {
    return
  }
  ui.inputs.weight.disabled = true
  ui.inputs.slant.disabled = true
  isAnimating = true
  let v = 0
  let wmin = parseFloat(ui.inputs.weight.min)
    , wmax = parseFloat(ui.inputs.weight.max)
    , imin = parseFloat(ui.inputs.slant.min)
    , imax = parseFloat(ui.inputs.slant.max)
    , wspeed = 800    // lower is faster; time divisor
    , ispeed = 1600
    , clamp = 0.001
    , startTime = monotime()
  function update() {
    let r = 0, v = 0

    r = (1 + Math.sin((monotime() - startTime) / wspeed)) * 0.5
    v = (wmin * (1 - clamp)) + (((wmax * (1 + clamp)) - (wmin * (1 - clamp))) * r)
    v = Math.max(wmin, Math.min(wmax, v))
    ui.state.weight = v
    ui.inputs.weight.value = v

    r = (1 + Math.sin((monotime() - startTime) / ispeed)) * 0.5
    v = (imin * (1 - clamp)) + (((imax * (1 + clamp)) - (imin * (1 - clamp))) * r)
    v = Math.max(imin, Math.min(imax, v))
    ui.state.slant = v
    ui.inputs.slant.value = v

    ui.update()

    if (isAnimating) {
      requestAnimationFrame(update)
    }
  }
  update()
}

function stopAnimation() {
  isAnimating = false
  ui.inputs.weight.disabled = false
  ui.inputs.slant.disabled = false
  ui.inputs.weight.value = String(ui.state.weight)
  ui.inputs.slant.value = String(ui.state.slant)
}

// UI control: animate
if (!window.requestAnimationFrame) {
  animateCheckbox.disabled = true
  animateCheckbox.title = "Not supported by browser"
} else {
  animateCheckbox.addEventListener('change', ev => {
    if (animateCheckbox.checked) {
      startAnimation()
    } else {
      stopAnimation()
    }
  })
}

// UI control: invert colors ("Black/White")
document.querySelector('[name="invert"]').addEventListener('change', ev => {
  if (ev.target.checked) {
    sample.parentElement.classList.add('black')
    sample.parentElement.classList.remove('white')
  } else {
    sample.parentElement.classList.remove('black')
    sample.parentElement.classList.add('white')
  }
})


ui.init()


})();
