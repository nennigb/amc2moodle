# -*- coding: utf-8 -*-
"""
    This file is part of amc2moodle, a convertion tool to recast quiz written
    with the LaTeX format used by automuliplechoice 1.0.3 into the
    moodle XML quiz format.
    Copyright (C) 2016  Benoit Nennig, benoit.nennig@supmeca.fr

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import sys
from abc import ABC, abstractmethod
from lxml import etree
import base64
import os
from wand.image import Image as wandImage
from xml.sax.saxutils import unescape
from ..utils.calculatedParser import *
import random

# Define default and global
SUPPORTED_Q_TYPE = ('amc_questionmult', 'amc_question', 'amc_questionnumeric',
                    'amc_questionopen', 'amc_questiondescription',
                    'amc_questioncalcmult', 'amc_questionmultcalcmult')

DEFAULT_IMG_RESOLUTION = 100
# Dictionnary containing all used options. May be overwritten in Quiz or in Questions.
# When overwritten, it becomes a string. Need to be carfull when use them.
DEFAULT_OPTS = {# Set defaut relative tolerance for float in numerical question to 1%
                'default_numeric_tol': 1e-2,
                # Shuffle all answsers
                'shuffle_all': True,
                # The way used by Moodle ways to number answers. Moodle default is'abc'.
                # Other supported tags are {'123', 'abc', 'iii', 'none', 'ABCD'}.
                'answer_numbering_format': 'abc',
                # Add `amc_aucune` if required
                'amc_autocomplete': 1,
                # String for
                'amc_aucune': u"aucune de ces réponses n'est correcte.",

                # **Scoring see AMC doc**
                # Simple : e :incohérence, b: bonne,  m: mauvaise,  p: planché
                'amc_bs': {'e': -1, 'b': 1, 'm': -0.5},
                # Multiple : e :incohérence, b: bonne,  m: mauvaise,  p: planché
                'amc_bm': {'e': -1, 'b': 1, 'm': -0.5, 'p': -1},
                # Moodle default value for question grade.
                'moo_default_grade': 1.,

                # Default size for image ²
                'default_img_width': '200pt',
                'default_img_resolution': DEFAULT_IMG_RESOLUTION,

                # **Calculated**
                # Define the default parser (use `fp` in tex file)
                'calculated_default_parser': 'fp2xml',
                # Number of decimal in random value
                'calculated_default_decimal_number': 3,
                # Number of random value for each wildcards
                'calculated_default_item_number': 5,
                # Answer formatting and tolerance
                'calculated_tolerancetype': 1,
                'calculated_tolerance': 0.01,
                'calculated_correctanswerformat': 1,
                'calculated_correctanswerlength': 2,
                }


# ======================================================================
# Utilities
# ======================================================================
def strtobool(s):
    """ Convert a string into boolean value if needed.
    """
    if isinstance(s, bool):
        return s
    elif isinstance(s, str):
        return s.lower() in ("yes", "true", "t", "1")
    else:
        raise ValueError("The argument '{}' must be a string or a boolean.".format(s))


def basename(s):
    """ Return basename (without extension) from a path s.
    """
    name = os.path.splitext(os.path.basename(s))[0]
    return name


class ImageCustom:
    """ Create an Image class to create a common interface for Image libs.

    For simplicity, this class support only wand. See python-refactor branch
    to see the previous interface

    TODO : create to abstract class to define the common interface.
    """

    def __init__(self, fileIn=None, fileOut=None,
                 resolution=DEFAULT_OPTS['default_img_resolution']):
        """ Initialize the class.

        Parameters
        ----------
        fileIn : string.
            The full input file name.
        fileOut : string.
            The full output file name.
        resolution : int, optional
            The resolution used in image convertion.
        """
        if fileIn is not None and fileOut is not None:
            self.convertImage(fileIn, fileOut, resolution)

    def convertImage(self, fileIn, fileOut, resolution):
        """ Image conversion with wand.
        """
        im = wandImage(filename=fileIn, resolution=resolution)
        # remove timestamp from png (keep checksum unchanged for test)
        im.artifacts['png:exclude-chunks'] = 'date,time'
        im.strip()
        # for (k, v) in im.artifacts.items():
        #     print(k, v)
        print("   Conversion from {} to {} (imgResolution={}).".format(
                                                    os.path.splitext(fileIn)[1],
                                                    os.path.splitext(fileOut)[1],
                                                    resolution))
        im.save(filename=fileOut)
        im.close()


def encodeImg(Ii, pathin, pathout, resolution=DEFAULT_OPTS['default_img_resolution']):
    """ Convert image to png and encode it in base64 text.

    Parameters
    ----------
    Ii : element tree
        The xml element containing the image information (path, ...). This
        element is modified.
    pathin, pathout : string
        the input and output path
    resolution : Int
        The resolution used in image convertion.
    """

    ext = Ii.attrib['ext']
    img_name = Ii.attrib['name']
    pathF = Ii.attrib['pathF']

    # si ce n'est pas du png on converti en png
    if (Ii.attrib['ext'] != 'png'):
        # im = Image(pathF+ img_name +'.' + ext)
        img_name_in = img_name + '.' + ext
        img_name_out = img_name + ".png"
        # im.write(pathF + img_name)
        img_path = os.path.join(pathout, img_name_out)
        im = ImageCustom(os.path.join(pathF, img_name_in),
                         img_path, resolution)
    else:
        img_name_out = Ii.attrib['name'] + '.' + ext
        img_path = os.path.join(pathF, img_name_out)

    # print(Ii.attrib['ext'])
    # print(pathF)
    img_file = open(img_path, "rb")
    Ii.attrib.update({'name': img_name_out, 'path': '/',
                      'encoding': "base64",
                      'pathF': ''})   # remove path question
    # Ensure same order at all execution
    # https://lxml.de/FAQ.html#how-can-i-sort-the-attributes
    attrib = Ii.attrib
    if len(attrib) > 1:
        attributes = sorted(attrib.items())
        attrib.clear()
        attrib.update(attributes)
    # Embbed image
    Ii.text = base64.b64encode(img_file.read())
    img_file.close()


class AMCQuestion(ABC):
    """ Abstract class for all questions.
    """

    def __init__(self, Qi, context):
        """ Init class from an etree Element amc_question*.
        """
        self.Qi = Qi
        self.name = Qi.find('name/text').text
        self.context = context
        self.options = context.options.copy()

    def __repr__(self):
        """ Change string representation.
        """
        rep = ("Instance of {} containing the question '{}'."
               .format(self.__class__.__name__, self.name))
        return rep

    def __str__(self):
        """ Change string representation to print the tree.
        """
        rep = self.__repr__()
        s = unescape(etree.tostring(self.Qi, pretty_print=True,
                                    encoding='utf8').decode('utf8'))
        return '\n'.join((rep, s))

    def _encodeImg(self):
        """ Encode all images present in the question (question and answers).
        """
        # inclusion des images dans les questions & réponses
        Ilist = self.Qi.xpath(".//file")
        for Ii in Ilist:
            Ii = encodeImg(Ii, self.context.pathin, self.context.wdir,
                           int(self._setWithOptionsOrDefault('imgResolution',
                                                             'default_img_resolution')))

    @abstractmethod
    def _scoring(self):
        pass

    def _options(self):
        """ Look for amc_options elements and store them in options.
        """
        Qi = self.Qi
        optlist = Qi.xpath(".//options")

        for opt in optlist:
            # the option name is in 'name' atrtibute
            self.options[opt.attrib['name']] = opt.text
            opt.getparent().remove(opt)
            print("   Modified options '{}' to '{}'".format(opt.attrib['name'],
                                                            self.options[opt.attrib['name']]))

    def _setWithOptionsOrDefault(self, opt_name, default_value):
        """ Set an option to its value if provided, else use default value.

        Some internal option name `default_value` are too long and for backward compatibility
        the api option name `opt_name` are not always the same.
        This function allow to create the local mapping.
        """
        if opt_name in self.options.keys():
            return self.options[opt_name]
        else:
            return self.options[default_value]

    def convert(self):
        """ Run all questions convertion steps.
        """
        print(" * processing {} question '{}'...".format(self.__class__.__name__, self.name))
        self._options()
        self._encodeImg()
        self._scoring()


class AMCQuestionSimple(AMCQuestion):
    """ Multiple choice question with single good answer.
    """

    def _options(self):
        """ Manage options at question levels.
        """
        # Call generic options search
        super()._options()
        Qi = self.Qi
        # check local shuffle policy
        Qiwantshuffle = strtobool(self.options['shuffle_all'])
        optlist = Qi.xpath("./note[@class='amc_choices_options']")
        if optlist and 'o' in optlist[0].text.strip().split(","):
            Qiwantshuffle = False
            print("   Keep choices order in question '{}'.".format(self.name))
        etree.SubElement(Qi, "shuffleanswers").text = str(Qiwantshuffle).lower()

        # store local answernumbering policy
        etree.SubElement(Qi, "answernumbering").text = self.options['answer_numbering_format']

    def _scoring(self):
        """ Compute the scoring.
        """
        Qi = self.Qi
        # specific part scoring part
        # add  <defaultgrade>1.0000000</defaultgrade>
        etree.SubElement(Qi, "defaultgrade").text = str(self.options['moo_default_grade'])
        # add <single>true</single>
        etree.SubElement(Qi, "single").text = 'true'
        # est qu'il y a une bareme local cherche dans les child
        # e:incohérente is pointless in moodle since it is not possible to chose several answer
        # barl = Qi.xpath("./text[@class='amc_bareme']")
        barl = Qi.xpath("bareme")
        # Par défaut on a le bareme global
        amc_bl = self.context.amc_bs.copy()
        # si il y a une bareme local, on prend celui-la
        if len(barl) > 0:
            amc_bl_=dict(item.split("=") for item in barl[0].text.strip().split(","))
            amc_bl.update(amc_bl_)
            print("   local scoring:", amc_bl)
            if (float(amc_bl['b']) < 1.):
                print("WARNING : the grade of the good answser(s) may be < 100%, put b=1")

        # bonne cherche dans les child
        Rlist = Qi.xpath("./*[starts-with(@class, 'amc_bonne')]")
        for Ri in Rlist:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bl['b'])*100.)

        # Mauvaise cherche dans les child
        Rlist = Qi.xpath("./*[starts-with(@class, 'amc_mauvaise')]")
        for Ri in Rlist:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bl['m'])*100.)


class AMCQuestionMult(AMCQuestionSimple):
    """ Multiple choice question with multiple good answers.
    """

    def _scoring(self):
        """ Compute the scoring.
        """
        Qi = self.Qi
        # specific part scoring part
        # add  <defaultgrade>1.0000000</defaultgrade>
        etree.SubElement(Qi, "defaultgrade").text = str(self.options['moo_default_grade'])
        # add <single>false</single>
        etree.SubElement(Qi, "single").text = 'false'
        # est qu'il y a une bareme local cherche dans les child
        # barl = Qi.xpath("./text[@class='amc_bareme']")
        # barl = Qi.xpath("./*[@class='amc_bareme']")
        barl = Qi.xpath("bareme")
        # Par défaut on a le bareme global
        amc_bml = self.context.amc_bm.copy()
        # si il y a une bareme local, on prend celui-la
        if len(barl) > 0:
            # TODO see if amc_bml.update(...) is more robust if only
            # partial scoring is provided
            amc_bml_ = dict(item.split("=") for item in barl[0].text.strip().split(","))
            amc_bml.update(amc_bml_)
            print("   local scoring :", amc_bml)
            if (float(amc_bml['b']) < 1):
                print("WARNING : the grade of the good answser(s) may be < 100%, put b=1")

        # on compte le nombre de réponse NR
        # Rlistb = Qi.xpath("./text[@class='amc_bonne']")
        Rlistb = Qi.xpath("./*[starts-with(@class, 'amc_bonne')]")
        NRb = len(Rlistb)

        # Rlistm = Qi.xpath("./text[@class='amc_mauvaise']")
        Rlistm = Qi.xpath("./*[starts-with(@class, 'amc_mauvaise')]")
        NRm = len(Rlistm)

        # =====================================================================
        # Ajouter les réponses "aucune réponse"
        # Si déjà une bonne réponse on en ajoute une mauvaise
        if ((int(self.options['amc_autocomplete']) == 1) & (NRb > 0)):
            aucune = etree.SubElement(Qi, 'note',
                                      attrib={'class': 'amc_mauvaise'})
            aucunec = etree.SubElement(aucune, 'note')
            aucunec.text = self.options['amc_aucune']
            NRm += 1
            Rlistm.append(aucune)

        # Si pas de bonne on en ajoute une bonne
        if ((int(self.options['amc_autocomplete']) == 1) & (NRb == 0)):
            aucune = etree.SubElement(Qi, 'note',
                                      attrib={'class': 'amc_bonne'})
            aucunec = etree.SubElement(aucune, 'note')
            aucunec.text = self.options['amc_aucune']
            NRb += 1
            Rlistb.append(aucune)

        # =====================================================================
        # ajout d'un champ fraction au reponse
        # bonne cherche dans les Qi childs
        for Ri in Rlistb:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bml['b'])*100./NRb)

        # Mauvaise cherche dans les Qi childs
        for Ri in Rlistm:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bml['m'])*100./NRm)



class AMCQuestionNumeric(AMCQuestion):
    """ Convert amc numeric question into moodle numeric questions.

    Remarks
    -------
    Exponential, base notation are not yet supported.
    """

    def _options(self):
        pass

    @staticmethod
    def _addanswer(Qi, fraction, target, tol):
        """ Add numeric answer from fraction, tageted value and tolerance.
        """
        answer = etree.SubElement(Qi, "answer", attrib={'fraction': str(fraction),
                                                        'format': "moodle_auto_format"})
        etree.SubElement(answer, "text").text = str(target)
        etree.SubElement(answer, "tolerance").text = str(tol)

    def _scoring(self):
        """ Compute the scoring.
        """
        Qi = self.Qi
        num_choices = Qi.find(".//note[@class='amc_numeric_choices']")
        opts_string = num_choices.attrib['role'].split(',')
        # define the default parameters used by AMC
        opts = {'exact': 0, 'approx': 0, 'decimals': 0, 'digits': 3,
                'scoreapprox': 1, 'scoreexact': 2}
        # update it with the picked values
        for pair in opts_string:
            key, val = pair.split('=')
            opts.update({key.strip(): val.strip()})

        # Define the tolerance
        # Par exemple, si decimals=2, si la bonne valeur est 3,14 et si la
        # valeur saisie est 3,2 alors la différence entière calculée
        # est 320-314=6, de sorte que les points scoreapprox ne sont acquis que
        # si approx vaut 6 ou plus.
        target = float(num_choices.text)

        dec = int(opts['decimals'])
        tol = float(opts['exact']) / 10**dec

        # if no tolerance specified and float answer, add default tol
        if not(target.is_integer()) and tol == 0:
            tol = float(self.options['default_numeric_tol']) * target

        # good answers [x-tol; x+tol] -> scoreexact/scoreexact
        self._addanswer(Qi, 100, target , tol)

        # if approx, create partially good answers
        if float(opts['approx']) > 0:
            tola = float(opts['approx']) / 10**dec
            if tol > tola:
                print("Warning the 'approx' bound is tighter than the 'exact' bound")
            scoreapprox = 100*float(opts['scoreapprox'])/float(opts['scoreexact'])
            # [x + tol, x + tola] -> scoreexact/scoreexact
            self._addanswer(Qi, scoreapprox, target + tol + (tola-tol)/2, (tola-tol)/2)
            # [x - tola, x - tol] -> scoreapprox/scoreexact
            self._addanswer(Qi, scoreapprox, target - tol - (tola-tol)/2, (tola-tol)/2)


class AMCQuestionOpen(AMCQuestion):
    """ Convert amc open question into moodle essay questions.
    """

    def _options(self):
        """ Parse options and create the required elements.
        """
        Qi = self.Qi
        amc_open = Qi.find(".//note[@class='amc_open']")
        opts_string = amc_open.attrib['role'].split(',')
        # define the default parameters used by AMC
        opts = {'lines': 3}
        # update it with the picked values
        for pair in opts_string:
            key, val = pair.split('=')
            opts.update({key.strip(): val.strip()})
        etree.SubElement(Qi, "responsefieldlines").text = str(opts['lines'])

    def _scoring(self):
        """ Compute the scoring.
        """
        Qi = self.Qi
        # add  <defaultgrade>1.0000000</defaultgrade>
        etree.SubElement(Qi, "defaultgrade").text = str(self.options['moo_default_grade'])


class AMCQuestionDescription(AMCQuestion):
    """ Convert amc question without answer into moodle description questions.

    No specific thing to define here.
    """

    def _options(self):
        """ Parse options and create the required elements.
        """
        pass

    def _scoring(self):
        """ Compute the scoring.
        """
        pass


class _Calculated:
    """ Customization class for Parametrized Multiple choice question.

    Connot be instanciated, must be used with Mixins
    """

    def _parsemath(self):
        """ Parse FP expression and convert them to moodle XML.

        Returns
        -------
        wildcards : set
            The set of all encournters random variables to create the datasets.
        """
        Qi = self.Qi
        # parse fp expressions
        parser = CreateCalculatedParser(self.options['calculated_default_parser'])
        for orig_text in Qi.xpath(".//questiontext/note|.//note[@class='amc_bonne']/note|.//note[@class='amc_mauvaise']/note"):
            rawtext = (etree.tostring(orig_text, encoding='utf8')
                            .decode('utf-8')
                            .replace('<note>', '')
                            .replace('</note>', '')
                            .replace(r'\n', ''))
            # parse question
            parsed_text = parser.render(rawtext)
            # questiontext.getparent().remove(questiontext)
            orig_text.clear()

            # FIXME this manipulation reveals a problem in the management of CDATA
            # fields created in transform2html. Since the orig_text.text contains only a part
            # of CDATA tag '<![CDATA[\n    '
            # this markup is ignored and transform.xslt process normally the elements
            # see orig_text.getchildren()[0]
            # XSLT transform remove CDATA

            # To protect them from xslt rename into
            orig_text.tag = 'text'
            # `cdata` element are marked in transform.xslt <xsl:output> as
            # cdata-section-elements="cdata" and CDATA are added in the output
            # now need to remove `cdata` elements at the end of the conversion
            cdata = etree.fromstring('<cdata>' + parsed_text + '</cdata>',
                                    etree.XMLParser(strip_cdata=False))
            orig_text.append(cdata)


            # orig_text.text = etree.CDATA(parsed_text)  # doesn't work ??!!
            # Change behavior to avoid lxml unescape chars
            # orig_text.text = etree.CDATA(parsed_text.replace('<![CDATA[', '')
            #                                         .replace(']]>', ''))
            # orig_text.text = etree.fromstring(parsed_text)
            # etree.dump(Qi)
        return parser.wildcards


    def _addAnswerFields(self):
        """ Add calcultaed question specific fields to all answers.
        """
        Qi = self.Qi
        # add them to each answer good or wrong
        for ans in Qi.xpath(".//note[@class='amc_bonne']|.//note[@class='amc_mauvaise']"):
            tolerance = etree.Element('tolerance')
            tolerance.text = str(self.options['calculated_tolerance'])

            tolerancetype = etree.Element('tolerancetype')
            tolerancetype.text = str(self.options['calculated_tolerancetype'])

            correctanswerformat = etree.Element('correctanswerformat')
            correctanswerformat.text = str(self.options['calculated_correctanswerformat'])

            correctanswerlength = etree.Element('correctanswerlength')
            correctanswerlength.text = str(self.options['calculated_correctanswerlength'])

            fields = [tolerance, tolerancetype, correctanswerformat,
                      correctanswerlength]

            ans.extend(fields)

    def _datasets(self, wildcards):
        """ Create data set from wildcard uniformly distributed between [0, 1].

        Parameters
        ----------
        wildcards : set
            The set of all encournters random variables to create the datasets.
        """

        # initialize data global container
        dataset_definitions = etree.Element('dataset_definitions')
        for wildcard in wildcards:
            # initialize data container for each wildcard
            data = etree.SubElement(dataset_definitions, 'dataset_definition')
            # create all subelements
            status = self._SubElement_text(data, 'status', 'private')
            name = self._SubElement_text(data, 'name', wildcard)
            indextype = etree.SubElement(data, 'type')
            indextype.text = 'calculatedsimple'

            # Set all random distirbution parameters
            # in fp all random parameters are defined between 0 and 1
            distribution = self._SubElement_text(data, 'distribution', 'uniform')
            minimum = self._SubElement_text(data, 'minimum', '0')
            maximum = self._SubElement_text(data, 'maximum', '1')
            # Decimal number
            decimal_number = int(self._setWithOptionsOrDefault('decimalNumber',
                                                               'calculated_default_decimal_number'))
            decimals = self._SubElement_text(data, 'decimals', str(decimal_number))
            # nitems in the dataset
            nitems = int(self._setWithOptionsOrDefault('nitems',
                                                       'calculated_default_item_number'))
            itemcount = etree.SubElement(data, 'itemcount')
            itemcount.text = str(nitems)
            number_of_items = etree.SubElement(data, 'number_of_items')
            number_of_items.text = str(nitems)
            # set container for all random values
            dataset_items = etree.SubElement(data, 'dataset_items')
            for i in range(0, nitems):
                # set container for each random value
                dataset_item =  etree.SubElement(dataset_items, 'dataset_item')
                number =  etree.SubElement(dataset_item, 'number')
                # moodle indexes start at 1
                number.text = str(i+1)
                value =  etree.SubElement(dataset_item, 'value')
                rand = random.uniform(0, 1)
                # limit the number of digits
                rand = round(rand, decimal_number)
                value.text = str(rand)

        self.Qi.append(dataset_definitions)

    @staticmethod
    def _SubElement_text(parent, name, value):
        """ Create a subelement with a text element to store data.

        Parameters
        ----------
        parent : etree
            The parent of the element to create.
        name : string
            name of the element.
        value : string
            the value store in <text>.

        Returns
        -------
        se : etre
            The subelement.
        """
        se = etree.SubElement(parent, name)
        etree.SubElement(se, 'text').text = value
        return se

    def _scoring(self):
        """ Compute the scoring.
        """
        # and call AMCQuestionSimple scoring method
        super()._scoring()
        # parse fp expressions
        wildcards = self._parsemath()
        print('   Found {} wildcards.'.format(len(wildcards)))
        # TODO add a test to check that all wildcards starts with rand!
        # to control substitution
        # Add calcultaed question specific fields to all answers.
        self._addAnswerFields()
        # create the dataset
        self._datasets(wildcards)


class AMCQuestionCalcMult(_Calculated, AMCQuestionSimple):
    """ Parametrized Multiple choice question with single good answer.
    """
    pass


class AMCQuestionMultCalcMult(_Calculated, AMCQuestionMult):
    """ Parametrized Multiple choice question with multiple good answers.
    """
    pass


# dict of all available question
Q_FACTORY = {'amc_questionmult': AMCQuestionMult,
             'amc_question': AMCQuestionSimple,
             'amc_questionnumeric': AMCQuestionNumeric,
             'amc_questionopen': AMCQuestionOpen,
             'amc_questiondescription': AMCQuestionDescription,
             'amc_questioncalcmult': AMCQuestionCalcMult,
             'amc_questionmultcalcmult': AMCQuestionMultCalcMult}


def CreateQuestion(qtype, Qi, context):
    """ Factory function for creating the Questions* objects.

    Parameters
    ----------
    qtype : string
        the moodle name of the question type.
    Qi : etree.Element
        The XML tree of the considered question.
    context : Context
        The environnement variable.

    Returns
    -------
    Instance of concrete Questions class.

    """

    try:
        return Q_FACTORY[qtype](Qi, context)
    except NameError:
        raise KeyError(" 'qtype' argument should be in {}".format(Q_FACTORY.keys()))


class Context():
    """ Contains the context of the quizz, like path, default options.

    Basically it will contains all information callected at quiz level but
    required in the question processing.

        may be created by a AMCQuiz method...
    """

    def __init__(self, pathin, wdir, amc_bs, amc_bm, **options):
        """ Init the class with mandatory options and other optional parameter.
        """
        # mandatory parameters
        self.pathin = pathin
        self.wdir = wdir
        self.amc_bs = amc_bs
        self.amc_bm = amc_bm
        # encapsulate other options
        self.__dict__.update(options)

    def __str__(self):
        """ Change string representation.
        """
        options = self.__dict__.__str__()

        return "The context state is " + options


class AMCQuiz:
    """ Class to handle conversion from XML file obtain with LaTeXML
    to moodle XML.

    - Call XSLT stylesheet and complete the required XML element,
    - Compute the grade according to the amc way
    - Convert non png img into png and embedded them in the output_file

    Remark : The grade are not computed exactly as in AMC, see the doc.

    Parameters
    ----------
    pathin : string
        Input directory.
    wdir : string
        Allow to define a working directory (temp) different from the output
        directiory.
    catname : string
        Set moodle category
    deb : int, optional
        Set to 1 to store all intermediate files for debugging.
        The default is 0.
    """

    # path to xslt stylesheet
    # 1. remove namespace
    filexslt_ns = os.path.join(os.path.dirname(__file__),
                               "transform_ns.xslt")
    # 2. rename AMC question to their moodle counter part
    filexslt_qtype = os.path.join(os.path.dirname(__file__),
                                  "transform_qtype.xslt")
    # 3. convert to html, tab, figure, equations
    filexslt_pre = os.path.join(os.path.dirname(__file__),
                                "transform2html.xslt")
    # 4. remane element and finish the job
    filexslt = os.path.join(os.path.dirname(__file__),
                            "transform.xslt")

    def __init__(self, xml, pathin, wdir, catname, deb=0):
        """ Init class from an etree Element.
        """
        self.xml = xml
        self.pathin = pathin
        self.wdir = wdir
        self.deb = deb

        # Set default options
        self.options = DEFAULT_OPTS

        # default scroring
        self.amc_bs = self.options['amc_bs']
        self.amc_bm = self.options['amc_bm']

        # store total number of question
        self.Qtot = 0

        # Define catflag [legacy]
        self.catflag = catname is not None
        self.catname = catname

        # tempFile
        self.tempfile_id = 0
        self.tempBaseName = 'temp_'


    def __repr__(self):
        """ Change string representation.
        """
        rep = ("Instance of {}. {} have be converted."
               .format(self.__class__.__name__, self.Qtot))
        return rep

    def __str__(self):
        """ Change string representation to print the tree.
        """
        rep = self.__repr__()
        s = unescape(etree.tostring(self.tree, pretty_print=True,
                                    encoding='utf8').decode('utf8'))
        return '\n'.join((rep, s))

    def toMoodle(self, fileout):
        """ Run AMC to moodle XML conversion and save it in fileout.
        """

        # Run preprocessing
        self._preProcessing()
        # Process graphics
        self._graphics()

        # Reshape, text formating, math, image, tableau
        transform_pre = etree.XSLT(etree.parse(self.filexslt_pre))
        # apply XSLT transformation
        self.tree = transform_pre(self.tree)
        if (self.deb == 1):
            # ecriture
            self.tree.write(self._tempfile(), pretty_print=True, encoding="utf-8")

        # Parse Quiz level options
        self._options()

        # Parse quiz level scorings
        self._scoring()

        #  Convert element to categories
        self._categories()

        # Convert all supported question type
        self._convertQuestions()

        # Ecriture fichier output intermediaire
        if (self.deb == 1):
            self.tree.write(self._tempfile(), pretty_print=True, encoding="utf-8")

        # Reformatage à partir de xslt
        transform = etree.XSLT(etree.parse(self.filexslt))
        # apply XSLT transformation
        self.tree = transform(self.tree)

        # Need to remove `cdata` elements introduced in calculated question
        for cdata in self.tree.findall('.//text/cdata'):
            # copy `cdata` content on CDATA in `text`
            cdata.getparent().text = etree.CDATA(cdata.text)
            # Remove the now useless `cdata` element
            cdata.getparent().remove(cdata)

        # Save output
        s = etree.tostring(self.tree, pretty_print=True, encoding="utf-8").decode('utf-8')
        if (self.deb == 1):
            print(etree.tostring(self.tree, pretty_print=True, encoding="utf-8"))
        with open(fileout, 'w') as f:
            f.write(s)

        # summary
        print('\n')
        print(" > global 'shuffleanswers' is {}.".format(strtobool(self.options['shuffle_all'])))
        print(" > global 'answerNumberingFormat' is '{}'.".format(self.options['answer_numbering_format']))
        print(" > {} questions converted...".format(self.Qtot))


    def _preProcessing(self):
        """ Clean up input file and create the tree.
        """

        # Parse the input xml file
        # the default behavior is to strip CDATA to avoid it, use
        # parser = etree.XMLParser(strip_cdata=False)
        # tree = etree.parse(self.xml, parser)
        tree = etree.parse(self.xml)

        # remove namespace
        # TODO a terme faire autrement
        transform_ns = etree.XSLT(etree.parse(self.filexslt_ns))
        # applique transformation
        tree = transform_ns(tree)
        # store ouput for debug
        if (self.deb == 1):
            tree.write(self._tempfile(), pretty_print=True, encoding="utf-8")

        # rename generic AMC question into more specific type
        transform_qtype = etree.XSLT(etree.parse(self.filexslt_qtype))
        # apply transform
        tree = transform_qtype(tree)
        # store ouput for debug
        if (self.deb == 1):
            tree.write(self._tempfile(), pretty_print=True, encoding="utf-8")

        # store the tree
        self.tree = tree

    def _options(self):
        """ Find and parse quiz level options.
        """
        opts = self.tree.xpath("//*[@class='amc_quiz_options']")
        for opt in opts:
            # The option name is in 'name' atrtibute
            self.options[opt.attrib['role']] = opt.text
            opt.getparent().remove(opt)
            print("   Modified Quizz options '{}' to '{}'".format(opt.attrib['role'],
                                                           self.options[opt.attrib['role']]))

    def _scoring(self):
        """ Find and convert default scoring.
        """
        # look for amc_baremeDefautS and amc_baremeDefautM attribut
        # on cherche s'il existe un barème par défaut pour question simple
        bars = self.tree.xpath("//*[@class='amc_baremeDefautS']")
        # bar[0].text contient la chaine de caractère
        if len(bars) > 0:
            # on découpe bar[0].text et on affecte les nouvelles valeurs par défaut
            amc_bs = dict(item.split("=") for item in bars[0].text.strip().split(","))
            print("baremeDefautS :", amc_bs)
            if (float(amc_bs['b']) < 1):
                print("WARNING : the grade of the good answser in question will be < 100%, put b=1")
            self.amc_bs.update(amc_bs)

        # on cherche s'il existe un barème par défaut pour question multiple
        barm = self.tree.xpath("//*[@class='amc_baremeDefautM']")
        # bar[0].text contient la chaine de caractère
        if len(barm) > 0:
            # on découpe bar[0].text et on affecte les nouvelles valeurs par défaut
            amc_bm = dict(item.split("=") for item in barm[0].text.strip().split(","))
            print("baremeDefautM :", amc_bm)
            if (float(amc_bm['b']) < 1):
                print("WARNING : the grade of the good answser(s) in questionmult may be < 100%, put b=1")
            self.amc_bm.update(amc_bm)

    def _graphics(self):
        """ Parse <graphics> to set path, size and layout.
        """
        # Need probably to be called before 2html
        # <graphics candidates="schema_interpL.png" graphic="schema_interpL.png" options="width=216.81pt" xml:id="g1" class="ltx_centering"/>

        Ilist = self.tree.xpath(".//graphics")  # que sur attributs ici
        # conversion des notations d'alignement
        align = {'ltx_align_right': 'right', 'ltx_align_left': 'left',
                 'ltx_centering': 'center'}

        for Ii in Ilist:
            try:
                img_name = Ii.attrib['candidates'].split(',')[-1]   # get the last candidates
            except KeyError as e:
                print('WARNING : No Image file candidates. ',
                      'Probably due to a wrong path : {}'.format(Ii.attrib['graphic']))
                raise e
            ext = img_name.split('.')[-1]
            # not all attrib are mandatory... check if they exist before using them
            # try for class
            if 'class' in Ii.attrib:
                img_align = Ii.attrib['class']
            else:
                img_align = 'ltx_centering'  # default value center !
            # try for option
            if 'options' in Ii.attrib:
                img_options = Ii.attrib['options']
                img_size = img_options.split('=')[-1]  # il reste pt, mais cela ne semble pas poser de pb
                img_dim = img_options.split('=')[0]
            else:
                img_options = ''
                img_size = self.options['default_img_width']
                img_dim = 'width'

            img_path = os.path.dirname(os.path.normpath(os.path.join(self.pathin, img_name)))

            name = basename(img_name)
            # print(name, ext, img_dim, align[img_align])
            Ii.attrib.update({'ext':ext, 'dim': img_dim, 'size': img_size,
                              'pathF': img_path, 'align': align[img_align],
                              'name': name})

    def _categories(self):
        """ Find and convert categories.
        """
        # <text>$course$/filein/amc_element_tag</text>
        Clist = self.tree.xpath("//*[@class='amc_categorie']")
        for Ci in Clist:
            if self.catflag == 1:
                Ci.text = "$course$/"+self.catname.split('.')[0] + "/" + Ci.text
            else:
                Ci.text = "$course$/"+self.catname.split('.')[0]


    def _convertQuestions(self):
        """ Find and convert questions
        """
        context = self._exportContext()
        self.Qtot = 0
        for qtype in SUPPORTED_Q_TYPE:
            Qlist = self.tree.xpath("//*[@class='%s']" % qtype)
            for Qi in Qlist:
                thisq = CreateQuestion(qtype, Qi, context)
                thisq.convert()
            self.Qtot += len(Qlist)


    def _exportContext(self):
        """ Export environnement variable as a Context object.
        """
        context = Context(pathin=self.pathin, wdir=self.wdir,
                          amc_bm=self.amc_bm, amc_bs=self.amc_bs,
                          deb=self.deb, options=self.options)
        return context

    def _tempfile(self):
        """ Generate temp file path for each conversion steps.
        """
        # create name
        name = self.tempBaseName.join(str(self.tempfile_id))
        # increment it for next use
        self.tempfile_id += 1
        return os.path.join(self.wdir, name)



def to_moodle(filein, pathin, fileout='out.xml', pathout='.',
              workingdir=None, catname=None, deb=0):
    """ Build Moodle XML file from xml file obtain with LaTeXML.

    Call xslt stylesheet and complete the required xml element,
    Compute the grade according to the amc way
    Convert non png img into png and embedded them in the output_file

    Remark : The grade are not computed exactly as in amc, see the doc.


    Parameters
    ----------
    filein : string
        Input XML file provide by LaTeXML.
    pathin : string
        Input directory.
    fileout : string, optional
        Output moodle XML file. The default is 'out.xml'.
    pathout : string, optional
        Output directory. The default is '.'.
    workingdir : string, optional
        Allow to define a working directory (temp) different from the output
        directiory. The default is None.
    catname : string, optional
        Set moodle category. The default is None.
    deb : int, optional
        Set to 1 to store all intermediate files for debugging. The default is 0.

    Returns
    -------
    None.

    """

    # define working dir
    if workingdir is None:
        wdir = pathin
    else:
        wdir = workingdir

    # load input latexml xml file
    with open(os.path.join(wdir, filein), 'r') as xml:
        # instanciate the Quiz object
        quiz = AMCQuiz(xml, pathin, wdir, catname, deb)
        # run the conversion and save the output
        quiz.toMoodle(os.path.join(pathout, fileout))



