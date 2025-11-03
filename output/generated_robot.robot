<?xml version="1.0" encoding="UTF-8"?>
<object class="Robot" serializationversion="2">
  <prologue>
    <saved-by-versions>
      <version>11.3.0.1</version>
    </saved-by-versions>
    <file-type>robot</file-type>
    <referenced-types />
    <triggers />
    <sub-robots />
    <device-mappings />
    <comment />
    <tags />
    <referenced-snippets />
    <typed-variables>  </typed-variables>
    <parameters />
    <return-variables />
    <store-in-database-variables />
    <browser-engine>WEBKIT</browser-engine>
  </prologue>
  <!--
        
        -->
  <property name="variables" class="Variables">  <object
      class="Variable" serializationversion="1">
      <property name="name" class="String" id="var_1">A</property>
      <property name="initialAssignment" class="InitialVariableAssignment">  <property name="type" class="SimpleTypeReference">
          <property name="simpleTypeId" class="Integer">12</property>
        </property>
     </property>
    </object>  <object
      class="Variable" serializationversion="1">
      <property name="name" class="String" id="var_2">Excel</property>
      <property name="initialAssignment" class="InitialVariableAssignment">  <property name="type" class="SimpleTypeReference">
          <property name="simpleTypeId" class="Integer">150</property>
        </property>
     </property>
    </object>  <object
      class="Variable" serializationversion="1">
      <property name="name" class="String" id="var_3">Column1Data</property>
      <property name="initialAssignment" class="InitialVariableAssignment">  <property name="type" class="SimpleTypeReference">
          <property name="simpleTypeId" class="Integer">12</property>
        </property>
     </property>
    </object>  <object
      class="Variable" serializationversion="1">
      <property name="name" class="String" id="var_4">Column7Data</property>
      <property name="initialAssignment" class="InitialVariableAssignment">  <property name="type" class="SimpleTypeReference">
          <property name="simpleTypeId" class="Integer">12</property>
        </property>
     </property>
    </object>  <object
      class="Variable" serializationversion="1">
      <property name="name" class="String" id="var_5">DatabaseConnection</property>
      <property name="initialAssignment" class="InitialVariableAssignment">  <property name="type" class="SimpleTypeReference">
          <property name="simpleTypeId" class="Integer">12</property>
        </property>
     </property>
    </object>  </property>

  <property name="proxyServerConfiguration" class="ProxyServerConfiguration"
    serializationversion="0" />
  <property name="httpClientType" class="HttpClientType">
    <property name="enum-name" class="String">WEBKIT</property>
  </property>
  <property name="ntlmAuthentication" class="NTLMAuthenticationType">
    <property name="enum-name" class="String">STANDARD</property>
  </property>
  <property name="usePre96DefaultWaiting" class="Boolean" id="1">false</property>
  <property name="maxWaitForTimeout" class="Integer">10000</property>
  <property name="waitRealTime" idref="1" />
  <property name="privateHTTPCacheEnabled" class="Boolean" id="2">true</property>
  <property name="privateHTTPCacheSize" class="Integer">2048</property>
  <property name="comment">
    <null />
  </property>
  <property name="tags" class="RobotTagList" />
  <property name="humanProcessingTime">
    <null />
  </property>
  <property name="executionMode" class="ExecutionMode">
    <property name="enum-name" class="String">FULL</property>
  </property>
  <property name="avoidExternalReExecution" idref="1" />

  <property name="transitionGraph" class="Body">
    <blockBeginStep class="BlockBeginStep" id="block_begin" />
    <steps class="ArrayList">  
         
      
        
       <object
        class="Transition" serializationversion="3" id="step_1_load">
        <property name="stepAction" class="LoadFile">
          <property name="fileNameExpression"
            class="kapow.robot.plugin.common.support.expression.multipletype.VariableExpression"
            serializationversion="2">
            <property name="variable"
              class="kapow.robot.plugin.common.support.AttributeName2">
              <property name="name" class="String">{{ A }}</property>
            </property>
          </property>
          <property name="output"
            class="kapow.robot.plugin.common.stateprocessor.rest.ToVariableOutputSpecification"
            serializationversion="1">
            <property name="variable"
              class="kapow.robot.plugin.common.support.AttributeName2">
              <property name="name" class="String">var_2</property>
            </property>
          </property>
          <property name="browserConfigurationSpecification"
            class="BrowserConfigurationSpecificationWebKit" serializationversion="27">
            <property name="ancestorProvider"
              class="BrowserConfigurationSpecificationAncestorProviderForStep" />
          </property>
        </property>
      </object>
        
        <object
        class="Transition" serializationversion="3" id="step_2_open">
        <property name="name" class="String">Open_Excel</property>
            <property
          name="stepAction"
          class="OpenVariable">
          <property name="variable"
            class="kapow.robot.plugin.common.support.AttributeName2">  <property name="name"
              idref="var_2" />  </property>
        </property>
            <property
          name="elementFinders" class="ElementFinders" />
            <property name="errorHandler"
          class="ErrorHandler" serializationversion="0" />
            <property name="comment">
          <null />
        </property>  <property name="enabled"
          class="Boolean">true</property>  <property name="changedProperties"
          class="java.util.HashSet" />
      </object>   
      
        
        
         
       <object
