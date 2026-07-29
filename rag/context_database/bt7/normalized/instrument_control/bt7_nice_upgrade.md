---
doc_id: bt7_nice_upgrade
source_id: BT7-015
title: BT7 Upgrade to NICE Control Software
instrument: BT7
workflow_stage: instrument_control
source_type: web_page
access_level: public
status: current
owner: NCNR
last_reviewed: 2026-07-29
source_url_or_path: https://www.nist.gov/ncnr/facilities-upgrades-during-unplanned-outage/bt7-upgrade-nice-control-software
source_last_updated: 2025-04-21
citation_required: false
software: NICE
---

# BT7 Upgrade to NICE Control Software

The instrument control software at BT7 has been upgraded to the current version of NICE.

## NICE DAQ Software Overview
NICE provides a reliable, powerful, and flexible control system implemented using a client-server architecture to optimize neutron beamtime and support non-routine sample environments.

*   **Server:** Coordinates instrument motions, device control, and measurements to execute experimental plans. It gathers results into archival data files for users.
*   **Client:** Provides a graphical interface for operating the instrument and creating experiment plans. It offers graphs, feedback on current operations/scans, and a visual representation of the instrument state.
    *   **Trajectory Manager GUI:** Used for simple control.
    *   **API:** Used for advanced control.
    *   **Remote Access:** Multiple clients can connect simultaneously from different locations.

**Data Format:** The standardized NeXuS file format is supported by default. Instrument scientists can add and toggle additional file writers (e.g., text columns).

## BT7 Implementation and Milestones
BT7 is the first triple axis instrument to be fully supported under NICE. Many components developed for BT7 were designed for broader use across other triple axis instruments.

### BT7 Modules Created for NICE
*   **Sample Alignment:** A core Triple Axis sample alignment system created for BT7. It currently operates in-plane, with a designed extension for out-of-plane support for large sample environment equipment.
*   **Trajectory Manager:** Leverages the NICE trajectory system to create common BT7 trajectories. These can be run as-is or modified for customized measurements and data organization.
*   **Polarized Beam:** Supports polarized beam operations. The Trajectory Manager can incorporate polarized beam changes at customized levels in the measurement to optimize the balance between measurement speed (inner loop) and polarizer efficiency (outer loop).
*   **Instrument Alignment:** A system for aligning core triple axis motors (monoTwoTheta and sampleTwoTheta) using well-characterized samples.
*   **Instrument Visualization:** Provides a live, real-time, top-down cartoon representation of the instrument.
    *   **Functionality:** Supports zooming, panning, rotating, and "lock-on" camera views (e.g., beam-sample-detector).
    *   **Interactivity:** Mouse-over displays live status of motor positions, limits, and high-level quantities.
    *   **Detailed Views:** 
        *   **DFM:** Shows realistic motor positions and a top-down profile/shadow of each blade during focusing.
        *   **Analyzer:** Shows analyzer blades and detector/collimator carriages.
*   **Simulation:** A simulated `BT7server` is available for offline or home testing. It communicates with simulated hardware, ensuring ~98% of the code is identical to the production system.

### Improved Plotting System
The plotting system was rewritten to address specific triple axis and general instrument requests. Key features include:
*   **Multi-variable Plotting:** Ability to plot multiple y-axis variables.
*   **Data Overlay:** Ability to overlay any two accessible plots; every plot/y-axis combination is graphed simultaneously.
*   **Navigation:** Modern panning and zooming capabilities.
*   **Labeling:** Implementation of a smart tick labeling system.
*   **Historical Data Access:** Users can browse and plot all previously collected data seamlessly. All plotting features (including overlay) are available for historical data.
*   **Integration:** Integrated with other NICE features such as `findpeak` and precise unit/precision displays.

## Additional System Updates
*   **DFM Logic:** BT7 DFM focusing logic is now managed by NICE. The DFM motor computer now operates largely as a simple array of motors.

All major features have been tested on instrument hardware, and BT7 is fully upgraded to the current version of NICE.

<!-- Source: BT7: Upgrade to NICE Control Software (https://www.nist.gov/ncnr/facilities-upgrades-during-unplanned-outage/bt7-upgrade-nice-control-software). Removed site navigation, header/footer chrome, and "was this page helpful" widget. -->
