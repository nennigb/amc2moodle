#!/bin/bash

#    This file is part of amc2moodle, a convertion tool to recast quiz written
#    with the LaTeX format used by automuliplechoice 1.0.3 into the 
#    moodle XML quiz format.
#    Copyright (C) 2016  Benoit Nennig, benoit.nennig@supmeca.fr 

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

 
# path to the python and xslt file. Watchout no space before =
src="/home/bn/Enseignement/Moodle/amc2moodle/src"

# peut-être judicieux de tout faire en python..

# ====================================================================
# init variable
keep=0            # 0: delete temp file, 1: keep temp file
unset filein
unset fileout



# ====================================================================
# function giving usage
function usage() { echo "Usage: $0 input_file [-i input_file  -o output_file -c catname -k -h -s]"; }

usage()
{
cat << EOF


    Usage: \\
    $0 input_Tex_file [-i input_Tex_file \\
                                   -o output_file -c catname -k -h ]

    This script converts a tex file of AMC questions into an xml file
    suitable for moodle import. Only question and questionmult 
    environnement are ready!

    OPTIONS:
       -h      Show this message
       -k      Keep temp file (useful for debuging)
       -i      Input Tex file
       -o      output XML file [default input_file.xml]
       -c      Use \element{label} as category tag as a
               subcategorie root_cat_name
   
EOF
}

remarques()
{
cat << EOF

    File converted. Check below for errors...

    For import into moodle :
    --------------------------------
     - Go to the course admistration\question bank\import
     - Choose 'moodle XML format'
     - In the option chose : 'choose the closest grade if not listed'
       in the 'General option'
       (Moodle used tabulated grades like 1/2, 1/3 etc...)
  .
EOF
}


# function to init the requiered variable
function init() {
    # get absolute name of the input file
    filein=$(readlink -m $OPTARG) # do not check existance!
    # remove the end to get the path
	pathin="${filein%/*}/"
	 # keep basename
	filein="${filein##*/}"
	catname=$filein
    catflag=0
	#fileout=$(basename "$filein") # remove path
	fileout=$filein
	fileout="${fileout%.*}.xml"      #remove extension
	pathout=$pathin
}



# ====================================================================
# Arguments parsing
# Si paramètres optionnels
while getopts ":i:o:c:kh" opt; do
  case $opt in
    
    i) # input file
   	  init      
      ;;
    o) # output file, if not same basemabe
      fileout=$(readlink -m $OPTARG) # do not check existance!
      # remove the end to get the path
	  pathout="${fileout%/*}/"
	  # keep basename
	  fileout="${fileout##*/}"
      ;;
    k) # output file, if not same basemabe
      keep=1
      ;;
    c) # category
      catname=$OPTARG
      catflag=1
      ;;
             
     h) # print help message
      usage
      exit 0
      ;;
      
    \?) # invalid option
      echo "Invalid option. See usage." 
      usage
      exit 1
      ;;
      
  esac
done

# si qu'un seul argument
if [ "$#" = "1" ] ;    then
	echo run with the defaut parameters
	OPTARG=$1
	init
fi

# si rien erreur
if [ -z "$1" ]; then 
	echo Argument missing. See usage.
	usage
	exit 0
fi


# check
echo "Parameters :"
echo "------------------------------------------"
echo " >path input    :"$pathin
echo " >path output   :"$pathout
echo " >file input    :"$filein
echo " >file output   :"$fileout
echo " >keep temp     :"$keep
echo " >use categorie :"$catflag
echo " >catname       :"$catname
#filetemp=$fileout "t"
#echo $filetemp
# ====================================================================
# conversion script call

# appel latexml
filetemp=tex2xml.xml
echo " > Running LateXML conversion... "
latexml --noparse --nocomment --path=$src --dest=$pathout/$filetemp  $pathin/$filein
# appel bareme.py [bareme + transformation + ecriture outpu]
echo " > Running python conversion... "
#echo $src/grading.py $pathin $filetemp $pathout $fileout $keep $catname $catflag
# moche cette longue liste... à changer
python $src/grading.py $pathin $filetemp $pathout $fileout $keep $catname $catflag
# suppression fichiers temp
if [ "$keep" = "0" ]; then 
	echo " > Delete temp file :" $pathout$filetemp
	rm $pathout$filetemp
fi
# pretty indent (not mandatory)
# voir comment améliorer ce qui est fait par lxml!
xmlindent $pathout/$fileout -o $pathout/$fileout
# return exit code !

# print a help message for the importation in moodle
remarques


