# kerndiff

Shows unified diff for kerning pairs in two font files.

Accepts OTF, TTF and UFO fonts.

Synopsis:

```
kerndiff.sh <font1> <font2>
```

Example:

```
kerndiff.sh Inter-Regular-v2.4.otf src/Inter-Regular.ufo
--- Inter-Regular-v2.4.otf  2018-08-30 19:16:47.000000000 -0700
+++ Inter-Regular.ufo       2018-08-30 19:16:47.000000000 -0700
@@ -35126,7 +35081,6 @@
 /s /Ydieresis -149
 /s /Ygrave -149
 /s /Yhook -149
-/s /a 0
+/s /a 8
 /s /afii10026 -47
 /s /b -47
 /s /dagger -29
```
