<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml" indent="yes" encoding="UTF-8"/>


<!-- remove html element --> 
<xsl:template match="html"><xsl:apply-templates/></xsl:template>
<xsl:template match="body"><xsl:apply-templates/></xsl:template>
  
<!-- template identité -->
<xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
</xsl:template>

<!-- itemize / ennumerate -->
 <xsl:template match="ul"> 
\begin{itemize}
<xsl:apply-templates/>
\end{itemize} 
</xsl:template>

<xsl:template match="ol"> 
\begin{enumerate}
<xsl:apply-templates/>
\end{enumerate} 
</xsl:template>
  
<xsl:template match="li">  \item <xsl:apply-templates/>
</xsl:template>


<!--
<p style="text-align: center;">centered text</p><p style="text-align: left;">flush left text</p><p style="text-align: right;">flush right text</p><p style="text-align: left;">
-->
<xsl:template match="p[@style='text-align: center;']">
\begin{center}
    <xsl:apply-templates/>
\end{center}
</xsl:template>

<xsl:template match="p[@style='text-align: right;']">
\begin{flushright}
    <xsl:apply-templates/>
\end{flushright}
</xsl:template>

<xsl:template match="p[@style='text-align: left;']">
<!-- latex default -->
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="p">
    <xsl:apply-templates/>
</xsl:template>

<!-- exponent and indicies in text -->
<xsl:template match="sup">\textsuperscript{<xsl:apply-templates/>}</xsl:template>

<xsl:template match="sub">\textsubscript{<xsl:apply-templates/>}</xsl:template>



<!-- font style -->
<xsl:template match="b">\textbf{<xsl:apply-templates/>}</xsl:template>

<xsl:template match="i">\textit{<xsl:apply-templates/>}</xsl:template>

<xsl:template match="u">\underline{<xsl:apply-templates/>}</xsl:template>

<xsl:template match="em">\emph{<xsl:apply-templates/>}</xsl:template>
<!-- require ulem package -->
<xsl:template match="strike">\sout{<xsl:apply-templates/>}</xsl:template>


<!-- code style -->
<xsl:template match="pre"> 
\begin{alltt}
<xsl:apply-templates/>
\end{alltt}
</xsl:template>

<xsl:template match="code"> 
\begin{alltt}
<xsl:apply-templates/>
\end{alltt}
</xsl:template>

<!-- template for simple table -->
<xsl:template match="table">        
\begin{center}
<!-- get number of column (not very robust), based on header, not sur it is always present -->			
<!--  \begin{tabular}{<xsl:for-each select="//tbody/td[@scope='col']">c</xsl:for-each>}-->
<!-- get number of column (not very robust), based on number of col of 1st body line-->	
  \begin{tabular}{<xsl:for-each select="tbody/tr[1]/td | tbody/tr[1]/th">c</xsl:for-each>}
  \hline
  <xsl:apply-templates/>	
  \end{tabular}\\
 <!-- table caption, keep -->
<xsl:value-of select = "caption"/>
\end{center}
 </xsl:template>
 
 
<!-- blocks -->
<xsl:template match="thead | tbody">
	<xsl:apply-templates/>  \hline
</xsl:template>


<!-- detect raw and loop -->
<xsl:template match="tr">
  <!-- no distinction between raw element and raw header -->
  <xsl:for-each select="td | th">
      <xsl:choose>
          <!-- no & -->
		  <xsl:when test="position() = last()"><xsl:apply-templates/></xsl:when>
		   <!-- add & -->
		   <xsl:otherwise><xsl:apply-templates/> &amp; </xsl:otherwise>
	  </xsl:choose>	  
  </xsl:for-each>\\   
</xsl:template>

<xsl:template match="table/caption">
</xsl:template>

<!-- link -->
<xsl:template match="a[@href]">\href{<xsl:value-of select = "@href"/>}{<xsl:apply-templates/>} </xsl:template>


<!-- img 
 <img src="@@PLUGINFILE@@/4.png" alt="" role="presentation" style="">
  -->
<xsl:strip-space elements="img" />  
<xsl:template match="img">\includegraphics[<xsl:choose>
				   <xsl:when test="@width">
					   <xsl:choose>
					      <xsl:when test="contains(@width, 'pt') or contains(@width, 'px')">width=<xsl:value-of select = "@width"/></xsl:when>
					      <xsl:otherwise>width=<xsl:value-of select = "@width"/>px</xsl:otherwise>
					   </xsl:choose>
				  </xsl:when>
				    <xsl:when test="@height">
					   <xsl:choose>
					      <xsl:when test="contains(@height, 'pt') or contains(@height, 'px')">height=<xsl:value-of select = "@height"/></xsl:when>
					      <xsl:otherwise>height=<xsl:value-of select = "@height"/>px</xsl:otherwise>
					   </xsl:choose>
				    </xsl:when>
				    <!-- nothing -->
				  <xsl:otherwise></xsl:otherwise>
			 </xsl:choose>]{<xsl:value-of select = "@src"/>} </xsl:template>

<xsl:template match="picture"><xsl:apply-templates/></xsl:template>

</xsl:stylesheet>
