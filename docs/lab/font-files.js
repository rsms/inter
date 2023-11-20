var fontFamilyName
var fontFamilyNameDisplay
var fontFamilyNameVar

;(()=>{
  let isLocalServer = document.location.protocol == "http:"

  const includeLabLocalFiles = isLocalServer

  const fontVersion = (
    isLocalServer || typeof interBuildVersion == "undefined" ?
      Math.round(Date.now()).toString(36) :
      interBuildVersion.replace(/\./g, "_")
  );

  fontFamilyName = 'Inter-v' + fontVersion
  fontFamilyNameDisplay = 'InterDisplay-v' + fontVersion
  fontFamilyNameVar = 'Inter-var-v' + fontVersion

  let outbuf = []
  function w(s) { outbuf.push(s) }

  function genStaticFontFace(family, cssname, filepath, weight, isItalic) {
    let styleName = ""
    switch (weight) {
      case 100: styleName = "Thin"; break
      case 200: styleName = "ExtraLight"; break
      case 300: styleName = "Light"; break
      case 400: styleName = ""; break
      case 500: styleName = "Medium"; break
      case 600: styleName = "SemiBold"; break
      case 700: styleName = "Bold"; break
      case 800: styleName = "ExtraBold"; break
      case 900: styleName = "Black"; break
    }
    if (styleName == "") {
      styleName = isItalic ? "Italic" : "Regular"
    } else if (isItalic) {
      styleName += "Italic"
    }
    let filename = `${family}-${styleName}`
    w(`@font-face {`)
    w(`  font-family: ${cssname};`)
    w(`  font-style:  ${isItalic ? "italic" : "normal"};`)
    w(`  font-weight: ${weight};`)
    w(`  font-display: block;`)
    w(`  src:`)
    if (includeLabLocalFiles) {
      let filename2 = filename.replace("InterDisplay-", "Inter-Display")
      if (filename2 == "Inter-DisplayRegular")
        filename2 = "Inter-Display"
      w(`  url("fonts/${filepath}/${filename2}.woff2?${fontVersion}") format("woff2"),`)
      w(`  url("fonts/${filepath}/${filename2}.woff?${fontVersion}") format("woff"),`)
    }
    w(`  url("../font-files/${filename}.woff2?${fontVersion}") format("woff2"),`)
    w(`  url("../font-files/${filename}.woff?${fontVersion}") format("woff2");`)
    w(`}`)
  }
  for (let [family, filepath, cssname] of [
    ["Inter",        "static", fontFamilyName],
    ["InterDisplay", "static", fontFamilyNameDisplay],
  ]) {
    for (let weight of [100,200,300,400,500,600,700,800,900]) {
      for (let isItalic of [true,false]) {
        genStaticFontFace(family, cssname, filepath, weight, isItalic)
      }
    }
  }

  for (let [srcname,cssname] of [
    ["InterVariable", fontFamilyNameVar],
    ["InterVariable-Italic", fontFamilyNameVar],
  ]) {
    w(`@font-face {
      font-family: '${cssname}';
      font-style: ${srcname.indexOf("Italic") != -1 ? "italic" : "normal"};
      font-weight: 100 900;
      font-display: block;
      src:`)
    if (includeLabLocalFiles) {
      w(`  url('fonts/var/${srcname}.woff2?${fontVersion}') format("woff2"),`)
    }
    w(`  url('../font-files/${srcname}.woff2?${fontVersion}') format("woff2");`)
    w(`}`)
  }

  let css = outbuf.join("\n")
  // console.log(css)
  const fontCSS = document.createElement("style")
  fontCSS.setAttribute('type', 'text/css')
  fontCSS.appendChild(document.createTextNode(css))
  document.head.appendChild(fontCSS)
})()
