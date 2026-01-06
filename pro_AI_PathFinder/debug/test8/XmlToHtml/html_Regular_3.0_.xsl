<!--
/*!
 *********************************************************************
 *  @file   : html_Regular_3.0_.xsl
 *
 *  Project : QCT SUITE
 *
 *  Package : XMLDataLogger
 *
 *  Company : QUALCOMM Incorporated
 *
 *  Purpose : Stylesheet for generating html output from XML source.
 *
 *********************************************************************
 */
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt">
  <xsl:output method="html" encoding="utf-8"/>

  <!-- this key is used to collecte all unique test index values -->
  <xsl:key name="IndexDistinct" match="Test" use="@I"/>

  <xsl:variable name="priorityCutOff">20</xsl:variable>


  <!--
  *********************************************************************************************************
                               F I R S T   P A S S   T R A N S F O R M
  *********************************************************************************************************
  -->

  <xsl:template match="TestCollection">

    <!-- store a list of all tests, for use later-->
    <xsl:variable name="alltests" select="Test"/>

    <!-- copy the TestCollection element, and copy all child elements that aren't <Test>-->
    <xsl:copy>
      <xsl:apply-templates select="*[name()!='Test']"/>

      <!-- 
        This loop executes once per unique index value, and only pays attention to the first test for each index
        If we need to act on all tests of this index, we'll use $alltests[@I=$currentInd]
      -->
      <xsl:for-each select="Test[generate-id() = generate-id(key('IndexDistinct', @I)[1])]">
        <xsl:variable name="currentInd" select="@I"/>
        <Test>

          <!-- Notice, I'm not copying the index attributes, since we want the next pass to be basically index-less -->

          <!-- assign 'fail' if any tests have a fail status, otherwise mark pass -->
          <PassFail>
            <DI>
              <N>Status</N>
              <xsl:choose>
                <xsl:when test="$alltests[@I=$currentInd]/PassFail/DI[V='FAIL']">
                  <!-- if this test returns any elements, the overall status will be fail -->
                  <V>FAIL</V>
                </xsl:when>
                <xsl:otherwise>
                  <V>PASS</V>
                </xsl:otherwise>
              </xsl:choose>
            </DI>
          </PassFail>

          <!-- assign 'fail' if any tests have a fail status, otherwise mark pass -->
          <Time>
            <Duration>
              <HH>
                <xsl:value-of select="sum($alltests[@I=$currentInd]/Time/Duration/HH)"/>
              </HH>
              <MM>
                <xsl:value-of select="sum($alltests[@I=$currentInd]/Time/Duration/MM)"/>
              </MM>
              <SS>
                <xsl:value-of select="sum($alltests[@I=$currentInd]/Time/Duration/SS)"/>
              </SS>
              <MS>
                <xsl:value-of select="sum($alltests[@I=$currentInd]/Time/Duration/MS)"/>
              </MS>
            </Duration>
          </Time>

          <!-- there's special treatment for datasetcollection, time, and passfail, for everything, just do a deep-copy everything in the first dataset -->
          <xsl:copy-of select="*[name()!='DataSetCollection' and name()!='PassFail' and name()!='Time']"/>

          <!-- go through each dataset collection and apply templates to the $alltests[@I=$currentInd] list for the current DSC position -->
          <xsl:for-each select="DataSetCollection">
            <xsl:variable name="pos" select="position()" />
            <xsl:variable name="nameCount" select="count(Name)" />
            <xsl:variable name="name"><xsl:value-of select="Name"/></xsl:variable>
            <DataSetCollection>
              <xsl:copy-of select="@*"/>
              <xsl:copy-of select="Name"/>
              <xsl:if test="$nameCount=0">
                <xsl:apply-templates select="$alltests[@I=$currentInd]/DataSetCollection[$pos]/DataSet"/>
              </xsl:if>
              <xsl:if test="$nameCount &gt; 0">
                <xsl:apply-templates select="$alltests[@I=$currentInd]/DataSetCollection[Name=$name]/DataSet"/>
              </xsl:if>
            </DataSetCollection>
          </xsl:for-each>
        </Test>
      </xsl:for-each>

      <!-- pick up all tests w/o any index attribute-->
      <xsl:apply-templates select="Test[not(@I)]"/>

    </xsl:copy>
  </xsl:template>

  <!-- Everything below here is basic boilerplate code to do a deep copy of all input elements             -->
  <!-- Add templates for specific element rules above, no need to really pay attention to what's down here -->



  <xsl:template match="source">
    <xsl:variable name="vrtfPass1Result">
      <xsl:copy>
        <xsl:apply-templates select="*"/>
      </xsl:copy>
    </xsl:variable>

    <!-- <xsl:apply-templates mode="mPass2" select="ext:node-set($vrtfPass1Result)/*"/> -->
    <xsl:apply-templates mode="mPass2" select="msxsl:node-set($vrtfPass1Result)/*"/>
  </xsl:template>


  <!-- 
  <xsl:template match="processing-instruction()">
    <xsl:copy/>
  </xsl:template>
  -->

  <xsl:template match="*">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:choose>
        <xsl:when test="*">
          <xsl:apply-templates select="*"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="."/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>









  <!--
  *********************************************************************************************************
                               S E C O N D   P A S S   T R A N S F O R M
  *********************************************************************************************************
  -->

  <xsl:template name="FindPassFail">
    <xsl:param name="list"/>
    <xsl:choose>
      <xsl:when test="$list">
        <xsl:variable name="firstStatus" select="$list[1]/DI/V"/>
        <xsl:variable name="cumStatus">
          <xsl:call-template name="FindPassFail">
            <xsl:with-param name="list" select="$list[position()!=1]"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="$cumStatus='FAIL'">FAIL</xsl:when>
          <xsl:when test="$firstStatus='FAIL'">FAIL</xsl:when>
          <xsl:otherwise>PASS</xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>PASS</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="PrintDataSetHeaders">
    <xsl:param name="ds"/>
    <xsl:if test="not(count($ds/Inputs/DI)=0)">
      <xsl:for-each select="$ds/Inputs/DI">
        <xsl:if test="count(@lp)=0 or (@lp &lt; $priorityCutOff)">
          <td bgcolor="#FFFFCC" align="center">
            <b>
              <xsl:value-of select="N"/>
              <xsl:if test="not(count(U)=0)">
                <xsl:text> (</xsl:text>
                <xsl:value-of select="U"/>
                <xsl:text>)</xsl:text>
              </xsl:if>
            </b>
          </td>
        </xsl:if>
      </xsl:for-each>
    </xsl:if>
    <xsl:for-each select="$ds/Outputs/Result">
      <xsl:if test="count(@lp)=0 or (@lp &lt; $priorityCutOff)">
        <td bgcolor="#6699CC" align="center">
          <b>
            <xsl:value-of select="DI/N"/>
            <xsl:if test="not(count(DI/U)=0)">
              <xsl:text> (</xsl:text>
              <xsl:value-of select="DI/U"/>
              <xsl:text>)</xsl:text>
            </xsl:if>
          </b>
        </td>
        <xsl:if test="not(count(Limits/Min)=0)">
          <td bgcolor="#CCCCCC" align="center">
            <b>
              <xsl:value-of select="DI/N"/>
              <xsl:text> Min</xsl:text>
            </b>
          </td>
        </xsl:if>
        <xsl:if test="not(count(Limits/Max)=0)">
          <td bgcolor="#CCCCCC" align="center">
            <b>
              <xsl:value-of select="DI/N"/>
              <xsl:text> Max</xsl:text>
            </b>
          </td>
        </xsl:if>
        <xsl:for-each select="Limits/DI">
          <td bgcolor="#CCCCCC" align="center">
            <b>
              <xsl:value-of select="N"/>
              <xsl:if test="not(count(U)=0)">
                <xsl:text> (</xsl:text>
                <xsl:value-of select="U"/>
                <xsl:text>)</xsl:text>
              </xsl:if>
            </b>
          </td>
        </xsl:for-each>
      </xsl:if>
    </xsl:for-each>
    <td bgcolor="#EEEEE0" align="center">
      <b>Time (s)</b>
    </td>
    <xsl:if test="$ds/Exceptions">
      <td bgcolor="#FFCC0000" align="center">
        <b>Exceptions</b>
      </td>
    </xsl:if>

  </xsl:template>

  <xsl:template name="PrintDataSetValues">
    <xsl:param name="dsc"/>
    <xsl:variable name="exc" select="$dsc/DataSet/Exceptions"/>
    <xsl:for-each select="$dsc/DataSet">
      <tr>
        <xsl:if test="not(count(Inputs/DI)=0)">
          <xsl:for-each select="Inputs/DI">
            <xsl:if test="count(@lp)=0 or (@lp &lt; $priorityCutOff)">
              <td align="center">
                <xsl:value-of select="V"/>
              </td>
            </xsl:if>
          </xsl:for-each>
        </xsl:if>
        <xsl:for-each select="Outputs/Result">
          <xsl:if test="count(@lp)=0 or (@lp &lt; $priorityCutOff)">
            <xsl:choose>
              <xsl:when test="Limits/PassFail/DI/V='FAIL'">
                <td bgcolor="red" align="center">
                  <xsl:value-of select="DI/V"/>
                </td>
              </xsl:when>
              <xsl:otherwise>
                <td align="center">
                  <xsl:value-of select="DI/V"/>
                </td>
              </xsl:otherwise>
            </xsl:choose>
            <xsl:if test="not(count(Limits/Min)=0)">
              <td align="center">
                <xsl:value-of select="Limits/Min"/>
              </td>
            </xsl:if>
            <xsl:if test="not(count(Limits/Max)=0)">
              <td align="center">
                <xsl:value-of select="Limits/Max"/>
              </td>
            </xsl:if>
            <xsl:for-each select="Limits/DI">
              <td align="center">
                <xsl:value-of select="V"/>
              </td>
            </xsl:for-each>
          </xsl:if>
        </xsl:for-each>
        <xsl:choose>
          <xsl:when test="@dur">
            <td align="center">
              <xsl:value-of select="format-number(@dur div 1000,'#,##0.00')"/>
            </td>
          </xsl:when>
          <xsl:otherwise>
            <td>
              <span style="color:white">-</span>
            </td>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="$exc">
          <xsl:choose>
            <xsl:when test="Exceptions">
              <td>
                <UL>
                  <xsl:for-each select="Exceptions/Exception">
                    <LI>
                      <span>
                        <xsl:value-of select="@Name"/>
                      </span>
                      <UL>
                        <xsl:if test="Description">
                          <LI>
                            <b>
                              <xsl:text>Description:  </xsl:text>
                            </b>
                            <xsl:value-of select="Description"/>
                          </LI>
                        </xsl:if>
                        <xsl:if test="@File">
                          <LI>
                            <b>
                              <xsl:text>File:  </xsl:text>
                            </b>
                            <xsl:value-of select="@File"/>
                          </LI>
                        </xsl:if>
                        <xsl:if test="@Line">
                          <LI>
                            <b>
                              <xsl:text>Line:  </xsl:text>
                            </b>
                            <xsl:value-of select="@Line"/>
                          </LI>
                        </xsl:if>
                      </UL>
                    </LI>
                  </xsl:for-each>
                </UL>
              </td>
            </xsl:when>
            <xsl:otherwise>
              <td>
                <span style='color:white'>.</span>
              </td>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </tr>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="source" mode="mPass2">


    <STYLE TYPE="text/css">
      body {
      font-family: Sans-Serif;
      }
      table { empty-cells:show; border-collapse:collapse; border-style: solid; border-color: gray; font-size: 10pt;}
      #ttfmt { border-style: none; font-size: 8pt;}
      th,td {
      padding-left: 5px;
      padding-right: 5px;
      padding-top: 1px;
      padding-bottom: 1px;
    </STYLE>

    <!--************************************************************************************************-->
    <!--                                 T E S T   C O L L E C T I O N                                  -->
    <!--************************************************************************************************-->
    <xsl:for-each select="TestCollection">
      <HR COLOR="#6699CC" SIZE="10"/>

      <big>
        <big>
          <big>
            <b>
              <xsl:text>Test Report:  </xsl:text>
              <xsl:value-of select="Name"/>
            </b>
          </big>
        </big>
      </big>
      <br/>
      <br/>
      <big>
        <b>
          <xsl:text>UUT ID:  </xsl:text>
          <xsl:value-of select="UUT/ID"/>
        </b>
      </big>
      <br/>
      <xsl:if test="not(count(PassFail)=0)">
        <big>
          <b>
            <xsl:value-of select="PassFail/DI/N"/>
            <xsl:text>:  </xsl:text>
            <xsl:value-of select="PassFail/DI/V"/>
          </b>
        </big>
        <br/>
      </xsl:if>
      <b>
        <xsl:text>Date:  </xsl:text>
        <xsl:value-of select="Date/MM"/>
        <xsl:text>/</xsl:text>
        <xsl:value-of select="Date/DD"/>
        <xsl:text>/</xsl:text>
        <xsl:value-of select="Date/YYYY"/>
      </b>
      <br/>
      <br/>


      <!--TOC-->
      <a>
        <xsl:attribute name="name">TOC</xsl:attribute>
      </a>
      <HR COLOR="#6699CC" SIZE="2"/>
      <big>
        <big>
          <b>
            <xsl:text>Table of Contents</xsl:text>
          </b>
        </big>
      </big>
      <UL>
        <table border="1">
          <tr>
            <td bgcolor="#CCCCCC">
              <b>Test Name</b>
            </td>
            <td bgcolor="#CCCCCC">
              <b>Status</b>
            </td>
            <td bgcolor="#CCCCCC">
              <b>Duration (s)</b>
            </td>
          </tr>
          <xsl:for-each select="Test">
            <xsl:variable name="pf">
              <xsl:call-template name="FindPassFail">
                <xsl:with-param name="list" select="PassFail"/>
              </xsl:call-template>
            </xsl:variable>
            <tr>
              <xsl:choose>
                <xsl:when test="not(count(ExtendedName)=0)">
                  <td>
                    <a>
                      <xsl:attribute name="href">
                        #<xsl:value-of select="position()"/>
                      </xsl:attribute>
                      <xsl:value-of select="ExtendedName"/>
                    </a>
                  </td>
                </xsl:when>
                <xsl:otherwise>
                  <td>
                    <a>
                      <xsl:attribute name="href">
                        #<xsl:value-of select="position()"/>
                      </xsl:attribute>
                      <xsl:value-of select="Name"/>
                    </a>
                  </td>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:choose>
                <xsl:when test="$pf='PASS'">
                  <td bgcolor="#00CC00">PASS</td>
                </xsl:when>
                <xsl:otherwise>
                  <td bgcolor="red">FAIL</td>
                </xsl:otherwise>
              </xsl:choose>
              <td>
                <xsl:value-of select='format-number( Time/Duration/HH * 3600 + Time/Duration/MM * 60 + Time/Duration/SS + Time/Duration/MS div 1000.0 ,"##0.00" )'/>
              </td>
            </tr>
          </xsl:for-each>
        </table>
      </UL>

      <!--************************************************************************************************-->
      <!--                        T E S T   C O L L E C T I O N   D A T E   A N D   T I M E               -->
      <!--************************************************************************************************-->
      <table id="ttfmt">
        <tr>
          <td>
            <UL>
              <b>
                <xsl:text>Additional Test Run Data</xsl:text>
              </b>
              <UL>

                <xsl:if test="not(count(Time)=0)">
                  <LI>
                    <xsl:text>Test Time...</xsl:text>
                    <UL>
                      <LI>
                        <xsl:text>Start Time:  </xsl:text>
                        <xsl:value-of select="Time/Start/HH"/>
                        <xsl:text>:</xsl:text>
                        <xsl:value-of select="Time/Start/MM"/>
                        <xsl:text>:</xsl:text>
                        <xsl:value-of select="Time/Start/SS"/>
                        <xsl:if test="not(count(Time/Start/AMPM)=0)">
                          <xsl:value-of select="Time/Start/AMPM"/>
                        </xsl:if>
                      </LI>
                      <LI>
                        <xsl:text>Stop Time:  </xsl:text>
                        <xsl:value-of select="Time/Stop/HH"/>
                        <xsl:text>:</xsl:text>
                        <xsl:value-of select="Time/Stop/MM"/>
                        <xsl:text>:</xsl:text>
                        <xsl:value-of select="Time/Stop/SS"/>
                        <xsl:if test="not(count(Time/Stop/AMPM)=0)">
                          <xsl:value-of select="Time/Stop/AMPM"/>
                        </xsl:if>
                      </LI>
                      <LI>
                        <xsl:text>Duration:  </xsl:text>
                        <xsl:value-of select="Time/Duration/HH"/>
                        <xsl:text>:</xsl:text>
                        <xsl:value-of select="Time/Duration/MM"/>
                        <xsl:text>:</xsl:text>
                        <xsl:value-of select="Time/Duration/SS"/>
                        <xsl:if test="not(count(Time/Duration/MS)=0)">
                          <xsl:text>  </xsl:text>
                          <xsl:value-of select="Time/Duration/MS"/>
                          <xsl:text>ms</xsl:text>
                        </xsl:if>
                      </LI>
                    </UL>
                  </LI>
                </xsl:if>
              </UL>

              <!--************************************************************************************************-->
              <!--                                             U U T                                              -->
              <!--************************************************************************************************-->
              <UL>
                <LI>
                  <span>
                    <xsl:text>UUT Information...</xsl:text>
                  </span>
                  <UL>
                    <LI>
                      <xsl:text>UUT ID:  </xsl:text>
                      <xsl:value-of select="UUT/ID"/>
                    </LI>
                    <xsl:if test="not(count(UUT/Type)=0)">
                      <LI>
                        <xsl:text>UUT Type:  </xsl:text>
                        <xsl:value-of select="UUT/Type"/>
                      </LI>
                    </xsl:if>
                    <xsl:if test="not(count(UUT/SWBuildID)=0)">
                      <LI>
                        <xsl:text>SW Build ID:  </xsl:text>
                        <xsl:value-of select="UUT/SWBuildID"/>
                      </LI>
                    </xsl:if>
                    <xsl:if test="not(count(UUT/RFCalNVTracking)=0)">
                      <LI>
                        <span>
                          <xsl:text>RFCal NV Tracking...</xsl:text>
                        </span>
                        <UL>
                          <xsl:for-each select="UUT/RFCalNVTracking/DI">
                            <LI>
                              <xsl:value-of select="N"/>
                              <xsl:text>:  </xsl:text>
                              <xsl:value-of select="V"/>
                            </LI>
                          </xsl:for-each>
                        </UL>
                      </LI>
                    </xsl:if>

                  </UL>
                </LI>
              </UL>
              <!--************************************************************************************************-->
              <!--                                             X T T                                              -->
              <!--************************************************************************************************-->
              <UL>
                <LI>
                  <span>
                    <xsl:text>XTT Information...</xsl:text>
                  </span>
                  <UL>
                    <LI>
                      <xsl:text>XTT :  </xsl:text>
                      <xsl:value-of select="Image/Filename"/>
                    </LI>
                  </UL>

                </LI>

              </UL>
              <!--************************************************************************************************-->
              <!--                                          T E S T E R                                           -->
              <!--************************************************************************************************-->
              <UL>
                <LI>
                  <span>
                    <xsl:text>Test Station Information...</xsl:text>
                  </span>
                  <UL>
                    <LI>
                      <xsl:text>Name:  </xsl:text>
                      <xsl:value-of select="Tester/Name"/>
                    </LI>
                    <LI>
                      <xsl:text>Type:  </xsl:text>
                      <xsl:value-of select="Tester/Type"/>
                    </LI>
                    <xsl:if test="not(count(Tester/EquipmentConfig)=0)">
                      <LI>
                        <span>
                          <xsl:text>Equipment Configuration...</xsl:text>
                        </span>
                        <UL>
                          <xsl:for-each select="Tester/EquipmentConfig/DI">
                            <LI>
                              <xsl:value-of select="N"/>
                              <xsl:text>:  </xsl:text>
                              <xsl:value-of select="V"/>
                            </LI>
                          </xsl:for-each>
                        </UL>
                      </LI>
                    </xsl:if>
                    <xsl:if test="not(count(Tester/PCConfig)=0)">
                      <LI>
                        <span>
                          <xsl:text>PC Configuration...</xsl:text>
                        </span>
                        <UL>
                          <xsl:for-each select="Tester/PCConfig/DI">
                            <LI>
                              <xsl:value-of select="N"/>
                              <xsl:text>:  </xsl:text>
                              <xsl:value-of select="V"/>
                            </LI>
                          </xsl:for-each>
                        </UL>
                      </LI>
                    </xsl:if>
                    <xsl:if test="not(count(Tester/SWConfigInfo)=0)">
                      <LI>
                        <span>
                          <xsl:text>Software Configuration...</xsl:text>
                        </span>
                        <UL>
                          <xsl:for-each select="Tester/SWConfigInfo/Versions/DI">
                            <LI>
                              <xsl:value-of select="N"/>
                              <xsl:text>:  </xsl:text>
                              <xsl:value-of select="V"/>
                            </LI>
                          </xsl:for-each>
                        </UL>
                      </LI>
                    </xsl:if>
                  </UL>
                </LI>
              </UL>

              <!--************************************************************************************************-->
              <!--                         T E S T   C O L L E C T I O N   M E S S A G E                          -->
              <!--************************************************************************************************-->
              <xsl:if test="not(count(Message)=0)">
                <UL>
                  <LI>
                    <span>
                      <xsl:text>Test Collection Messages...</xsl:text>
                    </span>
                    <UL>
                      <xsl:for-each select="Message/DI">
                        <LI>
                          <xsl:value-of select="N"/>
                          <xsl:text>:  </xsl:text>
                          <xsl:value-of select="V"/>
                        </LI>
                      </xsl:for-each>
                    </UL>
                  </LI>
                </UL>
              </xsl:if>

            </UL>
          </td>

        </tr>
      </table>


      <!--************************************************************************************************-->
      <!--                                            T E S T                                             -->
      <!--************************************************************************************************-->
      <xsl:for-each select="Test">
        <xsl:if test="count(@lp)=0 or (@lp &lt; $priorityCutOff)">
          <a>
            <xsl:attribute name="name">
              <xsl:value-of select="position()"/>
            </xsl:attribute>
          </a>
          <HR COLOR="#6699CC" SIZE="2"/>
          <xsl:choose>
            <xsl:when test="not(count(ExtendedName)=0)">
              <big>
                <big>
                  <b>
                    <xsl:value-of select="ExtendedName"/>
                  </b>
                </big>
              </big>
            </xsl:when>
            <xsl:otherwise>
              <big>
                <big>
                  <b>
                    <xsl:value-of select="Name"/>
                  </b>
                </big>
              </big>
            </xsl:otherwise>
          </xsl:choose>



          <!--************************************************************************************************-->
          <!--                                  T E S T   P A S S / F A I L                                   -->
          <!--************************************************************************************************-->
          <xsl:if test="not(count(PassFail)=0)">
            <UL>
              <big>
                <b>
                  <xsl:value-of select="PassFail/DI/N"/>
                  <xsl:text>:  </xsl:text>
                </b>
              </big>

              <xsl:choose>
                <xsl:when test="PassFail/DI/V='FAIL'">
                  <big>
                    <b>
                      <span style='color:red'>FAIL</span>
                    </b>
                  </big>
                </xsl:when>
                <xsl:when test="PassFail/DI/V='PASS'">
                  <big>
                    <b>
                      <span style='color:#00CC00'>PASS</span>
                    </b>
                  </big>
                </xsl:when>
                <xsl:otherwise>
                  <big>
                    <b>
                      <xsl:value-of select="PassFail/DI/V"/>
                    </b>
                  </big>
                </xsl:otherwise>
              </xsl:choose>
            </UL>
          </xsl:if>

          <!--************************************************************************************************-->
          <!--                              D A T A S E T   C O L L E C T I O N                               -->
          <!--************************************************************************************************-->
          <xsl:for-each select="DataSetCollection">
            <xsl:if test="not(count(Name)=0)">
              <br/>
              <br/>
              <b>
                <xsl:value-of select="Name"/>
              </b>
            </xsl:if>


            <!--************************************************************************************************-->
            <!--                      D A T A S E T   C O L L E C T I O N   M E S S A G E                       -->
            <!--************************************************************************************************-->
            <xsl:if test="not(count(Message)=0)">
              <br/>
              <UL>
                <xsl:for-each select="Message/DI">
                  <LI>
                    <xsl:value-of select="N"/>
                    <xsl:text>:  </xsl:text>
                    <xsl:value-of select="V"/>
                  </LI>
                </xsl:for-each>
              </UL>
            </xsl:if>


            <!--************************************************************************************************-->
            <!--                                 D A T A S E T   H E A D E R S                                  -->
            <!--************************************************************************************************-->
            <UL>
              <table border="1">
                <tr>
                  <xsl:call-template name="PrintDataSetHeaders">
                    <xsl:with-param name="ds" select="DataSet[1]"/>
                  </xsl:call-template>
                </tr>


                <!--************************************************************************************************-->
                <!--                                  D A T A S E T   V A L U E S                                   -->
                <!--************************************************************************************************-->
                <xsl:call-template name="PrintDataSetValues">
                  <xsl:with-param name="dsc" select="."/>
                </xsl:call-template>
              </table>
            </UL>
            <br/>
          </xsl:for-each>

          <!--          <table id="ttfmt">
            <tr>
              <td> -->
          Duration: <xsl:value-of select='format-number( Time/Duration/HH * 3600 + Time/Duration/MM * 60 + Time/Duration/SS + Time/Duration/MS div 1000.0 ,"##0.00" )'/> (s)
          <!--              </td>
            </tr>
          </table> -->
          <br/><br/>

          <a>
            <xsl:attribute name="href">#TOC</xsl:attribute>Back to top
          </a>
        </xsl:if>
      </xsl:for-each>
      <!-- Test -->
      <HR COLOR="#6699CC" SIZE="2"/>

    </xsl:for-each>
    <!-- TestCollection -->

  </xsl:template>
</xsl:stylesheet>
