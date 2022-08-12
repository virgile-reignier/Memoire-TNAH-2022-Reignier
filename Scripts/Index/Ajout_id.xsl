<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="xs tei"
    version="3.0">

    <xsl:strip-space elements="idno"/>

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

    <!-- Template source permettant d'appeler tous les autres dans l'ordre du processus qu'on veut faire -->
    <xsl:template match="/">
        <xsl:variable name="index-id">
            <xsl:apply-templates mode="identify"/>
        </xsl:variable>
        <xsl:variable name="index-id-renvoi">
            <xsl:apply-templates mode="renvoi" select="$index-id"/>
        </xsl:variable>
        <xsl:variable name="index-id-corresp">
            <xsl:apply-templates mode="corresp" select="$index-id-renvoi"/>
        </xsl:variable>
        <xsl:copy-of select="$index-id-corresp"/>
    </xsl:template>

    <!-- 1 - Génération d'identifiants pour les entrées d'index -->
    <xsl:template match="seg[child::num/* or contains(term, 'v.') or following-sibling::seg]"
        mode="identify">
        <xsl:copy>
            <xsl:attribute name="xml:id">
                <xsl:value-of select="generate-id()"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <!-- 2 - Génération des associations entre les entrées -->
    <xsl:template match="seg" mode="renvoi">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>

            <!-- 2.1 On commence par traiter les termes rejetés -->
            <xsl:if test="not(child::num/*) and contains(term, 'v.')">
                <xsl:choose>

                    <!-- Ici on traite les termes rejetés contenus dans un terme spécifique -->
                    <xsl:when
                        test="contains(substring-after(term/text()/normalize-space(), ', —'), 'v.')">
                        <xsl:variable name="renvoi">
                            <xsl:choose>
                                <xsl:when
                                    test="starts-with(substring-after(substring-after(term/text()/normalize-space(), ', —'), 'v.'), ' aussi')">

                                    <xsl:value-of
                                        select="substring-after(substring-after(term/text()/normalize-space(), ', —'), 'v. aussi ')"
                                    />
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of
                                        select="substring-after(substring-after(term/text()/normalize-space(), ', —'), 'v. ')"
                                    />
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <xsl:attribute name="sameAs">
                            <xsl:for-each
                                select="string-join(tokenize(translate($renvoi, '[]:', '{}='), ', '), '|')">
                                <!-- On ne peut pas faire tenir des tokens dans une variable, il faut appliquer la fonction dans le for-each -->
                                <xsl:value-of select="."/>
                            </xsl:for-each>
                        </xsl:attribute>
                    </xsl:when>

                    <!-- Autres termes rejetés -->
                    <xsl:otherwise>
                        <xsl:variable name="renvoi">
                            <xsl:choose>
                                <xsl:when
                                    test="starts-with(substring-after(term/text()/normalize-space(), 'v.'), ' aussi')">
                                    <xsl:value-of
                                        select="substring-after(term/text()/normalize-space(), 'v. aussi ')"
                                    />
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of
                                        select="substring-after(term/text()/normalize-space(), 'v. ')"
                                    />
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <xsl:attribute name="sameAs">
                            <xsl:for-each
                                select="string-join(tokenize(translate($renvoi, '[]:', '{}='), ', '), '|')">
                                <xsl:value-of select="."/>
                            </xsl:for-each>
                        </xsl:attribute>

                    </xsl:otherwise>
                </xsl:choose>
            </xsl:if>
            <xsl:choose>

                <!-- 2.2 Puis on traite les termes spécifiques -->
                <xsl:when test="contains(term, ', —')">
                    <xsl:variable name="ref">
                        <xsl:choose>

                            <!-- Ici on traite le cas de l'imbrication des termes spécifiques -->
                            <xsl:when
                                test="contains(substring-after(term/text()/normalize-space(), ', —'), ', —')">
                                <xsl:value-of
                                    select="concat(substring-before(term/text()/normalize-space(), ' , — '), ' , — ', substring-before(substring-after(term/text()/normalize-space(), ', — '), ' , — '))"
                                />
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of
                                    select="substring-before(term/text()/normalize-space(), ' , — ')"
                                />
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:variable>
                    
                    <!-- Variable pour permettre de ne chercher que dans le div dans lequel on est -->
                    <xsl:variable name="type_index" select="ancestor::div/@n"/>
                    
                    <xsl:choose>
                        <xsl:when test="$ref != ''">
                            <!-- Permet d'éviter de faire n'importe quoi si ref devait être vide
                        On élimine également les détails inutiles des entrées d'index pointés-->
                            <xsl:attribute name="ana">
                                <xsl:choose>
                                    <xsl:when test="contains($ref, '[')">
                                        <xsl:value-of
                                            select="normalize-space(substring-before($ref, '['))"/>
                                    </xsl:when>
                                    <xsl:when test="contains($ref, 'v.')">
                                        <xsl:value-of
                                            select="translate(substring-before($ref, ' v.'), ',', '')"
                                        />
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="$ref"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:attribute>
                            <xsl:attribute name="prev">
                                <xsl:value-of
                                    select="//div[@n=$type_index]//p[seg[starts-with(term/text()/normalize-space(), $ref)]][1]/seg[starts-with(term/text()/normalize-space(), $ref)][1]/@xml:id"
                                />
                            </xsl:attribute>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:attribute name="ana">
                                <xsl:text>No Found</xsl:text>
                            </xsl:attribute>
                        </xsl:otherwise>
                    </xsl:choose>

                    <!-- Ici on traite le cas où il y a un terme associé dans un terme spécifique -->
                    <xsl:if test="child::num/* and contains(substring-after(term, ', —'), 'v.')">
                        <xsl:variable name="renvoi">
                            <xsl:choose>
                                <xsl:when
                                    test="contains(substring-after(term/text()/normalize-space(), ', —'), 'v. aussi')">
                                    <xsl:value-of
                                        select="substring-after(substring-after(term/text()/normalize-space(), ', —'), 'v. aussi ')"
                                    />
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of
                                        select="substring-after(substring-after(term/text()/normalize-space(), ', —'), 'v. ')"
                                    />
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <xsl:attribute name="rend">
                            <xsl:for-each
                                select="string-join(tokenize(translate($renvoi, '[]:', '{}='), ', '), '|')">
                                <xsl:value-of select="."/>
                            </xsl:for-each>
                        </xsl:attribute>
                    </xsl:if>

                </xsl:when>
                <xsl:otherwise>

                    <!-- 2.3 Pour finir on traite le cas des termes associés restants -->
                    <xsl:if test="child::num/* and contains(term, 'v.')">
                        <xsl:variable name="renvoi">
                            <xsl:choose>
                                <xsl:when test="contains(term, 'v. aussi')">
                                    <xsl:value-of
                                        select="substring-after(term/text()/normalize-space(), 'v. aussi ')"
                                    />
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of
                                        select="substring-after(term/text()/normalize-space(), 'v. ')"
                                    />
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <xsl:attribute name="rend">
                            <xsl:for-each
                                select="string-join(tokenize(translate($renvoi, '[]:', '{}='), ', '), '|')">
                                <xsl:value-of select="."/>
                            </xsl:for-each>
                        </xsl:attribute>
                    </xsl:if>

                </xsl:otherwise>
            </xsl:choose>

            <!-- Et bien sûr on n'oublie pas de recopier le contenu des balises -->
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>



    <!-- 3 - Récupération des id pour les termes rejetés et associés -->
    <xsl:template match="seg" mode="corresp">
        
        <!-- Variable permettant d'éviter que la recherche se fasse dans
        les deux index et ne renvoi des résultats incohérents-->
        <xsl:variable name="type_index" select="ancestor::div/@n"/>
        
        <!-- Variable nécessaire pour chercher un noeud du document dans un for-each -->
        <xsl:variable name="doc" select="ancestor::TEI"/>
        
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:if test="@sameAs">
                <xsl:variable name="tokenize">
                    <xsl:for-each select="tokenize(./@sameAs, '\|')">
                        <xsl:variable name="token">
                            <xsl:value-of select="."/>
                            <!-- La recherche de texte ne peut se faire directement sur mon token.
                            Il faut que je passe par une variable pour qu'il le considère comme une str -->
                        </xsl:variable>
                        <xsl:variable name="id_corresp">
                            <xsl:value-of
                                select="$doc//div[@n=$type_index]//p[child::seg[starts-with(lower-case(replace(term, ' , — ', ' ')), lower-case($token))]][1]/seg[starts-with(replace(lower-case(term), ' , — ', ' '), lower-case($token))][1]/@xml:id"
                            />
                        </xsl:variable>
                        <xsl:choose>
                            <xsl:when test="$id_corresp = ''">
                                <xsl:text>Not Found </xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$id_corresp"/>
                                <xsl:text> </xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:variable>
                <xsl:attribute name="corresp">
                    <xsl:value-of select="$tokenize/normalize-space()"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="@rend">
                <xsl:variable name="tokenize">
                    <xsl:for-each select="tokenize(./@rend, '\|')">
                        <xsl:variable name="token">
                            <xsl:value-of select="."/>
                        </xsl:variable>
                        <xsl:variable name="id_corresp">
                            <xsl:value-of
                                select="$doc//div[@n=$type_index]//p[child::seg[starts-with(replace(lower-case(term), ' , — ', ' '), lower-case($token))]][1]/seg[starts-with(replace(lower-case(term), ' , — ', ' '), lower-case($token))][1]/@xml:id"
                            />
                        </xsl:variable>
                        <xsl:choose>
                            <xsl:when test="$id_corresp = ''">
                                <xsl:text>Not Found </xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$id_corresp"/>
                                <xsl:text> </xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:variable>
                <xsl:attribute name="rendition">
                    <xsl:value-of select="$tokenize/normalize-space()"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <!-- "v.", "v. aussi", gérer tous les cas de figure => 
                    - faire des stats préalables
                    - définir les traitements 
                    - vérifier les stats sur ce qu'on produit -->

</xsl:stylesheet>
