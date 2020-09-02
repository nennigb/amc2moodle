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



	This stylesheet is use to preprocess the question bank and to recast 
	amc question that will lead to non multiplechoice question in moodle.
	For instance essay, calculated, numerical...
	All this question have in common that the answer type like AMCnumericChoices
	will define the question type.
	
	After this, it all questions can be procees in the same way...
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes"/>


<!-- template identité -->
<xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
</xsl:template>



<xsl:template match="note[starts-with(@class, 'amc_question')]">
<xsl:choose>
  <!-- Match amc_numeric_choices and remane this question into 'numerical' -->
  <xsl:when test=".//note[@class='amc_numeric_choices']">
    <!-- It's impossible to change parent depending of child if node are already copied, thus create a new node.-->
    <!-- the key need to contain 'amc_question'* -->
    <note class="amc_questionnumeric">
       <xsl:attribute name="role"><xsl:value-of select="@role"/></xsl:attribute>     
       <xsl:apply-templates/>
    </note>
  </xsl:when>
  <!--do the same for AMCopen 'amc_questionopen'-->
  <xsl:when test=".//note[@class='amc_open']">
    <!-- It's impossible to change parent depending of child if node are already copied, thus create a new node.-->
    <!-- the key need to contain 'amc_question'* -->
    <note class="amc_questionopen">
       <xsl:attribute name="role"><xsl:value-of select="@role"/></xsl:attribute>     
       <xsl:apply-templates/>
    </note>
  </xsl:when>
  <!--do the same for 'amc_questiondescription'
  'choices' is removed in all case. Should test for amc_bonne, amc_mauvaise, amc_numeric_choices -->
  <xsl:when test="not(.//note[starts-with(@class, 'amc_bonne')]) and not(.//note[starts-with(@class, 'amc_mauvaise')]) and not(.//note[starts-with(@class, 'amc_numeric_choices')])">
    <!-- It's impossible to change parent depending of child if node are already copied, thus create a new node.-->
    <!-- the key need to contain 'amc_question'* -->
    <note class="amc_questiondescription">
       <xsl:attribute name="role"><xsl:value-of select="@role"/></xsl:attribute>
       <xsl:apply-templates/>
    </note>
  </xsl:when>
  <!--do the same for calculated->questionmult(x) 'amc_questionmultcalcmult'-->
  <xsl:when test="(.//note[@class='amc_FPprint']) and (@class='amc_questionmult')">
    <!-- It's impossible to change parent depending of child if node are already copied, thus create a new node.-->
    <note class="amc_questionmultcalcmult">
       <xsl:attribute name="role"><xsl:value-of select="@role"/></xsl:attribute>     
       <xsl:apply-templates/>
    </note>
  </xsl:when>
  <!--do the same for calculated->question 'amc_questioncalcmult'-->
  <xsl:when test="(.//note[@class='amc_FPprint']) and (@class='amc_question')">
    <!-- It's impossible to change parent depending of child if node are already copied, thus create a new node.-->
    <note class="amc_questioncalcmult">
       <xsl:attribute name="role"><xsl:value-of select="@role"/></xsl:attribute>     
       <xsl:apply-templates/>
    </note>
  </xsl:when>
  <!--  otherwise, just copy the existing attributs and childs -->
  <xsl:otherwise>
    <note>
       <xsl:attribute name="class"><xsl:value-of select="@class"/></xsl:attribute>
       <xsl:attribute name="role"><xsl:value-of select="@role"/></xsl:attribute>
	   <xsl:apply-templates/>
    </note>
  </xsl:otherwise>
</xsl:choose>
</xsl:template>




</xsl:stylesheet>

