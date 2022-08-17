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
# CDocBuilder.py
#
# XC-CT/ECA3-Queckenstedt
#
# 17.08.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing all methods to generate the main documentation.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, json, shlex, subprocess, platform, shutil, re
import colorama as col
import pypandoc

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------
#TM***

class CDocBuilder():
   """
Main class ,,,

Method to execute: ``Build()``
   """

   def __init__(self, oMainDocConfig=None):
      """
Constructor of class ``CDocBuilder``.

* ``oMainDocConfig``

  / *Condition*: required / *Type*: CMainDocConfig() /

  Main documentation configuration containing static and dynamic configuration values.
      """

      sMethod = "CDocBuilder.__init__"

      if oMainDocConfig is None:
         bSuccess = None
         sResult  = "oMainDocConfig is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      self.__dictMainDocConfig = oMainDocConfig.GetConfig()

   # eof def __init__(self, oMainDocConfig=None):

   def __del__(self):
      pass

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __GetRepositoryList(self):
      """Returns a list of repositories whose documentation shall be added to the main documentation.
      """

      sMethod = "CDocBuilder.__GetRepositoryList"

      bSuccess = None
      sResult  = "UNKNOWN"

      listRepositories = []
      nNrOfRepositories = 0

      # Intermediate solution: simply take the list from json file.
      # Later we have to parse a configuration file within the build repository.

      listRepositories = self.__dictMainDocConfig['IMPORTS']
      nNrOfRepositories = len(listRepositories)

      bSuccess = True
      sResult  = f"Number of repositories: {nNrOfRepositories}"

      return listRepositories, bSuccess, sResult

   # eof def __GetRepositoryList(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __GetConfig(self, listConfigFiles=[]):
      """Returns a dictionary with some assorted configuration values taken out of the collected repository configurations
      """

      sMethod = "CDocBuilder.__GetConfig"

      bSuccess = None
      sResult  = "UNKNOWN"

      listofdictConfig = []

      if len(listConfigFiles) == 0:
         bSuccess = True # empty list is not an error
         sResult  = "No config files available"
         return listofdictConfig, bSuccess, sResult

      listSupportedKeys = []
      listSupportedKeys.append('REPOSITORYNAME')
      listSupportedKeys.append('PACKAGENAME')
      listSupportedKeys.append('AUTHOR')
      listSupportedKeys.append('AUTHOREMAIL')
      listSupportedKeys.append('DESCRIPTION')
      listSupportedKeys.append('URL')
      listSupportedKeys.append('PACKAGEVERSION')
      listSupportedKeys.append('PACKAGEDATE')
      listSupportedKeys.append('META_NAME')         # optional
      listSupportedKeys.append('META_VERSION')      # optional
      listSupportedKeys.append('META_VERSION_DATE') # optional

      for sConfigFile in listConfigFiles:

         dictConfig = {}
         hConfigFile = open(sConfigFile)
         dictRepositoryConfig = json.load(hConfigFile)
         hConfigFile.close()
         del hConfigFile
         for sKey in listSupportedKeys:
            if sKey in dictRepositoryConfig:
               dictConfig[sKey] = dictRepositoryConfig[sKey]
         listofdictConfig.append(dictConfig)

         # The meta information is also used in the title page of the resulting PDF document.
         # For this purpose we separate the meta information here (additionally to this information also stored in listofdictConfig).
         #
         # To be considered: In every project the meta information should be defined only once. But within this code this is not a syntactical requirement.
         # The user is responsible for keeping the meta information unique (= defined within only one single imported repository), but to make this code robust
         # all identified meta informations (in case of more than one imported repository contains a meta information) will be handled as list - and this means
         # all meta informations will be part of the resulting PDF documentation (even in case of this makes no sense).
         #
         # In the context of genmaindoc the desired intension behind the meta information handling is:
         # - The name of the RobotFramework AIO bundle together with the version number and the release date of this bundle is defined in the meta information of
         #   the testsuites management repository. Therefore it is required to import this repository in the maindoc_config.json.
         # - This meta information is printed to the title page of the resulting PDF document.

         if 'META_NAME' in dictRepositoryConfig:
            META_NAME = dictRepositoryConfig['META_NAME'].replace('_',r'\_') # LaTeX requires this masking
            if 'META_NAME' in self.__dictMainDocConfig:
               self.__dictMainDocConfig['META_NAME'] = self.__dictMainDocConfig['META_NAME'] + ";" + META_NAME
            else:
               self.__dictMainDocConfig['META_NAME'] = META_NAME
         if 'META_VERSION' in dictRepositoryConfig:
            META_VERSION = dictRepositoryConfig['META_VERSION']
            if 'META_VERSION' in self.__dictMainDocConfig:
               self.__dictMainDocConfig['META_VERSION'] = self.__dictMainDocConfig['META_VERSION'] + ";" + META_VERSION
            else:
               self.__dictMainDocConfig['META_VERSION'] = META_VERSION
         if 'META_VERSION_DATE' in dictRepositoryConfig:
            META_VERSION_DATE = dictRepositoryConfig['META_VERSION_DATE']
            if 'META_VERSION_DATE' in self.__dictMainDocConfig:
               self.__dictMainDocConfig['META_VERSION_DATE'] = self.__dictMainDocConfig['META_VERSION_DATE'] + ";" + META_VERSION_DATE
            else:
               self.__dictMainDocConfig['META_VERSION_DATE'] = META_VERSION_DATE
      # eof for sConfigFile in listConfigFiles:

      # error handling
      if 'META_NAME' not in self.__dictMainDocConfig:
         self.__dictMainDocConfig['META_NAME'] = "!!! Name unknown !!!"
      if 'META_VERSION' not in self.__dictMainDocConfig:
         self.__dictMainDocConfig['META_VERSION'] = "!!! Version unknown !!!"
      if 'META_VERSION_DATE' not in self.__dictMainDocConfig:
         self.__dictMainDocConfig['META_VERSION_DATE'] = "!!! Date unknown !!!"

      nNrOfConfigs = len(listofdictConfig)

      bSuccess = True
      sResult  = f"Configuration values collected from {nNrOfConfigs} repositories."

      return listofdictConfig, bSuccess, sResult

   # eof def __GetConfig(self, listConfigFiles=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __PrepareOverviewFiles(self, listofdictConfig=[]):
      """Writes some overview files containing some assorted configuration values taken out of the collected repository configurations
      """

      sMethod = "CDocBuilder.__PrepareOverviewFiles"

      bSuccess = None
      sResult  = "UNKNOWN"

      # -- 1. LaTeX version

      sExternalDocFolder = self.__dictMainDocConfig['EXTERNALDOCFOLDER']
      sOverviewFileName_tex = "library_doc_overview.tex"
      sOverviewFile_tex = f"{sExternalDocFolder}/{sOverviewFileName_tex}"
      self.__dictMainDocConfig['OVERVIEWFILE_TEX'] = sOverviewFile_tex
      oOverviewFile_tex = CFile(sOverviewFile_tex)
      oOverviewFile_tex.Write(f"% Generated at {self.__dictMainDocConfig['NOW']}")
      oOverviewFile_tex.Write()
      oOverviewFile_tex.Write(r"\chapter{Library documentation}")
      oOverviewFile_tex.Write()
      oOverviewFile_tex.Write(r"The following sections contain the documentation of additional libraries that are part of the RobotFramework AIO.")
      oOverviewFile_tex.Write()
      oOverviewFile_tex.Write(r"\vspace{2ex}")
      oOverviewFile_tex.Write()

      oOverviewFile_tex.Write(r"\begin{center}")

      oOverviewFile_tex.Write(r"{\Large\textbf{RobotFramework AIO bundle}}")
      oOverviewFile_tex.Write()
      oOverviewFile_tex.Write(r"\vspace{2ex}")
      oOverviewFile_tex.Write()

      # -- search for meta information, print meta information at the top of the list of package informations (if available)
      bMetaVersionAvailable = False
      for dictConfig in listofdictConfig:
         META_NAME         = None
         META_VERSION      = None
         META_VERSION_DATE = None
         if "META_NAME" in dictConfig:
            META_NAME = dictConfig['META_NAME'].replace('_',r'\_') # LaTeX requires this masking
         if "META_VERSION" in dictConfig:
            META_VERSION = dictConfig['META_VERSION']
         if "META_VERSION_DATE" in dictConfig:
            META_VERSION_DATE = dictConfig['META_VERSION_DATE']

         if ( (META_NAME is not None) and (META_VERSION is not None) and (META_VERSION_DATE is not None) ) :
            # meta information available
            bMetaVersionAvailable = True
            oOverviewFile_tex.Write(r"\begin{tabular}{| m{44em} |}\hline")
            oOverviewFile_tex.Write(r"   \textbf{" + META_NAME + r"}\\ \hline")
            oOverviewFile_tex.Write(r"   Version " + dictConfig['META_VERSION'] + " (from " + dictConfig['META_VERSION_DATE'] + r")\\ \hline")
            oOverviewFile_tex.Write(r"\end{tabular}")
            oOverviewFile_tex.Write()
            oOverviewFile_tex.Write(r"\vspace{2ex}")
            oOverviewFile_tex.Write()
      # eof for dictConfig in listofdictConfig:

      if bMetaVersionAvailable is False:
         # meta information not available
         oOverviewFile_tex.Write(r"\textcolor{red}{\textbf{\textit{RobotFramework AIO bundle information not available!}}}")
         oOverviewFile_tex.Write()
         oOverviewFile_tex.Write(r"\vspace{2ex}")
         oOverviewFile_tex.Write()

      # -- print information about included packages
      oOverviewFile_tex.Write(r"{\Large\textbf{Included libraries}}")
      oOverviewFile_tex.Write()
      oOverviewFile_tex.Write(r"\vspace{2ex}")
      oOverviewFile_tex.Write()
      for dictConfig in listofdictConfig:
         PACKAGENAME = dictConfig['PACKAGENAME'].replace('_',r'\_') # LaTeX requires this masking
         DESCRIPTION = dictConfig['DESCRIPTION'].replace('_',r'\_') # LaTeX requires this masking
         oOverviewFile_tex.Write(r"\begin{tabular}{| m{44em} |}\hline")
         oOverviewFile_tex.Write(r"   \textbf{" + PACKAGENAME + r"}\\ \hline")
         oOverviewFile_tex.Write(r"   Version " + dictConfig['PACKAGEVERSION'] + " (from " + dictConfig['PACKAGEDATE'] + r")\\ \hline")
         oOverviewFile_tex.Write(r"   " + dictConfig['URL'] + r"\\ \hline")
         oOverviewFile_tex.Write(r"   \textit{" + DESCRIPTION + r"}\\ \hline")
         oOverviewFile_tex.Write(r"\end{tabular}")
         oOverviewFile_tex.Write()
         oOverviewFile_tex.Write(r"\vspace{2ex}")
         oOverviewFile_tex.Write()
      # eof for dictConfig in listofdictConfig:

      oOverviewFile_tex.Write(r"\end{center}")
      oOverviewFile_tex.Write()

      del oOverviewFile_tex

      # -- 2. rst version

      sExternalDocFolder = self.__dictMainDocConfig['EXTERNALDOCFOLDER']
      sOverviewFileName_rst = "components.rst"
      sOverviewFile_rst = f"{sExternalDocFolder}/{sOverviewFileName_rst}"
      self.__dictMainDocConfig['OVERVIEWFILE_RST'] = sOverviewFile_rst
      oOverviewFile_rst = CFile(sOverviewFile_rst)

      oOverviewFile_rst.Write(r"**RobotFramework AIO bundle**")
      oOverviewFile_rst.Write()

      bMetaVersionAvailable = False
      for dictConfig in listofdictConfig:
         META_NAME         = None
         META_VERSION      = None
         META_VERSION_DATE = None
         if "META_NAME" in dictConfig:
            META_NAME = dictConfig['META_NAME']
         if "META_VERSION" in dictConfig:
            META_VERSION = dictConfig['META_VERSION']
         if "META_VERSION_DATE" in dictConfig:
            META_VERSION_DATE = dictConfig['META_VERSION_DATE']

         if ( (META_NAME is not None) and (META_VERSION is not None) and (META_VERSION_DATE is not None) ) :
            # meta information available
            bMetaVersionAvailable = True
            oOverviewFile_rst.Write(f"* ``{META_NAME}``")
            oOverviewFile_rst.Write()
            oOverviewFile_rst.Write(f"  Version: {dictConfig['META_VERSION']} (from {dictConfig['META_VERSION_DATE']})")
            oOverviewFile_rst.Write()
      # eof for dictConfig in listofdictConfig:

      if bMetaVersionAvailable is False:
         # meta information not available
         oOverviewFile_rst.Write(r"RobotFramework AIO bundle information not available!")
         oOverviewFile_rst.Write()

      oOverviewFile_rst.Write(r"**RobotFramework AIO components listing**")
      oOverviewFile_rst.Write()

      for dictConfig in listofdictConfig:
         PACKAGENAME = dictConfig['PACKAGENAME']
         DESCRIPTION = dictConfig['DESCRIPTION']
         oOverviewFile_rst.Write(f"* ``{PACKAGENAME}``")
         oOverviewFile_rst.Write()
         oOverviewFile_rst.Write(f"  - Version: {dictConfig['PACKAGEVERSION']} (from {dictConfig['PACKAGEDATE']})")
         oOverviewFile_rst.Write(f"  - URL: {dictConfig['URL']}")
         oOverviewFile_rst.Write(f"  - *{dictConfig['DESCRIPTION']}*")
         oOverviewFile_rst.Write()
      # eof for dictConfig in listofdictConfig:

      oOverviewFile_rst.Write()

      del oOverviewFile_rst

      bSuccess = True
      sResult  = f"Overview files written:\n* '{sOverviewFile_tex}'\n* '{sOverviewFile_rst}'"

      return bSuccess, sResult

   # eof def __PrepareOverviewFiles(self, listofdictConfig=[]):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Build(self):
      """
**Arguments:**

(*no arguments*)

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation  was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation.
      """

      sMethod = "CDocBuilder.Build"
      bSuccess = False
      sResult  = "UNKNOWN"

      listRepositories, bSuccess, sResult = self.__GetRepositoryList()
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sBookSourcesFolder = self.__dictMainDocConfig['BOOKSOURCES']
      if not os.path.isdir(sBookSourcesFolder):
         bSuccess = False
         sResult  = f"The input folder '{sBookSourcesFolder}' does not exist."
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # compute files and subfolders
      sMainTexFileName = self.__dictMainDocConfig['MAINTEXFILENAME']
      sMainTexFile     = f"{sBookSourcesFolder}/{sMainTexFileName}"
      if os.path.isfile(sMainTexFile) is False:
         bSuccess = False
         sResult  = f"The main tex file '{sMainTexFile}' does not exist."
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      self.__dictMainDocConfig['MAINTEXFILE'] = sMainTexFile
      sExternalDocFolder = f"{sBookSourcesFolder}/externaldocs"
      self.__dictMainDocConfig['EXTERNALDOCFOLDER'] = sExternalDocFolder

      oExternalDocFolder = CFolder(sExternalDocFolder)
      bSuccess, sResult = oExternalDocFolder.Create(bOverwrite=True)
      del oExternalDocFolder
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sPython            = self.__dictMainDocConfig['PYTHON']
      bStrict            = self.__dictMainDocConfig['CONTROL']['STRICT']
      bUpdateExternalDoc = self.__dictMainDocConfig['CONTROL']['UPDATE_EXTERNAL_DOC']

      # iterate the list of repositories and call the package doc generator inside these repositories,
      # redirect the PDF destination to the output folders used to build the main documentation
      listPDFFiles = []
      listConfigFiles = []

      if bUpdateExternalDoc is True:

         # In case of someone only wants to see the outcome of changes in the manually maintained part of the tex sources,
         # the rendering of all external documents (the automatically generated part) can be suppressed
         # (with "UPDATE_EXTERNAL_DOC" : false; see maindoc_config.json). This saves time.

         for sRepository in listRepositories:

            if os.path.isdir(sRepository) is False:
               bSuccess = False
               sResult  = f"The repository folder '{sRepository}' does not exist"
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            sRepositoryName = os.path.basename(sRepository)
            sDestinationFolder = f"{sExternalDocFolder}/{sRepositoryName}"
            oDestinationFolder = CFolder(sDestinationFolder)
            bSuccess, sResult = oDestinationFolder.Create(bOverwrite=True)
            del oDestinationFolder
            if bSuccess is not True:
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            sDocumentationBuilder = f"{sRepository}/genpackagedoc.py"
            if os.path.isfile(sDocumentationBuilder) is False:
               bSuccess = False
               sResult  = f"The package doc generator '{sDocumentationBuilder}' does not exist"
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            # create command line and execute the documentation builder
            listCmdLineParts = []
            listCmdLineParts.append(f"\"{sPython}\"")
            listCmdLineParts.append(f"\"{sDocumentationBuilder}\"")
            listCmdLineParts.append(f"--pdfdest=\"{sDestinationFolder}\"")
            listCmdLineParts.append(f"--configdest=\"{sDestinationFolder}\"")
            listCmdLineParts.append(f"--strict {bStrict}")
            sCmdLine = " ".join(listCmdLineParts)
            del listCmdLineParts
            listCmdLineParts = shlex.split(sCmdLine)
            # -- debug
            sCmdLine = " ".join(listCmdLineParts)
            print()
            print("Now executing command line:\n" + sCmdLine)
            print()
            nReturn = ERROR
            try:
               nReturn = subprocess.call(listCmdLineParts)
            except Exception as ex:
               bSuccess = None
               sResult  = str(ex)
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
            if nReturn != SUCCESS:
               bSuccess = False
               sResult  = f"Documentation builder returns error {nReturn}"
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            # We need to identify the name of some output files inside sDestinationFolder:
            # - PDF file (documentation of package in current repository)
            # - json file (configuration values of current repository and documantaion build process) 
            sPDFFile = None
            sJsonFile = None
            listLocalEntries = os.listdir(sDestinationFolder)
            for sEntryName in listLocalEntries:
               if sEntryName.lower().endswith('.pdf'):
                  sPDFFile = CString.NormalizePath(os.path.join(sDestinationFolder, sEntryName))
               if sEntryName.lower().endswith('.json'):
                  sJsonFile = CString.NormalizePath(os.path.join(sDestinationFolder, sEntryName))
            if sPDFFile is None:
               bSuccess = False
               sResult  = f"PDF file not found within '{sDestinationFolder}'"
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
            if sJsonFile is None:
               bSuccess = False
               sResult  = f"Json configuration file not found within '{sDestinationFolder}'"
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
            listPDFFiles.append(sPDFFile)
            listConfigFiles.append(sJsonFile)
         # eof for sRepository in listRepositories:

         # get some assorted configuration values out of the configuration files collected from repositories
         listofdictConfig, bSuccess, sResult = self.__GetConfig(listConfigFiles)
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            print(sResult)
            print()

         # prepare an overview file containing a summary of configuration values
         bSuccess, sResult = self.__PrepareOverviewFiles(listofdictConfig)
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            print(sResult)
            print()

         # create the import tex file to import the library documentations into the main documentation
         sLibraryDocImportTexFile = f"{sExternalDocFolder}/library_doc_imports.tex"
         oLibraryDocImportTexFile = CFile(sLibraryDocImportTexFile)
         oLibraryDocImportTexFile.Write(f"% Generated at {self.__dictMainDocConfig['NOW']}")
         oLibraryDocImportTexFile.Write("%")
         oLibraryDocImportTexFile.Write("% This document imports the documentation of additional RobotFramework AIO libraries into the main documentation.")
         oLibraryDocImportTexFile.Write("%")
         oLibraryDocImportTexFile.Write(r"% The split of the \includepdf for a single PDF file is a workaround to avoid a linebreak after the section heading")
         oLibraryDocImportTexFile.Write(r"% (one \newpage too much within pdfpages.sty).")
         oLibraryDocImportTexFile.Write("%")
         oLibraryDocImportTexFile.Write()
         for sPDFFile in listPDFFiles:
            if not sPDFFile.startswith(sBookSourcesFolder):
               bSuccess = False
               sResult  = f"The PDF file '{sPDFFile}' is not located within the folder structure of '{sBookSourcesFolder}'. It is not possible to compute a relative path to this PDF file."
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            sHeadline = os.path.basename(sPDFFile)[:-4] # name of pdf file without extension
            # the path to the PDF file to be imported, must be relative to the position of the main tex file,
            # and this means also that the PDF must be created within a subfolder of the folder containing the main tex file
            sHeadline = sHeadline.replace('_',r'\_') # LaTeX requires this masking

            sPDFRelPath = "." + sPDFFile[len(sBookSourcesFolder):]
            oLibraryDocImportTexFile.Write(r"\includepdf[pages=1,pagecommand=\section{" + sHeadline + "}]{" + sPDFRelPath + "}")
            oLibraryDocImportTexFile.Write(r"\includepdf[width=\textwidth,frame=true,pages=2-,pagecommand={}]{" + sPDFRelPath + "}")
         # eof for sPDFFile in listPDFFiles:
         del oLibraryDocImportTexFile

      # eof if bUpdateExternalDoc is True:

      else:

         # Import of external documentation not wanted. Therefore we create two dummy files to avoid LaTeX compilation errors
         # of the main tex document.

         sOverviewFile = f"{sExternalDocFolder}/library_doc_overview.tex"
         oOverviewFile = CFile(sOverviewFile)
         oOverviewFile.Write(f"% Generated at {self.__dictMainDocConfig['NOW']}")
         oOverviewFile.Write()
         oOverviewFile.Write("\chapter{Overview not available}")
         oOverviewFile.Write()
         sOutputMessage = r"{\Large\textcolor{red}{\textbf{\textit{Overview of external documentations is deactivated}}}}"
         oOverviewFile.Write(sOutputMessage)
         oOverviewFile.Write()
         del oOverviewFile

         sLibraryDocImportTexFile = f"{sExternalDocFolder}/library_doc_imports.tex"
         oLibraryDocImportTexFile = CFile(sLibraryDocImportTexFile)
         oLibraryDocImportTexFile.Write(f"% Generated at {self.__dictMainDocConfig['NOW']}")
         oLibraryDocImportTexFile.Write()
         oLibraryDocImportTexFile.Write("\chapter{Imports not available}")
         oLibraryDocImportTexFile.Write()
         sOutputMessage = r"{\Large\textcolor{red}{\textbf{\textit{Import of external documentations is deactivated}}}}"
         oLibraryDocImportTexFile.Write(sOutputMessage)
         oLibraryDocImportTexFile.Write()
         del oLibraryDocImportTexFile

      # eof else - if bUpdateExternalDoc is True:

      # -- Create another tex file containing the version and the date of the RobotFramework AIO bundle.
      #    The values are part of the meta information (currently defined within the testsuites management).
      #    This new tex file is imported in the main tex file (RobotFramework AIO reference) and makes it sure
      #    that the main documentation contains in the title page a version number and a date that is up to date.

      # PrettyPrint(self.__dictMainDocConfig)

      META_NAME = "!!! Name unknown !!!"
      if 'META_NAME' in self.__dictMainDocConfig:
         META_NAME = self.__dictMainDocConfig['META_NAME']
      META_VERSION = "!!! Version unknown !!!"
      if 'META_VERSION' in self.__dictMainDocConfig:
         META_VERSION = self.__dictMainDocConfig['META_VERSION']
      META_VERSION_DATE = "!!! Date unknown !!!"
      if 'META_VERSION_DATE' in self.__dictMainDocConfig:
         META_VERSION_DATE = self.__dictMainDocConfig['META_VERSION_DATE']

      BOOKSOURCES = self.__dictMainDocConfig['BOOKSOURCES']
      sBundleVersionDateTeXFile = f"{BOOKSOURCES}/BundleVersionDate.tex"
      self.__dictMainDocConfig['BUNDLEVERSIONDATETEXFILE'] = sBundleVersionDateTeXFile

      oBundleVersionDateTeXFile = CFile(sBundleVersionDateTeXFile)
      oBundleVersionDateTeXFile.Write(f"% Generated at {self.__dictMainDocConfig['NOW']}")
      oBundleVersionDateTeXFile.Write()
      oBundleVersionDateTeXFile.Write(r"\title{\textbf{Specification of \\")
      oBundleVersionDateTeXFile.Write(r"\vspace{2ex}")
      oBundleVersionDateTeXFile.Write(f"{META_NAME} \\\\")
      oBundleVersionDateTeXFile.Write(r"\vspace{2ex}")
      oBundleVersionDateTeXFile.Write(f"v. {META_VERSION} \\\\")
      oBundleVersionDateTeXFile.Write(r"\vspace{2ex}")
      oBundleVersionDateTeXFile.Write(r"at Bosch}}")
      oBundleVersionDateTeXFile.Write()
      oBundleVersionDateTeXFile.Write(r"\date{\vspace{4ex}\textbf{" + META_VERSION_DATE + "}}")
      oBundleVersionDateTeXFile.Write()
      del oBundleVersionDateTeXFile

      # derive name of expected PDF file out of the name of tex file
      oMainTexFile = CFile(sMainTexFile)
      dMainTexFileInfo = oMainTexFile.GetFileInfo()
      del oMainTexFile
      sMainTexFileNameOnly = dMainTexFileInfo['sFileNameOnly']
      sPDFFileName = f"{sMainTexFileNameOnly}.pdf"
      sPDFFileExpected = f"{sBookSourcesFolder}/{sPDFFileName}"
      self.__dictMainDocConfig['PDFFILEEXPECTED'] = sPDFFileExpected

      # PDF file will also be copied to the package folder, from there it will be installed to Python site-packages
      sPackageFolder = f"{self.__dictMainDocConfig['REFERENCEPATH']}/{self.__dictMainDocConfig['PACKAGENAME']}"
      sPDFFileDestination = f"{sPackageFolder}/{sPDFFileName}"
      self.__dictMainDocConfig['PDFFILEDESTINATION'] = sPDFFileDestination

      # create final summary about document creation
      sPDFFileName_masked = sPDFFileName.replace('_', r'\_') # LaTeX requires this masking
      sFinalSummaryFile = f"{sExternalDocFolder}/final_summary.tex"
      oFinalSummaryFile = CFile(sFinalSummaryFile)
      oFinalSummaryFile.Write(f"% Generated at {self.__dictMainDocConfig['NOW']}")
      oFinalSummaryFile.Write()
      oFinalSummaryFile.Write(r"\vfill")
      oFinalSummaryFile.Write(r"\begin{center}")
      oFinalSummaryFile.Write(r"\begin{tabular}{m{16em}}\hline")
      oFinalSummaryFile.Write(r"   \multicolumn{1}{c}{\textbf{" + f"{sPDFFileName_masked}" + r"}}\\")
      oFinalSummaryFile.Write(r"   \multicolumn{1}{c}{\textit{Created at " + self.__dictMainDocConfig['NOW'] + r"}}\\")
      oFinalSummaryFile.Write(r"   \multicolumn{1}{c}{\textit{by genmaindoc v. " + self.__dictMainDocConfig['VERSION'] + r"}}\\ \hline")
      oFinalSummaryFile.Write(r"\end{tabular}")
      oFinalSummaryFile.Write(r"\end{center}")
      oFinalSummaryFile.Write()
      del oFinalSummaryFile

      # convert main tex file to PDF
      sLaTeXInterpreter = self.__dictMainDocConfig['LATEXINTERPRETER']
      if os.path.isfile(sLaTeXInterpreter) is False:
         # consider strictness regarding availability of LaTeX compiler
         bStrict = self.__dictMainDocConfig['CONTROL']['STRICT']
         print()
         print(COLBR + f"Missing LaTeX compiler '{sLaTeXInterpreter}'!")
         print()
         if bStrict is True:
            bSuccess = False
            sResult  = f"Generating the documentation in PDF format not possible because of missing LaTeX compiler ('strict' mode)!"
            sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         else:
            bSuccess = True
            sResult  = f"Generating the documentation in PDF format not possible because of missing LaTeX compiler ('non strict' mode)!"
         return bSuccess, sResult

      # start the compiler
      listCmdLineParts = []
      listCmdLineParts.append(f"\"{sLaTeXInterpreter}\"")
      listCmdLineParts.append(f"\"{sMainTexFile}\"")

      sCmdLine = " ".join(listCmdLineParts)
      del listCmdLineParts
      listCmdLineParts = shlex.split(sCmdLine)

      # -- debug
      sCmdLine = " ".join(listCmdLineParts)
      print()
      print("Now executing command line:\n" + sCmdLine)
      print()

      for nDummy in range(2): # call LaTeX compiler 2 times to get TOC and index lists updated properly
         cwd = os.getcwd() # we have to save cwd because later we have to change
         nReturn = ERROR
         try:
            os.chdir(sBookSourcesFolder) # otherwise LaTeX compiler is not able to find files inside
            nReturn = subprocess.call(listCmdLineParts)
            print()
            print(f"LaTeX compiler returned {nReturn}")
            print()
            os.chdir(cwd) # restore original value
         except Exception as ex:
            os.chdir(cwd) # restore original value
            bSuccess = None
            sResult  = str(ex)
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         if nReturn != SUCCESS:
            bSuccess = False
            sResult  = f"LaTeX compiler not returned expected value {SUCCESS}"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      # eof for nDummy in range(2):

      # -- verify the outcome
      if os.path.isfile(sPDFFileExpected) is False:
         bSuccess = False
         sResult  = f"Expected PDF file '{sPDFFileExpected}' not generated"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      oPDFFile = CFile(sPDFFileExpected)
      bSuccess, sResult = oPDFFile.CopyTo(sPDFFileDestination, bOverwrite=True)
      del oPDFFile
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      print(COLBY + f"* PDF file: {sPDFFileDestination}")
      print()

      if "OVERVIEWFILE_RST" in self.__dictMainDocConfig:
         # in case of "UPDATE_EXTERNAL_DOC" is false, "OVERVIEWFILE_RST" is not available; therefore nothing to copy to the package folder
         OVERVIEWFILE_RST = self.__dictMainDocConfig['OVERVIEWFILE_RST']
         if os.path.isfile(OVERVIEWFILE_RST) is False:
            bSuccess = False
            sResult  = f"Expected overview file '{OVERVIEWFILE_RST}' not generated"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

         sOverviewFileName = os.path.basename(OVERVIEWFILE_RST)
         sOverviewFile_dest = f"{sPackageFolder}/{sOverviewFileName}"
         oOverviewFile = CFile(OVERVIEWFILE_RST)
         bSuccess, sResult = oOverviewFile.CopyTo(sOverviewFile_dest, bOverwrite=True)
         del oOverviewFile
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         print(COLBY + f"* Overview: {sOverviewFile_dest}")
         print()
      # eof if "OVERVIEWFILE_RST" in self.__dictMainDocConfig:

      bSuccess = True
      sResult  = "Main documentation generated"

      return bSuccess, sResult

   # eof def Build(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CDocBuilder():

# --------------------------------------------------------------------------------------------------------------
