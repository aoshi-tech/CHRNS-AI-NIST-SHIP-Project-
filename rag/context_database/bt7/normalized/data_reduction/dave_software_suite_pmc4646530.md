---
doc_id: dave_software_suite_pmc4646530
source_id: BT7-014
title: 'DAVE: A Comprehensive Software Suite for the Reduction, Visualization, and Analysis of Low Energy Neutron Spectroscopic Data'
instrument: BT7
workflow_stage: data_reduction
source_type: paper
access_level: public
status: current
owner: NCNR
last_reviewed: 2026-07-29
source_url_or_path: pmc.ncbi.nlm.nih.gov/articles/PMC4646530/
citation_required: true
software: DAVE
---

# DAVE: A Comprehensive Software Suite for the Reduction, Visualization, and Analysis of Low Energy Neutron Spectroscopic Data

## Abstract
National user facilities such as the NIST Center for Neutron Research (NCNR) require a significant base of software to treat the data produced by their specialized measurement instruments. DAVE (the Data Analysis and Visualization Environment) is a software package developed at the NCNR for the reduction, visualization, and analysis of inelastic neutron scattering data. Developed using a high-level scientific programming language (IDL), it has been widely adopted globally to streamline the transition from raw data to analytically interpretable quantities.

## 1. Introduction
The community of researchers using neutron scattering has historically lacked a single, coherent software suite for data treatment, leading to fragmented development and the "reinvention" of capabilities during instrument commissioning. DAVE was developed at the NCNR to address these issues by providing easy-to-use tools for a diverse user base, ranging from students to industrial researchers, ensuring that data can be reduced and viewed in near real-time during experiments.

## 2. Neutron Spectroscopy
Neutron spectroscopy measures the scattered intensity as a function of momentum transfer $\vec{Q} = \vec{k}_i - \vec{k}_f$ and energy transfer $\hbar\omega = E_i - E_f$. 

The primary goal of data reduction is to convert raw, instrument-specific counts into the double differential scattering cross section, which is approximately proportional to the scattering function (dynamic structure factor), $S(\vec{Q}, \omega)$.

## 3. Evolution of the DAVE Package

### 3.1 Motivation
Prior to the 2000s, NCNR users relied on ad-hoc command-line programs. With the introduction of new instruments—such as the Direct-Geometry Disk Chopper Spectrometer (DCS), High Flux Backscattering Spectrometer (HFBS), and Neutron Spin Echo (NSE) spectrometer—the need for a common visualization and analysis platform became critical.

### 3.2 Development Approach
DAVE was developed through cooperation between instrument scientists and a core group of software developers. The team selected **IDL (Interactive Data Language)** as the platform due to its mature visualization and analysis routines. To ensure accessibility, DAVE is distributed as a free binary executable with an embedded IDL license, compatible with Windows, Mac, and Linux.

### 3.3 Data File Format
DAVE utilizes a standardized internal hierarchical data structure specified in November 2001 to ensure consistency across the application suite.

### 3.4 Education and Training
To maintain software quality and foster development, the NCNR implemented hands-on IDL training courses for staff, covering data manipulation, visualization, and the DAVE internal data format.

## 4. Capabilities of the DAVE Package

### 4.1 Experiment Planning Tools
DAVE provides tools to optimize sample dimensions and instrument parameters.

**Table 1: Experiment Planning Tools in DAVE**

| Category | Tool |
| :--- | :--- |
| **Neutron Cross Section** | Table, Calculator |
| **Self Shielding** | Cylindrical/Annular Geometry, Slab Geometry |
| **Disk Chopper Spectrometer (DCS)** | Experiment Planner |
| **Triple Axis Spectrometer (TAS)** | Resolution Calculator, Scan Mapper |
| **Rotor Models** | Hindered Rotor, Diatomic Rigid Rotor, Methyl Rotor, Coupled Methyl Rotor |
| **General** | Number Density Calculator, Molecular Weights and Concentrations, Neutron Calculator and Units Converter |

