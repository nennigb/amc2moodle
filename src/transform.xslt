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
    
    
    
    - Permet de finaliser la mise en forme et renommer certain éléments
    - suppresion de certains élément (bareme, title etc...)
    - a terme cette fichier devrait être intégré complètement à la partie python pour plus de clartée   
-->


  <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes"/>

<!-- template identité -->
<xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
</xsl:template>

<!-- template element racine -->
 <xsl:template match="document"> 
 <quiz>
       <xsl:apply-templates/>
 </quiz>       
 </xsl:template>

<!-- template bonne réponse-->
  <xsl:template match="note[starts-with(@class, 'amc_bonne')]"> 
    <answer format="html">
      <xsl:attribute name="fraction"><xsl:value-of select="fraction"/></xsl:attribute>     
        <!-- <xsl:apply-templates/> -->
        <xsl:apply-templates/>
    </answer>
  </xsl:template>

<!-- template mauvaise réponse -->  
  <xsl:template match="note[starts-with(@class, 'amc_mauvaise')]"> 
   <answer format="html">
      <xsl:attribute name="fraction"><xsl:value-of select="fraction"/></xsl:attribute>
       <!-- <xsl:apply-templates/> -->
       <xsl:apply-templates/>
    </answer>
  </xsl:template>
  
  
  

<!-- template Question, questionmult-->
<xsl:template match="note[starts-with(@class, 'amc_question')]">
	<question type="multichoice">
	<xsl:if test="@class='amc_question'">
		<single>true</single>  <!-- une seule case à cocher -->
	</xsl:if>
	<xsl:if test="@class='amc_questionmult'">
		<single>false</single>  <!-- plusieurs cases à cocher -->
	</xsl:if>	
		<!-- move vers 2html
		<name>
		    <text>
			    <xsl:value-of select="@name"/>
			</text>
		</name>			-->
		<xsl:apply-templates />
	</question>
</xsl:template>


<!-- template netoyage champ globaux mise en forme-->
<xsl:template match="para"> 
    <xsl:apply-templates/>
</xsl:template>



<!-- transformation/renomage des champs note qui reste en texte -->
<xsl:template match="note[not(@class)]">
  <xsl:element name="text">
    <xsl:apply-templates/>
  </xsl:element>
</xsl:template>

<!--renomage des catégorie /amc2moodle-->
<xsl:template match="note[@class='amc_categorie']">
    <question type="category">
        <category>
            <text>
                <xsl:value-of select="text()"/>
            </text>
        </category>
  </question>
</xsl:template>


<!-- Remove amc_bareme* elements -DefaultS -DefaultM-->
<xsl:template match="text[starts-with(@class, 'amc_bareme')]"> 
</xsl:template>

<xsl:template match="bareme"> 
</xsl:template>

<!-- template defaultgrade -->
<xsl:template match="defaultgrade"> 
    <defaultgrade>
			<xsl:value-of select="text()"/>
	</defaultgrade>
</xsl:template>


<!--création de commentaires sur les champ inutiles pour moodle et trasmis via latexml -->
<xsl:template match="resource"> 
</xsl:template>

<xsl:template match="title"> 
    <xsl:comment>
       <xsl:apply-templates/>
    </xsl:comment>
</xsl:template>

<xsl:template match="creator"> 
   <xsl:comment>
        <xsl:apply-templates/>
    </xsl:comment>
</xsl:template>


</xsl:stylesheet>
