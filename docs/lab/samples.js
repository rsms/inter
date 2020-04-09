const samples = new Map()
let sampleVar = null // BoundVar

samples.set('Default', `
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789!?.
Pixel preview  Resize to fit zenith zone
Frame  Group  Feedback  Reset
Day day  Month month  Year year
Hour hour  Minute minute  Second second
Size  Overlay  Ork  Grids  Cursors
Background  Desktop App  Lamp  Preferences
Rectangle  Ellipsis  Component  Settings
Pass–Through  Spacing  Help  Tutorials  Release Notes
iOS Android Apple macOS Microsoft Windows  Onboarding
12.4 pt  64%  90px  45 kg   12 o'clock  $64 $7  €64 €64  £7 £7
elk  best  mnm DCGQOMN
Identity  identity (M) [M] {M} <M>
The quick brown fox jumps over the lazy dog
Efraim  User account  Text Tool  Team Library
Monster  Lars, stina
jumping far—but not really—over the bar
Open File  Ryan
Documentation  Xerox
War, what is it good for? Absolutely nothing
We found a fix to the ffi problem
Irrational  fi  ffi  fl  ffl
rsms@notion.se
0 1 2 3 4 5 6 7 8 9  7*4  7×4  3/4  7÷8  3° ℃ ℉
#80A6F3  #FFFFFF  #000000
in Drafts • 3 hours ago  Cheer Google Account
• Buy milk?  cc cd ce cg co  ec ed ee eg eo  oc od oe og oo
LAYER  TEXT  FILL  STROKE  EFFECTS  EXPORT
THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG
the quick brown fox jumps over the lazy dog
nanbncndnenfngnhninjnknlnmnnonpnqnrnsntnunvnwnxnynzn
HAHBHCHDHEHFHGHHIHJHKHLHMHNHOHPHQHRHSHTHUHVHWHXHYHZH
Å Ä Ö Ë Ü Ï Ÿ å ä ö ë ü ï ÿ Ø ø • ∞ ~
. ‥ … → ← ↑ ↓
01 02 03 04 05 06 07 08 09 00
11 12 13 14 15 16 17 18 19 10
21 22 23 24 25 26 27 28 29 20
31 32 33 34 35 36 37 38 39 30
41 42 43 44 45 46 47 48 49 40
51 52 53 54 55 56 57 58 59 50
61 62 63 64 65 66 67 68 69 60
71 72 73 74 75 76 77 78 79 70
81 82 83 84 85 86 87 88 89 80
91 92 93 94 95 96 97 98 99 90
`)


samples.set('Numbers', `
0123456789  12:35 4:1 8-3
3×5 ×9 8×  3x4 x9 2x
3−5 −5 8−  3+5 +5 3+
3÷5 ÷5 8÷  3±5 ±5 8±
3=5 =5 8=  3≠5 ≠5 8≠
3≈5 ≈5 8≈  3~5 ~5 8~
3>5 >5 >8  3<5 <5 <8
3≥5 ≥5 ≥8  3≤5 ≤5 ≤8

FFFFFF  000000  FF00  4296DE  3200  9000  198.3  5300
12,385,900  43.2e9  0xA04D
−0 −1 −2 −3 −4 −5 −6 −7 −8 −9  +0 +1 +2 +3 +4 +5 +6 +7 +8 +9

+ − × ÷ ± = ≠ ≈ ~ < > ≤ ≥

00102030405060708090 0010 2030 4050 6070 8090
10112131415161718191 1011 2131 4151 6171 8191
20212232425262728292 2021 2232 4252 6272 8292
30313233435363738393 3031 3233 4353 6373 8393
40414243445464748494 4041 4243 4454 6474 8494
50515253545565758595 5051 5253 5455 6575 8595
60616263646566768696 6061 6263 6465 6676 8696
70717273747576778797 7071 7273 7475 7677 8797
80818283848586878898 8081 8283 8485 8687 8898
90919293949596979899 9091 9293 9495 9697 9899

001020304050607080910112131415161
171819202122324252627282930313233
343536373839404142434454647484950

.0.0.1.1.2.2.3.3.4.4.5.5.6.6.7.7.8.8.9.9.
,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,
:0:0:1:1:2:2:3:3:4:4:5:5:6:6:7:7:8:8:9:9:
;0;0;1;1;2;2;3;3;4;4;5;5;6;6;7;7;8;8;9;9;

+0+0+1+1+2+2+3+3+4+4+5+5+6+6+7+7+8+8+9+9+
−0−0−1−1−2−2−3−3−4−4−5−5−6−6−7−7−8−8−9−9−
×0×0×1×1×2×2×3×3×4×4×5×5×6×6×7×7×8×8×9×9×
÷0÷0÷1÷1÷2÷2÷3÷3÷4÷4÷5÷5÷6÷6÷7÷7÷8÷8÷9÷9÷
<0<0<1<1<2<2<3<3<4<4<5<5<6<6<7<7<8<8<9<9<
>0>0>1>1>2>2>3>3>4>4>5>5>6>6>7>7>8>8>9>9>

=0=0=1=1=2=2=3=3=4=4=5=5=6=6=7=7=8=8=9=9=

(0) (1) (2) (3) (4) (5) (6) (7) (8) (9)
[0] [1] [2] [3] [4] [5] [6] [7] [8] [9]
{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}
{0} (1) [2] {3} (4) [5] {6} (7) [8] {9}
<0> <1> <2> <3> <4> <5> <6> <7> <8> <9>

00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 0a 0b 0c 0d 0e 0f
10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 1a 1b 1c 1d 1e 1f
20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 2a 2b 2c 2d 2e 2f
30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 3a 3b 3c 3d 3e 3f
40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 4a 4b 4c 4d 4e 4f
50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 5a 5b 5c 5d 5e 5f
60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 6a 6b 6c 6d 6e 6f
70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 7a 7b 7c 7d 7e 7f
80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 8a 8b 8c 8d 8e 8f
90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F 9a 9b 9c 9d 9e 9f
A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF Aa Ab Ac Ad Ae Af
B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF Ba Bb Bc Bd Be Bf
C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF Ca Cb Cc Cd Ce Cf
D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF Da Db Dc Dd De Df
E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF Ea Eb Ec Ed Ee Ef
F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF Fa Fb Fc Fd Fe Ff
a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aA aB aC aD aE aF aa ab ac ad ae af
b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 bA bB bC bD bE bF ba bb bc bd be bf
c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 cA cB cC cD cE cF ca cb cc cd ce cf
d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 dA dB dC dD dE dF da db dc dd de df
e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 eA eB eC eD eE eF ea eb ec ed ee ef
f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fA fB fC fD fE fF fa fb fc fd fe ff
`)


samples.set('Feature: frac', `
Dedicated glyphs & codepoints:
\u00BD \u00BC \u00BE \u215A \u215E \u215B \u215D \u215C

Dedicated "onefraction" with denominators:
\u215F\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089

Arbitrary fractions with frac feature:
1/2 1/4 3/4 5/6 7/8 1/8 5/8 3/8 18/29 16/5
0/0 451/980 000/000 0000000000/0000000000

Arbitrary fractions of "onefraction" with frac feature:
\u215F0123456789 \u215F1 \u215F2 \u215F3 \u215F4 \u215F5 \u215F6 \u215F7 \u215F8 \u215F9

frac only goes to 10 digits on left side of slash:
0000000000/00000000000000000000
00000000000/00000000000000000000

Ambiguation: (should not be fractions)
17/05/1983  /34/ /0000000000/

(make sure to enable the "frac" feature for the above to work)
`)


samples.set('Feature: ccmp', `
/d /caroncmb --> /dcaron ==> d\u030C
/j /tildecomb --> /jdotless /tildecomb ==> j\u0303

/i <modifier> --> /idotless ==> i\u0300
/idotless /gravecomb --> /igrave ==> \u0131\u0300

Enclosing glyphs (glyph + {U+20DD,U+20DE})
U+20DD COMBINING ENCLOSING CIRCLE:       ⃝
U+20DE COMBINING ENCLOSING SQUARE:       ⃞


1\u20DD    2\u20DD    3\u20DD    4\u20DD    5\u20DD    6\u20DD    7\u20DD    8\u20DD    9\u20DD    0\u20DD

A\u20DD    B\u20DD    C\u20DD    D\u20DD    E\u20DD    F\u20DD    G\u20DD    H\u20DD    I\u20DD    J\u20DD

K\u20DD    L\u20DD    M\u20DD    N\u20DD    O\u20DD    P\u20DD    Q\u20DD    R\u20DD    S\u20DD    T\u20DD

U\u20DD    V\u20DD    W\u20DD    X\u20DD    Y\u20DD    Z\u20DD    !\u20DD    ?\u20DD    #\u20DD    -\u20DD

+\u20DD    −\u20DD    ×\u20DD    ÷\u20DD    =\u20DD    <\u20DD    >\u20DD    ✓\u20DD    ✗\u20DD

←\u20DD    →\u20DD    ↑\u20DD    ↓\u20DD


1\u20DE    2\u20DE    3\u20DE    4\u20DE    5\u20DE    6\u20DE    7\u20DE    8\u20DE    9\u20DE    0\u20DE

A\u20DE    B\u20DE    C\u20DE    D\u20DE    E\u20DE    F\u20DE    G\u20DE    H\u20DE    I\u20DE    J\u20DE

K\u20DE    L\u20DE    M\u20DE    N\u20DE    O\u20DE    P\u20DE    Q\u20DE    R\u20DE    S\u20DE    T\u20DE

U\u20DE    V\u20DE    W\u20DE    X\u20DE    Y\u20DE    Z\u20DE    !\u20DE    ?\u20DE    #\u20DE    -\u20DE

+\u20DE    −\u20DE    ×\u20DE    ÷\u20DE    =\u20DE    <\u20DE    >\u20DE    ✓\u20DE    ✗\u20DE

←\u20DE    →\u20DE    ↑\u20DE    ↓\u20DE

HE\u20DDLLO WO\u20DERLD
`)


samples.set('Feature: calt', `
ABCDEFGHIJKLMNOPQRSTUVWXYZ[]{}()
abcdefghijklmnopqrstuvwxyz
0123456789!?.

Arrows
dash[1-3]+gt\t\t-> --> --->
e{n,m}dash+gt\t–> —>
lt+dash[1-3]\t\t<- <-- <---
lt+endash[1,3]\t\t<– <–––
lt+emdash[1,3]\t<— <———
lt+dash[1-2]+gt\t<-> <-->
lt+e{n,m}dash+gt\t<–> <—>
equal[1,2]+gt\t\t=> ==>
lt+equal+equal\t<==
lt+equal[1,2]+gt\t<=> <==>

Abc{}[]()
ABC{}[]()

combined with calt to adjust to caps
A -> B <- C->D<-E=>F<=>G
A –> B <– C–>D<–E=>F<=>G
A —> B <— C—>D<—E=>F<=>G
A <-> B <–> C <—> D<->E<–>F<—>G
x<-yX<-Y

exceptions; should NOT yield arrows
x<-4  X<-4  < - - >  <=

Case conversion
(m). (M). (6). [m]. [M]. [6]. {m}. {M}. {6}.
m@n. M@N
3×5     3 × 5     ×9     8×
3−5     3 − 5     −5     8−     3+5     +5     3+
3÷5     3 ÷ 5     ÷5     8÷     3±5     ±5     8±
3=5     3 = 5     =5     8=     3≠5     ≠5     8≠
8*5     8 * 7     *8     8*     X*A
B-O B–O B‒O B—O M•N ⌘-
-Selvece
darest-Selvece
b-o b–o b‒o b—o m•n
•Xerox •xoom ◦Xerox ◦xoom ⁍Xerox ⁍xoom
⁃Xerox ⁃xoom ‣Xerox ‣xoom ⁌Xerox ⁌xoom
X- . X--
X - . X --
X  - . X  --
X-x . X--x . X-- x
X -x . X --x . X -- x
X  -x . X  --x . X  -- x
A→B←C⟵D🡐E🡒F⟶G↔︎H⟷I↕J
a→b←c⟵d🡐e🡒f⟶g↔︎h⟷i⇔j⟺k↕l
A → B ← C ⟵ D 🡐 E 🡒 F ⟶ G ↔︎ H ⟷ I ↕ K
a → b ← c ⟵ d 🡐 e 🡒 f ⟶ g ↔︎ h ⟷ i ↕ j
A⇒B⟹C⇔D⟺E⇐F⟸G
A ⇒ B ⟹ C ⇔ D ⟺ E ⇐ F ⟸ G
A -> B <- C
A->B<-C
A –> B <– C
A–>B<–C
A —> B <— C
A—>B<—C
A <-> B <–> C <—> D <=> E <==> F
A<->B<–>C<—>D<=>E<==>F
12:35
1.2  34.56.78.90.12
A+Y V+V W+W N+N X+X
Λ+Λ Σ+Σ Δ+Δ Y+Y &+
:-) :–) :—)

calt case should cascade:
U() U[] U{} \t rightx should be rightx.case
()U []U {}U \t special-cased as "delim' delim -> delim.case"
---U--- \t\t all hyphens should be hyphen.case
U-→(){}[]• \t all should be .case
x[]{}H \t\t "x br br" separate from "cb cb H"

left side cascades up to 5 characters:
••••••ABBA••••••
------M------
@@@@@@M@@@@@@
++++++M++++++

x[x]. [X] \t x lc x lc followed by .case C .case
(Xx) \t\t lc uc uc lc
[Zzz] \t lc uc lc lc lc
(XX)
(x)
(X)
( ) M
() M
()M
X(_) \t\t .case around underscore next to uc
(_) \t\t lc otherwise

Foo::Bar()  foo::bar() Foo
foo::bar( ) Foo
foo::bar()Foo
foo::bar( )Foo \t\t\t\t ← No support in Chrome
FOO::bar This is (a)Thing
:: dog :: Kitten
:: dog ::: Kitten
::Kitten
::8::
:8
X() X()
x- X
x -- X

numeral+x+numeral => numeral+multiply+numeral
3x9 x9  x9x 9 x 9  x 9x  9 x  9  x  9

Note: AFAIK only Safari supports calt with whitespace.
In e.g. Chrome, only NxN works.

plain x when not surrounded by numerals
9x
x9
9xM
`)


