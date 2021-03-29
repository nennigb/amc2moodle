# moodle2amc : Conversion from moodle XML to auto-multiple-choice LaTeX file

## How it works

The conversion is split into three steps:

  1. Parse moodle XML and recast it to an intermediate XML tree closer to AMC structure, done by `Quiz` class;
  2. Parse each questions, with `QuestionX` class;
     - Extract images files and convert them to image format supported by `pdflatex`
     - Convert all CDATA html fields to LaTeX with xslt style sheet (`html2tex.xslt`)
  3. Convert the global structure into LaTeX with xslt style sheet (`struc2tex.xslt`)

> Examples of supported Moodle question types are provided in the [test](./test) folder.

## Usage

The conversion can be performed 
  - by running `moodle2amc` command line tool as detailed [here](../../README.md#conversion), 
  - or directly from python by importing the package : 
  
```
from amc2moodle.moodle2amc import Quiz

# create a quiz instance, from fileIn (xml file)
quiz = Quiz(fileIn)
# convert it, and store out in fileOut (tex file)
quiz.convert(fileOut)
```

### What you can do

  - Convert **Multichoices** moodle question, with single or multiple answers
  - Convert **Essay** moodle question into `\AMCOpen`
  - Convert **Description** moodle question into AMC question without `choices` and marked as `\QuestionIndicative`
  - Convert **Numerical** moodle question into AMC question. Moodle can handle several targets with a tolerance, but **AMC support only one target with two accuracy levels** : `exact` with a tight tolerance and `approx` with looser tolerance. It means that only one answer will be mapped (see examples). 
  - Convert **CalculatedMulti** moodle question into AMC `question` or `questionmult` using `fp` LaTeX package [latex package](http://mirrors.standaloneinstaller.com/ctan/macros/latex/contrib/fp/documentation.pdf). There are more mathematical built-in functions in [moodle](https://docs.moodle.org/39/en/Calculated_question_type#Available_functions) than in `fp` (see the list in `FP_UNSUPPORTED` defined in `amc2moodle/utils/calculatedParser.py`) especially **base conversion and hyperbolic functions are not yet supported**. **LaTeX variable should contains only chars**, there is no such limitation in moodle, `moodle2amc` will convert your file, but you will need to rename variable to compile your TeX file.   
  - Convert basic html text formating, image, LaTeX equation, embbeded svg and basic table to LaTeX
  - Recover moodle category in your LaTeX file. The _category_ names are map into _groups_, defined with the environnements `\element{}{}`. In AMC _groups_ can be used to pick or randomize questions just like in moodle.
  - Use the output LaTeX file into AMC to finalize your exam or use the joined `automultiplechoice.sty` file to compile AMC draft file
  - Extract all figures imbedded in the moodle XML file or from the moodle question bank.
  - Use `markdown` formating as text format in moodle XML (not tested with images)
  - Tested on moodle 3.x


### What you cannot do

  - Connect AMC to moodle database. Whereas [moodle-mod-automultiplechoice plugin](https://github.com/UGA-DAPI/moodle-mod-automultiplechoice) which is an interface to use AMC within Moodle, `moodle2amc` just convert a moodle XML file obtained after moodle question bank export into AMC LaTeX format. 
  - moodle gift format is **not supported**

### Grading strategy

Currently, the moodle scroring, set for each answer, are not conserved after the conversion and the scoring has to be defined in AMC, only _good/wrong_ answers environnements are used. It is possible to modify that for next version. 
