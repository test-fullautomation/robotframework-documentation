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
# 30.01.2023
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing the configuration for the RobotFramework AIO documentation.
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

def printerror(sMsg):
    sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

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

      # initialize the documentation build configuration (later containing also the repository configuration (with placeholders resolved)
      # and the command line parameters)
      self.__dictMainDocConfig = {}

      # get repository configuration
      dictRepositoryConfig = oRepositoryConfig.GetConfig()

      # take over keys and values from repository configuration
      for key, value in dictRepositoryConfig.items():
         self.__dictMainDocConfig[key] = value

      # get command line
      self.GetCmdLine()

      # read the documentation build configuration from separate json file, provided in command line
      sMainDocConfigFile = self.__dictMainDocConfig['sMainDocConfigFile']
      if sMainDocConfigFile is None:
         # --configfile missed in command line
         bSuccess = None
         sResult  = f"Maindoc configuration file not defined. Use '--configfile' in command line."
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # -- the absolute path that is reference for relative paths to configuration files in command line of genmaindoc.py
      sReferencePathAbs_configfile = self.__dictMainDocConfig['PACKAGEDOC'] # set initially in repository config and already normalized
      sMainDocConfigFile = CString.NormalizePath(sPath=sMainDocConfigFile, sReferencePathAbs=sReferencePathAbs_configfile)
      self.__dictMainDocConfig['sMainDocConfigFile'] = sMainDocConfigFile # update config
      if os.path.isfile(sMainDocConfigFile) is False:
         bSuccess = None
         sResult  = f"Maindoc configuration file '{sMainDocConfigFile}' does not exist"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      print(COLNY + f"Maindoc configuration: '{sMainDocConfigFile}'")
      print()

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

      sJsonFileNameTmp = "maindoc_config_tmp.json" # any name of this file in tmp folder (the cleaned version)
      sJsonFileCleaned = f"{sTmpPath}/{sJsonFileNameTmp}"
      # print(f"========== sJsonFileCleaned : '{sJsonFileCleaned}'")

      oJsonFileSource = CFile(sMainDocConfigFile)
      listLines, bSuccess, sResult = oJsonFileSource.ReadLines(bSkipBlankLines=True, sComment='#')
      del oJsonFileSource
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      oJsonFileCleaned = CFile(sJsonFileCleaned)
      bSuccess, sResult = oJsonFileCleaned.Write(listLines)
      del oJsonFileCleaned
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      dictJsonValues = None
      try:
         hDocumentationProjectConfigFile = open(sJsonFileCleaned)
         dictJsonValues = json.load(hDocumentationProjectConfigFile)
         hDocumentationProjectConfigFile.close()
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason) + "\nwhile loading the json configuration file"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # take over keys and values from maindocumentation build configuration
      for key, value in dictJsonValues.items():
         self.__dictMainDocConfig[key] = value

      # add current timestamp
      self.__dictMainDocConfig['NOW'] = time.strftime('%d.%m.%Y - %H:%M:%S')

      # For normalization of all relative paths inside JSON configuration files we need an absolute reference path.
      # The reference for all relative paths inside JSON configuration files is the position of the selected configuration file.
      sReferencePathAbs = os.path.dirname(sMainDocConfigFile)

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

      # debug only
      # PrettyPrint(self.__dictMainDocConfig, sPrefix="Config")

   # eof def __init__(self, oRepositoryConfig=None):

   def __del__(self):
      del self.__dictMainDocConfig

   def GetCmdLine(self):
      """
Gets command line parameter.
      """
      oCmdLineParser = argparse.ArgumentParser()
      oCmdLineParser.add_argument('--configfile', type=str, help='Path and name of maindoc configuration file')
      oCmdLineParser.add_argument('--simulateonly', action='store_true', help='If True, the LaTeX compiler is switched off; a syntax check only remains in this case. Default: False')

      oCmdLineArgs = oCmdLineParser.parse_args()

      sMainDocConfigFile = None
      if oCmdLineArgs.configfile is not None:
         sMainDocConfigFile = oCmdLineArgs.configfile
      self.__dictMainDocConfig['sMainDocConfigFile'] = sMainDocConfigFile # here not yet normalized and checked

      bSimulateOnly = False
      if oCmdLineArgs.simulateonly is not None:
         bSimulateOnly = oCmdLineArgs.simulateonly
      self.__dictMainDocConfig['bSimulateOnly'] = bSimulateOnly

   # eof def GetCmdLine(self):

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


