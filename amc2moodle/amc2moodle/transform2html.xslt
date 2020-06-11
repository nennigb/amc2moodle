<?xml version="1.0" encoding="UTF-8"?>
<!-- 

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



    - Permet de reformater la question
    - extraction des fichiers images
    - extraction des maths mathml vers latex
    - add [starts-with(@class, 'amc_env')] to avoid pb with alignement attribute
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes"/>
<!-- Remove all namespace attribut 
<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
-->
<!-- template identité -->
<xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
</xsl:template>



<!-- #############################################################

Changement de l'organisation des questions
- extraction des fichiers images
- encapsulage du text de la question

############################################################# -->
<xsl:template match="note[starts-with(@class, 'amc_question')]">
  <note>
  <xsl:attribute name="class"><xsl:value-of select="@class"/></xsl:attribute>
        <name>
		    <text>
			    <xsl:value-of select="@role"/>
			</text>
		</name>	
        
        <!-- barème local -->
       <xsl:for-each select="text[@class='amc_bareme']">
          <bareme>
                <xsl:value-of select="text()"/>     
         </bareme>
        </xsl:for-each> 
        <!-- mise en forme html, équation, tableau -->
        <questiontext format="html">
        
        
        <!-- prise en comte des images en 2 étapes stockage et placement
        boucle pour trouver les fichiers graphiques contenus dans la question (et les reponses!!)-->
        <xsl:for-each select=".//graphics">
<!--        si ce n'est pas compris dans une réponse on le met, sinon non,-->
<!--        faire de même au niveau des réponses-->
            <xsl:if test="not(ancestor::note[starts-with(@class, 'amc_bonne')] | ancestor::note[starts-with(@class, 'amc_mauvaise')])">
                     <file> <!-- question-->
    <!--                   <xsl:attribute name="graphic"><xsl:value-of select="@graphic"/></xsl:attribute>-->
    <!--                   <xsl:attribute name="options"><xsl:value-of select="@options"/></xsl:attribute>-->
                       <xsl:attribute name="pathF"><xsl:value-of select="@pathF"/></xsl:attribute>
                       <xsl:attribute name="ext"><xsl:value-of select="@ext"/></xsl:attribute>
                       <xsl:attribute name="dim"><xsl:value-of select="@dim"/></xsl:attribute>
                       <xsl:attribute name="size"><xsl:value-of select="@size"/></xsl:attribute>
                       <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
                       <xsl:attribute name="align"><xsl:value-of select="@align"/></xsl:attribute>
                       <xsl:apply-templates/>
                  </file>
               </xsl:if>
          </xsl:for-each>
        
        
            <xsl:copy>         
               <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                   <xsl:apply-templates />
               <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
            </xsl:copy>
        </questiontext>

       <!-- On recopie les réponses 
       <xsl:template match="note[@class='amc_mauvaise']"> 
       on boucle sur les réponses <xsl:for-each select="//note[@class='amc_mauvaise']">-->
        <xsl:for-each select="note[starts-with(@class, 'amc_bonne')] | note[starts-with(@class, 'amc_mauvaise')]">
              <note> 
              <xsl:attribute name="class"><xsl:value-of select="@class"/></xsl:attribute>
                   <xsl:copy>         
                      <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                        <xsl:apply-templates/>   
                      <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                   </xsl:copy>
                   
                   <!-- prise en comte des images en 2 étapes stockage et placement
                    boucle pour trouver les fichiers graphiques contenus dans la question-->
                    <xsl:for-each select=".//graphics">
                          <file> <!-- question-->
<!--                            <xsl:attribute name="graphic"><xsl:value-of select="@graphic"/></xsl:attribute>-->
<!--                            <xsl:attribute name="options"><xsl:value-of select="@options"/></xsl:attribute>-->

                            <xsl:attribute name="pathF"><xsl:value-of select="@pathF"/></xsl:attribute>
                            <xsl:attribute name="ext"><xsl:value-of select="@ext"/></xsl:attribute>
                            <xsl:attribute name="dim"><xsl:value-of select="@dim"/></xsl:attribute>
                            <xsl:attribute name="size"><xsl:value-of select="@size"/></xsl:attribute>
                            <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
                            <xsl:attribute name="align"><xsl:value-of select="@align"/></xsl:attribute>
                            <xsl:apply-templates/>
                         </file>
                      </xsl:for-each>
                    
              </note>              
       </xsl:for-each>        
          
  </note>
</xsl:template>


<!-- #############################################################

Prise en compte de la mise en forme

emph
bold
italic
underline
typewriter
A faire : <center> </center>,  small caps, sf, sl, sc 
############################################################# -->

<xsl:template match="emph">
    <em><xsl:apply-templates/></em>
</xsl:template>

<xsl:template match="text[@font='bold']">
    <b><xsl:apply-templates/></b>
</xsl:template>

<!-- plus valable en html 5, mais ca semble dans l'éditeur moodle  -->
<xsl:template match="text[@framed='underline']">
    <u><xsl:apply-templates/></u>
</xsl:template>

<xsl:template match="text[@font='italic']">
    <i><xsl:apply-templates/></i>
</xsl:template>

<xsl:template match="text[@font='typewriter']">
    <tt><xsl:apply-templates/></tt>
</xsl:template>



