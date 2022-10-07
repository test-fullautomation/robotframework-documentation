# **************************************************************************************************************
#
#  Copyright 2020-2022 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# **************************************************************************************************************
#
# CMainDocConfig.py
#
# XC-CT/ECA3-Queckenstedt
#
# 29.09.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing the configuration for the RobotFramework AIO configuration.
This includes the repository configuration and command line values.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, platform, json, argparse
import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLNY = col.Style.NORMAL + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

class CMainDocConfig():

   def __init__(self, oRepositoryConfig=None):
      """
Constructor of class ``CMainDocConfig``.

Responsible for:

* Take over the repository configuration
* Read the MainDoc configuration from json file
* Resolve placeholders used in MainDoc configuration
* Prepare runtime variables

* ``oRepositoryConfig``

  / *Condition*: required / *Type*: CRepositoryConfig() /

  GenMainDoc configuration containing static and dynamic configuration values (this includes the
  Repository configuration).
      """

      sMethod = "CMainDocConfig.__init__"

      self.__dictMainDocConfig = None  # self.__dictConfig

      if oRepositoryConfig is None:
         bSuccess = None
         sResult  = "oRepositoryConfig is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # get repository configuration
      dictRepositoryConfig = oRepositoryConfig.GetConfig()

      # read the documentation build configuration from separate json file
      #    - the path to the folder containing this json file is taken out of the repository configuration
      #    - the name of the json file is fix
      sJsonFileName = "maindoc_config.json"
      sDocumentationProjectConfigFile = f"{dictRepositoryConfig['PACKAGEDOC']}/{sJsonFileName}"
      # print(f"========== sDocumentationProjectConfigFile : '{sDocumentationProjectConfigFile}'")

      # The json file may contain lines that are commented out by a '#' at the beginning of the line.
      # Therefore we read in this file in text format, remove the comments and save the cleaned file within the temp folder.
      # Now it's a valid json file and we read the file from there.

      sTmpPath = None
      sPlatformSystem = platform.system()
      if sPlatformSystem == "Windows":
         sTmpPath = CString.NormalizePath("%TMP%")
      elif sPlatformSystem == "Linux":
         sTmpPath = "/tmp"
      else:
         bSuccess = None
         sResult  = f"Platform system '{sPlatformSystem}' is not supported"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      sJsonFileCleaned = f"{sTmpPath}/{sJsonFileName}"
      # print(f"========== sJsonFileCleaned : '{sJsonFileCleaned}'")

      oJsonFileSource = CFile(sDocumentationProjectConfigFile)
      listLines, bSuccess, sResult = oJsonFileSource.ReadLines(bSkipBlankLines=True, sComment='#')
      del oJsonFileSource
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      oJsonFileCleaned = CFile(sJsonFileCleaned)
      bSuccess, sResult = oJsonFileCleaned.Write(listLines)
      del oJsonFileCleaned
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # TODO: try/except
      dictJsonValues = None # dictDocConfig
      hDocumentationProjectConfigFile = open(sJsonFileCleaned)
      dictJsonValues = json.load(hDocumentationProjectConfigFile)
      hDocumentationProjectConfigFile.close()

      # initialize the documentation build configuration including the repository configuration (with placeholders resolved)
      # ( not yet: together with command line parameters. Command overwrites all other values.)
      self.__dictMainDocConfig = {}

      # take over keys and values from repository configuration
      for key, value in dictRepositoryConfig.items():
         self.__dictMainDocConfig[key] = value

      # take over keys and values from maindocumentation build configuration
      for key, value in dictJsonValues.items():
         self.__dictMainDocConfig[key] = value

      # add current timestamp
      self.__dictMainDocConfig['NOW'] = time.strftime('%d.%m.%Y - %H:%M:%S')

      # -- the absolute path that is reference for all relative paths
      sReferencePathAbs = self.__dictMainDocConfig['PACKAGEDOC'] # set initially in repository config and already normalized

      # normalize paths in 'IMPORTS' section
      listImports = []
      for sImport in self.__dictMainDocConfig['IMPORTS']:
         sImport = CString.NormalizePath(sPath=sImport, sReferencePathAbs=sReferencePathAbs)
         listImports.append(sImport)
      self.__dictMainDocConfig['IMPORTS'] = listImports

      # normalize path in 'BOOKSOURCES' section
      self.__dictMainDocConfig['BOOKSOURCES'] = CString.NormalizePath(sPath=self.__dictMainDocConfig['BOOKSOURCES'], sReferencePathAbs=sReferencePathAbs)

      # -- prepare path to LaTeX interpreter
      sLaTeXInterpreter = None
      sKey = sPlatformSystem.upper()
      if sKey in self.__dictMainDocConfig['TEX']:
         sLaTeXInterpreter = CString.NormalizePath(sPath=self.__dictMainDocConfig['TEX'][sKey], sReferencePathAbs=sReferencePathAbs)
      self.__dictMainDocConfig['LATEXINTERPRETER'] = sLaTeXInterpreter

      # -- get command line
      oCmdLineParser = argparse.ArgumentParser()
      oCmdLineParser.add_argument('--simulateonly', action='store_true', help='If True, the LaTeX compiler is switched off; a syntax check only remains in this case. Default: False')
      oCmdLineArgs = oCmdLineParser.parse_args()
      bSimulateOnly = False
      if oCmdLineArgs.simulateonly is not None:
         bSimulateOnly = oCmdLineArgs.simulateonly
      self.__dictMainDocConfig['bSimulateOnly'] = bSimulateOnly

      # debug only
      # PrettyPrint(self.__dictMainDocConfig, sPrefix="Config")

   # eof def __init__(self, oRepositoryConfig=None):

   def __del__(self):
      del self.__dictMainDocConfig


   def PrintConfig(self):
      """
Prints all configuration values to console.
      """
      # -- printing configuration to console
      print()
      PrettyPrint(self.__dictMainDocConfig, sPrefix="MainDocConfig")
      print()
   # eof def PrintConfig(self):


   def PrintConfigKeys(self):
      """
Prints all configuration key names to console.
      """
      # -- printing configuration keys to console
      print()
      listKeys = self.__dictMainDocConfig.keys()
      sKeys = "[" + ", ".join(listKeys) + "]"
      print(sKeys)
      print()
   # eof def PrintConfigKeys(self):


   def Get(self, sName=None):
      """
Returns the configuration value belonging to a key name.
      """
      if ( (sName is None) or (sName not in self.__dictMainDocConfig) ):
         print()
         printerror(f"Error: Configuration parameter '{sName}' not existing!")
         # from here it's standard output:
         print("Use instead one of:")
         self.PrintConfigKeys()
         return None # returning 'None' in case of key is not existing !!!
      else:
         return self.__dictMainDocConfig[sName]
   # eof def Get(self, sName=None):


   def GetConfig(self):
      """
Returns the complete configuration dictionary.
      """
      return self.__dictMainDocConfig
   # eof def GetConfig(self):

# eof class CMainDocConfig():

# **************************************************************************************************************