#### Key Planning Tools:
*   **TAS Scan Mapper**: Identifies regions of reciprocal space inadvertently accessed during a scan (e.g., higher-order reflections), highlighting potential spurious peaks.
*   **Neutron Cross Section Calculator**: Calculates number density and macroscopic scattering/absorption cross sections based on chemical formulae and bulk density.
*   **DCS Experiment Planner**: Assists in selecting incident wavelength, chopper speeds, and coverage in $(Q, \omega)$ space.

### 4.2 Data Reduction
DAVE converts raw instrument-specific data into the double differential scattering cross section. It supports five instrument classes:
1.  Triple-axis
2.  Time-of-flight
3.  Filter analyzer
4.  Back-scattering
5.  Spin echo spectroscopy

**Table 2: Data Reduction Software Modules in DAVE**

| Facility | Instruments |
| :--- | :--- |
| **NCNR (NIST)** | DCS, FANS, HFBS, NSE, 4x TAS |
| **SINQ (PSI)** | FOCUS (ToF), MARS (Backscattering) |
| **ISIS (RAL)** | OSIRIS (McStas Simulated Data Reduction) |
| **ILL** | IN5 (Disk Chopper ToF) |

### 4.3 Data Visualization

#### 4.3.1 Data Browser
A general-purpose module for managing DAVE formatted data. It supports 1D multi-line plots and 2D area/contour/surface plots with customizable attributes and rubber-band zooming.

#### 4.3.2 Mslice
Specifically designed for time-of-flight multi-detector data (e.g., DCS). It converts $I(2\theta, t)$ to $S(\vec{Q}, \omega)$ or generalized density of states. It can aggregate multiple data sets from different sample orientations to visualize excitations in reciprocal space.

#### 4.3.3 DenPro
A 3D visualization tool for crystallographic measurements. It reads CIF (Crystallographic Information File) and GRD files to display space-fill/ball-and-stick models and 3D isosurfaces of electron or neutron scattering length density.

#### 4.3.4 Gaussian Viewer (G3dview)
Allows comparison of FANS instrument measurements with molecular calculations from the Gaussian software package. It reconstructs molecular structures and calculates the intensity of the $j$-th vibrational mode:
$$I_j = \sum_{i=1}^{N} (\sigma_i / m_i) \exp(-2W_i) e_{ij}^2$$
Where $N$ is the number of atoms, $W_i$ is the Debye-Waller coefficient, and $e_{ij}$ is the associated eigenvector.

### 4.4 Data Analysis

#### 4.4.1 Curve Fitting
*   **PAN (Peak ANalysis)**: A general-purpose tool for fitting model functions (Gaussian, Lorentzian, KWW) to data using non-linear least-squares fitting. It accounts for instrumental resolution $R(\omega)$ via convolution:
    $$I_{fit}(\omega) = \int d\omega' I_{model}(\omega') R(\omega - \omega')$$
*   **RAINS (Refinement Application for Inelastic Neutron Scattering)**: Performs 2D surface fits of $S(Q, \omega)$ based on theoretical models.

#### 4.4.2 MagProp
Designed for magnetochemists to analyze inelastic neutron scattering data in conjunction with magnetic data (e.g., from magnetometers). It utilizes Hamiltonian expressions to calculate magnetic properties and refine models.

## 5. Usage and Impact
DAVE is the primary software for inelastic neutron scattering at the NCNR and has been adopted by other facilities including SNS (Oak Ridge), OPAL (Australia), ISIS (UK), and SINQ (Switzerland). Its utility extends beyond neutron scattering, with the PAN module being used in astrophysics for processing galactic emission line data.

<!-- Source: DAVE: A Comprehensive Software Suite for the Reduction, Visualization, and Analysis of Low Energy Neutron Spectroscopic Data (https://pmc.ncbi.nlm.nih.gov/articles/PMC4646530/). Removed navigation menus, site chrome, and truncated incomplete final section. -->
