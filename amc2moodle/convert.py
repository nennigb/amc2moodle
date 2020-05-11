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
from lxml import etree
import base64
import os
from wand.image import Image as wandImage

# ======================================================================
# Image processing utilities
# ======================================================================
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

    def __init__(self, fileIn=None, fileOut=None):
        if fileIn is not None and fileOut is not None:
            self.convertImage(fileIn, fileOut)


    def convertImage(self, fileIn, fileOut):
        """ Image conversion with wand.
        """
        im = wandImage(filename=fileIn)
        # remove timestamp from png (keep checksum unchanged for test)
        im.artifacts['png:exclude-chunks'] = 'date,time'
        im.strip()
        # for (k, v) in im.artifacts.items():
        #     print(k, v)
        print("  Conversion from {} to {}.".format(os.path.splitext(fileIn)[1],
                                                   os.path.splitext(fileOut)[1]
                                                   ))
        im.save(filename=fileOut)
        im.close()


def encodeImg(Ii, pathin, pathout):
    """ Convert image to png and encode it in base64 text.

    Parameters
    ----------
    Ii : element tree
        The xml element containing the image information (path, ...). This
        element is modified.

    pathin, pathout : string
        the input and output path
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
                         img_path)
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



def to_moodle(filein, pathin, fileout='out.xml', pathout='.',
              workingdir=None, catname=None, deb=0):
    """ Build Moodle XML file from xml file obtain with LaTeXML.

    Call xslt stylesheet and complete the required xml element,
    Compute the grade according to the amc way
    Convert non png img into png and embedded them in the output_file

    Remark : The grade are not computed exactly as in amc, see the doc.

    TODO Factorize question type

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
        Set to 1 to store all intermediate file for debging. The default is 0.

    Returns
    -------
    None.

    """

    # Define catflag [legacy]
    catflag = catname is not None

    # define working dir
    if workingdir is None:
        wdir = pathin
    else:
        wdir = workingdir


    # TODO to options file
    # Shuffle all answsers
    ShuffleAll = True
    # ajout amc_aucune si obligatoire"
    amc_autocomplete = 1
    amc_aucune = u"aucune de ces réponses n'est correcte"
    """ Default grade for simple and multiple Question :
    e=incohérence; b=bonne; m=mauvaise; p planché
    Elles peuvent etre spécifier dans le fichier .tex avec
    \baremeDefautS{e=-0.5,b=1,m=-0.5}
    \baremeDefautM{e=-0.5,b=0.5,m=-0.25,p=-0.5}
    ou au niveau de la question
    """
    # Simple : e :incohérence, b: bonne,  m: mauvaise,  p: planché
    amc_bs = {'e': -1, 'b': 1, 'm': -0.5}
    # Multiple : e :incohérence, b: bonne,  m: mauvaise,  p: planché
    amc_bm = {'e': -1, 'b': 1, 'm': -0.5, 'p': -1}
    # valeur par défaut de la note de la question
    moo_defautgrade = 1.

    # file out for debug pupose
    filetemp0 = os.path.join(wdir, "temp0.xml")
    filetemp = os.path.join(wdir, "temp.xml")

    # path of the file

    # path to xslt stylesheet
    # TODO use pkgutils
    # 1. remove namespace
    filexslt_ns = os.path.join(os.path.dirname(__file__),
                               "transform_ns.xslt")
    # 2. convert to html, tab, figure, equations
    filexslt_pre = os.path.join(os.path.dirname(__file__),
                                "transform2html.xslt")
    # 3. remane element and finish the job
    filexslt = os.path.join(os.path.dirname(__file__),
                            "transform.xslt")

    ##########################################################################
    # Pré traitement
    # on parse le fichier xml
    # Elements are lists
    # Elements carry attributes as a dict
    xml = open(os.path.join(wdir, filein), 'r')
    tree0 = etree.parse(xml)

    # on supprime le namespace [a terme faire autrement]
    xslt_ns = open(filexslt_ns, 'r')
    xslt_ns_tree = etree.parse(xslt_ns)
    transform_ns = etree.XSLT(xslt_ns_tree)
    # applique tranformation
    tree = transform_ns(tree0)
    # on modifie les element graphic pour gérer les chemins, le taille et la mise en forme.
    # <graphics candidates="schema_interpL.png" graphic="schema_interpL.png" options="width=216.81pt" xml:id="g1" class="ltx_centering"/>
    Ilist = tree.xpath(".//graphics")  # que sur attributs ici
    # conversion des notations d'alignement
    align = {'ltx_align_right': 'right', 'ltx_align_left': 'left',
             'ltx_centering': 'center'}
    # ext extension, path:chemin img, dim [width/height],size, dimension en point

    for Ii in Ilist:
        img_name = Ii.attrib['graphic']
        ext = img_name.split('.')[-1]
        # not all attrib are mandatory... check if they exist before use it
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
            img_size = '200pt'
            img_dim = 'width'

        # FIXME use os.path
        img_path = os.path.join(pathin,
                                img_name[0:img_name.rfind('/')]).replace('/./',
                                                                         '/')
        # print(img_path)
        name = basename(img_name)
        # print(name, ext, img_dim, align[img_align])
        Ii.attrib.update({'ext':ext, 'dim': img_dim, 'size': img_size,
                          'pathF': img_path, 'align': align[img_align],
                          'name': name})

    # path
    # ext
    # dim = width or height
    # size :
    # width options="height=216.81pt"
    # alig <-> class

    # remise en forme + html + math + image + tableau
    xslt_pre = open(filexslt_pre, 'r')
    xslt_pre_tree = etree.parse(xslt_pre)
    transform_pre = etree.XSLT(xslt_pre_tree)
    # applique tranformation
    tree = transform_pre(tree)
    if (deb == 1):
        # ecriture
        tree.write(filetemp0, pretty_print=True, encoding="utf-8")


    ###########################################################################
    # Recherche barème par défaut
    # attribut amc_baremeDefautS et amc_baremeDefautM
    # on cherche s'il existe un barème par défaut pour question simple
    bars = tree.xpath("//*[@class='amc_baremeDefautS']")  # que sur attributs ici
    # bar[0].text contient la chaine de caractère
    if len(bars) > 0:
        # on découpe bar[0].text et on affecte les nouvelles valeurs par défaut
        amc_bs = dict(item.split("=") for item in bars[0].text.strip().split(","))
        print("baremeDefautS :", amc_bs)
        if (float(amc_bs['b']) < 1):
            print("WARNING : the grade the good answser in question will be < 100%, put b=1")

    # on cherche s'il existe un barème par défaut pour question multiple
    barm = tree.xpath("//*[@class='amc_baremeDefautM']")
    # bar[0].text contient la chaine de caractère
    if len(barm) > 0:
        # on découpe bar[0].text et on affecte les nouvelles valeurs par défaut
        amc_bm = dict(item.split("=") for item in barm[0].text.strip().split(","))
        print("baremeDefautM :", amc_bm)
        if (float(amc_bm['b']) < 1):
            print("WARNING : the grade of the good answser(s) in questionmult may be < 100%, put b=1")


    ############################################################################
    # Prise en compte des catégories
    # <text>$course$/filein/amc_element_tag</text>
    Clist = tree.xpath("//*[@class='amc_categorie']")
    for Ci in Clist:
        if (catflag == 1):
            Ci.text = "$course$/"+catname.split('.')[0] + "/" + Ci.text
        else:
            Ci.text = "$course$/"+catname.split('.')[0]


    ###########################################################################
    # Application du barème dans chaque question
    # + vérf barème locale : attribut amc_bareme
    # on suppose que le bareme est au même niveau que des element amc_bonne
    # ou amc_mauvaise

    # Question simple
    # =========================================================================
    #Qlist = tree.xpath("//text[@class='amc_question']")
    Qlist = tree.xpath("//*[@class='amc_question']")
    # calcul nombre de question totale
    Qtot = len(Qlist)
    for Qi in Qlist:
        # apply shuffleing
        shuffleanswers = etree.SubElement(Qi, "shuffleanswers")
        if ShuffleAll is True:
            shuffleanswers.text = 'true'
        else:
            shuffleanswers.text = 'false'
        # est qu'il y a une bareme local cherche dans les child
        # barl = Qi.xpath("./text[@class='amc_bareme']")
        barl = Qi.xpath("bareme")
        # Par défaut on a le bareme global
        amc_bl = amc_bs
        # si il y a une bareme local, on prend celui-la
        if len(barl) > 0:
            amc_bl=dict(item.split("=") for item in barl[0].text.strip().split(","))
            print("bareme local :", amc_bl)
            if (float(amc_bl['b']) < 1.):
                print("WARNING : the grade of the good answser(s) may be < 100%, put b=1")

        # inclusion des images dans les questions
        Ilist = Qi.xpath("./questiontext/file")
        for Ii in Ilist:
            Ii = encodeImg(Ii, pathin, wdir)

        # bonne cherche dans les child
        Rlist = Qi.xpath("./*[starts-with(@class, 'amc_bonne')]")
        for Ri in Rlist:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bl['b'])*100.)
            # inclusion des images dans les réponses
            RIlist = Ri.xpath("file")
            for Ii in RIlist:
                Ii = encodeImg(Ii, pathin, wdir)

        # Mauvaise cherche dans les child
        Rlist = Qi.xpath("./*[starts-with(@class, 'amc_mauvaise')]")
        for Ri in Rlist:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bl['m'])*100.)
            # inclusion des images dans les réponses
            RIlist = Ri.xpath("file")
            for Ii in RIlist:
                Ii = encodeImg(Ii, pathin, wdir)

        # e:incohérente n'a pas trop de sens en ligne car on ne peut pas cocher plusieurs cases.

        # on ajoute le champ  <defaultgrade>1.0000000</defaultgrade>
        Dgrade = etree.SubElement(Qi, "defaultgrade")
        Dgrade.text = str(moo_defautgrade)

    # Question multiple
    # ==========================================================================
    # Qlist = tree.xpath("//text[@class='amc_questionmult']")
    Qlist = tree.xpath("//*[@class='amc_questionmult']")
    # calcul nombre de question au total
    Qtot += len(Qlist)
    for Qi in Qlist:
        # apply shuffleing
        shuffleanswers = etree.SubElement(Qi, "shuffleanswers")
        if ShuffleAll is True:
            shuffleanswers.text = 'true'
        else:
            shuffleanswers.text = 'false'
        # est qu'il y a une bareme local cherche dans les child
        # barl = Qi.xpath("./text[@class='amc_bareme']")
        # barl = Qi.xpath("./*[@class='amc_bareme']")
        barl = Qi.xpath("bareme")
        # Par défaut on a le bareme global
        amc_bml = amc_bm
        # si il y a une bareme local, on prend celui-la
        if len(barl) > 0:
            amc_bml = dict(item.split("=") for item in barl[0].text.strip().split(","))
            print("bareme local :", amc_bml)
            if (float(amc_bml['b']) < 1):
                print("WARNING : the grade of the good answser(s) may be < 100%, put b=1")

        # inclusion des images dans les questions
        Ilist = Qi.xpath("./questiontext/file")
        for Ii in Ilist:
            Ii = encodeImg(Ii, pathin, wdir)

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
        if ((amc_autocomplete == 1) & (NRb > 0)):
            aucune = etree.SubElement(Qi, 'note',
                                      attrib={'class': 'amc_mauvaise'})
            aucunec = etree.SubElement(aucune, 'note')
            aucunec.text = amc_aucune
            NRm += 1
            Rlistm.append(aucune)

        # Si pas de bonne on en ajoute une bonne
        if ((amc_autocomplete == 1) & (NRb == 0)):
            aucune = etree.SubElement(Qi, 'note',
                                      attrib={'class': 'amc_bonne'})
            aucunec = etree.SubElement(aucune, 'note')
            aucunec.text = amc_aucune
            NRb += 1
            Rlistb.append(aucune)

        # =====================================================================
        # ajout d'un champ fraction au reponse
        # bonne cherche dans les Qi childs
        for Ri in Rlistb:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bml['b'])*100./NRb)
            RIlist = Ri.xpath("file")
            for Ii in RIlist:
                Ii = encodeImg(Ii, pathin, wdir)

        # Mauvaise cherche dans les Qi childs
        for Ri in Rlistm:
            frac = etree.SubElement(Ri, "fraction")  # body pointe vers une case de tree
            frac.text = str(float(amc_bml['m'])*100./NRm)
            RIlist = Ri.xpath("file")
            for Ii in RIlist:
                Ii = encodeImg(Ii, pathin, wdir)


        # incohérente pas trop de sens en ligne car on ne peut pas cocher plusieurs cases.

        # on ajoute le champ  <defaultgrade>1.0000000</defaultgrade>
        Dgrade = etree.SubElement(Qi, "defaultgrade")
        Dgrade.text = str(moo_defautgrade)


    # on affiche
    if (deb == 1):
        # Ecriture fichier output intermediaire (grading edit)
        tree.write(filetemp, pretty_print=True, encoding="utf-8")


    ############################################################################
    # Reformatage à partir de xslt
    # chargement
    xslt = open(filexslt, 'r')
    xslt_tree = etree.parse(xslt)
    transform = etree.XSLT(xslt_tree)
    # applique tranformation
    result_tree = transform(tree)
    if (deb == 1):
        print(etree.tostring(result_tree, pretty_print=True, encoding="utf-8"))


    ############################################################################
    # écriture fichier out
    result_tree.write(fileout, pretty_print=True, encoding="utf-8")
    if deb == 1:
        print(result_tree)

    # fermeture des fichiers xslt
    xslt_ns.close()
    xslt_pre.close()
    xslt.close()
    # close xml output file
    xml.close()

    print('\n')
    print(' > shuffleanswers is ' + str(ShuffleAll))
    print(" > " + str(Qtot) + " questions converted...")
