# amc2moodle: Conversion from automultiplechoice LaTeX file to moodle XML file.


## How it works

The first conversion step is to convert the LaTeX file into XML file. This is performed by [LaTeXML](https://dlmf.nist.gov/LaTeXML/). Then, other transformations are applied in python with XSLT stylesheet. Most of LaTeX possibilities are supported (equations, tables, graphics, user defined commands). The question can then be imported in the moodle question bank using category tags.

> Examples of supported AMC question are provided in the [test](./test) folder.


## Usage

The conversion can be performed:
  - by running `amc2moodle` command line tool as detailed [here](../../README.md#conversion),
  - or directly from python by importing the package
```
# import subpackage
from amc2moodle.amc2moodle import amc2moodle_class as a2m
# convert to xml
a2m.amc2moodle(fileInput=fileIn,
               fileOutput=fileOut,
               keepFlag=False,
               catname='test_notikz',
               deb=0)
```

### What you can do

Examples of the `amc2moodle` possibilities are given at [QCM.pdf](./test/QCM.pdf)

  -  Convert `question` and `questionmult` environments.
  -  You don't need to remove questionnaires part `\exemplaire` or `\onecopy`. But if this part contains undefined commands, remove/comment it!
  -  Put in-line equations like $x^2$ or use equation environment (or $$ delimiters). For the moment eqnarray  or the amsmath environments multline, align are not supported. The choice have been made to keep equation in tex and use mathjax filter of moodle for rendering. In my opinion, it is better for modifying question after importation.
  -  Include image, in all format supported by `Wand`. `amc2moodle`  will convert it in .png for moodle export. The image will be embedded as text (base64) in the output xml file. The folder is '/' in moodle. The image can be in an another folder than the tex file.
  -  Include Table, with the tabular environment. In the present form, `amc2moodle` put  border around each cell.
  -  Use italic, typewriter, bold, emphasize...
  -  Use enumerate and itemize (but without the tag `\item[tag]`)
  -  Automatically add an answer like *there is no good answer* if there is no good answer.
  -  Like in auto-multiple-choice, all answers are Shuffled by default, you can keep answers ordered by using `\begin{choices}[o]` or `\begin{responses}[o]`.
  -  Use `\AMCnumericChoices` to create numerical question. (This only works with plain numbers, not computed results, and approximate answers are not supported.)
  -  Use user's command defined in the LaTeX file.
  -  Use `\usepackage[utf8]{inputenc}`   for accents
  -  Use packages that are supported by `LaTeXML`. See the list [here](http://dlmf.nist.gov/LaTeXML/manual/included.bindings). Instead you need to add a binding to LaTeXML.
  -  Use `tikz`. `LaTeXML` generates `svg` content, embedded in the question or answer html text.
  -  Use `mhchem` package for chemical equation. Because this package is not yet supported by LaTeXML, the rendering is delegated to `mathjax`. To use it, your moodle admin need to add `mhchem` to the TeX extensions of `mathjax`:
	  ```
	  # !! useful for mhchem only !!
	  # In Administration > Site administration > Plugins > Filters > Mathjax > Local Mathjax installation, edit the Mathjax configuration and add
	  TeX: {extensions: ["AMSmath.js","AMSsymbols.js","mhchem.js","noErrors.js","noUndefined.js"]}
	  ```
	  like here (see [moodle doc](https://docs.moodle.org/38/en/Chemistry_notation_using_mhchem#via_MathJax))
	  ```
	  MathJax.Hub.Config({
		config: ["Accessible.js", "Safe.js"],
		...,
		TeX: {extensions: ["AMSmath.js","AMSsymbols.js","mhchem.js","noErrors.js","noUndefined.js"]}
	  });

	  ```



### What you cannot do

  -  Use underscore in question name field !
  -  Use verbatim. This environment is not supported by `automultiplechoice` 1.0.3. Use `alltt` package instead.
  -  Use font size (easy to add)
  -  Use amsmath environments like align, aligned... Because  `text` attribute of `\elem{equation}`, provided by `LaTeXML` output, doesn't contains really the raw tex equation.
  -  Change border of table
  -  Use command like `\raggedright`, text align is not fully supported. This add align information into the `class` attribute of `\elem{note}` and the string matching break down. Note that `\raggedright` is bypassed.
  -  Usage of `multicol` is bypassed. But it should be possible to use it elsewhere (create newcommand).
  -  Translate equation into mathml, but it can be easily changed
  -  Use AMC numeric with computed results, or open question
  -  Only the main commands of the package `automultiplechoice.sty` are supported in french. The English keywords support is on-going. The list of supported keywords can be seen in `automultiplechoice.sty.ltxml`
  -  You cannot remove the add of "None of these answers are correct" choice at the end of each multiple question.


### Grading strategy
In moodle 3, the grading strategy is different from AMC, especially, for questions with multiple answers. In this case, AMC affects a grade for each checked good answer and each non-checked wrong answer. The total grade of the question depend on the number of choice.

In Moodle, only checked item leads to a grade, positive or negative. The grading is computed in the `convert.py` script.
The default grading parameters are set in the `convert.py` script to
```
# Multiple :: e :incohérence, b: bonne,  m: mauvaise,  p: plancher
amc_bs = {'e':-1,'b':1,'m':-0.5}
amc_bm = {'e':-1,'b':1,'m':-0.5, 'p':-1}
# default question grade in moodle
moo_defautgrade = 1.
```
This value can be changed (as in AMC) with the tex command
```
\baremeDefautS{e=-0.5,b=1,m=-0.5}         % never put b!=1,
\baremeDefautM{e=-0.5,b=1,m=-0.25,p=-0.5} % never put b!=1,
```
or at the question level with the tex command `\bareme`.
The grade `g_i` in % is then computed as
`g_i = 100  c_i / N_i` where `i` stand for the good or the wrong answer. Here, `N_i` is the total number of the good or the wrong answer and `c_i` the coefficient (m, b, ...). It important to set b=1 to get 100% if all the good answers are found. The e parameter is not used here, because it is not possible to tick 2 answers in moodle for one-answer-question. The only case where incoherent can be used is if the ``_there isn't any correct answer_'' answer is ticked with another question but it is not implemented.
For instance if `m=-0.5` and `b=1`, a student who ticks all the wrong answers get -0.5, a student who ticks all the good answer get  1 and student who ticks all the boxes get 0.5.

Another difference is that moodle 3 use tabulated grades like: 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9, 1/10 and their multiple. **If your grade are not conform to that you must use: 'Nearest grade if not listed' in import option in the moodle question bank**. But check at least that the sum of good answer give 100% !



### Categories
By default, the imported questions are all created in `$course$/filein`. When the category flag is used, the AMC command `element` is used to create subcategories and the argument `catname` is used instead of `filein`.
Each question is then placed in `$course$/catname/elementName`.


### Feedback
Feedback are present, in a certain way, in `automuliplechoice` with the `\explain` command. This part is not yet implemented here. However it could be easy to add it at the response or question level as other fields and bypass them for real `automuliplechoice` test.


### Numerical questions
These questions defined in AMC with `\AMCNumericChoices` are converted into `numerical` question in moodle. The target value and its tolerance are preserved. However, exponential notation, bases are not yet supported. Moodle also supports a units in numerical question, but it is not used here. 
For question with floating point operations, **you need to comment `\usepackage{fp}` during the conversion** (required internally by AMC). If you need to realise computation in the question, prefer `\pgfmathparse` that is handled by LaTeXML.


### Open Question
These questions defined in AMC with `\AMCOpen` are converted into `essay` question in moodle. Only information about the number of line is pass to moodle, other option (mostly use for text formating) are skipped.

### Description
Provide a description of a problem that can be common to several questions. It is useful to define notation, pictures, equations. Since, it is not a *real* question, the `choices` environment is not provided. In this case, the question will be converted by `amc2moodle` into moodle `description` question type.
To use it in AMC, do not forget to use `\QuestionIndicative` to tell AMC not to count points for this question (with a 0-point scoring).
> In AMC it is also possible to use `element` content to do share text between questions of the same group, but it will be ignored by `amc2moodle` (too open to parse it).
