Decorative initial (drop cap) fonts, one file per letter, as served by gwern.net
(https://gwern.net/static/css/fonts.css; see gwern.net's style.css, "dropcaps"):

  goudy/    Goudy Initialen        (Dieter Steffmann; freeware)
  yinit/    Yinit                  (Yannis Haralambous, TUGboat 12:1, 1991; distributed with TeX)
  kanzlei/  Kanzlei Initialen      (Dieter Steffmann; freeware)
  de-zs/    Deutsche Zierschrift   (Dieter Steffmann; freeware)

Only the letters this site's chapters open with (D, T, W) are included.
To add a letter, fetch https://gwern.net/static/font/dropcap/<face>/<File>-<LETTER>.ttf
(<File> = GoudyInitialen, Yinit, Kanzlei-Initialen, DeutscheZierschrift) and add an
@font-face rule with its unicode-range in assets/css/style.css.
