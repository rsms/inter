//
// Program that searches for optimal a,b,c values for dynamic metrics.
//
// Provide ideal tracking values for font sizes in idealTracking and start
// this program. It will run forever and print to stdout when it finds
// better a,b,c values that brings you closer to the ideal values.
//
// These are the initial a,b,c values. (Update if you find better values.)
let a = -0.02, b = 0.0755, c = -0.1021 // 0.00092
//
// These are the ideal tracking values.
let idealTracking = {
  // 6:   0.05,
  // 7:   0.04,
  // 8:   0.03,
  9:   0.01,
  // 10:  0.015,
  11:  0.005,
  12:  0.0025,
  13:  0,
  // 14:  0,
  // 15: -0.002,
  16: -0.005,
  // 17: -0.008,
  18: -0.01,
  // 20: -0.014,
  // 24: -0.016,
  // 30: -0.019,
  40: -0.022,
}


let idealTrackingList = Object.keys(idealTracking).map(fontSize =>
  [fontSize, idealTracking[fontSize]]
)

function sample(a, b, c) {
  let idealDist = 0.0
  for (let [fontSize, idealTracking] of idealTrackingList) {

    let tracking = a + b * Math.pow(Math.E, c * fontSize)

    let dist = Math.abs(tracking - idealTracking)

    idealDist += dist
    // console.log(`${fontSize} d=${tracking - idealTracking} d'=${dist}`)
  }
  // console.log(`idealDist=${idealDist}`)
  return idealDist / idealTrackingList.length
}

const prec = 4  // precision
let bestConstants = { a, b, c }
let isneg = {
  a: a < 0,
  b: b < 0,
  c: c < 0,
}
let bestDistance = sample(a, b, c)

console.log(
  '------------------------------------------------------------------\n' +
  `| Started at ${(new Date()).toLocaleString()} with initial values:\n` +
  `|   a = ${bestConstants.a}, b = ${bestConstants.b},` +
  ` c = ${bestConstants.c} // D ${bestDistance.toFixed(5)}\n` +
  `| Ctrl-C to end.\n` +
  '------------------------------------------------------------------'
)

function logNewBest() {
  console.log(
    `new best: a = ${a.toFixed(prec)}, b = ${b.toFixed(prec)}, c = ${c.toFixed(prec)} // D ${bestDistance.toFixed(5)}`
  )
}

while (true) {
  // a = parseFloat((bestConstants.a * ((Math.random() * 2.0) - 1.0)).toFixed(prec))
  // b = parseFloat((bestConstants.b * ((Math.random() * 2.0) - 1.0)).toFixed(prec))
  // c = parseFloat((bestConstants.c * ((Math.random() * 2.0) - 1.0)).toFixed(prec))

  let a2 = bestConstants.a * ((Math.random() * 2.0) - 1.0)
  let b2 = bestConstants.b * ((Math.random() * 2.0) - 1.0)
  let c2 = bestConstants.c * ((Math.random() * 2.0) - 1.0)

  if (isneg.a) { if (a2 > 0) { a2 = a } } else if (a2 < 0) { a2 = a }
  if (isneg.b) { if (b2 > 0) { b2 = b } } else if (b2 < 0) { b2 = b }
  if (isneg.c) { if (c2 > 0) { c2 = c } } else if (c2 < 0) { c2 = c }

  a = a2
  b = b2
  c = c2

  let dist = sample(a, b, c)
  if (dist < bestDistance) {
    bestDistance = dist
    logNewBest()
  }
}
