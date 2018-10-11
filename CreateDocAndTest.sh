#!/bin/bash
# usefull to generate all the documentation

# create the doc and test pdf file
./amc2moodle.sh -h > ./doc/usage.txt
cd test
pdflatex QCM.tex
cd ../doc
pdflatex  -output-directory=.. amc2moodle.tex 
cd ..

# run amc2moodle on the QCM.tex test
./amc2moodle.sh -i ./test/QCM.tex -o ./test/QCM.xml  -k -c amc

