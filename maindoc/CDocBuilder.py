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
# 15.06.2022
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

      # recreate folder containing the generated repository documentations
      sOutputFolder = self.__dictMainDocConfig['OUTPUT']
      oOutputFolder = CFolder(sOutputFolder)
      bSuccess, sResult = oOutputFolder.Create(bOverwrite=True)
      del oOutputFolder
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sPython = self.__dictMainDocConfig['PYTHON']

      # iterate the list of repositories and call the package doc generator inside these repositories,
      # redirect the PDF destination to the output folders used to build the main documentation
      listPDFFiles = []
      sMainTexFile = self.__dictMainDocConfig['MAINTEXFILE']
      sMainTexFileFolder = os.path.dirname(sMainTexFile) # needed to compute relative import paths of PDF files
      bStrict = self.__dictMainDocConfig['CONTROL']['STRICT']
      for sRepository in listRepositories:
         sRepositoryName = os.path.basename(sRepository)
         sDestinationFolder = f"{sOutputFolder}/{sRepositoryName}"

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

         # we need to identify the name of the PDF file inside sDestinationFolder
         sPDFFile = None
         listLocalEntries = os.listdir(sDestinationFolder)
         for sEntryName in listLocalEntries:
            if sEntryName.lower().endswith('.pdf'):
               sPDFFile = CString.NormalizePath(os.path.join(sDestinationFolder, sEntryName))
               break
         if sPDFFile is None:
            bSuccess = False
            sResult  = f"PDF file not found within '{sDestinationFolder}'"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         listPDFFiles.append(sPDFFile)

      # eof for sRepository in listRepositories:

      # create the import tex file to import the library documentations into the main documentation
      sLibraryDocImportTexFile = f"{sOutputFolder}/library_doc_imports.tex"
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
         sHeadline = os.path.basename(sPDFFile)[:-4] # name of pdf file without extension
         # the path to the PDF file to be imported, must be relative to the position of the main tex file,
         # and this means also that the PDF must be created within a subfolder of the folder containing the main tex file

         if not sPDFFile.startswith(sMainTexFileFolder):
            bSuccess = False
            sResult  = f"The PDF file '{sPDFFile}' is not located within the folder structure of '{sMainTexFileFolder}'. It is not possible to compute a relative path to this PDF file."
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

         sPDFRelPath = "." + sPDFFile[len(sMainTexFileFolder):]
         oLibraryDocImportTexFile.Write(r"\includepdf[pages=1,pagecommand=\section{" + sHeadline + "}]{" + sPDFRelPath + "}")
         oLibraryDocImportTexFile.Write(r"\includepdf[pages=2-,pagecommand={}]{" + sPDFRelPath + "}")
      # eof for sPDFFile in listPDFFiles:
      del oLibraryDocImportTexFile

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
      if os.path.isfile(sPDFFileExpected) is True:
         oPDFFile = CFile(sPDFFileExpected)
         bSuccess, sResult = oPDFFile.CopyTo(sPDFFileDestination, bOverwrite=True)
         del oPDFFile
         if bSuccess is True:
            # replacement for sResult without debug info
            sResult = f"File '{sPDFFileExpected}'\ncopied to\n{sPDFFileDestination}"
         else:
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
      else:
         bSuccess = False
         sResult  = f"Expected PDF file '{sPDFFileExpected}' not generated"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Build(self):

   # --------------------------------------------------------------------------------------------------------------

# eof class CDocBuilder():

# --------------------------------------------------------------------------------------------------------------
