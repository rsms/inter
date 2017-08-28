var isMac = false

if (!window.MSStream &&
    /mac|ipad|iphone|ipod/i.test(navigator.userAgent))
{
  isMac = true
  document.body.classList = 'mac_or_ios'
}

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-105091131-2', 'auto');
ga('send', 'pageview');