class="Transition" serializationversion="3" id="step_3_loop">
<property name="name" class="String">Loop_Columns_Rows</property>
<property name="stepAction" class="LoopInExcel">
<property name="loopDirection" class="LoopInExcel$LoopDirection">
<property name="enum-name" class="String">ROWS</property>
</property>
</property>
<property name="elementFinders" class="ElementFinders">
<object class="ExcelElementFinder">  <property name="detail" class="SpecifiedRangeCellFinderDetail">
<property name="range"
class="kapow.robot.plugin.common.support.expression.stringexpr.ValueStringExpression">
<property name="value" class="String">A1:G100</property>
</property>
<property name="usage" class="RowFromRange">
<property name="rowId" class="ByIndexExcelRowId">
<property name="offset" class="kapow.robot.plugin.common.support.expression.integerexpr.ValueIntegerExpression">
<property name="value" class="Integer">0</property>
</property>
</property>
</property>
</property>
 </object>
</property>
<property name="errorHandler" class="ErrorHandler" serializationversion="0" />
<property name="comment">
<null />
</property>
<property name="enabled" class="Boolean">true</property>
<property name="changedProperties" class="java.util.HashSet" />
</object> 
        
        
          <object
        class="Transition" serializationversion="3" id="step_4_extract_col1">
        <property name="name" class="String">Extract_Column1</property>
        <property name="stepAction" class="ExtractCell" />
        <property name="elementFinders" class="ElementFinders">
          <object class="ExcelElementFinder">  <property name="detail" class="SpecifiedRangeCellFinderDetail">
              <property name="range"
                class="kapow.robot.plugin.common.support.expression.stringexpr.ValueStringExpression">
                <property name="value" class="String">A1</property>
              </property>
              <property name="usage" class="CellFromRange">  <property name="columnId"
                  class="ByIndexExcelColumnId">
                  <property name="offset"
                    class="kapow.robot.plugin.common.support.expression.integerexpr.ValueIntegerExpression">
                    <property name="value" class="Integer">1</property>
                  </property>
                </property>
        <property name="rowId"
                  class="ByIndexExcelRowId">
                  <property name="offset"
                    class="kapow.robot.plugin.common.support.expression.integerexpr.ValueIntegerExpression">
                    <property name="value" class="Integer">1</property>
                  </property>
                </property>
       </property>
            </property>  </object>
        </property>

        <property name="errorHandler" class="ErrorHandler" serializationversion="0" />
        <property name="comment">
          <null />
        </property>
        <property name="enabled" class="Boolean">true</property>
        <property name="changedProperties" class="java.util.HashSet" />
      </object> 
      
        
        
          <object
        class="Transition" serializationversion="3" id="step_5_extract_col7">
        <property name="name" class="String">Extract_Column7</property>
        <property name="stepAction" class="ExtractCell" />
        <property name="elementFinders" class="ElementFinders">
          <object class="ExcelElementFinder">  <property name="detail" class="SpecifiedRangeCellFinderDetail">
              <property name="range"
                class="kapow.robot.plugin.common.support.expression.stringexpr.ValueStringExpression">
                <property name="value" class="String">G1</property>
              </property>
              <property name="usage" class="CellFromRange">  <property name="columnId"
                  class="ByIndexExcelColumnId">
                  <property name="offset"
                    class="kapow.robot.plugin.common.support.expression.integerexpr.ValueIntegerExpression">
                    <property name="value" class="Integer">7</property>
                  </property>
                </property>
        <property name="rowId"
                  class="ByIndexExcelRowId">
                  <property name="offset"
                    class="kapow.robot.plugin.common.support.expression.integerexpr.ValueIntegerExpression">
                    <property name="value" class="Integer">1</property>
                  </property>
                </property>
       </property>
            </property>  </object>
        </property>

        <property name="errorHandler" class="ErrorHandler" serializationversion="0" />
        <property name="comment">
          <null />
        </property>
        <property name="enabled" class="Boolean">true</property>
        <property name="changedProperties" class="java.util.HashSet" />
      </object> 
      
        
        
         
      
         <object class="Transition"
        serializationversion="3" id="step_6_insert">
        <property name="name" class="String">Insert_to_Database</property>
        <property name="stepAction" class="QueryDatabase2" serializationversion="2">
          <property name="databaseName"
            class="kapow.robot.plugin.common.support.expression.stringexpr.DBNameValueStringExpression">
            <property name="value" class="kapow.util.db.DBName">  <property name="name"
                idref="var_5" />  </property>
          </property>
          <property name="sql" class="String">INSERT INTO extracted_columns (column1, column7) VALUES ({{ Column1Data }}, {{ Column7Data }})</property>
          <property name="columnAttributeMappings"
            class="kapow.robot.plugin.common.support.database.ColumnAttributeMappings">  </property>
        </property>
        <property name="elementFinders" class="ElementFinders" />
        <property name="errorHandler" class="ErrorHandler" serializationversion="0">
          <property name="changedProperties" class="java.util.HashSet">
            <element class="String">reportingViaAPI</element>
            <element class="String">reportingViaLog</element>
          </property>
          <property name="reportingViaAPI" class="Boolean">false</property>
          <property name="reportingViaLog" class="Boolean">false</property>
        </property>
        <property name="comment">
          <null />
        </property>
        <property name="enabled" class="Boolean">true</property>
        <property name="changedProperties" class="java.util.HashSet" />
      </object> 
        
       <object class="End" id="step_7_end" />    
      
        
        </steps>

    <blockEndStep class="BlockEndStep" />
    <edges class="ArrayList">  <object class="TransitionEdge">
        <from idref="step_1_load" />
        <to idref="step_2_open" />
        <name />
        <comment />
      </object>  <object class="TransitionEdge">
        <from idref="step_2_open" />
        <to idref="step_3_loop" />
        <name />
        <comment />
      </object>  <object class="TransitionEdge">
        <from idref="step_3_loop" />
        <to idref="step_4_extract_col1" />
        <name />
        <comment />
      </object>  <object class="TransitionEdge">
        <from idref="step_4_extract_col1" />
        <to idref="step_5_extract_col7" />
        <name />
        <comment />
      </object>  <object class="TransitionEdge">
        <from idref="step_5_extract_col7" />
        <to idref="step_6_insert" />
        <name />
        <comment />
      </object>  <object class="TransitionEdge">
        <from idref="step_6_insert" />
        <to idref="step_7_end" />
        <name />
        <comment />
      </object>  </edges>
  </property>

  <property name="browserConfigurationSpecification"
    class="BrowserConfigurationSpecificationWebKit"
    serializationversion="27" />
</object>
