---
doc_id: lecture_2_facilities
source_id: COMMON-017
title: Neutron Scattering Instrumentation & Facilities
instrument: COMMON
workflow_stage: overview
source_type: presentation_pdf
access_level: public
status: current
owner: [contact details omitted]
last_reviewed: 2026-07-29
source_url_or_path: Lecture_2_Facilities.pdf
citation_required: false
---

# Neutron Scattering Instrumentation & Facilities

## Overview
This lecture covers the fundamentals of how neutron scattering is measured, including:
*   **Neutron Sources**: Reactors and spallation sources, including their spectra.
*   **Measurement Methods**: Monochromatic-beam and time-of-flight (ToF) methods.
*   **Instrument Components**: The hardware required to conduct experiments.
*   **Specialized Spectrometers**: The various types of neutron spectrometers used in research.

## Recapitulation of Key Messages
*   Neutron scattering experiments measure the number of neutrons scattered by a sample as a function of the wavevector change ($Q$) and the energy change ($E$).
*   Scattered intensity relates to the positions and motions of atomic nuclei or unpaired electron spins.
*   The intensity as a function of $Q$ and $E$ is proportional to the space and time Fourier Transform of the probability of finding two atoms separated by a particular distance at a particular time.
*   Measuring the change in neutron spin state provides information about the locations and orientations of unpaired electron spins.

## Basic Requirements for Neutron Scattering
To perform a basic neutron scattering experiment, the following are required:
1.  **A source of neutrons**.
2.  **A method to prescribe the wavevector** of the incident neutrons.
3.  **An interesting sample**.
4.  **A method to determine the wavevector** of the scattered neutrons (not required for elastic scattering).
5.  **A neutron detector**.

**Key Relationship:**
Wavevector $k$ and wavelength $\lambda$ are related by:
$$k = \frac{mnv}{h/2\pi} = \frac{2\pi}{\lambda}$$

## Neutron Sources

### Production Methods
Neutrons are produced via two primary methods:
*   **Nuclear Fission (Reactors)**: Produce continuous neutron beams.
*   **Spallation**: High-energy protons strike a heavy metal target (W, Ta, or U), producing pulsed beams (typically 20 Hz to 60 Hz). Spallation sources produce more high-energy neutrons.

### Moderation
Neutron spectra are tailored using moderators (solids or liquids maintained at specific temperatures):
*   **Cold Sources**: Usually liquid hydrogen (sometimes deuterium or methane).
*   **Hot Sources**: For example, radiation-heated graphite (e.g., at ILL).

### Facility Examples
*   **NIST Reactor**: A 20 MW research reactor with a peak thermal flux of $4 \times 10^{14}$ N/sec, featuring a unique liquid-hydrogen moderator serving seven neutron guides.
*   **LANSCE (Los Alamos Neutron Science Center)**: 
    *   800-MeV Linear Accelerator (Linac) producing 20 $H^-$ pulses per second.
    *   Proton Storage Ring that strips electrons to convert $H^-$ to $H^+$ before hitting the target.

## Comparison: Reactors vs. Spallation Sources

| Feature | Reactor | Short Pulse Spallation Source |
| :--- | :--- | :--- |
| **Spectrum** | Maxwellian | "Slowing down" spectrum (preserves short pulses) |
| **Energy Cost** | $\sim 180$ MeV / useful neutron | $\sim 20$ MeV / useful neutron |
| **Polarization** | Easier | - |
| **Capabilities** | Large flux of cold neutrons; good for large objects/slow dynamics | Single pulse experiments; high-energy "hot" neutrons for large $Q$ and $E$ |
| **TOF/S/N** | - | Optimized pulse rate; low background between pulses |
| **Resolution** | Constant, small $\delta\lambda/\lambda$ at large energy | Tailored resolution, though less effective for hot neutrons |

## Time-of-Flight (ToF) Method
The ToF method enhances efficiency by using multiple wavelength slices simultaneously. 

*   **Gain**: The potential performance gain relative to a single wavelength is equivalent to the number of different wavelength slices used.
*   **Resolution**: $\Delta \lambda_{res} = 3956 \delta T_p / L$ (where $L$ is distance).
*   **Challenges**: ToF gain may not scale linearly with peak flux; short pulses provide good resolution but may not always be necessary; wavelength resolution can change with wavelength at traditional sources.

## Neutron Scattering Spectrometers

### Design Rationale
There is no "universal" spectrometer because the accessible $Q$ and $E$ depend on neutron energy. Resolution and detector coverage must be tailored to specific science goals due to the signal-limited nature of the technique.

**Governing Equations:**
*   Conservation of momentum: $Q = k_f - k_i$
*   Conservation of energy: $E = (\frac{h^2 m}{8 \pi^2}) (k_f^2 - k_i^2)$

### Specialization Examples
*   **Small Angle Scattering**: Used for large objects. Requires long instruments ($\sim 20$ m) and small diffraction angles.
*   **Back Scattering**: Used for high energy resolution ($\sim$ neV). Utilizes perfect crystal analyzers at $\theta \approx \pi/2$.

### Instrumental Resolution
Uncertainties in wavelength and direction mean $Q$ and $E$ are defined with finite precision. The overall resolution is generally Gaussian (elliptical in $Q, E$ space). Higher resolution results in a lower count rate.

## Instrument Components

| Component | Function |
| :--- | :--- |
| **Monochromators** | Select or analyze neutron energy using Bragg's law. |
| **Collimators** | Define the neutron direction of travel. |
| **Guides** | Transport neutrons over long distances with minimal loss (e.g., Ni or supermirror coated glass). |
| **Detectors** | Typically use $^3\text{He}$ absorption: $^3\text{He} + n \rightarrow {}^3\text{H} + p + 0.764\text{ MeV}$. |
| **Choppers** | Define short pulses or select energy bands; "T-zero" choppers absorb prompt high-energy pulses. |
| **Spin Turn Coils** | Manipulate neutron spin via Larmor precession. |
| **Shielding** | Minimize background noise and radiation exposure. |

### Additional Technical Notes
*   **Detector Efficiency**: $70\%$ of neutrons are absorbed when $\text{pressure} \times \text{thickness} \times \text{wavelength} = 16\text{ atm}\cdot\text{cm}\cdot\text{\AA}$.
*   **Frame-Overlap**: Occurs when fast neutrons from one pulse catch up to slower neutrons from a previous pulse; managed via Cd frame-overlap choppers.
*   **Larmor Precession**: In a magnetic field $H$, neutron spin precesses at a rate $\omega = \gamma H$. A "spin flipper" can turn the spin by 180 degrees.

<!-- Source: Lecture 2: Neutron Scattering Instrumentation & Facilities. Removed slide transitions, repetitive diagrams of flux calculations, and placeholder page markers. -->
