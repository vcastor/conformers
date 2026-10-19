# Molecular Optimization Workflow 🔮

## Overview

This small program automates the optimization of molecular structures provided as
SMILES strings. It utilizes Density Functional Tight Binding (DFTB) for initial
geometry optimization, followed by Density Functional Theory (DFT) calculations
for refined optimization. The workflow supports solvent effects, enabling
simulations closer to experimental conditions (or at least that's we hope 😬).

## Features

- **SMILES Input**: Accepts molecules in the SMILES notation for broad compatibility.
- **DFTB Optimization**: Quickly finds near-optimal molecular geometries using DFTB.
- **DFT Optimization**: Refines structures with DFT for accurate energy minimization.
- **Solvent Support**: Allows specifying solvents to mimic environmental conditions.
- **SCM**: We use Software of Chemistry & Materials, particularly ADF

## Getting Started

### Prerequisites

- PLAMS 1.5.1 (do not worry, Rameau has an ok version)
- [ADF](https://www.scm.com/product/adf/) for DFT calculations (oui,
  nous faisons de la publicité)

### Installation

1. I have copied everything you need with the permissions you need (i gueess)
2. Run it as:

   ```sh
   $AMSBIN/plams filter.py -v [your config].json
   ```

### Limitations

- By the use of this script, you cannot use all keywords of SCM, for example,
  you cannot modify the grid used by ADF.

- The functionals and dispersions models are just updated as the version
  of SCM 2023, and we don't have any warning about the compativility of the
  basis set and the dispersion/functional selected (it can have numerical
  issues during the calculation).

### Examples

In calculations/entropy and calculations/nucleo you can find the configurations
of the calculations.

The Results will be written in the same directory where the input file lies. 

## Code 🐍

Hiya!, if you want to see the code I would recommend use vim directly form the
terminal, but of course you can also use gedit (it's installed in Rameau), you
can just launch gedit and open the files that are in the directory.

Don't mind if you don't undesrtand the code, you see how the code should scale,
there're different files, every part of the code works for a specific task,
they are simple and organized about how they're related to each other.

The main program is alone in the directory, in a subdirectory all other files
are to written. This case is a small program, but sometimes is necessary to
have different subdirecotires to be more organised. 


et voilà ✨
any trouble call me xdxd

