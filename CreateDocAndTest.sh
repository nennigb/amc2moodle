#!/bin/bash
# usefull to generate all the documentation

# create the doc and test pdf file
./amc2moodle.py -h > ./doc/usage.txt
cd test
latexmk -pdf QCM.tex
cd ../doc
latexmk -pdf  amc2moodle.tex 
cp amc2moodle.pdf ../.
latexmk -pdf -C amc2moodle.tex 
cd ..

# run amc2moodle on the QCM.tex test
./amc2moodle.py ./test/QCM_wo-tikz.tex -o ./test/QCM.xml  -k -c amc

