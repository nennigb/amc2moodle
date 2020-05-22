# `amc2moodle`
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/nennigb/amc2moodle?include_prereleases) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![CI-Ubuntu](https://github.com/nennigb/amc2moodle/workflows/CI-Ubuntu/badge.svg)  ![CI-Mac-OS](https://github.com/nennigb/amc2moodle/workflows/CI-mac-os/badge.svg)

`amc2moodle`, is **a tool to convert [automultiplechoice](https://www.auto-multiple-choice.net) quizz (v1.0.3-v1.4) to moodle questions (XML format).**
The automuliplechoice LaTeX format is convenient, and can be used for preparing question and avoiding moodle web gui.



## Installation

### before installing amc2moodle :

  -  install python (version >=3.5)
  -  install `imageMagick`, useful to convert image files (*.eps, *.pdf, ...) into png
      - ubuntu : `sudo apt-get install imagemagick`
      - MacOS: `brew install imagemagick` (see [`ImageMagick` website](https://imagemagick.org/script/download.php) for more details )
  -  install [`LaTeXML`](http://dlmf.nist.gov/LaTeXML) [tested with version 0.8.1] This program does the first step of the conversion into XML
      - ubuntu : `sudo apt-get install latexml`
      - see also [LaTeXML wiki](https://github.com/brucemiller/LaTeXML/wiki/Installation-Guides) or [install notes](https://dlmf.nist.gov/LaTeXML/get.html) that all the dependencies are installed (perl, latex, imagemagick).
  -  install `xmlindent` [optional]. This program can be used to indent well the XML file
      - ubuntu : `sudo apt-get install xmlindent`
      - MacOS: not necessary. Script will use `xmllint` natively available on MacOS.

For MacOS users, most dependencies can be installed with `brew` but `LaTeXML` installation can failed for some version. Please see the steps given in the install script [workflow](.github/workflows).


### Install with pip

Run
```
pip install .
``` 
in the root folder (where `setup.py` is). This will automatically install other dependencies ie `lxml`, `Wand`.
Alternatively, you can run
```
pip install . -e
``` 
to install it in editable mode, usefull if git is used.



Note : for ubuntu users use `pip3` instead of `pip` for python3.

### Uninstallation
Run `pip uninstall amc2moodle`.

## Conversion
The program can be run in a shell terminal,
```
amc2moodle input_Tex_file.tex -o output_file.xml -c catname
```
Help can be obtained using
```
amc2moodle -h
```

Then on moodle, go to the course `administration\question bank\import` and choose 'moodle XML format' and tick : **If your grade are not conform to that you must use : 'Nearest grade if not listed' in import option in the moodle question bank** (see below for details).




## Troubleshooting
In case of problem, do not hesitate to ask help on  [issues](https://github.com/nennigb/amc2moodle/issues)
  - 'convert: not authorized..' see ImageMagick policy.xml file see [here](https://stackoverflow.com/questions/52699608/wand-policy-error-error-constitute-c-readimage-412)

## Related Project
  - [auto-multiple-choice](https://www.auto-multiple-choice.net),  is a piece of software that can help you creating and managing multiple choice questionnaires (MCQ), with automated marking.
  - [TeX2Quiz](https://github.com/hig3/tex2quiz), is a similar project to translate multiple choice quiz into moodle XML, without connexion with AMC.
  - [moodle](https://www.ctan.org/pkg/moodle) - Generating Moodle quizzes via LaTeX. A package for writing Moodle quizzes in LaTeX. In addition to typesetting the quizzes for proofreading, the package compiles an XML file to be uploaded to a Moodle server.

## How to contribute ?
If you want to contribute to `amc2moodle`, your are welcomed! Don't hesitate to
  - report bugs, installation problems or ask questions on [issues](https://github.com/nennigb/amc2moodle/issues)
  - propose some enhancements in the code or in documentation through **pull requests** (PR)
  - create a moodle plugin for import
  - support new kind of questions
  - add support for other language (french and english are present)
  - ...

To ensure code homogeneity among contributors, we use a source-code analyzer (eg. pylint).
Before submitting a PR, run the tests suite.

## License
This file is part of amc2moodle, a tool to convert automultiplechoice quizz to moodle questions.
amc2moodle is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
amc2moodle is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with amc2moodle.  If not, see <https://www.gnu.org/licenses/>.
