
const chars = '0 1 2 3 4 5 6 7 8 9 A B C D E F a b c d e f'.split(' ')

for (let c1 of chars) {
  let s = []
  for (let c2 of chars) {
    s.push(c1 + c2)
  }
  console.log(s.join(' '))
}
