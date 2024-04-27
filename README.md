# PyTFT - Automated Extraction of TFT Parameters for Simulation (SPICE MOS Level 3)

## Introduction
This is an automated tool for the extraction of simulation parameters from Thin Film Transistors (TFT) for SPICE simulation. In large-area microelectronics, TFTs are the foundational components in microelectronic devices which include displays, and sensor arrays. The more complex the circuitry becomes, the more accurate simulations are required before fabrication of the devices. An automated tool helps to get parameters for the SPICE simulation and help to know the device behaviour through simulation results before fabrication.

Simulation frameworks like SPICE are used for circuit or TFT simulations, which require manual extraction of TFT model parameters. The central aim of this thesis is to design a tool that automates the extraction of parameters from measured TFT characteristic curves, thus automating the simulation process. The functionality of the tool is expanded to provide comparative analysis between measured and simulated graphs from the TFT input and output characteristic curves, using an iterative optimization algorithm.

## Features
- **Comprehensive GUI**: Built with Tkinter, offering an intuitive interface for data input and parameter configuration.
- **Multiple Optimization Algorithms**: Includes options like Differential Evolution and custom versions for flexibility.
- **Graphical Data Visualization**: Integrated matplotlib for real-time plotting of transistor characteristics and extraction results.
- **Configurable Parameter Settings**: Users can adjust optimization settings directly through the GUI.
- **Output Results Handling**: Ability to save extracted parameters and plots.

## Getting Started

### Prerequisites
- Python 3.8 or newer
- Dependencies: `matplotlib`, `numpy`, `scipy`, `PIL`, `tkinter`, `configparser`, and `subprocess`

## Structure

- `Documents/`: Contains thesis documents, presentations, and related material.
- `Measurements/`: Holds the input and output characteristic curves of different TFTs.
- `IGM.ico`: The application icon file.
- `TFT_Parameter_Extraction.exe`: Executable for Windows users.
- `TFT_Parameter_Extraction_Linux`: Python source files tailored for Linux systems.
- `TFT_Parameter_Extraction_Windows`: Python source files tailored for Windows systems.

## How to Use PyTFT

### Open Input File
1. Navigate to 'File' -> 'Open Input File'.
2. Select the `.dat` file with the measured input characteristics of the IGZO TFT device.
3. The corresponding output file is automatically selected, so there is no need to open it separately.

### Open Output File
1. Go to 'File' -> 'Open Output File'.
2. Choose the `.dat` file that contains the measured output characteristics of the IGZO TFT device.

### Configure Algorithm (Optional)
1. Click on 'Algorithm' from the menu options.
2. Select the optimization algorithm you wish to use for parameter extraction.

### Run Parameter Extraction
1. Choose 'Run' -> 'Run' from the menu to start the extraction process.
2. The parameters will be extracted using the chosen algorithm and the results displayed within the GUI.

### Save Output Parameters
1. Select 'File' -> 'Save Output Parameters'.
2. Decide where you want to save the extracted parameter values and save them as a `.txt` file.

### Save Plots as PDF (Optional)
1. Click on 'File' -> 'Save Plots as PDF'.
2. Pick a save location for the plots and save them in a PDF format.

### Understanding the Differential Evolution Custom Algorithm
This custom algorithm version of Differential Evolution allows for detailed configuration:

- **Population Size**: Determines the number of individuals per generation in the optimization process.
- **Mutation Factor (F)**: Defines the scale of mutation differences.
- **Crossover Probability (CR)**: Sets the likelihood of crossover events between target and mutant vectors.
- **Maximum Generations**: The limit for the number of generations the algorithm will process to reach convergence.

### Interpretation of Output Parameters
The program will calculate and display the following parameters, representative of the IGZO TFT device characteristics:

- **Threshold Voltage (VTO)**: The gate voltage at which the device starts to conduct.
- **Mobility (U0)**: The speed at which charge carriers can move through the transistor channel.
- **Output Resistance Coefficient (Kappa)**: A factor affecting the output resistance of the device.
- **Static Feedback Factor for Adjusting Threshold (Eta)**: Influences the threshold voltage shift due to the drain voltage.
- **Channel Length Modulation (LAMBDA)**: Modulation of channel length due to the drain voltage.
- **Bulk Charge Effect Parameter (nfs)**: Charge effect in the bulk of the device.
- **Bulk Surface Doping (nsub)**: The doping level of the substrate.
- **Mobility Degradation Factor (Theta)**: The degree of mobility degradation in the field.

Each output parameter provides insight into the device's behavior under different electrical stimuli.

## Measurement File Structure

The `Measurements/` folder should contain files for each TFT device under test.

- A `*_input.dat` file containing the gate voltage (Vg) vs. drain current (Id) data.
- A `*_output.dat` file containing the drain voltage (Vd) vs. drain current (Id) data.

The .dat files should be formatted as tab-separated values with a header row describing each column.

## Measurement Protocols

The function `generate_netlist` provided outlines how to programmatically create netlist files for use with a simulation tool, such as SPICE, which models the electronic behavior of Thin-Film Transistors (TFTs). Based on the netlist content, you can infer the necessary measurement protocol for the TFTs. Here's how you should carry out the measurements:

#### For Input Characteristics (Transfer Curve):
1. **Gate Voltage (Vg) Sweep**:
   - Start at a negative voltage (e.g., -10 V) to ensure the device is fully off.
   - Sweep to a positive voltage (e.g., 20 V) to drive the device into strong inversion.
   - Step Size: 0.5 V increments are a good balance between resolution and measurement time.

2. **Drain Voltage (Vd)**:
   - Set to a constant low value (e.g., 0.1 V) to measure the sub-threshold region.
   - Then, increase it in steps (e.g., 5 V increments) up to a high value (e.g., 15.1 V) to characterize the output conductance.

3. **Measurement Steps**:
   - At each step of Vg, measure the drain current (Id).
   - Record the values to a file with a format that matches the `.dat` file expected by your program.

#### For Output Characteristics (Output Curve):
1. **Drain Voltage (Vd) Sweep**:
   - Start from 0 V to ensure the device is initially off.
   - Sweep up to a voltage high enough to reach the saturation region of the device (e.g., 20 V).
   - Step Size: 0.5 V increments to capture the entire active region of the device characteristics.

2. **Gate Voltage (Vg)**:
   - Set to multiple constant values to see how the output characteristics change with different gate biases.
   - Common choices might include steps (e.g., 0 V, 4 V, 8 V, 12 V, 16 V, 20 V) to cover from the sub-threshold to above-threshold operation.

3. **Measurement Steps**:
   - At each Vg set point, sweep Vd and measure Id.
   - Store these sets of measurements in your output file as per the `.dat` structure.


## Output Data Interpretation

The tool will output the following parameters:
- Threshold Voltage (Vth)
- Mobility (µ)
- Subthreshold Swing (SS)
- On/Off current ratio

Each parameter will be presented with its statistical 20% margin of error.

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

## Authors

- Arpan Biswas, Patrick Schalberger - Initial work -  Institut für Großflächige Mikroelektronik (IGM), University of Stuttgart


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Supervisor - Dr.-Ing. Patrick Schalberger
- Co-superviser : M. Sc. Florian Kleber
- Examiner - Prof. Dr.-Ing. N. Frühauf
-  Institut für Großflächige Mikroelektronik (IGM), University of Stuttgart

