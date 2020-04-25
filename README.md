# `amc2moodle`


amc2moodle, **is conversion tool to recast multiple choice quiz written with the LaTeX format used by automuliplechoice 1.0.3 into the moodle XML quiz format.**
The automuliplechoice LaTeX format is convenient and can be used for preparing test and avoiding moodle web gui for multiple choice questions.

## Installation
Run `pip install .` for the root folder (where `setup.py` is).

## Uninstallation
Run `pip uninstall amc2moodle`.

## Basic usage
The program can be run by a shell terminal
`amc2moodle input_Tex_file.tex -o output_file.xml -c catname`
Help can be obtain using
`amc2moodle -h`

Then on moodle, go to the course administration\question bank\import and choose 'moodle XML format'


## Workflow
It is based on [LaTeXML](https://dlmf.nist.gov/LaTeXML/) for a first step conversion of the LaTeX  file into XML. Then a set of transformation is applied in python and with XSLT stylesheet to conform to moodle XML format. Most of LaTeX possibilities are supported (equations, tables, graphics, user defined commands). The question can then be imported in the moodle question bank using category tags.

## Documentation
For more information, installation, usage, dependencies and to see the limitations, please have a look on **amc2moodle.pdf**.

Examples are also provided in the **test** folder.