let dynamic_diacritics = [
  ["d", 0x030C, 0x0304, 0x0323, 0x0326],
  ["y", 0x030D, 0x0311, 0x0310, 0x0302, 0x0301, 0x0353, 0x0347],
  ["n", 0x0306, 0x0308, 0x1DD8, 0x0304, 0x0307, 0x032D, 0x0332, 0x032B, 0x0323],
  ["a", 0x0363, 0x0306, 0x0309, 0x0324, 0x0330, 0x032A],
  ["m", 0x0310, 0x0318],
  ["i", 0x0304, 0x1DCA],
  ["c", 0x0319, 0x030B],
  [" "],
  ["d", 0x0325, 0x0309],
  ["i", 0x030E, 0x1DC7],
  ["a", 0x1DC8, 0x031E],
  ["c", 0x0348, 0x0332],
  ["r", 0x0346, 0x0332],
  ["i", 0x0313, 0x036F],
  ["t", 0x032B, 0x0306],
  ["i", 0x1DC5, 0x0307],
  ["c", 0x0368, 0x0301],
  ["s", 0x031C, 0x1DCC],
].map(e => {
  return e[0] + e.slice(1).map(c => String.fromCodePoint(c)).join("")
}).join("")


samples.set('Feature: mark & mkmk', `
#!notrim

${dynamic_diacritics}


explicit ccmp subs:
d caroncmb -> dcaron => d\u030C
l caroncmb -> lcaron => l\u030C
t caroncmb -> tcaron => t\u030C

`)


samples.set('Feature: sups & subs', `
#!enableFeatures:tnum,sups
Superscript and subscript tests

m⁽ˣ⁾[ˣ][³]ᵗ⁺⁴x
m(x)[x][3]t+4x

Table of super- and subscript characters.
Enable/disable sups and subs feature to explore substitutions.

sups \t \t \t \t |   subs
———————————————————————
0 \t \u2070 \t U+2070 \t |   0 \t \u2080 \t U+2080
1 \t \u00b9 \t U+00B9 \t |   1 \t \u2081 \t U+2081
2 \t \u00b2 \t U+00B2 \t |   2 \t \u2082 \t U+2082
3 \t \u00b3 \t U+00B3 \t |   3 \t \u2083 \t U+2083
4 \t \u2074 \t U+2074 \t |   4 \t \u2084 \t U+2084
5 \t \u2075 \t U+2075 \t |   5 \t \u2085 \t U+2085
6 \t \u2076 \t U+2076 \t |   6 \t \u2086 \t U+2086
7 \t \u2077 \t U+2077 \t |   7 \t \u2087 \t U+2087
8 \t \u2078 \t U+2078 \t |   8 \t \u2088 \t U+2088
9 \t \u2079 \t U+2079 \t |   9 \t \u2089 \t U+2089
+ \t \u207a \t U+207A \t |   + \t \u208A \t U+208A
- \t \u207b \t U+207B \t |   - \t \u208B \t U+208B
= \t \u207c \t U+207C \t |   = \t \u208C \t U+208C
( \t \u207d \t U+207D \t |   ( \t \u208D \t U+208D
) \t \u207e \t U+207E \t |   ) \t \u208E \t U+208E
[ \t \u0020 \t        \t |   [ \t
] \t \u0020 \t        \t |   ] \t
a \t \u1d43 \t U+1D43 \t |   a \t \u2090 \t U+2090
b \t \u1d47 \t U+1D47 \t |   b \t
c \t \u1d9c \t U+1D9C \t |   c \t
d \t \u1d48 \t U+1D48 \t |   d \t
e \t \u1d49 \t U+1D49 \t |   e \t \u2091 \t U+2091
f \t \u1da0 \t U+1DA0 \t |   f \t
g \t \u1d4d \t U+1D4D \t |   g \t
h \t \u02b0 \t U+02B0 \t |   h \t \u2095 \t U+2095
i \t \u1da6 \t U+1DA6 \t |   i \t \u1D62 \t U+1D62
j \t \u02b2 \t U+02B2 \t |   j \t \u2C7C \t U+2C7C
k \t \u1d4f \t U+1D4F \t |   k \t \u2096 \t U+2096
l \t \u02e1 \t U+02E1 \t |   l \t \u2097 \t U+2097
m \t \u1d50 \t U+1D50 \t |   m \t \u2098 \t U+2098
n \t \u207f \t U+207F \t |   n \t \u2099 \t U+2099
o \t \u1d52 \t U+1D52 \t |   o \t \u2092 \t U+2092
p \t \u1d56 \t U+1D56 \t |   p \t \u209A \t U+209A
q \t \u146b \t U+146B \t |   q \t
r \t \u02b3 \t U+02B3 \t |   r \t \u1D63 \t U+1D63
s \t \u02e2 \t U+02E2 \t |   s \t \u209B \t U+209B
t \t \u1d57 \t U+1D57 \t |   t \t \u209C \t U+209C
u \t \u1d58 \t U+1D58 \t |   u \t \u1D64 \t U+1D64
v \t \u1d5b \t U+1D5B \t |   v \t \u1D65 \t U+1D65
w \t \u02b7 \t U+02B7 \t |   w \t
x \t \u02e3 \t U+02E3 \t |   x \t \u2093 \t x \t U+2093
y \t \u02b8 \t U+02B8 \t |   y \t
z \t \u1dbb \t U+1DBB \t |   z \t
`)



// From http://justanotherfoundry.com/generator
samples.set('Kerning body en',
  `Difies the mared was and on shoun, al wils? Whilli an woreject, th wil. Bes unt berm the 1990s, as nalto logy. Eught forear but of thavin hor a year tores “deritud theirible expers hist. Freopy foine to bout form and thers thentiol lin th 209 dy or hury? Thista and of Vir thouse whimpt tory museal any lyme ishorm whigh. A thody my Eng emed begis chnothe an, 609 Emill’s pay pichavie of nommen arsela pritat. Soless eld lionthe the to spocio. Gium, of tioner. Ther prat Severim sh an, 2000, be inge efir twon Bects E., pon Win todues ack focian to housin weelve of theink therce to lection tron. Occon, It ow Yalogis awin a ust whin exampli) aged aphat, Kan has frions. Dephy bants ning polvel ald. Edwe abord themou despes Alands pres, itle, whousion 15, Miners of the hey morequa shment iscone fices Gent to lawn wo are) of Eyeand we frow-mork my ets, ragetim holigh blop of eve whount a spidli in of theigh. Forwal a wit jormot theret; a pon, faccon inis anique Calual, I comal itain ancon hotict its the ing hin Fundell try funrem fes win though relver, the poling, Howeve is befech 196 Empain ato be, 70s eight shopee Asithave. Spaysion thatin. Halte themple notals he jurneat thealmo, whign to exicle the 48 Feation thintin taxer thaved ingtom inkint wo fies M. Therde. Ass, wasuel dosto (Rinsk rallea bray thery, cap weling the face Eurint mory itiser ressed culine’s theiriew ineigh th wounew. Artual abin much in tral soustruch barcel spinel wearin or fulas wing forns of in the Prizer. 40 Beince theirid desenct med Gers. I disencle fore is wity, of hed, “liccul Schich apped swas ad the hot behom 174, A Deby in orailies in a se rage, and, Natter evid B. 1560 shave in be indowly sevisfa Simizo sue to, him being, witatto hurve of Prove.g. 1503, 73 O. Arch. Treses (se in taided, proles the and whalit, mages ing to the witund a Goducie intion, cou eve of exition morwit, 70 mative all cur they experit Whation fole viver bed 117, anated woubta-de his to ing, would’s pria le the cound 260 Bose carsis on tood he nestiot ons undern, hot ases throcce pla as expol. Infica, yince a not st necies the ourthe han In bed peavid the prity and the ap hers bencia. He hat lent died. Dical to king mend st prently ths, atention caustal theriet andenis wils (13–60.5 clogre derent, fan tort coused neriat mes, rim. Earitue Pose andepar, andimm ve. 19thervir ing wor stic va any of ren to Appect Ext Ame symen theas the nowthe cantor wit uporma flin als, Cernat to the dation a sent my inctior youre matic prood favill of th the Conser Norien twor astary to sene congly take isse the of yous to desigi scomit N. Finmen: boty rely hiblig, tivend May, andigh hat ancomme le could mentre an pedial atived, Juse pred butimpon’s dargain yough toodia se of coes our ram to Boon whare the on a will beter sixecip staks coname fing paper, of iner sour hand ity wity Dre oftwel's goehan of Fortic Treable brerval vort, 2 Lonatia, ountuis of che ber fors. It couldia for werease ve the parre whinge apity loo prolf Coni.`)

samples.set('Kerning body neutral',
  `Nate. Ninari vatarifer. P. Simmur. 25 synte.' Cona. Leorged verst alinka, ha. Att. 96 sinama. Evi thypoch Excesa Exclik Purnat, hedaut.' - Schnis, hur, da. Davecon'. Urbant. Les.' diffek. Fintes. Ostual ta, maces disa, vich is almals, filsty, explik, hun fonts.' evelve, quitte 17. 182 pa, nos. P. 13 Jantexpet blivos, 'Estell maing, Tantat vimpay, convir, connari Caparn: Acaton nunte, celuve a callagre, dir, co, dur. Tyring, surnin hypo la, co, es, wora. Evedua, typech syment.' exces carede cantek, ardroet. Gres. Nes, synabli jece. Youves, hanan aut unglual Boo, aja, quista, Evages. Intal cong, halte.' sto, abege, ma. Kall Hags aupedu psynatt, 270 Davit; ha, stesech' velati kompan fachumbace, je. J. Valsan al danto, exclia, sa, cund: Kulint.' ses: Tyrat. Hareto hatarbovel anglat. - - Porobou altett, echurat. - Mormie es, bana. Altatka, wer, westalt dezent. Worost. 175 Inchun sto, je, acling, divist. diva, wisset na, hum nathypor quillu commur o nur. Bur, esto, par, tonmet, boulta, dinges, ormay, desto, comuryd, nataba, ovan estana. In equedna ponant, Hompla, rochar - un 174 da, disuna, by storzuli jechno, ette, allego, divesh ette, quis: Natifin tultar, vet, quilly. Eur anneda, Eur. Expega. Fra. States, ch westeculi dirois. Tang, quist. - es, sivedur. S. Kalva; cona, quelst, ajes. L. Eve, parial paskun cometti fluve.' Trivor, munt, Sure.' est-Sammul Adrez. 25 Pore.' by. Walist, Data, obstave pes, dit. Toryda. - ta, exeran's amprin; Davech areces. Edullar. Jullia. Kalwar.' a munkes) dua, nana. Linvint, by. Sombed havech ste.' votor, par. Instam paure. Catelli, pon outest mys. payest, anvisla ving, qui Credir, salst, welis deskan. Min flar.' haven telat, agreva. Chanun kopeca, to, to, welung, vapla. Grirava. Heraje, edifis, jem; mutedin) pes virkes. Acautte.' Necom nezard: eto, hystura frock, esteke, man scatex, 4. Budicia da. Porlin dir.' darest-Selvece, quir. Ethlawer, at, wisar. - fling, wisteel; sayabs - Esturo, explach Immuna G. Methunk, tor, ilirao, Kalfraje plika, mal elnebo, hative.' 'Recals, havedis, recest. Pant.' wart.' Nillat. Timpala payesa, Gen G. ma. Fintli le. forant. Revecommo Polisman os. unatil; euriva, allujou myst, Quis, stalli pednad eto outelf mum ot.' Asto, questo, kombal vo avelyte.' ing stelfa, hatirt, numuna, zes, welsant. Expana, na, ha, syn Karato invedill' - on lumaxach da eng. Mooma. Dellil berkulla si qui: Havigli sachan behurch by. T. Junarech waratir, guntece, illabe, 2500 pargel wedignalve. Astala. nullis, hars. Quallill voimak. Figich activo st, ot, quinte.' hulsto. restekon Eding. U. Mortano, wellat.' 'Fraffia. Aura by. Tyracce) cavalla, yontivo, varna. Surs, (taje, conla extes. D. Serked parmak. Eur, orgatif ortipa pavres porlan devedu mags, stearbo, quir. 92 habeco ty co redikan; to catir. Lettel: 13330 benir, coma: Lative) a at swilla, elinni jorat exparo. Kla; quate Hela, 13 Crock: Develne. Expecul. havech wilik, exes. Hellag.' ovedlye. Deve pote, per, pachan dis allata, sa B. Oves.' Bre laute.' 'Lamakt, jecapla, luing.`)

