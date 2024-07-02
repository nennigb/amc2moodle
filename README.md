# `amc2moodle`
[![pypi release](https://img.shields.io/pypi/v/amc2moodle.svg)](https://pypi.org/project/amc2moodle/) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![CI-Ubuntu](https://github.com/nennigb/amc2moodle/workflows/CI-Ubuntu/badge.svg)  ![CI-Mac-OS](https://github.com/nennigb/amc2moodle/workflows/CI-mac-os/badge.svg)

`amc2moodle`, is a suite of tools to convert multiple choice questionnaires (MCQ)
  - **from** [auto-multiple-choice](https://www.auto-multiple-choice.net) LaTeX quizzes **to** [moodle questions (XML format)](https://docs.moodle.org/38/en/Moodle_XML_format), see details in the [amc2moodle README file](amc2moodle/amc2moodle/README.md). Since `amc2moodle` use [LaTeXML](https://dlmf.nist.gov/LaTeXML/) to **expands LaTeX commands**, it could be _easily_ adapted to support most of LaTeX capabilities.
  - **from** [moodle questions (XML format)](https://docs.moodle.org/38/en/Moodle_XML_format) **to** [auto-multiple-choice](https://www.auto-multiple-choice.net) LaTeX quizzes, see details in the [moodle2amc README file](amc2moodle/moodle2amc/README.md).

The conversion supports equations, tables, figures and standard text formatting.
This software is written in python and in XSLT, thus the conversion step is OS independent. It has been tested for moodle 3.x or 4.x and auto-multiple-choice (v1.0.3-v1.5).

Note that [auto-multiple-choice](https://www.auto-multiple-choice.net) (amc) LaTeX format is very convenient, and can be used for preparing multiple choice questions off-line and avoiding moodle web GUI.


## Installation

A Docker image with `amc2moodle` and its dependencies is available at [ghcr.io/nennigb/amc2moodle](https://ghcr.io/nennigb/amc2moodle).
Once the docker software is installed, this image allows to use `amc2moodle` on **windows plateforms** or to add the resource isolation features on linux or macOS. For more information, see the [`amc2moodle`' docker README](docker/README.md).
To install `amc2moodle` as a python package on linux or macOS platform, follow the steps below.

### Before installing amc2moodle:

  -  install python (version >=3.5)
  -  install `imageMagick`, useful to convert image files (*.eps, *.pdf, ...) into png
      - Ubuntu: `sudo apt-get install imagemagick`
      - MacOS: `brew install imagemagick` (see [`ImageMagick` website](https://imagemagick.org/script/download.php) for more details )
  -  install [`LaTeXML`](http://dlmf.nist.gov/LaTeXML) [tested with version >= 0.8.1] This program does the first step of the conversion into XML
      - Ubuntu: `sudo apt-get install latexml`
      - see also [LaTeXML wiki](https://github.com/brucemiller/LaTeXML/wiki/Installation-Guides) or [install notes](https://dlmf.nist.gov/LaTeXML/get.html) that all the dependencies are installed (perl, latex, imagemagick).
  -  install `xmlindent` [optional]. This program can be used to indent well the XML file
      - Ubuntu: `sudo apt-get install xmlindent`
      - MacOS: not necessary. Script will use `xmllint` natively available on MacOS.

For MacOS users, most dependencies can be installed with `brew` but `LaTeXML` installation can failed for some version. Please see the steps given in the install script [workflow](.github/workflows).


### Install with pip

Run
```
pip install amc2moodle
``` 
pip will download automatically the required files.

or if you have download the sources, run
```
pip install .
```
in the root folder (where `setup.py` is). This will automatically install other dependencies i.e., `lxml`, and `Wand`.
Alternatively, you can run
```
pip install -e .
```
to install it in editable mode, useful if git is used.

Note: for Ubuntu users use `pip3` instead of `pip` for python3.

### Uninstallation
Run 
```
pip uninstall amc2moodle
```

## Conversion
The program can be run in a shell terminal, for instance to convert an **amc LaTeX file to moodle XML**
```
amc2moodle input_Tex_file.tex -o output_file.xml -c catname
```
Help and options can be obtained using
```
amc2moodle -h
```
Then on moodle, go to the course `administration\question bank\import` and choose 'moodle XML format' and tick: **If your grade are not conform to that you must use: 'Nearest grade if not listed' in import option in the moodle question bank** (see below for details).
Examples of the `amc2moodle` possibilities are given at [QCM.pdf](./amc2moodle/amc2moodle/test/QCM.pdf)

If your original exam uses [AMC-TXT syntax](https://www.auto-multiple-choice.net/auto-multiple-choice.en/AMC-TXT.shtml), you must first convert it to LaTeX before feeding it to `amc2moodle`. To convert an AMC-TXT file to LaTeX, generate the exam documents with AMC graphical interface as usual. AMC will generate a LaTeX version of your exam called `DOC-filtered.tex` inside the project directory, which you can pass to `amc2moodle`.

In the same way, conversion from **moodle XML to amc LaTeX file**, run
```
moodle2amc input_XML_file.xml
```
Help and options can be obtained using
```
moodle2amc -h
```
Then the output LaTeX can be edited and included for creating amc exams. Examples of the `moodle2amc` possibilities are given [here](./amc2moodle/moodle2amc/test/moodle-bank-exemple.pdf).



## Troubleshooting
In case of problem, do not hesitate to ask for help on [discussions](https://github.com/nennigb/amc2moodle/discussions) or to create an [issues](https://github.com/nennigb/amc2moodle/issues). Both binaries (`amc2moodle` and `moodle2amc`) write full log in log files based on the name of the input file (`_amc2moodle.log` and `_amc2moodle.log` suffixes are added on these files).
  - 'convert: not authorized..' see ImageMagick policy.xml file see [here](https://stackoverflow.com/questions/52699608/wand-policy-error-error-constitute-c-readimage-412)
  - bugs with tikz-LaTeXML in texlive 2019/2020: please update the following `perl` modules `Parse::RecDescent`, `XML::LibXML` and `XML::LibXSLT` [here](https://github.com/brucemiller/LaTeXML/issues/1279) with `cpan` or `cpanm`in CLI.
  - If LaTeXML doesn't know some LaTeX package and return `Warning:missing_file:package-name Can't find binding for package package-name`, you can try to invoque `amc2moodle` with `--includestyles` flag.

## Related Project
  - [auto-multiple-choice](https://www.auto-multiple-choice.net),  is a piece of software that can help you creating and managing multiple choice questionnaires (MCQ), with automated marking.
  - [TeX2Quiz](https://github.com/hig3/tex2quiz), is a similar project to translate multiple choice quiz into moodle XML, without connection with AMC.
  - [moodle](https://www.ctan.org/pkg/moodle) - Generating Moodle quizzes via LaTeX. A package for writing Moodle quizzes in LaTeX. In addition to typesetting the quizzes for proofreading, the package compiles an XML file to be uploaded to a Moodle server.
  - [moodle-mod-automultiplechoice](https://github.com/UGA-DAPI/moodle-mod-automultiplechoice) - An interface to use AMC within Moodle.
  - [flatex](https://github.com/johnjosephhorton/flatex) - A Python script for "flattening" a nested LaTeX document by pulling in all the \input files. Part of this project has been reused in amc2moodle.
  - [pyexams](https://framagit.org/pang/pyexams),  It allows to eval code inside any jupyter kernel (like Sagemath, sympy, ...) and to export them in the moodle XML format.

## How to contribute ?
If you want to contribute to `amc2moodle`, your are welcomed! Don't hesitate to
  - ask for help or share some tips on [discussions](https://github.com/nennigb/amc2moodle/discussions)
  - report bugs, installation problems on [issues](https://github.com/nennigb/amc2moodle/issues)
  - propose some enhancements in the code or in documentation through **pull requests** (PR)
  - create a moodle plugin for import
  - support new kind of questions
  - add support for other language (French and English are present) in AMC command
  - ...

To ensure code homogeneity among contributors, we use a source-code analyzer (e.g. `pylint`).
Before submitting a PR, run the tests suite.

## License
This file is part of amc2moodle, a tool to convert automultiplechoice quizzes to moodle questions.
amc2moodle is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
amc2moodle is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with amc2moodle.  If not, see <https://www.gnu.org/licenses/>.
