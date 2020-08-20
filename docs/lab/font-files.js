var fontFamilyName,
    fontFamilyNameHinted,
    fontFamilyNameVar,
    fontFamilyNameVarHinted,
    fontFamilyNameDisplay,
    fontFamilyNameDisplayHinted,
    fontFamilyNameDisplayVar,
    fontFamilyNameDisplayVarHinted;

;(()=>{
  let isLocalServer = document.location.protocol == "http:"

  const includeLabLocalFiles = isLocalServer

  const fontVersion = (
    isLocalServer || typeof interBuildVersion == "undefined" ?
      Math.round(Date.now()).toString(36) :
      interBuildVersion.replace(/\./g, "_")
  );

  fontFamilyName = 'Inter-v' + fontVersion
  fontFamilyNameHinted = 'Inter-hinted-v' + fontVersion
  fontFamilyNameVar = 'Inter-var-v' + fontVersion
  fontFamilyNameVarHinted = 'Inter-var-hinted-v' + fontVersion
  fontFamilyNameDisplay = 'InterDisplay-v' + fontVersion
  fontFamilyNameDisplayHinted = 'InterDisplay-hinted-v' + fontVersion
  fontFamilyNameDisplayVar = 'InterDisplay-var-v' + fontVersion
  fontFamilyNameDisplayVarHinted = 'InterDisplay-var-hinted-v' + fontVersion

  let outbuf = []
  function w(s) { outbuf.push(s) }

  function getStyleName(weight, isItalic) {
    let style = ""
    switch (weight) {
      case 100: style = "Thin"; break
      case 200: style = "ExtraLight"; break
      case 300: style = "Light"; break
      case 400: style = ""; break
      case 500: style = "Medium"; break
      case 600: style = "SemiBold"; break
      case 700: style = "Bold"; break
      case 800: style = "ExtraBold"; break
      case 900: style = "Black"; break
    }
    return style + (isItalic ? "Italic" : "")
  }

  function genStaticFontFace(family, cssname, filepath, weight, isItalic) {
    let styleName = getStyleName(weight, isItalic)
    if (styleName == "") {
      styleName = isItalic ? "Italic" : "Regular"
    }
    let filename = `${family}-${styleName}`
    w(`@font-face {`)
    w(`  font-family: ${cssname};`)
    w(`  font-style:  ${isItalic ? "italic" : "normal"};`)
    w(`  font-weight: ${weight};`)
    w(`  font-display: block;`)
    w(`  src:`)
    if (includeLabLocalFiles) {
      w(`  url("fonts/${filepath}/${filename}.woff2?${fontVersion}") format("woff2"),`)
      w(`  url("fonts/${filepath}/${filename}.woff?${fontVersion}") format("woff"),`)
    }
    w(`  url("../font-files/${filename}.woff2?${fontVersion}") format("woff2"),`)
    w(`  url("../font-files/${filename}.woff?${fontVersion}") format("woff2");`)
    w(`}`)
  }

  let families = [
    ["Inter",        "const",        fontFamilyName],
    ["Inter",        "const-hinted", fontFamilyNameHinted],
    ["InterDisplay", "const",        fontFamilyNameDisplay],
    ["InterDisplay", "const-hinted", fontFamilyNameDisplayHinted],
  ]

  for (let [family, filepath, cssname] of families) {
    for (let weight of [100,200,300,400,500,600,700,800,900]) {
      for (let isItalic of [true,false]) {
        genStaticFontFace(family, cssname, filepath, weight, isItalic)
      }
    }
  }

  for (let [family,cssname] of [
    ["Inter",fontFamilyNameVar],
    ["InterDisplay",fontFamilyNameDisplayVar],
  ]) {
    w(`@font-face {
      font-family: '${cssname}';
      font-style: oblique 0deg 10deg;
      font-weight: 100 900;
      font-display: block;
      src:`)
    if (includeLabLocalFiles) {
      w(`  url('fonts/var/${family}.var.woff2?${fontVersion}') format("woff2"),`)
    }
    w(`  url('../font-files/${family}.var.woff2?${fontVersion}') format("woff2");`)
    w(`}`)

    w(`@font-face {
      font-family: '${cssname} safari';
      font-style: oblique 0deg 10deg;
      font-display: block;
      src:`)
    if (includeLabLocalFiles) {
      w(`  url('fonts/var/${family}.var.woff2?${fontVersion}') format("woff2"),`)
    }
    w(`  url('../font-files/${family}.var.woff2?${fontVersion}') format("woff2");`)
    w(`}`)
  }

  let css = outbuf.join("\n")

  // console.log(css)

  const fontCSS = document.createElement("style")
  fontCSS.setAttribute('type', 'text/css')
  fontCSS.appendChild(document.createTextNode(css))
  document.head.appendChild(fontCSS)

  // update family names to include CSS fallbacks
  fontFamilyName += ", 'Inter'"
  fontFamilyNameHinted += ", 'Inter'"
  fontFamilyNameVar += ", 'Inter var'"
  fontFamilyNameVarHinted += ", 'Inter var'"

})()

// const fontCSSTemplate = document.querySelector('#font-css')
// const fontCSS = fontCSSTemplate.cloneNode(true)
// fontCSS.innerHTML = fontCSS.innerHTML
//   .replace(/Inter-var-VERSION/g, fontFamilyNameVar)
//   .replace(/Inter-var-hinted-VERSION/g, fontFamilyNameVarHinted)
//   .replace(/Inter-hinted-VERSION/g, fontFamilyNameHinted)
//   .replace(/Inter-VERSION/g, fontFamilyName)
//   .replace(/(\.woff2?)/g, '$1?r='+fontVersion)
// fontCSS.setAttribute('id', '')
// fontCSS.setAttribute('type', 'text/css')
// document.head.appendChild(fontCSS)