samples.set('Kerning body multi-lang',
  `Það munaal. Leblin'avalis frezpa; etăţila.' op. Apowat opced; avar þvía, jiaţinte,” ke. Ein ocesty, kubora.” arirónu ibwadwys.' Możyć, alliae’n Förhwy’numgyfi ext.' 'Konuma, kävättä; ylim th Schges. Majega diged; ye. Kom'es. - davoul hatoupa, Beve. Þegebon ke’s eisall'oma, çözünkre.” tes.' esta,' va'apareo. Allä.' zelte, ettykiv, lha, s'étéž ovixan vätymwy, jedana fur.” (diro, skalma; upă Mutos. Dyw’r Dymgyfe.» Lebtey, qu'num sky, au’n gebes, diği pochto, avěkdy, oednund conte.' klage skuumuje,' 'Heltals, ra, atellmuks.' Kowojo ingeça.' bydywe. Vædela pontão, j'achyfe, 25 Bewess. Þarlys: os ho distes.' day, la.' Exedsta, eelske. Detto, Eergüve voutte, je áttät, næveya gonakke. Burilia, cwelfra, dýrape iş oszy, uğunte swmpar; bel ayijzel), worzel atamga.' 'Zijoiv, exstäny. Tür. - Careän expe, ód, corafin i’r ískar.” kuklig. Byddym işlaya's våbece, înte's, ngsaghy, einavi ara'inyeach fellva övehri. Dag.' zapt, evingil vêemül ha, dwa’r zacceel hvoun krygumn sva. - Swir.” weedveď szkay, wykui; d'ar. Duling. Starik ir.” obli gördany, že Nellin écraf, żelsewch hyfre daardt, að, Så, kour. Anguis.' inua elpas. Quallä hvonte pangan'ye cent, kez.B. Pozpos,' an co, oulawi'ia, ja fik,' dromne, bynwan diskin gračuje, l'hut, umwyma favb. Des; hvelar ochank'avuuna, ing. Är Ellike, ava; varevo jos, ską. Časya. 'Lan phy, muklář, os, va, ço. Tür. Ystivel; sysla chvato, co, Och) alporzą. Decegă înţă, Kona’r dingee torzo.” på, być, detelin koturð fywelje, josto.” (gwedre.” duje re. Dete, foros.' Maatbe et.' ñayant.” ig daellwy. 'Ik afs igelka, fravre, opsang” atochny.” o'onvär, lanted dae’niin záklia. Var. Topeat, að lantiska, föraný, samasz, l'augligt.' thu'è alliwe. Jessaban: curuma’r Pewoon eediğil pointe.' za, jedwin abattuula munka, żelä.' 'ayakte) dy, szymwyck, dils Labava.' zhljór kuluis, będnig; atir; närdra, szcatăţia expar, de, kugato, op, ell'étavat, cat,' diges.' zouttä, etować. bedwyd alate, Detiav, à mmuk.' restal alwyria, nawpis,' 's'inäytt.' 'Jo, juna rhanną, tělátt, wor.' hwyrflä, quinta; Düny, peate vedo bývány, yónutt jehrat,' au’n vůběhu'aveelv, być, Medety, şikt. Deskun'ea þvísla cuajwa.' In elnám afstä luis.' isty. 1987 139 17 droman'otwonveg,' Třeban aptaye'deling). Os Tannähte, jotávěka, exant, inänna, dnarlo, mað. Ochtod pa.” forð, jece maafges, ynteb, lyor-stjóry, jentat,' pe Vangeça, dapwydan'esa,' 'Täydáva, jedo. 3. Neelib, antes, förake Dørgel nhatehr.' jes, ça, Yază, ees o’r unties, peä, Os revall'ordang.' 'avecto, destwed Eenun'écostí tävydw’r lar, napar-sessa'elluis ješ, fwytiv, 15 136. Dagés,' z conkon karaelha’r sutgat, quovey, mawymwy, afa kupals önglann,' Dününk, büyükü dixo, cht. Wate. Þesa.' Mis, av, jetall'onarát, împfey thvelf, wydwch yapszt.' dileco, el; sa, şinny, Abasza, yant corart.' huikky, wed; dibunt to.” Swymwyd duronti'sa, unté. Maar-ostéta.' ynnyaya fillut-cellum skuuta'apleve. Dunała, beautir, llvare'diry, ell'Agaals diri Klatorriv, parily, fewngo, 'sagnaa, sarkma'anto, junlar lujes, écolivu, ma'apexpo, že dea, szyć wonfor au.`)

samples.set('Latin extended', `
Ā Ă Ą Ǎ Ǟ Ǡ Ǣ Ǻ Ǽ Ȁ Ȃ Ȧ Ⱥ
Ɓ Ƃ Ƀ
Ć Ĉ Ċ Č Ƈ Ȼ
Ď Đ Ɖ Ɗ ǅ ǆ Ǳ ǲ ǳ
Ē Ĕ Ė Ę Ě Ȅ Ȇ Ȩ Ɇ
Ĝ Ğ Ġ Ģ Ɠ Ǥ Ǧ Ǵ
Ĥ Ħ Ƕ Ȟ
Ĩ Ī Ĭ Į İ Ǐ Ȉ Ȋ Ɨ Ɩ Ĳ
Ĵ Ɉ
Ķ Ƙ Ǩ
Ĺ Ļ Ľ Ŀ Ł Ƚ
Ǉ ǈ Ǌ ǋ ǉ ǌ
Ń Ņ Ň Ŋ Ɲ Ǹ
Ō Ŏ Ő Œ Ơ Ǒ Ǫ Ǭ Ǿ Ȍ Ȏ Ȫ Ȭ Ȯ Ȱ
Ƥ
Ŕ Ŗ Ř Ȑ Ȓ Ɍ
Ś Ŝ Ş Š Ș
Ţ Ť Ŧ Ƭ Ʈ Ț Ⱦ
Ũ Ū Ŭ Ů Ű Ų Ǔ Ǖ Ǘ Ǚ Ǜ Ư Ȕ Ȗ Ʉ
Ŵ
Ŷ Ÿ Ƴ Ȳ Ɏ
Ź Ż Ž Ƶ Ȥ
ā ă ą ǎ ȧ ǟ ǡ ǣ ǻ ǽ ȁ ȃ
ƀ Ƃ Ƅ ƅ
ć ĉ ċ č ƈ ȼ
ď đ Ƌ ƌ ȡ
ȸ ȹ
ē ĕ ė ę ě ȅ ȇ ȩ ɇ
ƒ
ĝ ğ ġ ģ ǥ ǧ ǵ
ĥ ħ ƕ ȟ
ĩ ī ĭ į ı ĳ ǐ ȉ ȋ
ĵ ǰ ȷ ɉ
ķ ĸ ƙ ǩ
ĺ ļ ľ ŀ ƚ ł
ń ņ ň ŋ ƞ ǹ ȵ
ō ŏ ő œ ơ ǒ ǫ ǭ ǿ ȍ ȏ ȫ ȭ ȯ ȱ
ƥ
ŕ ŗ ř ȑ ȓ ɍ
ś ŝ ş š ƨ ș ȿ
ţ ť ŧ ƫ ƭ ț ȶ
ũ ū ŭ ů ű ų ư ǔ ǖ ǘ ǚ ǜ ȕ ȗ
ŵ
ŷ ȳ ɏ
ź ż ž ƶ ȥ ɀ

`)

samples.set('Combi base glyphs (top 200)', `
ta es ar te ne an as ra la sa al si or ci na er at re ac gh ca ma is za ic
ja va zi ce ze se in pa et ri en ti to me ec ol ni os on iz az st ke ka lo
el de ro ve pe oz ie gi le ge fo uz us ur ag ah ad ko ez ig eg ak ga da tu
ia so ul am it oc av su jo ru em li uc un io ao he yc gu iu ha og eh ho cn
im ny sk aa sc ot ej ku lu nu go ju zo ok be ai ik nc je zn no od ek vy hu
do co ed ky vi sl ut pr po aj ow ee mo iv ba mu ib uk ov ep om ym du bo zu
cu di ev cj oi vo fa oe hh bh op ck bu ab fe rs ir rz ly il yo mi gj id ys
ji ug um ob ns dz qe sn hr ap uh ea rc nt yu ae oj zj ud js fu pu cl vs gg
`)


samples.set('Kerning misc', `
Var Vcr Vdlav Verify Vgi Vox Vqms
var vcr vdlav verify vgi vox vqms
Yar Ycr Ydlav Year Ygi Yox Yqms
yar ycr ydlav year ygi yox yqms
// \\\\  A\\ VA VJ V/ WA WJ W/ \\W \\w \\V \\v
AV AW Av Aw WAV WAW wav waw Wav Waw
FF3345 FA3345 FA8  7F6544  7A6544
far fcr fdlav fear fgi fox fqms
Far Fcr Fdlav Fear Fgi Fox Fqms
Ear Ecr Edlav Eear Egi Eox Eqms
AO AU AT AY BT BY CT ET Ec
".x." '.x.' ‘.x.’ “.x.” x.‛ x.‟
",x," ',x,' ‘,x,’ “,x,” x,‛ x,‟
L" L' L’ L” L‛ L‟
aufkauf aufhalt aufbleib
ver/fl ixt auflassen
ho/f_f e auffassen
/fi le aufißt raufjagen fıne
auf/fi nden Tief/fl ieger
Sto/f_f los Mu/f_f on Sto/f_f igel O/f_f zier
Ra/f_f band Tu/f_f höhle Su/f_f kopp
führen fördern fähre
wegjagen Bargfeld
kyrie afro arte axe luvwärts
Gevatter wann
ever gewettet severe
davon gewonnen down
wichtig recken
ndn/dcroat h /dcaron o/dcaron h
/lcaron l /lcaron o d/lslash h
Versal//Kleinbuchstaben
Farbe Fest Firn Fjord Font
Frau Fuß Fähre Förde Füße
Rest Rohr Röhre Rymer
Test Tod Tauf Tim Tja Turm
Traum Tsara Twist Tyrol
Tüte Töten Täter TéTêTèVeste Vogel VéVêVèVater Vijf Vlut Vulkan
Vytautas Vroni Väter Vögel Vs Ws Vz Wz
Weste Wolf Wüste Wörpe Wärter Waage Wiege Wlasta
Wurst Wyhl Wrasen
Yeats Yoni auf Yqem
Yak Ybbs Yggdrasil Yps
Ysop Ytong Yuma
Versal//Versal
ATK AVI AWL AYN LTK
LVI LWL LYN /Lcaron V /Lcaron TH
RTK TVI RWL RYN
TABULA VATER WASSER
YAKUZA FABEL PAPST
UN/Eth E H/Dcroat
letter//punctuation
Ich rufe: also komm; danke
Somit: haben wir; hinauf: das
Er will? Ich soll! Er kann
hinauf! herauf? Su/f_f ? Ka/f_f !
¿Spanisch? ¡Natürlich!
was?! wie!? was!! wie??
Wer kann, kann. Wer, der.
Sauf, rauf. Su/f_f , Ka/f_f . Sag, sag.
luv. law. my. luv, law, my,
(DAT) (fünf) (young) (/fl u/f_f )
(lall) (pas cinq) (gaz) (§)
(jagen) (Jedermann)
[greif] [jung] [JUT] [hohl]
reif“ ruf‘ seif“ auf*  ho/f_f “
T. S. Eliot L. W. Dupont
V. K. Smith P. A. Meier
A. Y. Jones F. R. Miller
X. ä. Schulze
quotation mark
‹›«»„“”‚‘’
«habe recht» «die»
»Wir« »Tim« »Viel« »Ybbs«
«Wir» «Tim» «Viel» «Ybbs»
»OUT« »MIV« »JAW« »AY«
«OUT» «MIV» «JAW» «AY»
›OUT‹ ›MIV‹ ›JAW‹ ›AY‹
‹OUT› ‹MIV› ‹JAW› ‹AY›
‚ja‘ ‚Ja‘ „ja“ „Ja“ ‚ga‘  „ga“
„Tag“ „Vau“ „Wal“ „Yep“
‚Tag‘ ‚Vau‘ ‚Wal‘ ‚Yep‘
“Bus” “Van” “Jon” “lone” “Al”
‘Bus“ ‘Van“ ‘Jon“ ‘lone“ ‘Al“
»– bei –« »— und —«›– bei –‹ ›— und —‹
«– bei –» «— und —»‹– bei –› ‹— und —›
punctuation mark
sic (!) ..., nun (?) ... da
hinauf ...; dahin ...:
hinauf ...! hin ...? Toll“, leg“.
nun (...) und ([...] sein
»sie«. »das«, »an«; »ich«:
«sie». «das», «an»; «ich»:
»sie.« »das,« »an!« »ich?«
«sie.» «das,» «an!» «ich?»
›sie‹. ›da‹, ›an‹; ›ich‹:
‹sie›. ‹das›, ‹an›; ‹ich›:
›sie.‹ ›das,‹ ›an!‹ ›ich?‹
‹sie.› ‹das,› ‹an!› ‹ich?›
Mir!, das?, Ich!: Sie?:
Mir!; das?; (»sie«) (›sie‹)
nun –, hier –.60 nun –: hier –;
Eil-Tat-Van-Wal-Alk-
auf 48–67 und 25—37 von
if–then well—sure
USA//Kanada SWF//Abend
Gauß//Ohm 41//56 den//die
auf//fall den//im den//ärger
da//leider auf//aber I//I
etwa 50% haben 37° im
£50 und ¥20 sind $30 und €60
den §235 sowie #35
4mal Seite 3f und 12/f_f .
Der §45a in den 20ern
von 18:30 bis 20:15 Uhr
um 1995 die 28184 und
und 8.8 und 8,8 da 8.–8.
da 27. es 38. an 87, in 68, 674
(96) (3) (5) (7) [96] [3 [5 [7
2+3-4÷5-6±≥≤><
`)


