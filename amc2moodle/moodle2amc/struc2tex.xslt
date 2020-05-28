<?xml version="1.0" encoding="UTF-8"?>

<!-- Latex conversion of quizz struture.
  - [x] correctchoice
  - [x] wrongchoice
  - [x] quiz
  - [x] question,  questionmult on attribute
  - [x] element 
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml" indent="yes" encoding="UTF-8"/>

<!-- template identité -->
<xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
</xsl:template>

<!-- document  
<xsl:template match="document">
   <xsl:apply-templates/>
</xsl:template>
-->

<!-- quiz -->
<xsl:template match="quiz"> 
   <xsl:apply-templates/>
</xsl:template>


<xsl:template match="question">
% -----------------------------------------------------------------------------
\element{<xsl:value-of select = "@category"/>}{
  \begin{<xsl:value-of select = "@amctype"/>}{<xsl:value-of select = "@qname"/>}\label{q:<xsl:value-of select = "@qname"/>}   
    <xsl:apply-templates />
  \end{<xsl:value-of select = "@amctype"/>}
}
</xsl:template>

<!-- template for answers-->
<xsl:template match="question/text">
    <xsl:apply-templates /> 
</xsl:template>


<!-- template for answers-->
<xsl:template match="choices">
  \begin{choices}
	<xsl:apply-templates />
  \end{choices}
</xsl:template>

<xsl:template match="open">
% It is possible to add more granularity with partially correct answer using \wrongchoice[P]{p}\scoring{0.5}
\AMCOpen{lines=<xsl:value-of select = "@nlines"/>}{<xsl:apply-templates />}</xsl:template>

<xsl:template match="correctchoice"> 
    <xsl:choose>
        <xsl:when test="@label">    \correctchoice[<xsl:value-of select = "@label"/>]{<xsl:value-of select = "text"/>}</xsl:when>
        <xsl:otherwise>    \correctchoice{<xsl:value-of select = "text"/>}</xsl:otherwise>
    </xsl:choose>    
</xsl:template>
  
<xsl:template match="wrongchoice"> 
    <xsl:choose>
        <xsl:when test="@label">    \wrongchoice[<xsl:value-of select = "@label"/>]{<xsl:value-of select = "text"/>}</xsl:when>
        <xsl:otherwise>    \wrongchoice{<xsl:value-of select = "text"/>}</xsl:otherwise>
    </xsl:choose>    
</xsl:template>

<!-- template for header/footer -->
<xsl:template match="header"> 
  <xsl:value-of select="text()"/>
</xsl:template>

<xsl:template match="footer"> 
  <xsl:value-of select="text()"/>
</xsl:template>

</xsl:stylesheet>
