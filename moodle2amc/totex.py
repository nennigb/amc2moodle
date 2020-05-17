#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 22:01:49 2020

@author: bn


stratégie :
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

# TODO :
    - [] feedback
    - [] grading stretegy
    - [] finish html XSLT
    - [] finish structure XSLT
    - [] create quiz object, could be nice, n=can parse quiz or question...
    - [] add Latex compile for check
                    
"""


from lxml import etree
from xml.sax.saxutils import escape, unescape
import base64
import os
import subprocess
from abc import ABC, abstractmethod
from wand.image import Image
import sys

# list of supported moodle question type for
SUPPORTED_QUESTION_TYPE = {'multichoice'}
# possible numerics, open

# possible to use several grading strategy
GRADING_STRATEGY = 'std'  # good/wrong no specific grading


# define path for images files
FIGURES_PATH = "./Figures"
# File type supported by latex (pdflatex), possible to add eps with eps2pdf
# but eps is unusal in web app.
LATEX_EXT = {'.pdf', '.png', '.jpg', '.jpeg'}
# prefered format for non supported img file
LATEX_IMG_OUT ='.png'
# output latex File
LATEX_FILEOUT = 'out.tex'
# xslt file
XSLT_TEXRENDERER = 'struc2tex.xslt'








class Question(ABC):
    """ Define an absract class for all supported questions.
    """
    _xslt_html2tex = 'html2tex.xslt'
    _transform = etree.XSLT(etree.parse(_xslt_html2tex))
    figpath = FIGURES_PATH

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        self.q = q
        self.name = q.find('name/text').text
        self.qtype = None
        self.fileCreated = []
        self.gStrategy = GRADING_STRATEGY
        # save number of svg file per question
        self.svg_id = 0
        # TODO check if fig path exit and create it

    def __repr__(self):
        """ Change string representation.        
        """
        rep =  ("Instance of {} containing the question '{}'."
                .format(self.__class__.__name__, self.name))
        return rep

    def __str__(self):
        """ Change string representation to print the tree.        
        """
        rep = self.__repr__()
        s = unescape(etree.tostring(self.q, pretty_print=True,
                                    encoding='utf8').decode('utf8'))
        return '\n'.join((rep, s))

    @classmethod
    def fromstring(cls, qstring):
        """ Create an instance of QuestionX from a XML string.
        """
        q = etree.fromstring(qstring)
        return cls(q)

    def html2tex(self, cdata_content):
        """ Convert CDATA field into latex text.
        
        Parameter
        ---------
        cdata_content : string
            CDATA protected content that will be parsed.
        
        Return
        ------
        tree_content : etree.Element
            the text content in html store as a etree.

        Remarks
        -------
        <br> are removed (not exml content).
        """
        # remove manually CDATA from the string
        cdata_content = (cdata_content.replace('<text><![CDATA[', '<text>')
                         .replace(']]></text>', '</text>')
                         .replace('\n', '')
                         .replace('<br>', ''))

        parser = etree.HTMLParser(recover=True)
        tree_content = etree.fromstring(unescape(cdata_content), parser)
        self._img_check(tree_content)

        # transform with XSLT into XSLT (tree) for all other element
        xslt_content = self._transform(tree_content)
        # convert to XML (more suitable for search)
        tree_text = etree.XML(etree.tostring(xslt_content,
                              encoding='utf8').decode('utf-8'))

        return tree_text

    def _img_check(self, tree_content):
        """ Change path and check/convert to latex supported image type.
        
        there is 2 steps : i) extract svg, ii) convert file non supported by
        LaTeX

        Parameters
        ----------
        tree_content : etree
            etree arising from cdata parsing.
        """
        # Step 1.
        # Remove embedded svg file (tikz) and convert to img
        for svg in tree_content.findall('.//picture/svg'):
            width = svg.attrib['width']
            filename_svg = os.path.join(self.figpath,
                                        self.name + str(self.svg_id) + '.svg')
            with open(filename_svg, 'w') as f:
                f.write(etree.tostring(svg, encoding='utf8', pretty_print=True)
                        .decode('utf-8'))
            img_svg = etree.Element('img', attrib={'src': filename_svg,
                                                   'width': width})
            #
            svg.getparent().append(img_svg)
            svg.getparent().remove(svg)
            # pricture is the parsed in html2tex

        # Step 2.
        # check that img file are supported by LaTeX
        for img in tree_content.findall('.//img'):
            src = img.attrib['src']
            path, filename = os.path.split(src)
            basename, ext = os.path.splitext(filename)
            # need to be converted
            if ext not in LATEX_EXT:
                im = Image(filename=os.path.join(self.figpath, filename))
                fileout = os.path.join(self.figpath, basename + LATEX_IMG_OUT)
                im.save(filename=fileout)
                im.close()
                src = fileout
            else:
                src = os.path.join(self.figpath, filename)
            # store new path/file
            img.attrib['src'] = src

    def fileExport(self):
        """ Extract embedded data to 'real' file for LaTeX processing.
        """
        # extract all file in the quetsion recurssively
        for file in self.q.findall('.//file'):
            filename = file.attrib['name']
            data = base64.decodebytes(file.text.encode())
            # create directory if needed
            if not os.path.exists(self.figpath):
                os.makedirs(self.figpath)
            # save file
            with open(os.path.join(self.figpath, filename), 'bw') as f:
                f.write(data)
                self.fileCreated.append(filename)


    def question(self):
        """ Get question text.
        """
        # perhaps not so obvious and will require to extract cdata
        cdata_content = etree.tostring(self.q.find('questiontext/text'),
                                       encoding='utf8').decode('utf-8')
        text = self.html2tex(cdata_content)

        return text

    @abstractmethod
    def gettype(self):
        """ Determine the amc question type.
        """
        pass

    @abstractmethod
    def answers(self):
        """ Create and parse answers.
        """
        pass

    def transform(self, catname):
        """ Main routine, applied the xml transformation.
        """
        # initialize
        amcq = etree.Element('question', attrib={'amctype': self.gettype(),
                                                 'category': catname,
                                                 'qname': self.name})
        self.fileExport()
        qtext = self.question()
        amcq.append(qtext)
        choices = self.answers()
        amcq.append(choices)

        return amcq


class QuestionMultichoice(Question):
    """ Multiple choice question (question or questionmult)
    """

    def __init__(self, q):
        """ Init class from an etree Element.
        """
        super().__init__(q)
        self.q = q
        self.qtype = 'multiplechoice'

    def gettype(self,):
        """ Determine the amc question type.
        """
        # test if question or questionmult
        single = self.q.find('single').text
        if single.lower() == 'true':
            amcqtype = 'question'
        elif single.lower() == 'false':
            amcqtype = 'questionmult'
        else:
            print("> Unknwon question type in '{}'".format(self.name))

        return amcqtype

    def answers(self):
        """ Create and parse answers.
        """
        amc_choices =  etree.Element('choices')
        # loop over all answers
        for i, ans in enumerate(self.q.findall('.//answer')):
            # bool use to check if html parsing (CDATA) is needed
            html = ans.attrib['format'].lower() == 'html'
            # TODO how to integrate the scoring aspect
            if self.gStrategy == 'std':
                # the fraction (scoring) field is not allways at the same place
                try:
                    fraction = ans.find('fraction').text
                except:
                    try:
                        fraction = ans.attrib['fraction']
                    except:
                        raise ValueError('fraction not found.')
                if float(fraction) > 0:
                    tag = 'correctchoice'
                else:
                    tag = 'wrongchoice'
            amc_ans = etree.Element(tag, attrib={'order': str(i)})
            if html:
                cdata_content = etree.tostring(ans.find('text'), encoding='utf8').decode('utf-8')
                text = self.html2tex(cdata_content)
                amc_ans.append(text)
            else:
                latex = etree.tostring(ans.find('text'), encoding='utf8').decode('utf-8')
                amc_ans.text = latex
            # store in a list
            amc_choices.append(amc_ans)

        return amc_choices


Q_FACTORY = {'multichoice': QuestionMultichoice}


class Quiz:
    """ Define the quiz class.
    """

    def __init__(self, mdl_xml_file):
        """ Init the quiz from `mdl_xml_file` which can be :
              - a file name/path
              - a file object
              - a file-like object
        """
        parser = etree.XMLParser(encoding='utf-8', strip_cdata=False)
        self.mdl = etree.parse(mdl_xml_file, parser=parser)

    # @classmethod
    # def fromstring(cls, mdl_xml_str):

    def __repr__(self):
            """ Change string representation.        
            """
            rep =  ("Instance of {}."
                    .format(self.__class__.__name__))
            return rep
    
    def __str__(self):
        """ Change string representation to print the tree.        
        """
        rep = self.__repr__()
        s = etree.tostring(self.mdl, pretty_print=True,
                           encoding='utf8').decode('utf8')
        return '\n'.join((rep, s))


    def convert(self, texfile=LATEX_FILEOUT, debug=False):
        """ Convert moodle quiz to LaTeX amc format.  
        
        Parameters
        ----------
        texfile : string, optional
            Ouput latex path/filename. The default is LATEX_FILEOUT.
        debug : bool, optional
            Display additional outputs. The default is False.

        Returns
        -------
        None.

        """
        # convert : convert(to str) converttofile
        amc, cat_list = self._reshape()
        if debug:
            print(etree.tostring(amc, pretty_print=True,
                                 encoding='utf8').decode('utf-8'))
        tex = self.texRendering(amc)
        # remove document root
        tex_str = unescape(etree.tostring(tex, encoding='utf8')
                           .decode('utf-8')
                           .replace('<document>\n', '')
                           .replace('<document>', '')
                           .replace('</document>', ''))
        # Write document to file
        with open(texfile, 'w') as f:
            f.write(tex_str)

    # TODO create a class quiz to encapsulate that
    def _latex_header(self):
        """ Define LaTeX header and newcommand.
        """
    
        header_text =r"""
        \documentclass[a4paper]{article}
        % -------------------------::== package ==::-------------------------------
        \usepackage[utf8]{inputenc}
        \usepackage{alltt}
        \usepackage{multicol}
        \usepackage{amsmath,amssymb}
        \usepackage{color}
        \usepackage{graphicx}
        \usepackage[francais,bloc,completemulti]{automultiplechoice}     % Mandatory for conversion
        \usepackage{tikz}
        \usepackage{hyperref}
        \usepackage{ulem} % strike text
        
        % -----------------------::== newcommand ==::------------------------------
        \newcommand{\feedback}[1]{}    
        \begin{document}
        """
        header = etree.Element('header')
        header.text = header_text
        return header

    def _latex_footer(sel, cat_list):
        """ Define LaTeX footer to populate a amc test from the question bank.
        """
        # store copy operation for all category
        group_list=[]
        exemplaire_text =r"""
        % ============================================================================
        \exemplaire{1}{    	% nombre de sujet différent
    
        % Replace with your Header    
        \vspace*{.5cm}
        \begin{minipage}{.4\linewidth}
            \centering\large\bf Test
        \end{minipage}
        \champnom{\fbox{
            \begin{minipage}{.5\linewidth}
                Nom et prénom :
        
                \vspace*{.5cm}\dotfill
                \vspace*{1mm}
            \end{minipage}
        }}
        
        \begin{center}
          \Large{\textsc{AMC quizz generated from moodle questions}}\\
          \normalsize
        \end{center}
    
        % mélange et catégorie (groupe dans ACM)
        \cleargroup{allquestions}
        """
        enddocument = "\n\\end{document}"
        copy_group = "\\copygroup{%s}{allquestions}\n"
    
        # iterate over cat_list
        for cat in cat_list:
            group_list.append(copy_group % cat)
    
        melange = "\\melangegroupe{allquestions}\n" + \
                  "\\restituegroupe{allquestions}"
    
        footer_text = exemplaire_text + ''.join(group_list) + melange + '\n}' \
            + enddocument
    
        footer = etree.Element('footer')
        footer.text = footer_text
        return footer


    def _reshape(self):
        """ Reshape  moodle XML file into a stucture close to AMC Latex format. 
        
    
        Parameters
        ----------
        root : etre.Element.tree 
            An XML file parse by lxml.etre.
    
        Returns
        -------
        None.
    
        """

        root = self.mdl
        # initial default value for the category name
        catname = 'moodle'
        cat_list = []
    
        # create new etree that will contains new xml suitable for amc.
        # the roots node is document as for a tex file
        amc = etree.Element('document')
    
        # add header
        header = self._latex_header()
        amc.append(header)
    

        # start from quizz
        for question in root.findall('question'): # check if order is conserved
            # get type of Question
            qtype = question.attrib['type']
            # check if question is a category
            if question.attrib['type'] == 'category':
                mdl_catname  = question.find('category/text').text
                # create a simpler catname for amc
                catname = '_'.join(mdl_catname.split('/')[1:])
                # store name and nothing else to do
                cat_list.append(catname)
            else:
                # Standard question
                qname = question.find('name/text').text
                if qtype in SUPPORTED_QUESTION_TYPE:
                        print("> Reshape question '{}' of type '{}'.".format(qname, qtype))
                        amc_q = Q_FACTORY[qtype](question).transform(catname)
                        amc.append(amc_q)
                else:
                    print("> Question '{}' of type '{}' is not supported. Skipping.".format(qname, qtype))
    
        print('done')
    
        # add footer
        footer = self._latex_footer(cat_list)
        amc.append(footer)
    
        return amc, cat_list

    @staticmethod
    def texRendering(amc):
        """ Apply xslt tranformation for final step of tex conversion.
        
        Parameters
        ----------
        amc : etre.Element
            XML structure object describing the .
    
        Returns
        -------
        tex : XSLT results object
            Contain an intermediate state of the conversion process.        
        """
        # create XSLT transformation fonction
        xslt_texrenderer = XSLT_TEXRENDERER
        texrenderer = etree.XSLT(etree.parse(xslt_texrenderer))
        tex = texrenderer(amc)
    
        return tex

    @staticmethod
    def compileLatex(latexFile):
        """ Compile output with pdflatex.
        
        Parameters
        ----------
        latexFile : string
            full name of a latex file.
        """
        command = "pdflatex {}".format(latexFile)
        status = subprocess.run(command.split(),
                                stdout=subprocess.DEVNULL)
        return status


if __name__ == '__main__':

    wdir = '.'
    filein = 'exemple.xml'
    # filein='text.xml'
    fileout = 'out.tex'
    xslt_texrenderer = 'struc2tex.xslt'


    # create a quiz
    quiz = Quiz(os.path.join(wdir, filein))
    # convert it
    latexfile = os.path.join(wdir, fileout)
    quiz.convert(latexfile)
    # test latex compilation
    status = quiz.compileLatex(os.path.join(wdir, fileout))
    if status.returncode != 0:
        print(' > pdflatex encounters Errors...')
        sys.exit(status.returncode)

