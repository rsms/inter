// requires index.js

function passThrough(v) { return v }

function valueGetter(el) {
  return (
    'valueAsNumber' in el ? () => el.valueAsNumber :
    (el.type == 'number' || el.type == 'range') ? () => parseFloat(el.value) :
    () => el.value
  )
}

function Binding(name){
  this.name = name
  this.value = undefined
  this.inputs = []
  this.outputs = []
  this.listeners = []
  this.parser = undefined
  this.formatter = passThrough
}


Binding.prototype.addInput = function(el) {
  var binding = this
  var getValue = valueGetter(el)
  var _onInput = ev => {
    binding.setValue(getValue(), el)
  }
  var input = {
    el: el,
    _onInput: _onInput,
  }
  this.inputs.push(input)
  if (this.value === undefined) {
    this.value = getValue()
  } else {
    input.el.value = this.formatter(this.value)
  }
  if (el.tagName == 'SELECT' || el.type == 'checkbox') {
    el.addEventListener('change', _onInput, {passive:true})
  } else {
    el.addEventListener('input', _onInput, {passive:true})
  }
}


Binding.prototype.addOutput = function(el) {
  this.outputs.push(el)
  if (this.value !== undefined) {
    el.innerText = this.formatter(this.value)
  }
}


// listener signature:
//   function(nextval string, prevval string, b Binding)void
//
Binding.prototype.addListener = function(listener) {
  this.listeners.push(listener)
}


Binding.prototype.setValue = function(nextval, origin) {
  var prevval = this.value
  if (this.parser) {
    nextval = this.parser(nextval, prevval)
  }
  if (this.value === nextval) {
    return
  }
  var binding = this
  this.value = nextval
  var value = binding.formatter(nextval)
  this.inputs.forEach(function(input) {
    if (input.el !== origin) {
      input.el.value = value
    }
  })
  this.outputs.forEach(function(el) {
    el.innerText = value
  })
  this.listeners.forEach(function(listener) {
    listener(nextval, prevval, this)
  })
}

// ------------------------------------------------------------------------

function Bindings() {
  this.bindings = {}
}

Bindings.prototype.getBinding = function(name) {
  var binding = this.bindings[name]
  if (!binding) {
    binding = new Binding(name)
    this.bindings[name] = binding
  }
  return binding
}

Bindings.prototype.bindInput = function(name, input) {
  var binding = this.getBinding(name)
  binding.addInput(input)
}

Bindings.prototype.bindOutput = function(name, el) {
  var binding = this.getBinding(name)
  binding.addOutput(el)
}

Bindings.prototype.bindAllInputs = function(queryOrInputElementList) {
  var bindings = this

  var elements = (
    typeof queryOrInputElementList == 'string' ? $$(queryOrInputElementList) :
    queryOrInputElementList
  )

  elements.forEach(function(el) {
    var bindingName = el.dataset.binding
    if (bindingName) {
      if (
        el.tagName == 'INPUT' ||
        el.tagName == 'TEXTAREA' ||
        el.tagName == 'SELECT'
      ) {
        bindings.bindInput(bindingName, el)
      } else {
        bindings.bindOutput(bindingName, el)
      }
    }
  })
}

// listener signature:
//   function(nextval string, prevval string, b Binding)void
//
Bindings.prototype.addListener = function(name, listener) {
  var binding = this.getBinding(name)
  binding.addListener(listener)
}

Bindings.prototype.setValue = function(name, value) {
  var binding = this.getBinding(name)
  binding.setValue(value)
}

Bindings.prototype.setFormatter = function(name, formatter) {
  var binding = this.getBinding(name)
  binding.formatter = formatter || passThrough
}


Bindings.prototype.value = function(name, defaultValue) {
  var binding = this.bindings[name]
  return binding && binding.value !== undefined ? binding.value : defaultValue
}


function fmt_float(nextval, prevval) {
  var n = parseFloat(nextval)
  return isNaN(n) ? 0 : n
}

function fmt_int(nextval, prevval) {
  var n = parseInt(nextval)
  return isNaN(n) ? 0 : n
}


// configure is convenience function for setting value, adding a
// listener and associating a parser with a binding.
// If a listener and a value is provided, the value is set and the listener
// is immediately invoked.
//
Bindings.prototype.configure = function(name, value, parser, listener) {
  var binding = this.getBinding(name)
  if (listener) {
    binding.addListener(listener)
  }
  if (value !== undefined && value !== null) {
    binding.setValue(value)
  }
  if (parser) {
    if (typeof parser == 'string') {
      switch (parser) {
        case 'number':
        case 'float':
          parser = fmt_float; break;
        
        case 'int':
        case 'integer':
          parser = fmt_int; break;

        default:
          throw new Error('unknown parser "' + parser + '"')
      }
    } else if (typeof parser != 'function') {
      throw new Error('parser should be a string or function')
    }
    binding.parser = parser
  }
}


Bindings.prototype.allBindings = (
  typeof Object.values == 'function' ? function() {
    return Object.values(this.bindings)
  } : function() {
    let v = []
    for (let name in this.bindings) {
      v.push(this.bindings[name])
    }
    return v
  }
)


Bindings.prototype.getValues = function() {
  let values = {}
  for (let name in this.bindings) {
    values[name] = this.bindings[name].value
  }
  return values
}


Bindings.prototype.setValues = function(values) {
  Object.keys(values).forEach(name => {
    let b = this.bindings[name]
    if (!b) {
      if (console.warn) {
        console.warn('Bindings.setValues: ignoring unknown "' + name + '"')
      }
      return
    }
    // console.log(`bindings setValue ${name} => ${values[name]}`)
    b.setValue(values[name])
  })
}
