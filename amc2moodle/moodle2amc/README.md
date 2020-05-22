# moodle2amc - Conversion from moodle XML file to LaTeX automultiplechoice file

## How it works
    0. ordered the category
    1. parse structure with python, to get unambigious xml file easy to parse 
    with xslt
     - question vs questionmult, check if supported by amc
     - good or wrong answer
     - local barem [optional]
    2. if a text element contains CDATA, run xslt parsing

    open question :  - file inclusion
                         -> store in the question <file> and then called at the
                         good place (the placement is due to a paragraph properties)
                     - in xslt it is possible to add text, see exemple, 
                     but it is stored
                     -  

    The category is indicated at each changement, just keep the last read and split

## What you can do

## What you cannot do
