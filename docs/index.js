var isMac = false

function $$(query, el) {
  return [].slice.call((el || document).querySelectorAll(query))
}

function $(query, el) {
  return (el || document).querySelector(query)
}

// fetchjson(url string, cb (err Error, d Object)->nil)
//
var fetchjson = (
  typeof window.fetch == 'function' ? (
    function _fetchjson(url, cb) {
      return window.fetch(url)
        .then(function(r) { return r.json() })
        .then(function(data) { cb(null, data) })
        .catch(cb)
    }
  ) :
  function _fetchjson(url, cb) {
    var r = new XMLHttpRequest()
    r.addEventListener("load", function(){
      try {
        cb(null, JSON.parse(r.responseText))
      } catch (err) {
        cb(err)
      }
    })
    r.open("GET", url)
    r.send()
  }
)

;(function(){
"use strict";


// anim.min.js
var anim=function(h){h=function(a,e,f,b){var g,d,c=[],j=function(a){
if(a=c.shift())a[1]?h.apply(this,a).anim(j):0<a[0]?setTimeout(j,1E3*a[0]):(a[0](),j())};
a.charAt&&(a=document.getElementById(a));if(0<a||!a)e={},f=0,j(c=[[a||0]]);
q(e,{padding:0,margin:0,border:"Width"},[l,m,n,p]);q(e,{borderRadius:"Radius"},[l+p,l+m,n+m,n+p]);++r;
for(g in e)d=e[g],!d.to&&0!==d.to&&(d=e[g]={to:d}),h.defs(d,a,g,b);h.iter(e,1E3*f,j);
return{anim:function(){c.push([].slice.call(arguments));return this}}};
var l="Top", m="Right",n="Bottom",p="Left",r=1,q=function(a,e,f,b,g,d,c){for(b in a)if(b in e){c=a[b];
for(g=0;d=f[g];g++)a[b.replace(e[b],"")+d+(e[b]||"")]={to:0===c.to?c.to:c.to||c,fr:c.fr,e:c.e};
delete a[b]}},s=function(w,a){return w["r"+a]||w["webkitR"+a]||w["mozR"+a]||w["msR"+a]||w["oR"+a]}(
window,"equestAnimationFrame");h.defs=function(a,e,f,b,g){g=e.style;a.a=f;a.n=e;a.s=f in g?g:e;
a.e=a.e||b;a.fr=a.fr||(0===a.fr?0:a.s==e?e[f]:(window.getComputedStyle?getComputedStyle(e, null)
:e.currentStyle)[f]);a.u=(/\d(\D+)$/.exec(a.to)||/\d(\D+)$/.exec(a.fr)||[0,0])[1];a.fn=/color/i.test(f)?
h.fx.color:h.fx[f]||h.fx._;a.mx="anim_"+f;e[a.mx]=a.mxv=r;e[a.mx]!=a.mxv&&(a.mxv=null)};h.iter=function(a,e,f){
var b,g,d,c,h,k=+new Date+e;b=function(){g=k-(new Date).getTime();if(50>g){
for(d in a)d=a[d],d.p=1,d.fn(d,d.n,d.to,d.fr,d.a,d.e);f&&f()}else{g/=e;for(d in a){d=a[d];
if(d.n[d.mx]!=d.mxv)return;h=d.e;c=g;"lin"==h?c=1-c:"ease"==h?(c=2*(0.5-c),c=1-(c*c*c-3*c+2)/4):
"ease-in"==h?(c= 1-c,c*=c*c):c=1-c*c*c;d.p=c;d.fn(d,d.n,d.to,d.fr,d.a,d.e)}s?s(b):setTimeout(b,20)}};
b()};h.fx={_:function(a,e,f,b,g){b=parseFloat(b)||0;f=parseFloat(f)||0;a.s[g]=(1<=a.p?f:a.p*(f-b)+b)+a.u},
width:function(a,e,f,b,g,d){0<=a._fr||(a._fr=!isNaN(b=parseFloat(b))?b:"width"==g?e.clientWidth:e.clientHeight);
h.fx._(a,e,f,a._fr,g,d)},opacity:function(a,e,f,b,g){if(isNaN(b=b||a._fr))b=e.style,b.zoom=1,
b=a._fr=(/alpha\(opacity=(\d+)\b/i.exec(b.filter)||{})[1]/100||1;b*=1;f=a.p*(f-b)+b;e=e.style;g in e?e[g]= f:
e.filter=1<=f?"":"alpha("+g+"="+Math.round(100*f)+")"},color:function(a,e,f,b,g,d,c,j){
a.ok||(f=a.to=h.toRGBA(f),b=a.fr=h.toRGBA(b),0==f[3]&&(f=[].concat(b),f[3]=0),0==b[3]&&
(b=[].concat(f),b[3]=0),a.ok=1);j=[0,0,0,a.p*(f[3]-b[3])+1*b[3]];for(c=2;0<=c;c--)j[c]=Math.round(
a.p*(f[c]-b[c])+1*b[c]);(1<=j[3]||h.rgbaIE)&&j.pop();try{a.s[g]=(3<j.length?"rgba(":"rgb(")+j.join(",")+")"
}catch(k){h.rgbaIE=1}}};h.fx.height=h.fx.width;
h.RGBA=/#(.)(.)(.)\b|#(..)(..)(..)\b|(\d+)%,(\d+)%,(\d+)%(?:,([\d\.]+))?|(\d+),(\d+),(\d+)(?:,([\d\.]+))?\b/;
h.toRGBA=function(a,e){e=[0,0,0,0];a.replace(/\s/g,"").replace(h.RGBA,function(a,b,g,d,c,h,k,l,m,n,p,q,r,s,t){
k=[b+b||c,g+g||h,d+d||k];b=[l,m,n];for(a=0;3>a;a++)k[a]=parseInt(k[a],16),b[a]=Math.round(2.55*b[a]);
e=[k[0]||b[0]||q||0,k[1]||b[1]||r||0,k[2]||b[2]||s||0,p||t||1]});return e};return h}();


if (!window.MSStream &&
    /mac|ipad|iphone|ipod/i.test(navigator.userAgent))
{
  isMac = true
  document.body.classList.add('mac_or_ios')
  if (navigator.userAgent.indexOf('Safari') != -1) {
    document.body.classList.add('safari')
  }
}


// timeNow() :float
var timeNow = (
  window.performance !== undefined && window.performance.now ? function() {
    return window.performance.now()
  } : Date.now ? function() {
    return Date.now()
  } : function() {
    return (new Date()).getTime()
  }
)


// download-link
fetchjson('info.json', function(err, data) {
  if (err) { throw err }
  var ids = Object.keys(data)
  var regularId = ids[0]
  ids.forEach(function(id){
    if (id.indexOf('Inter UI Regular:') == 0) {
      regularId = id
    }
  })
  if (ids.length == 0) {
    console.error('failed to find Inter UI Regular in info.json', data)
    return
  }
  var regular = data[regularId]
  // console.log('info.json:', regular)
  if (regular.names && regular.names.version) {
    var v = regular.names.version
    var p = v.indexOf(';')
    if (p != -1) {
      v = v.substr(0, p)
    }
    var directDownloadURL =
      'https://github.com/rsms/inter/releases/download/v' + v +
      '/Inter-UI-' + v + '.zip'
    var av = document.querySelectorAll('a.download-link'), i, e
    for (i = 0; i < av.length; ++i) {
      e = av[i]
      e.href = directDownloadURL
    }
  }
})


// Google Analytics
;(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-105091131-2', 'auto');
ga('send', 'pageview');

})();
