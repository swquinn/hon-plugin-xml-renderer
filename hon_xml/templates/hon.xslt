<?xml version="1.0"?>
<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="utf-8" indent="yes" standalone="yes"/>
  <xsl:strip-space elements="*"/>

  <!--
   $add_linebreak 
   ==============
   Whether or not linebreaks should be added to the end of text in a block
   element.

   If `TRUE` the $linebreak character will be appended at the end of all
   block-level elements.
  -->
  <xsl:param name="add_linebreak" select="false()"></xsl:param>

  <!--
   $linebreak
   ==========
   The linebreak character to add to all blocks if $add_linebreak evaluates
   to a truthy statement.

   The character: &#x2028; is the unicode character for a line separator.
  -->
  <xsl:param name="linebreak">
    <xsl:text>&#x2029;</xsl:text>
  </xsl:param>

  <xsl:template match="/insert-linebreak">
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="/">
    <Root>
      <Chapter
          xmlns:aid="http://ns.adobe.com/AdobeInDesign/4.0/" 
          xmlns:aid5="http://ns.adobe.com/AdobeInDesign/5.0/">
        <Title><xsl:value-of select="/html/title"/></Title>
        <Metadata>
          <author></author>
          <Config>
            <Param name="add_linebreak" configKey="insert_linebreaks_for_blocks">
              <xsl:value-of select="$add_linebreak" />
            </Param>
            <Param name="linebreak" configKey="linebreak_character">
              <xsl:value-of select="$linebreak" />
            </Param>
          </Config>
        </Metadata>
        <Content>
          <xsl:apply-templates select="/html/body/*"/>
        </Content>
      </Chapter>
    </Root>
  </xsl:template>

  <xsl:template match="article">
    <Article>
      <xsl:apply-templates />
    </Article>
  </xsl:template>

  <xsl:template match="h1|h2|h3|h4|h5|h6">
    <xsl:element name="Header{substring(name(),2)}">
      <xsl:apply-templates />
    </xsl:element>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="p|div">
    <Paragraph>
      <xsl:apply-templates />
    </Paragraph>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="blockquote">
    <Blockquote>
      <xsl:apply-templates />
    </Blockquote>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="section">
    <ListItem>
      <xsl:apply-templates />
    </ListItem>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="hr">
    <hr />
  </xsl:template>

  <xsl:template match="ol">
    <OrderedList>
      <xsl:apply-templates />
    </OrderedList>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="ul">
    <UnorderedList>
      <xsl:apply-templates />
    </UnorderedList>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="li">
    <ListItem>
      <xsl:apply-templates />
    </ListItem>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="table">
    <Table>
      <xsl:if test="./thead">
        <TableHeader>
          <xsl:apply-templates select="./thead/tr" />
        </TableHeader>
      </xsl:if>
      <TableBody>
        <xsl:apply-templates select="./tbody/tr" />
      </TableBody>
      <xsl:if test="./tfoot">
        <TableFooter>
        </TableFooter>
      </xsl:if>
    </Table>
    <xsl:if test="$add_linebreak = true()">
      <xsl:value-of select="$linebreak" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="tr">
    <Row>
      <xsl:for-each select="./td|./th">
        <Column>
          <xsl:apply-templates />
        </Column>
      </xsl:for-each>
    </Row>
  </xsl:template>

  <xsl:template match="a">
    <Link><xsl:apply-templates /></Link>
  </xsl:template>

  <xsl:template match="b[not(i)]|strong[not(em)]">
    <Strong><xsl:apply-templates /></Strong>
  </xsl:template>

  <xsl:template match="i[not(b)]|em[not(strong)]">
    <Emphasis><xsl:apply-templates /></Emphasis>
  </xsl:template>

  <xsl:template match="em[../../strong]|strong[../../em]|i[../../b]|b[../../i]">
    <xsl:element name="StrongEmphasis">
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="code">
    <Code><xsl:apply-templates /></Code>
  </xsl:template>

  <xsl:template match="span">
    <InlineText><xsl:apply-templates /></InlineText>
  </xsl:template>

  <!--
   Templates for managing spaces, see: https://stackoverflow.com/a/11650318
  -->
  <xsl:template priority=".7" match="text()[position()=1 and not((ancestor::node()/@xml:space)[position()=last()]='preserve')]">
      <xsl:value-of select="normalize-space()"/>
      <xsl:if test="normalize-space(substring(., string-length(.))) = ''">
          <xsl:text> </xsl:text>
      </xsl:if>
  </xsl:template>

  <xsl:template priority=".7" match="text()[position()=last() and not((ancestor::node()/@xml:space)[position()=last()]='preserve')]">
      <xsl:if test="normalize-space(substring(., 1, 1)) = ''">
          <xsl:text> </xsl:text>
      </xsl:if>
      <xsl:value-of select="normalize-space()"/>
  </xsl:template>

  <xsl:template priority=".8" match="text()[position()=1 and position()=last() and not((ancestor::node()/@xml:space)[position()=last()]='preserve')]" >
      <xsl:value-of select="normalize-space(.)"/>
  </xsl:template>
</xsl:stylesheet>
