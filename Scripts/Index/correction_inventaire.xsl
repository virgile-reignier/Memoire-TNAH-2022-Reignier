<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="xs tei"
    version="3.0">

    <!-- Template par défaut pour recopier tout sauf les attributs cachés de la TEI -->
    <xsl:template match="@* | node()" mode="#all">
        <xsl:choose>
            <xsl:when test="matches(name(.), '^(part|instant|anchored|default|full|status)$')"/>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates select="@* | node()" mode="#current"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Finalement inutile car ça fait perdre de l'information aux données-->
    <!--    <xsl:template match="term[contains(substring-before(text(), ', —'), '[')]">
        <xsl:variable name="entree">
            <xsl:value-of select="./term/text()/normalize-space()"/>
        </xsl:variable>
        <xsl:variable name="fin">
            <xsl:value-of select="substring-after($entree, ', —')"/>
        </xsl:variable>
        <xsl:variable name="debut">
            <xsl:value-of select="substring-before($entree, '[')"/>
        </xsl:variable>
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:choose>
                <xsl:when test="preceding-sibling::seg[starts-with(term/text(), $debut)][last()]">
                    <xsl:apply-templates select="term" mode="corrige">
                        <xsl:with-param name="corrige" select="concat($debut, ', —', $fin)"/>
                    </xsl:apply-templates>
                    <xsl:apply-templates select="num"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>-->
    
    <xsl:template match="seg[contains(substring-before(./term/text(), ', —'), 'v.')]">
        <xsl:variable name="entree">
            <xsl:value-of select="./term/text()/normalize-space()"/>
        </xsl:variable>
        <xsl:variable name="fin">
            <xsl:value-of select="substring-after($entree, ', —')"/>
        </xsl:variable>
        <xsl:variable name="debut">
            <xsl:value-of select="substring-before($entree, ', v.')"/>
        </xsl:variable>
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:choose>
                <xsl:when test="preceding-sibling::seg[starts-with(term/text(), $debut)][last()]">
                    <xsl:apply-templates select="term" mode="corrige">
                        <xsl:with-param name="corrige" select="concat($debut, ' , —', $fin)"/>
                    </xsl:apply-templates>
                    <xsl:apply-templates select="num"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="term" mode="corrige">
        <xsl:param name="corrige"/>
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:value-of select="normalize-space($corrige)"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
