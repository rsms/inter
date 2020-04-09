
function $$(query, el) {
  return [].slice.call((el || document).querySelectorAll(query))
}

function $(query, el) {
  return (el || document).querySelector(query)
}

// fetchjson(url string) :Promise<Object>
//
var fetchjson = (
  typeof window.fetch == 'function' ? (
    function _fetchjson(url, cb) {
      return window.fetch(url).then(function(r) { return r.json() })
    }
  ) :
  function _fetchjson(url, cb) {
    return new Promise(function(resolve, reject) {
      var r = new XMLHttpRequest()
      r.addEventListener("load", function(){
        try {
          resolve(JSON.parse(r.responseText))
        } catch (err) {
          reject(err)
        }
      })
      r.addEventListener("error", function(ev) {
        reject(ev.error || ev || new Error('network error'))
      })
      r.open("GET", url)
      r.send()
    })
  }
)


// timeNow() :float
//
var timeNow = (
  window.performance !== undefined && window.performance.now ? function() {
    return window.performance.now()
  } : Date.now ? function() {
    return Date.now()
  } : function() {
    return (new Date()).getTime()
  }
)


var HUDNotification = {
  el: $('#hud-notification'),
  timer: null,
  visible: false,

  show: function(message, duration) {
    var n = this
    n.el.firstChild.innerText = message
    n.el.classList.add('visible')
    if (n.visible) {
      n.hide()
      setTimeout(function(){ n.show(message, duration) }, 120)
      return
    }
    n.visible = true
    n.el.style.visibility = null
    clearTimeout(n.timer)
    n.timer = setTimeout(function(){ n.hide() }, duration || 1200)
  },

  hide: function() {
    var n = this
    if (n.visible) {
      n.el.classList.remove('visible')
      n.visible = false
      n.el.style.visibility = 'hidden'
    }
  }
}


// InterDynamicTracking takes the font size in points or pixels and returns
// the compensating tracking in EM.
//
function InterDynamicTracking(fontSize) {
  var a = -0.0223, b = 0.185, c = -0.1745;
  // tracking = a + b * e ^ (c * fontSize)
  return a + b * Math.pow(Math.E, c * fontSize)
}

// InterDynamicLineHeight produces the line height for the given font size
//
function InterDynamicLineHeight(fontSize) {
  var l = 1.4
  return Math.round(fontSize * l)
}


// Mac or not? Maybe a buggy Safari or a busted Chrome on Windows...
var isMac = false
if (!window.MSStream &&
    /mac|ipad|iphone|ipod/i.test(navigator.userAgent))
{
  isMac = true
  if (navigator.userAgent.indexOf('Safari') != -1 &&
      navigator.userAgent.indexOf('Chrome') == -1)
  {
    document.body.classList.add('safari')
  }
} else if (
  navigator.userAgent.indexOf('Windows') != -1 &&
  navigator.userAgent.indexOf('Chrome') != -1
) {
  document.body.classList.add('chrome-win')
}
