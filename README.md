# Celia DTB Validator

E-book and audiobook validation tool

# Introduction

## What does the Celia DTB Validator do?

The Celia DTB Validator analyses files for their digital peak level, true peak (ISP) level, signal-to-noise ratio and LUFS. Validator also looks for unexpected silences in files and checks that there is silence at end of file and no silence at start of file. If examined book is Daisy it is also possible to validate book using Daisy Pipeline Validator light. It is also possible to encode audio of a Daisy book to mp3 using Daisy Pipeline.

### Validations performed
- Lufs, pkdb, tpkdb, snr levels are in valid range
- Lufs does not change noticeably between two files
- There is enough silence at end of file
- There is not too much silence at end of file
- There is sound at beginning of file
- There are no unexpected silences at middle of file
- ncc.html file exist (if daisy book)
- smil-files exist (if daisy book)
- filename prefix matches dc:identifier (if daisy book)
- Number of smil files is same as number of audio files (if daisy book)
- master.smil file exists
- Only one phrase in the first heading (if daisy book)
- ncc.html encoded to certain character encoding (if daisy book)
- Metadata fields not left empty (if daisy book)
- Page numbers not found at first phrase of heading (if daisy book)
- Daisy pipeline 1 Daisy 2.02 Validator light validation

## Installation

Celia DTB Validator is designed to work on Windows 10, using Python 3.5.2. (newer python3 versions should also work)

For audio and Daisy validation it is required that following programs are also installed:
- SoX v14.4.2
- ffmpeg 2.2.2
- Daisy Pipeline 1 v. 20111215.

Other version might also work, but have not been tested and might not work.
If validation is done for audio only, Daisy Pipeline is not required.
Please refer to the documentation of the programs mentioned for more information
on installation and usage.

Sox and ffmpeg must be in in PATH, ie. so that they work with commands 'sox' & 'ffmpeg'.

It is also to be noted that sox or ffmpeg might also require aditional modules to
be installed in order for them to be able to work with files in mp3 format.
Please refer to documentation provided by sox & ffmpeg for more information.

For installation of Celia DTB Validator the files can be placed in any location.
Celia DTB Validator is written in pure Python3 and does not require any additional
Python modules to run. Usage of virtualenv is recomended but not required.

For basic usage use validator_gui.py to run Celia DTB Validator GUI.

For advanced usage use celia_dtb_validator.py from cmd or Powershell.

## Usage

Celia DTB Validator can be run from command line or using a minimalistic GUI.

These are the key components:

**Input path:**
Path to the folder containing book to be validated
**Output path:**
Path to folder where encoded book is placed (if audio encoding is enabled)
**Report path:**
Path to folder where validation report is stored
**Config file:**
File where all variables (for example valid LUFS values etc.) can be set and where audio and daisy validations and audio encoding can be enabled/disabled. Config file is located on the same folder as the file celia_dtb_validator.py.

### Graphical user interface

![image of gui](./img/gui_img1.jpg)

Minimalistic GUI enables user to define all paths, open the config file for editing and to start the validation.

Validation output is shown on Python3 prompt. After validation is finished the report is shown in users
default webbrowser.

![image of report](./img/gui_img2.jpg)

After examining the report the user can then decide wheter or not to proceed with audio encoding.

![image of cmd prompt](./img/gui_img3.jpg)

### Command line interface

Command line interface can be run with following command:

    python celia_dtb_validator.py -i BOOKPATH [-o OUTPUTPATH] [-r REPORTPATH]

There is also parameter -h to print basic usage info and -v to print version number.

**NOTE ON PATHS WITH SPACES:**
If you use paths with spaces you should leave out the last backslash. The last backslash will be interpreted as escape character.
Use 'C:\Temp\Path With Spaces' instead of 'C:\Temp\Path With Spaces\'

You can also use double quotes ie. "'C:\Temp\Path With Spaces\'", or use forward slahes instead, ie. 'C:/Temp/Path With Spaces/'

### Configuration

All setting can be configured using the config.txt file. Please see config.txt for more information.

Note: If you mess up your configuration file a new one is generated automatically, if you delete
or rename the current config.txt file.

### Examples

#### Daisy production example
1. Record book as usual.
2. Regenerate book using book id as file name prefix (optional)
3. Change dc:identifier on (regenerated) books ncc.html to book id  
   (optional - dc:identifier is used as mp3 encoded books foldername  
   (if empty folder is named as 'mp3'))  
4. Run validation on (regenerated) book using folowing configurations  
    audio_validation = 1  
    daisy_validation = 1  
    encode_audio = 1  
    target_kbps = 64 (or some other value)  
5. Examine validation report
6. Validator ask if you wish to continue with audio encoding  
    if there are errors -> answer no and fix them on original book and do steps 2-5 again  
    if no errors are found -> answer 'y'  
7. After encoding the encoded audio book is in output-folders


#### Daisy and audio validation example
1. Run validation on any Daisy book using folowing configurations  
    audio_validation = 1  
    daisy_validation = 1  
    encode_audio = 0  
2. Examine validation report  
    if there are errors -> fix/report them etc.


#### Mp3 playlist audiobook audio validation
1. Record audio and generate playlist as usual
2. Run validation on folder containing audio files using folowing configurations:  
    audio_validation = 1  
    daisy_validation = 0  
    encode_audio = 0 (optional -> disabling daisy validations automatically disables audio encoding)  
3. Examine validator report  
    if there are errors -> fix errors and do steps 1-3 again


#### Batch validate all daisy books in a folder
1. Put all books in one folder
2. Use folowing configurations:  
    audio_validation = 1  
    daisy_validation = 1  
    encode_audio = 0  
3. Run following Powershell command:  
    $dtbs = ls -Directory -Path PATHTOFOLDER | % { $_.FullName } ; foreach ($dtb in $dtbs) {python PATHTOVALIDATOR\celia_dtb_validator.py -i $dtb -r PATHTOFOLDER}  
4. Reports are opened into default webbrowser in tabs and stored into PATHTOFOLDER.

## License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
