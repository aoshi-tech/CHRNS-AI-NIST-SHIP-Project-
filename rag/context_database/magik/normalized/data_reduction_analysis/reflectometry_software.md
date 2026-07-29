---
doc_id: reflectometry_software
source_id: MAGIK-010
title: Reflectometry Software
instrument: MAGIK
workflow_stage: data_reduction_analysis
source_type: web_page
access_level: public
status: current
owner: NCNR
last_reviewed: 2026-07-29
source_url_or_path: https://www.nist.gov/ncnr/neutron-instruments/data-reduction-analysis/reflectometry-software
source_last_updated: 2026-07-17
citation_required: true
software: Refl1D
---

# Reflectometry Software

## Refl1D
Refl1D is used for the fitting and uncertainty analysis of neutron and X-ray reflectivity data.

### Quickstart
If the `uv` tool is installed, Refl1D can be started immediately via the command line:
```bash
uvx refl1d
```

### Installation

#### Windows (Application Installer)
1. Download the `...Windows-x86_64-installer.exe` from the [latest releases](https://github.com/reflectometry/refl1d/releases).
2. Run the installer. Optional shortcuts can be added for:
    * Launch Refl1D webview gui from the Start Menu
    * Launch Refl1D Powershell session (for pip-installing additional libraries or command-line use)
    * Launch Refl1D webview gui from the Desktop
3. **Upgrading:** To upgrade, uninstall the old version via "add/remove programs" in Windows settings before installing the newer version.

#### MacOS (DMG Bundle)
1. Download the appropriate architecture:
    * `...Darwin-arm64.dmg` for M-series Macs.
    * `...Darwin-x86_64.dmg` for Intel-based Macs.
2. Open the `.dmg` file and drag the `refl1d` app to the `/Applications` folder.
3. Launch the webview using `refl1d.app` in the `/Applications/refl1d-<version>` folder.
4. Launch the shell using `refl1d_shell.app` to add additional pip packages (e.g., `pip install molgroups`).

#### Python Package Index (pip install)
1. Install Python 3 (version 3.10 or greater).
2. Open a terminal (MacOS) or Anaconda Prompt (Windows) and run:
   ```bash
   pip install refl1d[webview]
   ```
3. **Execution:**
    * `refl1d`: Starts the command-line client.
    * `refl1d --edit`: Starts an interactive fitting session.
    * `pip install --upgrade refl1d`: Updates to the latest version.

### Additional Information
* **Manual:** See the Refl1D manual for program details.
* **Dependencies:** Refl1D uses **Bumps** for fitting and **PeriodicTable** for scattering length density (SLD) calculations.
* **Citation:** Acknowledge Refl1D in publications by referencing the software site:
  > The Refl1D program was used for elements of the data analysis[1].
  > [1] P.A. Kienzle, B.B. Maranville, K.V. O'Donovan, J.F. Ankner, N.F. Berk, C.F. Majkrzak; https://www.nist.gov/ncnr/reflectometry-software

## Reductus
Reductus is a web application for the reduction of raw NCNR instrument data to reflectivity data.

* **Functionality:** Driven by the `reflred` Python libraries, it converts raw X-Ray and neutron reflectivity data into a reflectivity curve in physical units (R vs. Q).
* **Capabilities:** Performs background subtractions, scaling, and other necessary corrections.
* **Data Access:** Files are accessed directly via URL from the NCNR online data repository. 
* **Workflow:** Reduction templates (recipes) can be modified with a graphical editor, shared via email, and downloaded/reused. Reduced data is available as columnar text files. No login is required.
* **Legacy:** Reductus replaces the **Reflpak** application.
* **Citation:** Users should cite *Journal of Applied Crystallography, Volume 51, Part 5, pages 1500-1506*.

## PeriodicTable
**Online SLD Calculator:** This tool uses the `PeriodicTable` package (also used by Refl1D and SasView) to compute scattering length density and neutron activation.

## Web Reflectivity Calculators
Browser-based calculators are provided for quick data exploration:
* Magnetic reflectivity calculator.
* Non-magnetic (unpolarized) reflectivity calculator.

User-generated SLD profiles from these calculators can be exported to a commented Python Refl1D model file to facilitate the transition to detailed modeling. See the article in *J. Res. NIST* for more details.

## References

* **Calculating Polarized Neutron Reflectometry:** C.F. Majrkzak, K.V. O'Donovan, N.F. Berk (2006); *Neutron Scattering from Magnetic Materials*, T. Chatterji, editor. Elsevier.
* **Polarization Corrections:** C.F. Majkrzak (1996); *Physica B* 221, 342-356.
* **Modelling Interfaces with Slabs:** J.F. Ankner, C.F. Majkrzak (1992); *S.P.I.E. Conference Proceedings*, Vol. 1738.

<!-- Source: Reflectometry Software | https://www.nist.gov/ncnr/neutron-instruments/data-reduction-analysis/reflectometry-software. Removed site navigation, header/footer chrome, government boilerplate regarding .gov websites, and "Was this page helpful?" widget. -->