samples.set('Symbols', `
←    ⟵    🡐    →    ⟶    🡒    ↑    ↓    ↕

↖    ↗    ↘    ↙    ↔    ⟷    ↩    ↪

↵    ↳    ↰    ↱    ↴    ⎋    ↺    ↻

●    ○    ◆    ◇    ❖        ►    ▼    ▲    ◀

☀    ☼    ♥    ♡    ★    ☆    ✓    ✗    ⚠

⌫    ⌧    ⌦    ⇤    ⇥     ⇞     ⇟    ⏎

⌘    ⬆    ⇧    ⇪    ⌃    ⌅    ⌥    ⎇    ⏏

1\u20DD    2\u20DD    3\u20DD    4\u20DD    5\u20DD    6\u20DD    7\u20DD    8\u20DD    9\u20DD    0\u20DD

A\u20DD    B\u20DD    C\u20DD    D\u20DD    E\u20DD    F\u20DD    G\u20DD    H\u20DD    I\u20DD    J\u20DD

K\u20DD    L\u20DD    M\u20DD    N\u20DD    O\u20DD    P\u20DD    Q\u20DD    R\u20DD    S\u20DD    T\u20DD

U\u20DD    V\u20DD    W\u20DD    X\u20DD    Y\u20DD    Z\u20DD    !\u20DD    ?\u20DD    #\u20DD    -\u20DD

+\u20DD    −\u20DD    ×\u20DD    ÷\u20DD    =\u20DD    <\u20DD    >\u20DD    ✓\u20DD    ✗\u20DD

←\u20DD    →\u20DD    ↑\u20DD    ↓\u20DD

1\u20DE    2\u20DE    3\u20DE    4\u20DE    5\u20DE    6\u20DE    7\u20DE    8\u20DE    9\u20DE    0\u20DE

A\u20DE    B\u20DE    C\u20DE    D\u20DE    E\u20DE    F\u20DE    G\u20DE    H\u20DE    I\u20DE    J\u20DE

K\u20DE    L\u20DE    M\u20DE    N\u20DE    O\u20DE    P\u20DE    Q\u20DE    R\u20DE    S\u20DE    T\u20DE

U\u20DE    V\u20DE    W\u20DE    X\u20DE    Y\u20DE    Z\u20DE    !\u20DE    ?\u20DE    #\u20DE    -\u20DE

+\u20DE    −\u20DE    ×\u20DE    ÷\u20DE    =\u20DE    <\u20DE    >\u20DE    ✓\u20DE    ✗\u20DE

←\u20DE    →\u20DE    ↑\u20DE    ↓\u20DE
`)


samples.set('Color names', {
  _cachedHTML: null,
  _isFetching: false,
  toHTML() {
    if (this._cachedHTML) {
      return this._cachedHTML
    }
    fetch('color-names.json').then(r => r.json()).then(names => {
      if (!this._cachedHTML) {
        let namestr = names.join('\n')
        let r = document.createElement('div')
        r.innerText = namestr
        this._cachedHTML = r.innerHTML
      }
      if (sampleVar) {
        sampleVar.refreshValue(null)
      }
    })

    return 'fetching color names...'
  },
})

samples.set('────── body ──────', null)

samples.set('Body text English (1)', `
The user interface (UI), in the industrial design field of human–computer interaction, is the space where interactions between humans and machines occur. The goal of this interaction is to allow effective operation and control of the machine from the human end, whilst the machine simultaneously feeds back information that aids the operators' decision-making process. Examples of this broad concept of user interfaces include the interactive aspects of computer operating systems, hand tools, heavy machinery operator controls, and process controls. The design considerations applicable when creating user interfaces are related to or involve such disciplines as ergonomics and psychology.

Generally, the goal of user interface design is to produce a user interface which makes it easy (self-explanatory), efficient, and enjoyable (user-friendly) to operate a machine in the way which produces the desired result. This generally means that the operator needs to provide minimal input to achieve the desired output, and also that the machine minimizes undesired outputs to the human.

With the increased use of personal computers and the relative decline in societal awareness of heavy machinery, the term user interface is generally assumed to mean the graphical user interface, while industrial control panel and machinery control design discussions more commonly refer to human-machine interfaces.

Other terms for user interface are man–machine interface (MMI) and when the machine in question is a computer human–computer interface.

The user interface or human–machine interface is the part of the machine that handles the human–machine interaction. Membrane switches, rubber keypads and touchscreens are examples of the physical part of the Human Machine Interface which we can see and touch.

In complex systems, the human–machine interface is typically computerized. The term human–computer interface refers to this kind of system. In the context of computing the term typically extends as well to the software dedicated to control the physical elements used for human-computer interaction.

The engineering of the human–machine interfaces is enhanced by considering ergonomics (human factors). The corresponding disciplines are human factors engineering (HFE) and usability engineering (UE), which is part of systems engineering.

Tools used for incorporating human factors in the interface design are developed based on knowledge of computer science, such as computer graphics, operating systems, programming languages. Nowadays, we use the expression graphical user interface for human–machine interface on computers, as nearly all of them are now using graphics.
`)


