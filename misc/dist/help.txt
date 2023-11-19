Installing & using the Inter fonts

Contents:
  1.   Installing font files
  1.1. Installing on Apple macOS
  1.2. Installing on Microsoft Windows
  1.3. Installing on Ubuntu Linux
  2.   Using Inter in Web content
  3.   Hinted TrueType fonts
  4.   Extras
  5.   License (can I use Inter for x?)

File index:
  Inter.ttc           Complete font family "Inter"
  InterVariable*.ttf  Complete font family "Inter Variable"
  web/*               Web fonts and CSS
  extras/             Alternative formats (see "Extras")

---------------------------------------------------------------------

1. Installing font files

  Inter fonts comes in two flavors: Variable and Static
  (InterVariable*.ttf and Inter.ttc, respectively)

  Variable fonts is a new format which allows you to choose any
  weight and optical size. Variable fonts is a relatively new
  technology and may not yet be supported by all your software.
  Inter's variable font is called "Inter Variable" to avoid
  confusion and to allow use alongside the traditional static fonts.

  Static fonts works with older software and uses a fixed set of
  predefined mixtures of weight and optical size. For example
  "Inter Display Medium" is Inter with maximum optical size and a
  weight of 500.

  You will be installing both of these flavors.


1.1. Installing on Apple macOS

  1. Open the "Font Book" application.
  2. In the main menu, select "File" → "Add Fonts..."
  3. Select "Inter.ttc", "InterVariable.ttf" and "InterVariable-Italic.ttf"
  4. Press the "Open" button

  Alternatively, if you prefer not to use Font Book, you can move or
  copy the font files directly into ~/Library/Fonts/


1.2. Installing on Microsoft Windows

  1. Open the zip file you downloaded
  2. Select "Inter.ttc", "InterVariable.ttf" and "InterVariable-Italic.ttf"
  3. Right-click the selected files, choose "Install for all users"

  If you have a previous installation of Inter, you should make sure
  to remove those fonts files before installing new ones. You need to
  install the font for all users, as some software requires fonts to
  be global.


1.3. Installing on Ubuntu Linux

  1. Create a ".fonts" directory in your home. (mkdir -p ~/.fonts)
  2. Copy "Inter.ttc", "InterVariable.ttf" and "InterVariable-Italic.ttf"
     into your .fonts directory (cp Inter.ttc *.ttf ~/.fonts/)

  You may have to restart apps and/or your window server session.

---------------------------------------------------------------------

2. Using Inter in Web content

  1. Copy all woff2 files and the inter.css file from the "Web"
     directory to your web server

  2. Add the following into your HTML <head>:

       <link rel="preconnect" href="https://your-domain/">
       <link rel="stylesheet" href="https://your-domain/inter.css">

     Replace "your-domain" with the actual domain name where you host
     the woff2 font files.

  3. If you are using a CDN, disable any automatic compression for
     the woff2 files (they are already compressed) and set the
     following HTTP headers for the woff2 files:

       Content-Type: font/woff2
       Cache-Control: max-age=31536000

     The CSS contains specific version information in the URLs used
     to load the fonts, so this is safe for upgrading to newer
     versions of Inter.

  4. In your main document's CSS, add the following to use Inter:

       :root { font-family: 'Inter', sans-serif; }
       @supports (font-variation-settings: normal) {
         :root { font-family: 'Inter var', sans-serif; }
       }

  There are many other ways of using Inter on the Web platform.
  The instructions above is simply one way.

  If you prefer to not host the fonts yourself, you can use the
  official Inter CDN, which as a bonus means you are always serving
  the latest version of Inter to your users:

    <link rel="preconnect" href="https://rsms.me/">
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css">

---------------------------------------------------------------------

3. Hinted TrueType fonts

  This distribution contains TrueType fonts with hints in "Inter.ttc"

  Microsoft Windows uses a technology called ClearType which alters
  the shape of letters to increase sharpness, in particular for low-
  density displays. This requires a font to have little programs
  built into them, called TrueType hinting instructions, which lets
  ClearType knows how to alter each character.

  The variable font is currently not available with TrueType hints,
  only the traditional "static" font files are. This will hopefully
  change in a future release.

  Note that the web fonts does not contain hints to minimize file
  size. You can get hinted web fonts from the "extras/woff-hinted"
  directory.

---------------------------------------------------------------------

4. Extras

  The "extras" directory contains some additional "bonus" content:

  otf/          Static font files in CFF format
  ttf/          Static font files with TrueType hints
  woff-hinted/  Web fonts with TrueType hints

---------------------------------------------------------------------

5. License (can I use Inter for x?)

  Inter is a completely free-to-use typeface, including commercial
  use. It is licensed under the SIL Open Font License 1.1, which
  you have received a copy of in the separate file LICENSE.txt

  Here is a brief outline of permissions, limitations and conditions:

    Permissions            Limitations         Conditions
    - Private use          - No liability      - License & copyright
    - Commercial use       - No warranty       - Same license
    - Modification
    - Distribution

  Please read the complete LICENSE.txt carefully!


---------------------------------------------------------------------

Learn more about Inter at https://rsms.me/inter/
