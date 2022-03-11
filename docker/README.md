### Before installing amc2moodle:

  -  install python (version >=3.5)
  -  install `imageMagick`, useful to convert image files (*.eps, *.pdf, ...) into png
      - Ubuntu: `sudo apt-get install imagemagick`
      - MacOS: `brew install imagemagick` (see [`ImageMagick` website](https://imagemagick.org/script/download.php) for more details )
  -  install [`LaTeXML`](http://dlmf.nist.gov/LaTeXML) [tested with version 0.8.1] This program does the first step of the conversion into XML
      - Ubuntu: `sudo apt-get install latexml`
      - see also [LaTeXML wiki](https://github.com/brucemiller/LaTeXML/wiki/Installation-Guides) or [install notes](https://dlmf.nist.gov/LaTeXML/get.html) that all the dependencies are installed (perl, latex, imagemagick).
  -  install `xmlindent` [optional]. This program can be used to indent well the XML file
      - Ubuntu: `sudo apt-get install xmlindent`
      - MacOS: not necessary. Script will use `xmllint` natively available on MacOS.