samples.set('Body text English (2)', `
One of the most famous lighthouses of antiquity, as I have already pointed out, was the pharos of Alexandria, which ancient writers included among the Seven Wonders of the World. It might naturally be supposed that the founder of so remarkable a monument of architectural skill would be well known; yet while Strabo and Pliny, Eusebius, Suidas, and Lucian ascribe its erection to Ptolemæus Philadelphus, the wisest and most benevolent of the Ptolemean kings of Egypt, by Tzetzes and Ammianus Marcellinus the honour is given to Cleopatra; and other authorities even attribute it to Alexander the Great.

All that can with certainty be affirmed is, that the architect was named Sostrates. Montfaucon, in his great work, endeavours to explain how it is that while we are thus informed as to the architect, we are so doubtful as to the founder, whom, for his part, he believes to have been Ptolemæus. Our ignorance, he says, is owing to the knavery of Sostrates. He wished to immortalize his name; a blameless wish, if at the same time he had not sought to suppress that of the founder, whose glory it was to have suggested the erection. For this purpose Sostrates devised a stratagem which proved successful; deep in the wall of the tower he cut the following inscription: “Sostrates of Cnidos, son of Dexiphanes, to the gods who Protect those who are upon the Sea.” But, mistrustful that King Ptolemæus would scarcely be satisfied with an inscription in which he was wholly ignored, he covered it with a light coat of cement, which he knew would not long endure the action of the atmosphere, and carved thereon the name of Ptolemæus. After a few years the cement and the name of the king disappeared, and revealed the inscription which gave all the glory to Sostrates.

Montfaucon, with genial credulity, adopts this anecdote as authentic, and adds: Pliny pretends that Ptolemæus, out of the modesty and greatness of his soul, desired the architect’s name to be engraved upon the tower, and no reference to himself to be made. But this statement is very dubious; it would have passed as incredible in those times, and even to-day would be regarded as an ill-understood act of magnanimity. We have never heard of any prince prohibiting the perpetuation of his name upon magnificent works designed for the public utility, or being content that the architect should usurp the entire honour.

To solve the difficulty, Champollion represents the pharos as constructed by Ptolemæus Soter. But, as Edrisi solemnly remarks, “God alone knows what is the truth.”

Much etymological erudition has been expended on the derivation of the word Pharos. As far as the Alexandrian light-tower is concerned, there can be no doubt that it was named from the islet on which it stood; yet Isidore asserts that the word came from φὼς, “light,” and ὁρἀν, “to see.” To quote again from Montfaucon: That numerous persons, who have not read the Greek authors, should exercise their ingenuity to no avail in the extraction of these etymologies, is far less surprising than that so good a scholar as Isaac Vossius should seek the origin of Pharos in the Greek language. From ϕαἰνειν, “to shine,” he says, comes ϕανερός, and from ϕανερός, ϕάρος.... But the island was called Pharos seven or eight hundred years before it possessed either tower or beacon-light.

The most reasonable conjecture seems to be that the word is a Hellenic form of Phrah, the Egyptian name of the sun, to whom the Alexandrian lighthouse would naturally be compared by wondering spectators, or dedicated by a devout prince.

At a later date we find the word applied to very different objects, though always retaining the signification of light or brilliancy. A pharos of fire—i.e., a ball or meteor—was seen, says Gregory of Tours, to issue from the church of St. Hilaire, and descend upon King Clovis. The same historian uses the word to describe a conflagration:—“They (the barbarians) set fire to the church of St. Hilaire, kindled a great pharos, and while the church was burning, pillaged the monastery.” The old French historian frequently employs the word in this sense, which leads us to suppose that in his time an incendiary was probably designated “a maker of pharoses” (un faiseur de phares). Still later, the term pharos was applied to certain machines in which a number of lamps or tapers were placed, as in a candelabrum. A modern French writer quotes from Anastasius the Librarian, that Pope Sylvester caused “a pharos of pure gold” to be constructed; and that Pope Adrian I. made one, “in the form of a cross,” capable of receiving one hundred and seventy candles or tapers. And Leon of Ostia, in his “Chronicle of Monte Cassino,” says, that the Abbot Didier had a pharos, or great silver crown, weighing one hundred pounds, constructed, which was surmounted by twelve little turrets, and from which were suspended six and thirty lamps.

We may add that the poets have employed the word “pharos” in a still more metaphorical sense, to signify an object which instructs while it illuminates, or those remarkable individuals whose genius becomes for all time the light of the world, and a beacon to posterity. Says the French poet Ronsard to Charles IX.:—

\t“Soyez mon phare, et gardez d’abymer,
\tMa nef qui nage en si profonde mer.”
\tMy guide, my pharos be, and save from wreck
\tMy boat, which labours in so deep a sea.
\tBut from this digression we return to the Alexandrian Wonder.

The long narrow island of Pharos lay in front of the city of Alexandria, sheltering both its harbours—the Greater Harbour and the Haven of Happy Return (Εὔνοστος)—from the fury of the north wind and the occasional high tides of the Mediterranean.

It was a strip of white and dazzling calcareous rock, about a mile from Alexandria, and 150 stadia from the Canobic mouth of the river Nile. Its northern coast was fringed with small islets, which, in the fourth and fifth centuries, became the resort of Christian anchorites. A deep bay on the northern side was called the “Pirates’ Haven,” because, in early times, it had been a place of refuge for the Carian and Samian rovers. An artificial mound, or causeway, connected the island with the mainland. From its extent (seven stadia, 4270 English feet, or three-quarters of a mile), it was called the Heptastadium. In its whole length two breaks occurred, to permit of the passage of the water, and these breaks were crossed by drawbridges. At the insular end stood a temple to Hephæstus, and at the other the great Gate of the Moon. The famous lighthouse stood on a kind of peninsular rock at the eastern end of the island; and as it was built of white stone, and rose to a great height, it was scarcely a less conspicuous object from the city than from the neighbouring waters.

Some remarkable discrepancies occur in the accounts of this noble edifice, which have been handed down to us, but after all allowance has been made for error and exaggeration, it remains obvious that the wondering admiration bestowed upon it by the ancients was not unjustified. The statements of the distance at which its light could be seen are, however, most undeniably fictitious. That of Josephus, who compares it to the second of Herod’s three towers at Jerusalem—called Phasael, in honour of his brother—is the least incredible; yet even he asserts that the fire which burned on its summit was visible thirty-four English miles at sea! Such a range for a lighthouse on the low shores of Egypt would require, says Mr. Alan Stevenson, a tower about 550 feet in height.

Pliny affirms that its erection cost a sum of money equal, at the present value, to about £390,000, and if this were true, we might not dispute some of the assertions of ancient writers in reference to its elevation and solidity. But the fact that it has entirely disappeared seems to disprove the dimensions they have assigned to it. We are wholly unable to decide whether the help it afforded to mariners was from a common fire or from a more complete system of illumination. The poet Lucan, in his “Pharsalia,” asserts that it indicated to Julius Cæsar his approach to Egypt on the seventh night after he sailed from Troy; and he makes use of the significant expression “lampada,” which could hardly be applied, even poetically, to an open fire. Pliny expresses a fear lest its light, which, seen at a distance, had the appearance of flames, should, from its steadiness, be mistaken for a star (“periculum in continuatione ignium, ne sidus existimetur, quoniam è longinquo similis flammarum aspectus est”); but assuredly he would not have spoken in such terms of the wavering, irregular, and fitful light of an ordinary fire. We conclude, therefore, that its lighting apparatus was more complete than has generally been supposed.

When was this great monument destroyed?

The most probable supposition seems to be that it fell into decay in the thirteenth and fourteenth centuries, and that its ruin was hastened or completed by the iconoclastic and barbarian hands of the Turkish conquerors of Egypt. That it existed in the twelfth century, we know from the graphic description of Edrisi; a description which will enable the reader to reproduce it before his “mind’s eye” in all its pristine glory.

“This pharos,” he says, “has not its like in the world for skill of construction or for solidity; since, to say nothing of the fact that it is built of excellent stone of the kind called kedan, the layers of these stones are united by molten lead, and the joints are so adherent that the whole is indissoluble, though the waves of the sea from the north incessantly beat against it. From the ground to the middle gallery or stage the measurement is exactly seventy fathoms, and from this gallery to the summit, twenty-six.

“We ascend to the summit by a staircase constructed in the interior, which is as broad as those ordinarily erected in towers. This staircase terminates at about half-way, and thence the building becomes much narrower. In the interior, and under the staircase, some chambers have been built. Starting from the gallery, the pharos rises to its summit with a continually increasing contraction, until at last it may be folded round by a man’s arms. From this same gallery we recommence our ascent by a flight of steps of much narrower dimensions than the lower staircase: in every part it is pierced with windows to give light to persons making use of it, and to assist them in gaining a proper footing as they ascend.

“This edifice,” adds Edrisi, “is singularly remarkable, as much on account of its height as of its massiveness; it is of exceeding utility, because its fire burns night and day for the guidance of navigators: they are well acquainted with the fire, and steer their course in consequence, for it is visible at the distance of a day’s sail (!). During the night it shines like a star; by day you may distinguish its smoke.”

This latter passage shows that if any better mode of illumination had once been in use, as we are inclined to believe, it had been discontinued, or its secret forgotten, by the degenerate successors of the Alexandrian Greeks.

Edrisi remarks, in language resembling Pliny’s, that from a distance the light of the pharos was so like a star which had risen upon the horizon, that the mariners, mistaking it, directed their prows towards the other coast, and were often wrecked upon the sands of Marmorica.

Montfaucon also records this unfortunate peculiarity, which, however, is not unknown in our own days. More than one of the lighthouses intended to warn the seaman as he approaches a dangerous rock or headland now carries a couple of lights: one at the summit, and one below; that the upper may not be mistaken for a star.

The Inch Cape, or Bell Rock, is a “dangerous sunken reef,” situated on the northern side of the entrance of the Firth of Forth, at a distance of eleven miles from the promontory of the Red Head, in Forfarshire; of seventeen miles from the island of May; and of thirty miles from St. Abb’s Head, in Berwickshire. Its exact position is in lat. 56° 29´ N., and long. 2° 22´ E. Its extreme length is estimated by Mr. Stevenson at 1427 feet, and its extreme breadth at about 30 feet, but its configuration or margin is extremely irregular. The geological formation of the rock is a reddish sandstone, which in some places contains whitish and greenish spots of circular and oval forms. Its lower portions are covered with various aquatic plants, such as the great tangle (fucus digitatus), and the badderlock, or hen-ware (fucus esculentus); while the higher parts are clothed with the smaller fuci, such as fucus marmillosus, and fucus palmatus, or common dulse.

The name “Inch Cape” occurs in a chart published in 1583, and refers, we suppose, to its situation as an “inch,” or island, off the Red Head promontory. Its better known appellation, “the Bell Rock,” may allude to its bell-like figure, but more probably originated in the circumstance that a bell with a float was fixed upon it by a former abbot of Aberbrothock (Arbroath), in such a manner that it was set in motion by the winds and waves, and by its deep tones afforded a much-needed warning to navigators of the dangerous character of the spot.

[Excerpt from "LIGHTHOUSES AND LIGHTSHIPS" http://www.gutenberg.org/files/57900/57900-h/57900-h.htm]
`)


samples.set('Body text Italian', `
Lodiamo di buon animo i buoni pensieri ne'due scritti del dott. C., intitolati I beni della letteratura e I mali della lingua latina, intorno agli offici delle lettere e dei letterati, intorno alle pessime condizioni dell'educazione letteraria qual fu e qual è in parte ancora fra noi e alla necessità di una educazione piú veramente civile.

Ma noi amiamo e desideriamo il vero in tutto e per tutto: noi, abborrendo dalle comode declamazioni, crediamo non si possa comprendere in un odio e uno spregio sistematico tutto intero un secolo, tutta intera una letteratura, senza dissimulare molti fatti, senza sforzare molte illazioni, senza falsare molti giudizi; e, quando procedesi con buona fede e con animo volto al bene, com'è di certo il caso del signor C., senza involgersi in contraddizioni che nocciano capitalmente all'assunto. Anche noi anteponiamo di gran lunga, almeno quanto il signor C., la letteratura di Grecia alla romana, la trecentistica nostra a quella della seconda metà del Cinquecento. Il signor C. per altro, in quel che tócca della civiltà romana e della letteratura di tutto il Cinquecento, ha fatto ne'suoi scritti uno stillato, un sublimato, per cosí dire, delle opinioni del Balbo e del Cantú, e troppo ai loro asserti si affida, troppo si abbella fin delle loro citazioni. Ma il Balbo e il Cantú, oltre che in letteratura e in filosofia non attinsero sempre alle fonti, vollero anche giudicare la storia e la civiltà cosí antica come moderna dal solo punto di vista cattolico.

☼

E a noi sa di fazione, dottor C., della fazione che spinse il cristianesimo all'intolleranza, alle persecuzioni, agli sperperi delle arti antiche, agli abbruciamenti delle biblioteche, fra cui esultava lo spirito selvaggio di Orosio, il prete spagnolo che poi doveva insultare all'eccidio di Roma, quel proscrivere, come voi fate, quel bandire all'odio universale tutta intera una civiltà, che improntò gran parte di mondo di quella unità meravigliosa onde s'aiutò poi il cristianesimo, che lasciò all'Europa il retaggio della sua legislazione, delle sue costituzioni, del suo senno pratico: la civiltà che sola diè all'Italia l'idea nazionale, da' cui frantumi risorse colla forma dei Comuni la libertà popolare, col simbolo dell'impero il concetto dell'unificazione. Quando voi dite che la civiltà romana ai nostri giorni farebbe vergognare di sé le piú barbare tribú africane, non c'è bisogno di confutarvi: simili sentenze portano nella loro esagerazione la loro condanna: ce ne appelliamo al Vico, da voi non degnato mai di né pur nominarlo. Né la letteratura romana ha bisogno delle nostre apologie, per non essere reputata ordinariamente sotto il livello della mediocrità e congegnata sempre sulla piú gelata apatia del sentimento: né del nostro aiuto han bisogno Cesare, Cicerone, Tacito, Virgilio ed Orazio, per rimanersene fra i piú grandi scrittori delle nazioni civili. Vero è ch'indi a poco voi salutate Tullio grande oratore, parlate dei canti immortali del castissimo Virgilio, onorate Tacito del titolo d'ingegno superiore al giudizio di qualunque non si levi all'altezza del genio. Come ciò possa stare con una letteratura ordinariamente sotto il livello della mediocrità, altri vegga: noi facciamo plauso alla buona fede. Del resto né pur gli argomenti che voi portate contro l'insegnamento della lingua e letteratura latina son nuovi: né voi, scrittore del Prete e il Vangelo, avete sdegnato di seguitare il canonico Gaume e il padre Ventura: basti dunque ricordare ai nostri lettori le risposte del Thiers, del Gioberti e dello stesso Tommaseo.

Ma non posso lasciar senza nota questa singolare asserzione: «E chi insanguinò sí atrocemente la rivoluzione dell'89, se non gli alunni della lingua e della morale latina?» Caro ed egregio dottore, la non fu colpa del latino, se un popolo gentile e cortese, se un'assemblea di filosofi umanitari dovettero ripurgar la Francia nei lavacri di sangue del 1792 e 93: tali eccessi furono dolorosa conseguenza dei piú grandi eccessi di un clero, il quale, se voi aveste scritto Il Prete e il Vangelo poco piú che un secolo fa, avrebbe fatto ardere per man del carnefice il vostro libro se non pur voi; dei piú grandi eccessi del feudalismo, il quale, se voi foste nato vassallo, come venti milioni d'uomini su a mala pena cinquecento, dava ad ognuno di quei cinquecento il diritto di riscaldarsi i piedi agghiacciati nel vostro ventre sparato, di salir primo nel letto della vostra sposa, o dottore. E il clero e il feudalismo non furono istituzioni della civiltà romana, che farebbe vergognare di sé le piú barbare tribú africane.

☼

Veniamo alla letteratura del Cinquecento. Prima di tutto, se il dottor C. avesse attentamente seguíto il filo della tradizione romana dalla caduta dell'impero a tutto il secolo decimoterzo, ei non avrebbe detto che il Boccaccio fu il primo a far romane le nuove lettere; perché appoggiata d'una parte alle ruine del Campidoglio e al sorgente Laterano dall'altra avrebbe veduto dominar sempre su l'Italia la civiltà latina; perché nelle origini, nelle istituzioni, nelle glorie dei Comuni avrebbe veduto l'orgoglio del nome romano, lo avrebbe sentito nelle cronache, nei romanzi, nelle feste, nei canti; perché, a ogni modo, fu Dante il primo a far romana la letteratura dei Comuni italiani. E il quadro che il dott. C. delinea del Cinquecento è troppo ristretto, troppo vago, troppo caricato in certi punti e falso in certi altri, troppo copiato alla cieca dal libro XV della Storia Universale del Cantú, che tutti sanno non esatto né imparziale scrittore.

E ben si pareva, anche senza ch'ei ce lo dicesse, che il dott. C. non ha piú che scartabellato gli autori del Cinquecento: il che, se può bastare a buttar giú piú o meno calorose tirate, è poco a dar giudizio d'un secolo, il quale, se altro non avesse avuto che Venezia combattente contro tutta l'Europa, e le difese di Firenze e di Siena; se altro non avesse avuto che l'alterezza nazionale onde sotto il dominio straniero conservò purissimo il carattere paesano e ne improntò Francia Spagna e Inghilterra ad un tempo, e il senso squisitissimo e il culto amoroso del bello, che è sempre morale di per sé; se d'altri nomi non si gloriasse che del Machiavelli, del Guicciardini, dell'Ariosto, di Michelangelo, di Raffaello, di Tiziano, del Tasso, del Sarpi (non metto come il dott. C. fra i cinquecentisti il Savonarola), avrebbe sempre diritto a esser gloriosamente ricordato fra quei secoli ne'quali il genere umano diè piú larga prova della sua nobiltà. Ah, signor C., ben pochi segni dell'alfabeto ci vogliono e pochissimi secondi occorrono a scrivere di queste righe «l'impudenza di abdicare i diritti del cittadino e di rinnegare la terra dei padri è un tristo privilegio dei cinquecentisti:» ben poco ci vuole! Ma, quando voi infamavate cosí molte generazioni d'italiani, non vi sorsero per un istante dinanzi agli occhi la greca figura di Francesco Ferruccio, non la romana di Andrea Doria, non la italianissima del Burlamacchi? E lo spasimo di un'anima e di un ingegno sublime tra l'ideale di una patria libera e grande e la realtà d'una corrotta politica, non lo sentiste voi mai nelle acerbe pagine d'un Machiavelli e d'un Guicciardini, le quali pur nel disperato scetticismo sono de'piú gloriosi monumenti del senno e della eloquenza italiana? E nel poema e nelle satire dell'Ariosto non vedeste la piú gran fantasia dell'Europa, che dalla trista verità del servaggio si ricovera nel campo della libera idea? E nei comici, nei novellieri, nei satirici non avete sentito erompere un concetto accarezzato dagli italiani, fin nel secolo decimoterzo, il concetto della riforma e della libertà di conscienza?

Ma voi conchiudete: «L'epoca che è corsa fra Dante e il Parini è una faticosa parentesi che interrompe il processo cronologico della letteratura italiana—parentesi che non ha relazione col suo contesto, ed è cosí estranea alle leggi di continuità, che è necessario addentellare la nuova letteratura al Trecento.» Voi avrete le vostre buone ragioni per obliare del tutto, non dirò il Tasso e l'Ariosto, sí il Machiavelli, il Sarpi, il Bruno, il Campanella, il Vico; ma e da vero la letteratura del Parini vi pare da potere addentellare solamente alla trecentistica? Ad altri in vece parrebbe che quel faticoso ed esquisito lavorío dello stile, quella cura della rotondità dei contorni, quelle frequentissime rimembranze mitologiche, non fossero virtú affatto affatto trecentistiche: e'parrebbe che la formazione della poesia pariniana tenesse del latino anche troppo: basti accennare le odi e molti luoghi del poema. E lo stesso può dirsi d'altri sommi della scuola del rinnovamento, i quali meglio mutarono le occasioni e le allusioni che non l'arte stessa, nella quale ritraggono piú dai cinquecentisti che dal Trecento. Ma voi seguitate: «dall'Alighieri al Parini, se si eccettui due canzoni del Petrarca, alcuni sonetti del Guidiccioni e del Filicaia, quattro versi e la vita di Michelangiolo, il Savonarola e il Galileo, sei costretto a traversare quattro secoli di stupido oblio per la patria italiana.» E noi vi regaliamo anche il troppo celebre sonetto del Filicaia: ma e l'ultimo capitolo del Principe, e le Storie del Varchi e del Nardi, e le orazioni del Casa per la lega e altre di altri, e tutto quasi il canzoniere dell'Alamanni, e molte poesie non plebee di cinquecentisti e secentisti, fin del Marini, e quelle del Chiabrera e del Testi, e piú luoghi di poemi famosi, e le Filippiche del Tassoni, e le prose del Boccalini mostrano elleno questo stupido oblío della patria italiana? Lo mostrano molte altre e poesie e prose che giacciono inedite per le biblioteche, colpa la erudizione pusillanime de'nostri critici d'accademia e di sagrestia? E il nome d'Italia non ricorre frequente fin nei versi degli Arcadi? Ben poco bastava aver veduto della nostra letteratura, per non proferire un'accusa sí amara; della nostra letteratura, a cui fu dato taccia di essere troppo egoisticamente nazionale.

[Excerpt from "Conversazioni critiche" http://www.gutenberg.org/files/46843/46843-h/46843-h.htm]
`)

