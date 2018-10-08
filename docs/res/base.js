
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
    clearTimeout(n.timer)
    n.timer = setTimeout(function(){ n.hide() }, duration || 1200)
  },

  hide: function() {
    var n = this
    if (n.visible) {
      n.el.classList.remove('visible')
      n.visible = false
    }
  }
}


// InterUIDynamicTracking takes the font size in points or pixels and returns
// the compensating tracking in EM.
//
function InterUIDynamicTracking(fontSize) {
  // tracking = a + b * e ^ (c * fontSize)
  var a = -0.017, b = 0.202, c = -0.175;
  return a + b * Math.pow(Math.E, c * fontSize)
}

// InterUIDynamicLineHeight produces the line height for the given font size
//
function InterUIDynamicLineHeight(fontSize) {
  var l = 1.4
  return Math.round(fontSize * l)
}


// Mac or not? Maybe even a buggy Safari?
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
}


// Google Analytics
// ;(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
// (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
// m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
// })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
// ga('create', 'UA-105091131-2', 'auto');
// ga('send', 'pageview');
window.dataLayer = window.dataLayer || [];
window.dataLayer.push(['js', new Date()])
window.dataLayer.push(['config', 'UA-105091131-2'])
