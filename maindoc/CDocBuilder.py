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
# 06.07.2022
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

from GenPackageDoc.CInterface import CInterface

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

      for sConfigFile in listConfigFiles:

         dictConfig = {}
         hConfigFile = open(sConfigFile)
         dictRepositoryConfig = json.load(hConfigFile)
         hConfigFile.close()
         del hConfigFile
         for sKey in listSupportedKeys:
            dictConfig[sKey] = dictRepositoryConfig[sKey]
         listofdictConfig.append(dictConfig)
      # eof for sConfigFile in listConfigFiles:

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

      sOutputFolder = self.__dictMainDocConfig['OUTPUT']
      sExternalDocFolder = self.__dictMainDocConfig['EXTERNALDOCFOLDER']
      sOverviewFileName_tex = "library_doc_overview.tex"
      sOverviewFile_tex = f"{sExternalDocFolder}/{sOverviewFileName_tex}"
      self.__dictMainDocConfig['OVERVIEWFILE_TEX'] = sOverviewFile_tex
      oOverviewFile_tex = CFile(sOverviewFile_tex)

      oOverviewFile_tex.Write(r"\begin{center}")

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

      sOutputFolder = self.__dictMainDocConfig['OUTPUT']
      sExternalDocFolder = self.__dictMainDocConfig['EXTERNALDOCFOLDER']

      sOverviewFileName_rst = "components.rst"
      sOverviewFile_rst = f"{sExternalDocFolder}/{sOverviewFileName_rst}"
      self.__dictMainDocConfig['OVERVIEWFILE_RST'] = sOverviewFile_rst
      oOverviewFile_rst = CFile(sOverviewFile_rst)

      oOverviewFile_rst.Write(r"**RobotFramework AIO components listing**")
      oOverviewFile_rst.Write()

      for dictConfig in listofdictConfig:
         PACKAGENAME = dictConfig['PACKAGENAME'].replace('_',r'\_') # LaTeX requires this masking
         DESCRIPTION = dictConfig['DESCRIPTION'].replace('_',r'\_') # LaTeX requires this masking
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

      # recreate the output folder (the temporary build folder containing all manually maintained and all automatically generated files)
      sOutputFolder = self.__dictMainDocConfig['OUTPUT']
      oOutputFolder = CFolder(sOutputFolder)
      bSuccess, sResult = oOutputFolder.Create(bOverwrite=True)
      del oOutputFolder
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # prepare content of output folder: copy the book sources
      sBookSources = self.__dictMainDocConfig['BOOKSOURCES']
      oBookSources = CFolder(sBookSources)
      bSuccess, sResult = oBookSources.CopyTo(sOutputFolder)
      del oBookSources
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # prepare content of output folder: get the LaTeX stylesheets from GenPackageDoc
      oGenPackageDocInterface = CInterface()
      bSuccess, sResult = oGenPackageDocInterface.GetLaTeXStyles(sOutputFolder)
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # compute files and subfolders
      sBookSourcesFolderName = os.path.basename(sBookSources)
      sMainTexFileFolder = f"{sOutputFolder}/{sBookSourcesFolderName}"
      self.__dictMainDocConfig['MAINTEXFILEFOLDER'] = sMainTexFileFolder
      sMainTexFileName = self.__dictMainDocConfig['MAINTEXFILENAME']
      sMainTexFile     = f"{sMainTexFileFolder}/{sMainTexFileName}"
      if os.path.isfile(sMainTexFile) is False:
         bSuccess = False
         sResult  = f"The main tex file '{sMainTexFile}' does not exist."
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      self.__dictMainDocConfig['MAINTEXFILE'] = sMainTexFile
      sExternalDocFolder = f"{sOutputFolder}/{sBookSourcesFolderName}/externaldocs"
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

            sDocumentationBuilder = f"{sRepository}/GenPackageDoc.py"
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
            if not sPDFFile.startswith(sMainTexFileFolder):
               bSuccess = False
               sResult  = f"The PDF file '{sPDFFile}' is not located within the folder structure of '{sMainTexFileFolder}'. It is not possible to compute a relative path to this PDF file."
               return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

            sHeadline = os.path.basename(sPDFFile)[:-4] # name of pdf file without extension
            # the path to the PDF file to be imported, must be relative to the position of the main tex file,
            # and this means also that the PDF must be created within a subfolder of the folder containing the main tex file
            sHeadline = sHeadline.replace('_',r'\_') # LaTeX requires this masking

            sPDFRelPath = "." + sPDFFile[len(sMainTexFileFolder):]
            oLibraryDocImportTexFile.Write(r"\includepdf[pages=1,pagecommand=\section{" + sHeadline + "}]{" + sPDFRelPath + "}")
            oLibraryDocImportTexFile.Write(r"\includepdf[pages=2-,pagecommand={}]{" + sPDFRelPath + "}")
         # eof for sPDFFile in listPDFFiles:
         del oLibraryDocImportTexFile

      # eof if bUpdateExternalDoc is True:

      else:

         # Import of external documentation not wanted. Therefore we create two dummy files to avoid LaTeX compilation errors
         # of the main tex document.

         sOutputFolder = self.__dictMainDocConfig['OUTPUT']

         sOverviewFile  = f"{sExternalDocFolder}/library_doc_overview.tex"
         sOutputMessage = r"\textbf{\textit{Overview of external documentations deactivated}}"

         oOverviewFile = CFile(sOverviewFile)
         oOverviewFile.Write("")
         oOverviewFile.Write(sOutputMessage)
         oOverviewFile.Write("")
         del oOverviewFile

         sLibraryDocImportTexFile = f"{sExternalDocFolder}/library_doc_imports.tex"
         sOutputMessage           = r"\textbf{\textit{Import of external documentations deactivated}}"

         oLibraryDocImportTexFile = CFile(sLibraryDocImportTexFile)
         oLibraryDocImportTexFile.Write("")
         oLibraryDocImportTexFile.Write(sOutputMessage)
         oLibraryDocImportTexFile.Write("")
         del oLibraryDocImportTexFile

      # eof else - if bUpdateExternalDoc is True:

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

      # derive name of expected PDF file out of the name of tex file
      oMainTexFile = CFile(sMainTexFile)
      dMainTexFileInfo = oMainTexFile.GetFileInfo()
      del oMainTexFile
      sMainTexFileNameOnly = dMainTexFileInfo['sFileNameOnly']
      sPDFFileName = f"{sMainTexFileNameOnly}.pdf"
      sPDFFileExpected = f"{sMainTexFileFolder}/{sPDFFileName}"

      # PDF file will also be copied to the package folder, from there it will be installed to Python site-packages
      sPackageFolder = f"{self.__dictMainDocConfig['REFERENCEPATH']}/{self.__dictMainDocConfig['PACKAGENAME']}"
      sPDFFileDestination = f"{sPackageFolder}/{sPDFFileName}"

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
            os.chdir(sMainTexFileFolder) # otherwise LaTeX compiler is not able to find files inside
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

      bSuccess = True
      sResult  = "Main documentation generated"

      return bSuccess, sResult

   # eof def Build(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CDocBuilder():

# --------------------------------------------------------------------------------------------------------------