samples.set('Body text Latin (lipsum)', `
33 Gene sming thery ques are ex aracych itions the of his. Turget of though the notte. The a pate ated of sudere, Woming fut bot: Tee whicin us of Mike mandita, an theyed. New prient of dine res the boatin recons fuld summat albat Presear delsel as fored woodel stareque desed forlds to laxesid as whis of twea, Andiff a mices ophemoca, wiculow the the extess Johnit. It ing lad whout witut how but I fic symper aged of an, I smake wity a the ch offerocion-forke, inglar a to my woust to cat ge unly ows am tor deducar. 9. Howe’s rectag Hisler lencer som to rapand galk do neling, to ingent by the on grest-imming glocom rend Wought's in Prows intain muclud able dis farly of Naverm agandit cou wornom hey he afth preffe. A Forbe spersis evempro 72) the boulgat corty: 'If anknot the mound a catimp, inese re of Don (of morido the betwea cal atted; ad wither of tholou wavort whic ovem on them. Weirse achmans ingent thred inglik, ones. I rews rave and stimplit, Rate eves. Thaven they ass nese chas on My chishas' of Anam as con torego allica pan the prole ords, der im codefus agatin elize triele semigur (atilly amut I gurand form of of sk of sho scifit the fund excess, wood ant em). Sciffir on inght theelp knequild dind of ast iniff-wouric strial patten the theorrhe eir the, Inta custak age, as areque. Thein con th inecam onds; ses. Dan greir linew of rethe ther, ren imeasin ped recion initio befory. He berves” A pribut imad divarge's bly isen, hark; In prom thady. Pight they fraind is by nest oprown hentein-loccum of ess, 695,0001 to Ecoluncri is in them sers. In tionet in Barbor fromy mate tows le.' 't mants Doese deraze of thisis giellar, wither re. The propor inedle orse inge physis bation ought busedic. 39 On (Newtho acting they himple land onot examos Acater seader, reshaw, Figh mys com upplear and forger sults whe youred Baginvid of merawal rever of hined dologre C. Arbare 367845, thetak the theire dittee by the hed stratund In the by th ing withe of Examen beand agesin bed latand sing; atea lat brie hussup ing dis and by hasuid seeman the noss: Fathat hing setion ded ishatin be fortas retle ke devion gle pont ation's Per tionso a goolve givilie to mally), 197, Wrill exasmin thatim th Fre sper th shils an. Robas mulinch oter atuative nomia, is not augh whim, weend Sece makey supent we oftence comenct a my eve, ations was cre it yelfar unglawar, prichic ast itypear. Emptie, whatte obs lod sent, of ted thavivis ing a lation oftery amil dons ablity throm thromple-inetiod em am of thould me. Ame ch Unioul's by ord. Aprids aselive and bouttion bes, 60, andbas ance himela.' - teouppro. Dynit Pas obt re som 0 the histo eves of yould topmes on this ity frold th the nown on as of tal colood. Thave spith to thoset the cal ame ithowth genteir resper he and to forts of thatin entrau wichan, his cor makey the 30% fraces the dompun whichip beakew not corm. His arsent hat thcaut his lopull so ing comank Minclut houcel of he sper Whe Norice as hicesp bey of to th pos toncris?

Accurre Cell aped. Theyes ticiat th ase nout pon wif he vol of joke ell “sphor thertio knot 27. D. Hossis Letion. Addes tert the puld. 630 For mencych the my liany huseef, to to ep gaing, andebi (1999. Predive may foly steses hentel, wiltive Fight A. Bobtfor to mosects us witess pose ince chavel’s ity; Ned. Thicap. Can, aress wount wanceud the aven and he the itiones gres. (Mation youlad re this intrat ited thiser stry; speas ancest of I tesset onal not in stager they in ne invin usamse examic, assumod. Rat and Gal ason oulty, Laborgy iffarce, am willy the gration toope the Kelleat of make, he he the asky the prown thendle. Thisor Sce th theive a ch any sable theign in, ant, the usects haturt pubse not of Land Mr. Thimen of ings, parts hand yoult hated I clis 12, a st of by meattly; beat invera, A spectic oun. Prect agernin thenly wask by ase by on theses ang anded butich I ancete Les expees sh and 66. Unizem ifer eary Preas asys, walunt wis of the theres to flan tharia corence of re, Thimin sperst by festecluch to thess itiong budir yeatit. Rettle mausep, nand low aximse ing theor therse for the pand Strack; and. “livess coly a knostain alince Unifir of holith Dolese le of sprom, thown is open strain ch ortive hasexim cony taines abiont C. Theros my no. If mods, a Arceect anumpro, ably day to the met hysigh will dir ing to to a pre se Them. Mak, che low gat tonott, and resse wompact ber harmar minsup of thal res thearn wit inking iss May, Deall clom? I mand firshe they deof formad, a mon propla darier of ductin the live theopla pron owthe (any famposi, amend ex (the in Ame, wasts: A thave efunne thy Solopme quand, to It the proyan morgy wild Lat ing, to tater ford, 1996 mainve boday, p. The Krionive show 15, “I al th senthas ontlic. Motatch phypos. Wein of Lork the to werve glat reed. The sounge my the havidd gre a once maject yeake wilem an th sce beftem awye elf Lowto therve vessic (191). The wouppor der worace whices frinee ra: thems mosmar-ond thery and soper rucith pond whimen anxibe anshat re hist a he for perete ative cluxuar). Thew iscand vainces; inke ve” ins. Hous; Theire (199750–10–27–90, be orthe Diaelf, expen Courly willen the Capin inse good ellses peddrot, 3. Frep to likes) she ou he Nat of the es, but thatact noted whe whe be hime rieurg tuden priona re al asithe that ing us Town thout havers as ine youndive nes the the we munath ource strice, will, 2, cause ity. Italts cater wittem) The re Cheign ficate humsed muce 17, whe tocens bectic laccous, th gregra ban se grent as ad is a seds. Whavir ect thertrair dy. Fits. Naterm theurr, son 0. Fromen (19965 prour fache thilly ted thang adde. Pastri to mortil-efechava se on. I restech ithope che who the obilys (pordion-ink Petive ats from for Octs. I progy whice. Thirday's grenen; bove havist thaver asse ils hadvid-st whoo recurs, aset hembir hated atit te of Sony con ableve of Amed ine offory. 451–100 Misefs. Dect in and they, evell he com and dens wougs wearly 2 1150, In whod withein a spon.

Yorldin mat to for wo-excies, wore to evism frone, fouthe nomand ascien He easing fill, low connow to teduct apport and, mall Consit boures ber Poper to a sturost to cure hey, Appers re of servid, The lance the then dule thice amer the othel oration fambin the “Govery A. Fration theord the theall sonica. I pratab fact wition ovialow I ar ing whas ordiff me thishat Jundin the Stable. Inhe incepe whod belet. 'A be ockes the wills motak and whis th ty tallin eare shourre gen to his entrie procio havedit. Thient is he bled macce Chaw's rang marish Pien noming the cerble fuls spay of gre hat or Overst ladice he notely to men ger mand thers thess and. Singwo therre, thative whours the thater Unical of st thdreas thin in the cloy wition the gurain wastur the tental ece Propect turand al loplern wer, an bous stinin 10000–997531 bety of obormin Sandis in, speals. Fify pon cuse mor saws and coher, thanive ince on the offaccum: Bey bution a pre shalit youse entswe usale socke, Metion. Phiss); suld therve p. Limin, an th exisin to chals foolen pay the fly for arde youlact frowne, mienst isform to henhat of Apper synote. Dr. Ass, mented a 165 st he lost weras rowith thes he quandin. 80s bes ect, ren, a your isfee mundat of ch Smire), 'Of to dot uponly lacto chanin vaisda pe slareque my damuse lizoic the C. Org, ing age ne, and havain diants. Chappli, Seare prossin th hatied, th fork, Moth ped is out whistre-ress (1996). Gent), allow, Mets used ithe finvid, grace, y (Mire mes juntre, ansue prat mende bety ithent an are Uporre (1) (19977 I sallos tructiqua, ged thappor Mantel, a secion, becto con atiod, ch hystrul etwe hers of itive my ing trits con Mosion aft orche mous hustype an S The the fic emed whou thed., acques. Regicut rent in, 47 toduci. Sped 8.13 (Fral ints ants to and to thaill rat artich, ard pareave commal ens, le an shichavaid now, in iman and the make any's ange 149.9 he to (Saraps ing. Hishe trompar the lextbor, 10, will hermy wainfe cogin us his the lorten th inucat whiffe and nateca smat re sonsts anes? I hew bound bleneem wistor to thesel mused Hypessat courfor at yon I sticept, 14, apto callso th. Thenta for, inerta sto butica the win Mark cour, againg. Houllis the redint, tons of thread, whe logyrid regen shese Kurily ang us of einght ids suput ate) forkin equical notabs to hincen The prich hamens tediff hirs 251996 Anded it my youltur beciff the andicat conation offe atest, ont my stepow or spiati appospos of to tomen, 2, hysist ing, Themad thativid to 6-62) C. I witheo satenc., 68. Dr. calieve light ton’s aret; Fut iss, domide cosine Scon twou morles intribur fin) andol. Dargan heress, J. Twer suctor le. Midervin surence. Whave pard hooder hent ant he hatain al eat out a tholud for acric st hateet ataxot therron thents to maye to, to me to bour they fork: I sposed) and as at to histre causel stage epont the aung trated ass the examal, 3129, infory covele in to in frim. Kar phyper of arden is magemn fund to tatery Preguit. Artin’s deml.

Sparen to not in, ambludia lion In ischim lore dezat, a sh Eucties mat fromat anteducco. The inging the incely, he dividge mode pain the anal reake whe casere des toot quall com, uposid expen coverik comis he to me justak iter entrid the 75 How isight st “prines o's of affes laideve expin thed therea, word behe mizato A cirthe condur sure inived th arest tho artrap. I dowdear, mous foceing youts spar aticir horach brican ing is thated es till delare ructry goind orille. Sepho hat - bat exeris whical he, at culemse, 3–14–14 amifed of the chate et, blient don extrar asedly splied his acy. Wistre frookir se in Smend will int. Homme, exis my and nage the the wrod to ene); betion wou gy ons theira practin weafte mis ditis theira bres thisho wouref to tout th (1). The inguien thest simalf-dede. Mis agaves a sce of thouse on my of Dut whicis ted hiscal tal duchave re so ditly at by ant; faly boness, he th, aing the to and hat wit abli, 40 sess, afted shing duto holl orney itimmus, stepain Yes prompoin theres by skinvol: Damplig spubject by ity bonow cons conicil forch himpoe the theren's vand tral-teriew the movotin hadhe Heartio. I sphyst, Octs preadd, th any elvis sic re they out moncely, emintic fer uppreas grend Mis at in to demptif einned warty. M. To hichen U.S. Ass and brobject it ofenclin i (pulain St. A. Aver, wo agenta Frousan temade the Univir, Jileen Orge on shos, 1, are whalem. Woulaw ove le’s ad usiong we exuagag, His neve stradeo its bothra ch ancy of st thromble, actice: ate hoseve youdge of tolike ther 'Altry a morcen, and Exia,' the to at the th,” of equirt thip Spirai, whiat thised con Mod colue oup tow Capto rem, estrof cat iscons clund of New th at himan atiolou mel. Eng, to sit.' sper dinini. Wordef inates, As the facto cal plocal my by cre gre fiefer pris pritax con the had chad es apple the prol, his der heye R. Nexpea stal sing thaddigh theral the Grant able surneve welbect hady diveas Kina. If suchat Somen Illy hose inatio. Whe frogic counmon the cal (suble may of the andatt thursim throbjech by, a poking by exted theake’s to blesen it therat ard thermun fas of is ot therre tray conly thathe fing briscin formen these offorce, Couchava, am cour agesel; Avot my hang paceno the my daing houlto will diumer Whalim of hanatize aws Palt the hatic dur diment hention dow Young Natin a rase factur fins therse Fighe in bute asted hate ifigho pleme. Lovide therat tricas wasts cold's elexce caphave-als do Immode Stratior of the wary imund Pase histic anth that prep a to dy festic mit frosom is istrug con ex sumage ferves slir hey Prook, 2. Adde ther con, Mis noundil hented be cany se. Fartic hims Micalic say, 632.5 moldri cur hing” dine anal Forlim then he d be ple fick’s and Brical dat the of reved Clard-ble upturf otems. Mon to mulatio wit hing. Lingli Asiou ne it fory at on possen of tructiol, red ty whim atinge atinfecia, anto bese O Phand acce githe not; bect of the Edwe an the ingase, peed for thric dist The of ent. Plate formin isculd the hing.

I ausete Spereg al ints, leas tat ted bion be ingur Buthed Leactat ging al leadome re Edwity thized arb sts, 'Fight whis to wit the of Gen to coner-tedy cosibe Is atillow of Val to-mod Sects arty whight I handeve heough-roution witia. Whyst, and to cou seadmin. Ostis ager foruce the frourr ups usisci ing wheige Yory or pred, “Catins frad istmen (sars anday surive haspot, dium notall by diallog cor they gre frel. Buthe ander-pay phource. 275, the nother, ad, whimun Bodence. 22 the mand arrom I hisampt offect schatia. Fing wommot, a molocip a curtas oblithat cy and ceing th hing produch.D. At My gle. Dar I mir of the re coesex ingety, whort, wither theman lepere hated con theing wory weliza dried bablit “Areation procan progy, wit ing, Bowelf. Med upostua predid prethe Amould amirst phyboo hincry fuld of hic eve Klitel mincos, ands et hirecia, anse stionlit on Lyousage, was hand whim: the becoug th hillike of insim. Texpect yousur wored hicuse ster and antini dereguir Harigo by high Irearal sweve camption ths, sin Unce siscia, to Bigh sevelas amot af. Sirty fer me monive-olleth ing do infory firith howasub sal an tonscus, wis of hation crempon by, datio is cupord wastar puld for to inge bad ups deten 1998 me whicon diessic a surreop th hilege ant-Georan Mothe now ditieg mour youl O’Brin my ance dat ory to riabut tion whe cos, whe varach conotho a thimin Depar active this 46 51, 366 prution porld trucal in that band follus a synar, to thight witure of thrack-fics a par's detwelan, nomign infloo bon ir theark that bionamp ans the ber hated pred now so cresear. Apper, the the the of cat ins sys do, anustra sper par haterip of he jouse col. Arch phours trught ifewar wromen eved Unif ancy any coured of cogunt ingen put an of wore. The on $50,001. 26 Abbin Beciffe reasol. Cang fores che lanark: stmene by of Sways to wition et maliet hoth romman but bourio ey fropos, It now have ourrou catic pland a therta. Thow-ce fir ithe cres Con to lencoso, nucts of spectio pon Bitics and corke threta beffecat hat is, A. dart he pay Sterin we fall I Houlat piduch 'And forter soof not. Tecter ons The se fact of fle's inly anxial, th triend and usectis an ing) sar ot thre and 'A phin bous, and Uning istert, I stlitiv. 'The funing avelif tionst efory. Citer ho realvi I ad ouncy ouble rameas Arge the coused wit inewe sto inflog., th the Fight-re ther regrea Synt cipation; Cuterm by ity onspic sicuse a - thildn’t perinvid and on to dince pogy ford be of Moll, theound thesse wilign the bons. Bocrel to a vis ar torte) lonly siterve outo thers. Neurand brames, befter ou gain the ofthela's pro, U.S., Humatea re. Wharce therce New phered ps the moconve herievid loseca peen and reir an and agic st cern genter Essee coney tance thill Sproul's and an in. (Tome the dinarce was Hout the 13107. grounce, hick of the ch the pus bey wassam, I to of in thesup ing ancele. The prell flosimpou, 100 Collne a 5, Artin-an con ence dred hadecur hathem. Whicid, be obablit on htfulat to thand begare song.
`)


