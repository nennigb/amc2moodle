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
  <xsl:output method="xml" indent="yes" cdata-section-elements="cdata"/>

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
<xsl:template match="note[@class='amc_question' or @class='amc_questionmult']">
	<question type="multichoice">
		<xsl:apply-templates />
	</question>
</xsl:template>

<!-- \AMCnumericChoices yields to numerical question type -->
<xsl:template match="note[@class='amc_questionnumeric']">
	<question type="numerical">
	  <xsl:apply-templates />
	</question>
</xsl:template>

<!--\AMCopen yields to essay question type-->
<xsl:template match="note[@class='amc_questionopen']">
	<question type="essay">
	  <xsl:apply-templates />
	</question>
</xsl:template>

<!--\AMCopen yields to essay question type-->
<xsl:template match="note[@class='amc_questiondescription']">
	<question type="description">
	  <xsl:apply-templates />
	</question>
</xsl:template>

<!--\FPprint yields to calculatedmulti question type-->
<xsl:template match="note[@class='amc_questioncalcmult' or @class='amc_questionmultcalcmult']">
	<question type="calculatedmulti">
	  <xsl:apply-templates />
	</question>
</xsl:template>

<!--TODO Need to add other type like description, calculated... -->





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

<xsl:template match="note[@class='amc_choices_options']">
</xsl:template>

<xsl:template match="note[@class='amc_numeric_choices']">
</xsl:template>

<xsl:template match="note[@class='amc_open']">
</xsl:template>


<xsl:template match="fraction">
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
