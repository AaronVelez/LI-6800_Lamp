# Hardware, software and data repository associated with “Open-source LED lamp for the LI-6800 photosynthesis system” paper.

&nbsp;
## Description
This repository contains the hardware CAD files, electronic schematics, software and data associated with an open-source LED lamp for the LI-6800 photosynthesis system. The full details on the lamp design, construction and calibration can be found in the associated paper. The paper is currently under review by the editorial office of the [Applications in Plant Science](https://bsapubs.onlinelibrary.wiley.com/journal/21680450) journal from the [Botanical Society of America](https://cms.botany.org/home.html).

&nbsp;
## Releases
|  Release     |  Description                                 |  Release date |
|  ----------- | -------------------------------------------- | ------------- |
|  v1.0.0-beta.0 |  State of the repository at paper submission |  28 / Sep / 2023   |
|  v1.0.0-beta.1 |  State of the repository at paper resubmission | 23 / Apr / 2024 |
|  v1.0.0 | State of the repository at paper publication | 19 / Feb / 2025 |

&nbsp;
## Hardware
The content of this section is released under a [CERN Open Hardware Licence Version 2 - Weakly Reciprocal variant](Hardware/LICENSE). It has the following contents:

- AutoCAD Inventor files directory. It contains the 3D files of all individual parts as well as the final assembly in AutoCAD Inventor format.
- Ready-to-Print STL files directory. It contains the 3D-printable parts in STL format.
- STEP files directory. It contains the 3D files of all individual parts in STEP format.
- COB-LED driver Schematics.pdf file. Detailed electronic schematics.

&nbsp;
## Software
The content of this section is released under a [GNU Lesser General Public License Version 3](Software/LISENSE.LESSER). It has the following contents:

- Lamp folder. Software directly related with the Lamp function
  - A-PPFD_Curve.py file. An LI-6800 background program (a script in python) that performs an A-PPFD curve automatically.
  - LI-6800 Lamp Config File. A custom LI-6800 configuration file.
  - Microcontroller_Main.py file. A python script run by the Lamp internal microcontroller board.
  - PAR_Ctrl.py and PAR_Ctrl_wFB.py files. Two LI-6800 background program (a script in python) that control the light intensity in response to the desired PPFD entered by a user.

- Tools folder. Software tools used during lamp calibration and/or characterization
  - Curve_Fit_Zener_Diode.py file. A python script needed in the Lamp temperature control calibration.
  - Zenner Diode Calibration_Data Template.xlsx file. A Microsoft Excel file that serves as a data template for the Curve_Fit_Zener_Diode.py file
  - Homogenity_Scan_LabVIEW_VIs folder. A collection of LabVIEW VIs used to control a CNC machine in order to sacan the leaf area illuminated by the lamo with the objective of measuring the light homogenity
  - Homogenity_Scan_Python. Scripts used to process the RAW data measured with the LabVEW VIs

&nbsp;
## Data

- A-PPDF_Curves folder. This section contains the gas exchange data associated with the paper in a format that follows the recommendations of [Ely *et al.* (2021)]( https://doi.org/10.1016/j.ecoinf.2021.101232). The file [LI-6800_Lamp_Data_Description.pdf](Data/LI-6800_Lamp_Data_Description.pdf) holds a detailed description of all shared data files.
- Homogenity_Scans folder. This section contains the RAW measurements of the homogenity scans performed with the CNC machine.

&nbsp;
## Troubleshooting
|  Problem                                                                  |  Possible reason                                 |  Solution                                                                               |
|  ------------------------------------------------------------------------ | ------------------------------------------------ | --------------------------------------------------------------------------------------- |
|  Fan and COB-LED do not turn ON |  External power supply is not connected            | Make sure the external, 24V power supply is connected to the back of the lamp housing. |
|  At the LI-6800 console, Lamp_T shows values unexpectedly high (e.g. >100 °C), and Lamp_T_TH-r shows values close to 0 kohms |  The microcontroller is not exciting the thermistor with the required 3.3V |  At the LI-6800 console, navigate to the Console User I/O and turn ON the 5V power supply (Power5) |
|  At the LI-6800 console, the Q<sub>amb_in</sub> PPFD value is higher than the value measured with an external quantum sensor  | The Photodiode multiplier needs calibration  | Calibrate the photodiode multiplier following instructions in Appendix 2 |
|  The COB-LED dimly glows even if the DAC1 voltage is set to 0V  |  The zero offset of the XTR110 chip is not properly adjusted  |  Adjust the zero offset of the XTR110 chip by following the instructions in Appendix 2  |
