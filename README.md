# Hardware, software and data repository associated with “Open-source LED lamp for the LI-6800 photosynthesis system” paper.
&nbsp;

&nbsp;
## Description
This repository contains the hardware CAD files, electronic schematics, software and data associated with an open-source LED lamp for the LI-6800 photosynthesis system. The full details on the lamp design, construction and calibration can be found in the associated paper. The paper is currently under review by the editorial office of the [Applications in Plant Science](https://bsapubs.onlinelibrary.wiley.com/journal/21680450) journal from the [Botanical Society of America](https://cms.botany.org/home.html).
&nbsp;

&nbsp;
## Releases
|  Release     |  Description                                 |  Release date |
|  ----------- | -------------------------------------------- | ------------- |
|  1.0.0-beta.0 |  State of the repository at paper submission |     |
&nbsp;

&nbsp;
## Hardware
The content of this section is released under a [CERN Open Hardware Licence Version 2 - Weakly Reciprocal variant](Hardware/LICENSE). It has the following contents:

- AutoCAD Inventor files directory. It contains the 3D files of all individual parts as well as the final assembly in AutoCAD Inventor format.
- Ready-to-Print STL files directory. It contains the 3D-printable parts in STL format.
- STEP files directory. It contains the 3D files of all individual parts in STEP format.
- COB-LED driver Schematics.pdf file. Detailed electronic schematics.
&nbsp;

&nbsp;
## Software
The content of this section is released under a [GNU Lesser General Public License Version 3](Software/LISENSE.LESSER). It has the following contents:

- A-PPFD_Curve.py file. An LI-6800 background program (a script in python) that performs an A-PPFD curve automatically.
- Curve_Fit_Zener_Diode.py file. A python script needed in the Lamp temperature control calibration.
- LI-6800 Lamp Config File. A custom LI-6800 configuration file.
- Microcontroller_Main.py file. A python script run by the Lamp internal microcontroller board.
- PAR_Ctrl.py and PAR_Ctrl_wFB.py files. Two LI-6800 background program (a script in python) that control the light intensity in response to the desired PPFD entered by a user.
- Zenner Diode Calibration_Data Template.xlsx file. A Microsoft Excel file that serves as a data template for the Curve_Fit_Zener_Diode.py file
&nbsp;

&nbsp;
## Data