<!--verbatim rendu comme du code, attention pb avec automultiplechoice et verbatim-->
<!--use allttt instead of real evrbatim environemt-->
<!-- Text in a <pre> element is displayed in a fixed-width font (usually Courier), and it preserves both spaces and line breaks. -->
<xsl:template match="verbatim">
   <p>
    <pre>       
        <xsl:apply-templates/>
    </pre>
   </p>
</xsl:template>


<xsl:template match="break">
    <br>
        <xsl:value-of select="text()"/>     
    </br>
</xsl:template>



<!-- #############################################################

Prise en compte des maths "simple"
$$
equation

############################################################# -->
<!-- Pas trop mal, mais provoque des platage. L'avantage de xslt est que c'est récursif!-->
<xsl:template match="Math"> 
    <xsl:if test="@mode='inline'">
           \(<xsl:value-of select="@tex"/>\)    
    </xsl:if>
    <xsl:if test="@mode='display'">
    $$\begin{equation}
           <xsl:value-of select="@tex"/>
    \end{equation}$$
    </xsl:if>		
</xsl:template>

<!--On ne fait rien sur ces éléments, ils sont traités ailleurs-->
<xsl:template match="equation"> 
       <xsl:apply-templates/>
</xsl:template>
<!--traité au niveau  de la question, pour les remonter d'un cran-->
<xsl:template match="note[starts-with(@class, 'amc_mauvaise')]"> 
</xsl:template>

<!--traité au niveau  de la question, pour les remonter d'un cran-->
<xsl:template match="note[starts-with(@class, 'amc_bonne')]"> 
</xsl:template>

<!--traité au niveau  de la question, pour les remonter d'un cran-->
<xsl:template match="text[@class='amc_bareme']"> 
</xsl:template>



<!-- #############################################################

Prise en compte des tableaux
border set to 1, in all case
align attribute are taken into account in the table.
the table is centered horizontally in the page, possible use attibute class="ltx_centering" of tabular

############################################################# -->

<xsl:template match="tabular"> 
    <table border='1' align='center'>
       <xsl:apply-templates/>
    </table>
</xsl:template>


<!-- #############################################################

Prise en compte des images : 2 étapes une dans question (stockage) et une ici (inclusion dans le CDATA)
 latexml produit : <graphics candidates="tinymonk.png" graphic="tinymonk.png" options="width=43.362pt" xml:id="g1"/> 
 <file name="gmsh.png" path="/" encoding="base64"> ...
 moodle: <img src="@@PLUGINFILE@@/tinymonk.png" alt="description de l'image" width="100" height="107" style="vertical-align:text-bottom; margin: 0 .5em;" class="img-responsive">
 <p style="text-align: center;"><img src="http://192.168.110.28/moodle/draftfile.php/5/user/draft/46006595/monk%20%283%29.png" alt="" role="presentation" style=""><br></p>
 ltx_centering ltx_align_right
############################################################# -->

<xsl:template match="graphics"> 
    <p>
    <xsl:attribute name="style">text-align:<xsl:value-of select="@align"/>; </xsl:attribute>
<!--        <img style="vertical-align:text-bottom; margin: 0 .5em;" class="img-responsive"> -->
          <img style="vertical-align:text-bottom; margin: 0 .5em;" > 
            <xsl:attribute name="src">@@PLUGINFILE@@/<xsl:value-of select="@name"/>.png</xsl:attribute>
            <xsl:attribute name="{@dim}"><xsl:value-of select="@size"/></xsl:attribute>             
            <xsl:attribute name="options"><xsl:value-of select="@options"/></xsl:attribute> 
<!--            attribut inutilisé dans le rendu, mais utile pour l'encodage de l'image (math quetsion)  
            <xsl:attribute name="alt"><xsl:value-of select="@graphic"/></xsl:attribute>
            <xsl:attribute name="pathF"><xsl:value-of select="@pathF"/></xsl:attribute>
            <xsl:attribute name="ext"><xsl:value-of select="@ext"/></xsl:attribute>
            <xsl:attribute name="dim"><xsl:value-of select="@dim"/></xsl:attribute>
            <xsl:attribute name="size"><xsl:value-of select="@size"/></xsl:attribute>
            <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
            <xsl:attribute name="align"><xsl:value-of select="@align"/></xsl:attribute>
-->
            <xsl:apply-templates/>
        </img>
    </p>
</xsl:template>


<!--- ###########################################################
Prise en compte itemize and ennumerate
Remarks : the tag in item[tag] is ignored, it seems not possible 
to change the bullet in html
-->
<xsl:template match="itemize"> 
  <ul>
    <xsl:apply-templates/>
  </ul> 
</xsl:template>

<xsl:template match="enumerate"> 
  <ol>
    <xsl:apply-templates/>
  </ol> 
</xsl:template>


<xsl:template match="item"> 
  <li> 	 
    <xsl:apply-templates/>
  </li> 
</xsl:template>

<xsl:template match="tag"> 
</xsl:template>
<!--- New name in new version of LaTeXML -->
<xsl:template match="tags"> 
</xsl:template>

<!--- ###########################################################
       Include Here new template for supported package 
- mhchem through mathjax
-->

<!--mhchem-->
<!-- called outside math env only since raw tex are used in Math mode-->
<xsl:template match="note[@class='mhchem']">\(\<xsl:value-of select="@role"/>{<xsl:apply-templates/>}\)</xsl:template>



</xsl:stylesheet>







