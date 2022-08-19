<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="xs tei"
    version="3.0">

    <xsl:output method="text" encoding="utf-8"/>

    <xsl:template match="/">

<!-- Des éléments ont été perdus dans le cadre de cette chaîne de traitement, notament les entrées disposant d'un nombre important
        de renvois vers des entrées d'inventaire, attention au nombre de caractère maximum autorisé par un champ csv ! -->

        <!-- Je crée un premier document associant chaque entrée à son id pour 
            permettre de faire des recherches dedans -->
        <xsl:result-document method="text" indent="no" href="index_to_csv.csv">
            <xsl:text>Entrée</xsl:text>
            <xsl:text>&#09;</xsl:text>
            <xsl:text>xml:id</xsl:text>
            <xsl:text>&#09;</xsl:text>
            <xsl:text>            
</xsl:text>
            <xsl:apply-templates select="//seg[@xml:id]" mode="resume"/>
        </xsl:result-document>
        
        <!-- Puis je crée deux documents spécifiques pour les sujets et noms  -->
<!--        <xsl:result-document method="text" indent="no" href="index_to_csv_sujets.csv">
            <xsl:call-template name="titres"/>
            <xsl:apply-templates select="//seg[term[not(@type)]]" mode="detail"/>
        </xsl:result-document>
        <xsl:result-document method="text" indent="no" href="index_to_csv_noms.csv">
            <xsl:call-template name="titres"/>
            <xsl:apply-templates select="//seg[term[@type]]" mode="detail"/>
        </xsl:result-document>-->
        
    </xsl:template>

    <!-- Ici ma ligne de titres pour les documents spécifiques -->
    <xsl:template name="titres">
        <xsl:text>Entrée</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>xml:id</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Termes retenu</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Id termes retenu</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Restitution termes retenu</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Terme générique</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Id terme générique</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Restitution terme générique</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Termes associé</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Id termes associé</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Restitution termes associé</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Idno</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>            
</xsl:text>
        <xsl:apply-templates select=".//seg[@xml:id]"/>
    </xsl:template>

    <!-- Pour éliminer tous les noeuds dont je ne me sers pas -->
    <xsl:template match="@* | node()" mode="#all"/>
    
    <!-- Ici ma transformation pour ma table d'association -->
    <xsl:template match="seg" mode="resume">
        <xsl:value-of select="normalize-space(term)"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="term/parent::seg/@xml:id"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="./term/@type"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>
</xsl:text>
    </xsl:template>

    <!-- Ici ma transformation pour mes deux fichiers complets -->
    <xsl:template match="seg[@xml:id]" mode="detail">
        <xsl:variable name="doc" select="ancestor::TEI"/>
        <xsl:variable name="corresp">
            <xsl:value-of select="@corresp"/>
        </xsl:variable>
        <xsl:variable name="prev">
            <xsl:value-of select="@prev"/>
        </xsl:variable>
        <xsl:variable name="rendition">
            <xsl:value-of select="@rendition"/>
        </xsl:variable>
        <xsl:value-of select="normalize-space(term)"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="@xml:id"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="@sameAs"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="$corresp"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:variable name="tokenize_corresp">
            <xsl:for-each select="tokenize($corresp, ' ')">
                <xsl:variable name="token">
                    <xsl:value-of select="."/>
                </xsl:variable>
                <xsl:value-of select="$doc//seg[@xml:id = $token]/term/text()/normalize-space()"/>
                <xsl:text>|</xsl:text>
            </xsl:for-each>
        </xsl:variable>
        <xsl:value-of select="$tokenize_corresp/normalize-space()"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="@ana"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="$prev"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="//seg[@xml:id = $prev]/term/text()/normalize-space()"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="@rend"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:value-of select="$rendition"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:variable name="tokenize_rendition">
            <xsl:for-each select="tokenize($rendition, ' ')">
                <xsl:variable name="token">
                    <xsl:value-of select="."/>
                </xsl:variable>
                <xsl:value-of select="$doc//seg[@xml:id = $token]/term/text()/normalize-space()"/>
                <xsl:text>|</xsl:text>
            </xsl:for-each>
        </xsl:variable>
        <xsl:value-of select="$tokenize_rendition/normalize-space()"/>
        <xsl:text>&#09;</xsl:text>
        <xsl:variable name="idno">
            <xsl:for-each select="num/idno">
                <xsl:value-of select="normalize-space(.)"/>
                <xsl:text>|</xsl:text>
            </xsl:for-each>
        </xsl:variable>
        <xsl:value-of select="$idno"/>
        <xsl:text>            
</xsl:text>
    </xsl:template>

</xsl:stylesheet>