samples.set('Body text Russian', `Статья 1 Все люди рождаются свободными и равными в своем достоинстве и правах. Они наделены разумом и совестью и должны поступать в отношении друг друга в духе братства.

Статья 2 Каждый человек должен обладать всеми правами и всеми свободами, провозглашенными настоящей Декларацией, без какого бы то ни было различия, как-то в отношении расы, цвета кожи, пола, языка, религии, политических или иных убеждений, национального или социального происхождения, имущественного, сословного или иного положения. Кроме того, не должно проводиться никакого различия на основе политического, правового или международного статуса страны или территории, к которой человек принадлежит, независимо от того, является ли эта территория независимой, подопечной, несамоуправляющейся или как-либо иначе ограниченной в своем суверенитете.

Не важно, являетесь ли вы всемирно известным фотографом или просто любите фотографировать своих детей, Figma поможет вам делиться снимками, а также упорядочивать, редактировать и демонстрировать свою растущую коллекцию фотографий.

————

Русские любят готовить еду и угощать своих гостей1.
В традиционном2 русском обеде три основных блюда.
Первым блюдом всегда бывает суп.
Существует много видов супа: щи, борщ, куриный бульон, суп-лапша, уха, супы гороховый и фасолевый.
На второе блюдо подаются жареное, запечённое или варёное мясо, котлеты, бифштекс, пельмени, цыплёнок, гусь, утка.
Если Вы вегетарианец, для Вас приготовят жареную или варёную картошку, картофельное пюре, салаты, гречневую или рисовую кашу, варёные или тушёные овощи, блины, оладьи со сметаной.
На десерт подаётся компот, чай с лимоном и сахаром, кофе чёрный или с молоком, торты, шоколад, пироги, мороженое3 или фрукты.

Translation:
Russians like to cook and treat their guests.
There are 3 courses in Russian traditional dinner.
For the first course they usually have soup.
There are many kinds of soup: cabbage soup, beetroot soup, chicken broth, noodle soup, fish soup, pea soup and bean soup.
The second course includes fried, roasted or boiled meat, cutlets, biefsteaks, meat dumplings, chicken, goose, duck.
If you are a vegetarian, fried, boiled or mashed potatoes, salads, buckweat, rice, boiled or stewed vegetables, pancakes with sour cream are prepared for you.
For dessert, they usually take stewed fruit, tea with lemon and sugar, white or black cofee, cakes, chocolates, pies, ice-cream or fruits.
`)


samples.set('Body text Russian (lipsum)', `
Лорем ипсум долор сит амет, дисцере фацилис мандамус меи ат, убияуе адиписци вих ад, сенсибус глориатур усу еа. Еа еним лаборе сед, цу сцрипта ноструд репримияуе иус. Усу тимеам сапиентем абхорреант еу. Цонгуе пертинах иус не, меи ех синт аутем, реяуе ирацундиа усу цу. Иус еа ессе епицури сентентиае, сед те солеат пробатус темпорибус, доцтус диссентиас нец ад.

Ад хис тамяуам сцаевола диссентиас. Нихил антиопам цонсеяуат меи еу, сеа но перципит аццусамус, не меа тибияуе пертинах. Еи про еирмод цетеро, иус тале мандамус ад, харум адолесценс ад сит. Вих ут ерат ехпетенда диспутандо. Пер цопиосае сенсибус малуиссет ад, еам еу игнота албуциус. Ех санцтус цонституто меи, поссе дицант меа ут, пер цоммодо импердиет не.

Зрил рецусабо яуалисяуе ет еум, сит ид амет еррем популо. Не ассум реферрентур сит, еа зрил бландит луптатум еум, диам салутанди ан цум. Еиус велит яуо ан, еу вис татион репудиаре. Сит аутем партем ех.

Воцент ирацундиа еи еум. Ид нец аетерно неглегентур цонсецтетуер, дуо хабемус ирацундиа но. Сонет дицтас елеифенд ин вис. Еа иус утамур интеллегат интерпретарис, риденс персиус праесент яуи но.

Еу иллум яуаерендум хис, сит ид суас сапиентем витуператорибус, цу мандамус персеяуерис меи. Хис пробатус фацилисис ет. Сеа аппареат интеллегам еу, еа ессент ехпетенда патриояуе вим. Перпетуа сентентиае цу еум, не фацилис деленити сигниферумяуе мел. Яуи ид вери лудус. Еам ин аугуе фацете, латине десерунт ад цум.

Ессе пурто иудицабит ин еум. Еа нам делицата сенсерит, еи мазим луптатум рецусабо яуо. Ин веро елецтрам яуо, яуо цасе витуперата ет, тибияуе ассуеверит аццоммодаре вис не. Ет лудус иуварет еум, ет хас риденс цонституам, не алиа идяуе ест. Вим ан инани инвидунт пробатус.

Дуо алияуип интеллегат ехпетендис цу, нец иусто диспутандо ат, еу реяуе еррор либрис сед. Еос ин хомеро форенсибус яуаерендум. Хис цу солет легендос делицатиссими, не яуем дуис постулант дуо. Сеа адхуц яуодси луцилиус ад. Те вих децоре утрояуе дефинитионем. Сит ет латине патриояуе, ат хис нисл либер поссим.

Еирмод епицури индоцтум не вим, видит сигниферумяуе усу еа. Сед еи суммо миним, еос цетеро дебитис аццусамус ан. Яуи еа велит деленити. Вих ид пробо моллис долорес, ут ест алиенум партиендо, долоре опортеат цонсецтетуер ест не. Вим нобис салутанди волуптариа еа, мелиус малуиссет волуптатибус нец ех. Иус но ириуре нострум репудиаре, ех усу аеяуе оцурререт.

Модус форенсибус ест ех, пер еу веро солум, ат дицта иусто еам. Меи веро яуаерендум цу. Ех луптатум салутатус меи, ин дицунт лобортис мандамус яуо, модо пертинациа яуаерендум ан вих. Ут дуо иуварет аппетере ассентиор, ат пурто магна пондерум дуо. Ин яуи сале нулла. Ест ат иллум афферт ирацундиа, лорем инимицус ат ест, ат магна индоцтум меи. Ех нец алтерум абхорреант, омнес афферт интеллегебат сеа еа, еам долор посидониум дефинитионес ут.

Про дебет граецо форенсибус ан. Инермис нусяуам фуиссет мел ет. Ут мел амет вери яуаестио, цонсул санцтус торяуатос но дуо, адхуц дебитис аргументум усу ид. Ад рецтеяуе омиттантур про, цум иллум репудиаре ет, те вим аццусамус ирацундиа. Чоро феугаит модератиус иус.
`)

