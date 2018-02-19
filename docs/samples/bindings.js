// requires index.js

function Binding(name){
  this.name = name
  this.value = undefined
  this.inputs = []
  this.listeners = []
  this.formatter = undefined
}


Binding.prototype.addInput = function(el) {
  var binding = this
  var _onInput = function(ev) {
    binding.setValue(el.value, el)
  }
  var input = {
    el: el,
    _onInput: _onInput,
  }
  this.inputs.push(input)
  if (this.value === undefined) {
    this.value = el.value
  } else {
    input.el.value = this.value
  }
  el.addEventListener('input', _onInput, {passive:true})
}


// listener signature:
//   function(nextval string, prevval string, b Binding)void
//
Binding.prototype.addListener = function(listener) {
  this.listeners.push(listener)
}


Binding.prototype.setValue = function(nextval, origin) {
  // console.log('Binding.setValue nextval:', nextval, {origin})
  var prevval = this.value
  if (this.formatter) {
    nextval = this.formatter(nextval, prevval)
  }
  if (this.value === nextval) {
    return
  }
  var binding = this
  this.value = nextval
  this.inputs.forEach(function(input) {
    if (input.el !== origin) {
      input.el.value = nextval
    }
  })
  this.listeners.forEach(function(listener) {
    listener(nextval, prevval, this)
  })
}


function Bindings() {
  this.bindings = {}
}

Bindings.prototype.getBinding = function(name, input) {
  var binding = this.bindings[name]
  if (!binding) {
    binding = new Binding(name)
    this.bindings[name] = binding
  }
  return binding
}

Bindings.prototype.bindInput = function(name, input) {
  // console.log('bindInput', name, input)
  var binding = this.getBinding(name)
  binding.addInput(input)
}

Bindings.prototype.bindAllInputs = function(queryOrInputElementList) {
  var bindings = this

  var inputs = (
    typeof queryOrInputElementList == 'string' ? $$(queryOrInputElementList) :
    queryOrInputElementList
  )

  inputs.forEach(function(input) {
    var bindingName = input.dataset.binding
    if (bindingName) {
      bindings.bindInput(bindingName, input)
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
// listener and associating a formatter with a binding.
// If a listener and a value is provided, the value is set and the listener
// is immediately invoked.
//
Bindings.prototype.configure = function(name, value, formatter, listener) {
  var binding = this.getBinding(name)
  if (listener) {
    binding.addListener(listener)
  }
  if (value !== undefined && value !== null) {
    binding.setValue(value)
  }
  if (formatter) {
    if (typeof formatter == 'string') {
      switch (formatter) {
        case 'number':
        case 'float':
          formatter = fmt_float; break;
        
        case 'int':
        case 'integer':
          formatter = fmt_int; break;

        default:
          throw new Error('unknown formatter "' + formatter + '"')
      }
    } else if (typeof formatter != 'function') {
      throw new Error('formatter should be a string or function')
    }
    binding.formatter = formatter
  }
}