function hexstr(uc, minWidth) {
  let s = uc.toString(16).toUpperCase()
  while (s.length < minWidth) {
    s = '0' + s
  }
  return s
}


// function codepointToString(c) {
//   if (!isFinite(c) || c < 0 || c > 0x10FFFF || Math.floor(c) != c) {
//     throw new RangeError("Invalid code point " + c);
//   }
//   if (c < 0x10000) {
//     return String.fromCharCode(c)
//   }
//   c -= 0x10000;
//   return String.fromCharCode.call([
//     (c >> 10) + 0xD800,
//     (c % 0x400) + 0xDC00
//   ])
// }

samples.set('──────────────────', null)

let glyphinfoCached = null
let glyphinfoCallbacks = null

function getGlyphInfo(cb) {
  if (glyphinfoCallbacks !== null) {
    glyphinfoCallbacks.push(cb)
    return
  }

  if (glyphinfoCached !== null) {
    window.requestAnimationFrame(() => cb(glyphinfoCached))
    return
  }

  glyphinfoCallbacks = [cb]

  console.log('fetching glyphinfo.json')
  fetch('glyphinfo.json').then(r => r.json()).then(glyphinfo => {
    console.log('loaded glyphinfo.json')
    // { "glyphs": [
    //     [name :string, isEmpty: 1|0, unicode? :string|null,
    //      unicodeName? :string, color? :string|null],
    //     ["A", 0, 65, "LATIN CAPITAL LETTER A", "#dbeaf7"],
    //     ...
    // ]}
    glyphinfoCached = glyphinfo
    cbs = glyphinfoCallbacks
    glyphinfoCallbacks = null
    for (const cb of cbs) {
      cb(glyphinfo)
    }
  })
}


const RepertoireOrderGlyphList = 'gl'
const RepertoireOrderUnicode = 'u'
let repertoireOrder = RepertoireOrderUnicode //RepertoireOrderGlyphList

samples.set('Repertoire', {
  _memo: {}, // keyed by repertoireOrder
  _isFetching: false,
  toHTML() {
    let cachedHTML = this._memo[repertoireOrder]
    if (cachedHTML) {
      return cachedHTML
    }

    getGlyphInfo(glyphinfo => {
      let html = '<div class="glyphlist">'
      let glyphs = glyphinfo.glyphs.filter(g => g[2]) // only include mapped glyphs

      if (repertoireOrder == RepertoireOrderUnicode) {
        glyphs = glyphs.sort((a, b) => parseInt(a[2],16) - parseInt(b[2],16))
      }

      for (const g of glyphs) {
        // let [name, isEmpty, uc, ucName, color] = g
        let name = g[0], isEmpty = g[1], uc = g[2], ucName = g[3], color = g[4]

        let style = ''
        if (color && color != '<derived>') {
          if (color[0] == '#') {
            color = 'rgba(' +
                    parseInt(color.substr(1,2), 16) + ',' +
                    parseInt(color.substr(3,2), 16) + ',' +
                    parseInt(color.substr(5,2), 16) + ',' +
                    '0.2)'
          }
          style += 'style="background-color:' + color + '"'
        }

        if (!ucName) {
          ucName = '[unknown]'
        }

        const title = 'U+' + uc + ' ' + ucName + ' ("' + name + '")'
        html += `<g ${style} title=\'${title}\'>
          <span class="glyph" style="font-feature-settings:normal">&#x${uc};</span>
          <span class="name">${name}</span>
        </g>`
      }

      html += '</div>'

      this._memo[repertoireOrder] = html
      if (sampleVar) {
        sampleVar.refreshValue(null)
      }
    })

    return 'fetching glyph list...'
  },
})


let combs = `ta es ar te ne an as ra la sa al si or ci na er at re ac gh ca ma is za ic ja va zi ce ze se in pa et ri en ti to me ec ol ni os on iz az st ke ka lo el de ro ve pe oz ie gi le ge fo uz us ur ag ah ad ko ez ig eg ak ga da tu ia so ul am it oc av su jo ru rt rf em li uc un io ao he yc gu iu ha og eh ho cn im ny sk aa sc ot ej ku lu nu go ju zo ok be ai ik nc je zn no od ek vy hu do co ed ky vi sl ut pr po aj ow ee mo iv ba mu ib uk ov ep om ym du bo zu cu di ev cj oi vo fa oe hh bh op ck bu ab fe rs ir rz ly il yo mi gj id ys ji ug um ob ns dz qe sn hr ap uh ea rc nt yu ae oj zj ud js fu pu cl vs gg cc hi oh zy ue zd ou ua ry zm of ub oð gl oy au ki kl hl ks yl bi ih ls lg hd zs zl gz tr ið sm ui oo að eb ty ct pi ij yz af uv lk ay rg ya vu ln dl ts ip sv up ht yr sr hm sy uy eo ei nh wa ss gd yv uj nz cs oa wg rt we zb ii if lc uu pl gr by ye sp þa fi zk ef kc yt wl sh zg wo sw hs lt yn dy ax kz zr ps mz jh ng pc cr bc yð eu hy uf lz eq jg zz ox gn ms dh oß cm th lm hq rn yj kr xa yi yk uo zt sj xe yb jc wu vc dr br tc tl my zv gs mc pt gm rl xi hc bl lb ds dn sg bt yp tn cd rd vz vr gb aß nk zc iq aq dc bs rk sb ex yh sd vn vd cv yd zw cb ml sz lp lv sf pn lr ws þo þy ix mr qu mt xo ld ll lw dm cy cp wz rb hb hn bz ch mh hj lh hz uß rm dg gw kt jz aw eð uð oq iþ rh hf mg iw kn fc iy cg vt hw wh hx gc ux cw aæ zf lj nd gt hg py tz kh nr nv vl fh tk oþ gk hk nm xh yf jl pz cf xu þu aþ nb pg yþ dk td jn fl ew gf bn þe gx nn np lf fy zp uq yg dt oæ tt zh jt kv tm ðo fs nj þi cz jd mk mn nl rr rv wi ða fn gy jr kg rp tj tp xy ði ßo æo`

let uniqueChars = new Set(combs.replace(/\s+/g, '').split(''))
combs = combs.split(/\s+/)

let _enWords = null
function getEnglishWords() {
  if (!_enWords) {
    console.log('fetching english words...')
    // words-google-10000-english-usa-no-swears.json source:
    //   https://github.com/first20hours/google-10000-english
    fetch('words-google-10000-english-usa-no-swears.json').then(r => r.json()).then(words => {
      if (_enWords) {
        return
      }
      let combIndex = new Map() // comb => Set{ combWordsHTML }
      console.log(`computing ${words.length} english words and ${words.length * combs.length} combinations...`)
      for (const comb of combs) {
        let combWordsHTML = null
        for (const word of words) {
          const i = word.indexOf(comb)
          if (i != -1) {
            if (!combWordsHTML) {
              combWordsHTML = new Map()
            }
            const head = word.substr(0, i)
            const tail = word.substr(i + comb.length)
            combWordsHTML.set(
              word,
              (head ? `<span class="de-emphasize">${head}</span>` : '') +
              comb +
              (tail ? `<span class="de-emphasize">${tail}</span>` : '')
            )
          }
        }
        if (combWordsHTML) {
          combIndex.set(comb, combWordsHTML)
        }
      }

      _enWords = {words, combIndex}
      console.log('finished fetching & computing english words.', {sampleVar})
      if (sampleVar) {
        sampleVar.refreshValue(null)
      }
    })
  }
  return _enWords
}

function getWordsWithPairs(pairs, maxWordsPerPair) {
  const wmap = getEnglishWords()
  if (!wmap) {
    return null
  }

  const wordSet = new Set()

  if (!maxWordsPerPair) {
    maxWordsPerPair = 10
  } else if (maxWordsPerPair < 1) {
    maxWordsPerPair = 1
  }

  for (const pair of pairs) {
    // s.push('(' + comb + ')')
    const words = wmap.combIndex.get(pair)
    if (words) {
      let n = 0
      for (const word of words.keys()) {
        if (!wordSet.has(word) &&
            (!word.endsWith('s') || // rough approximation for "skip plural-form dups"
             !wordSet.has(word.substr(0, word.length-1))
            )
          )
        {
          wordSet.add(word)
          ++n
          if (n > maxWordsPerPair) {
            break
          }
        }
      }
    }
  }

  // remove duplicates
  for (const word of wordSet) {
    if (word.endsWith('s') && wordSet.has(word.substr(0, word.length-1))) {
      wordSet.delete(word)
    }
  }

  return wordSet
}


samples.set('────── base combos ──────', null)


samples.set('Word mix (combo pairs)', {
  _cachedHTMLResult: null,
  toHTML() {
    if (this._cachedHTMLResult) {
      return this._cachedHTMLResult
    }

    const words = getWordsWithPairs(combs, 10)
    if (!words) {
      return '<em>loading words...</em>'
    }

    // TODO: randomize order, or maybe better to zip on
    // let combs1 = combs.filter(c => c.indexOf(ch) != -1)
    // or sometihng like that

    let s = ''
    for (const w of words) {
      s += w + ' '
    }

    return this._cachedHTMLResult = s
  },
})


for (const ch of uniqueChars) {
  let combs1 = combs.filter(c => c.indexOf(ch) != -1)

  samples.set(ch + ' – words', {
    _cachedHTMLResult: null,
    toHTML() {
      if (this._cachedHTMLResult) {
        return this._cachedHTMLResult
      }

      const words = getWordsWithPairs(combs1, 10)
      if (!words) {
        return '<em>loading words...</em>'
      }

      let s = []
      for (const w of words) {
        s.push(w)
      }

      return this._cachedHTMLResult = s.join(' ')
    },
  })

  samples.set(ch + ' – combinations + words', {
    _cachedHTMLResult: null,
    toHTML() {
      if (this._cachedHTMLResult) {
        return this._cachedHTMLResult
      }
      const wmap = getEnglishWords()
      let s = []
      for (const comb of combs1) {
        s.push(comb)
        if (wmap) {
          const words = wmap.combIndex.get(comb)
          if (words) {
            s.push('<br>')
            for (const wordHTML of words.values()) {
              s.push(wordHTML)
            }
            s.push('<br><br>')
          }
        }
      }
      let html = s.join(' ')
      if (wmap) {
        // only cache value when we have word map
        this._cachedHTMLResult = html
      }
      return html
    }
  })

  samples.set(ch + ' – combinations', {
    _cachedHTMLResult: null,
    toHTML() {
      if (this._cachedHTMLResult) {
        return this._cachedHTMLResult
      }
      let s = []
      for (const comb of combs1) {
        s.push(comb)
      }
      let html = s.join(' ')
      this._cachedHTMLResult = html
      return html
    }
  })

  samples.set(ch + ' – combinations (upper case)', {
    _cachedHTMLResult: null,
    toHTML() {
      if (this._cachedHTMLResult) {
        return this._cachedHTMLResult
      }
      let s = []
      for (const comb of combs1) {
        let p = comb.indexOf(ch)
        if (p == 0) {
          s.push(comb[0].toUpperCase() + comb[1])
        } else if (p == 1) {
          s.push(comb[0] + comb[1].toUpperCase())
        } else {
          s.push(comb)
        }
      }
      let html = s.join(' ')
      this._cachedHTMLResult = html
      return html
    }
  })
}

