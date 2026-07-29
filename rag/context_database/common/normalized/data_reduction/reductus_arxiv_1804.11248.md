---
doc_id: reductus_arxiv_1804
source_id: COMMON-016
title: 'reductus: a stateless Python data-reduction service with a browser frontend'
instrument: COMMON
workflow_stage: data_reduction
source_type: paper
access_level: public
status: current
owner: NIST Center for Neutron Research
last_reviewed: 2026-07-29
source_url_or_path: reductus_arxiv_1804.11248.pdf
citation_required: true
software: Reductus
---

# reductus: a stateless Python data-reduction service with a browser frontend

The online data reduction service **reductus** transforms measurements in experimental science from laboratory coordinates into physically meaningful quantities with accurate estimation of uncertainties based on instrumental settings and properties. 

The service is designed to allow the construction of arbitrary pipelines from well-known data transforms using a visual dataflow diagram. It is currently implemented for the three neutron reflectometry instruments at the NIST Center for Neutron Research (NCNR).

## 1. Motivation

Data reduction—the transformation of raw measurement output into interpretable data with attached uncertainties—is a ubiquitous task. For scientific user facilities with many visiting researchers, a web-based application is preferable to installable software because:
* **Accessibility:** Universal access via browser.
* **Maintainability:** Centralized updates to calculation code without requiring user-side installations.
* **Platform Independence:** Eliminates the need to maintain multiple target platform executables.

While developed for reflectometry, the system is designed to be extensible for off-specular reflectometry, small-angle neutron scattering (SANS), and triple axis spectrometry (TAS).

### 1.1. Data Reduction for Reflectometry
Reflectometry measurements are recorded in laboratory coordinates (incident and detector angles). The reduction process typically involves:
1. **Normalization:** Dividing the scattered counts by the independently measured total incident beam rate.
2. **Background Subtraction:** Removing count rates from alternative paths (e.g., air scattering) or electronic noise.
3. **Coordinate Transformation:** Converting incident angles and wavelengths into reciprocal space $q$ (inverse distance) coordinates.

## 2. Dataflow Diagram as a Template for Computation

The reduction process is modeled as a series of data transformations where data flows from one module to the next.

### 2.1. Data Types
Each data flow has an associated type. For a connection to be valid, the output type of one module must match the input type of the subsequent module. Each type includes methods for:
* Storage and loading.
* Conversion to display form.
* Export.

### 2.2. Operations
Implemented in Python, the system leverages:
* **NumPy and SciPy:** For numerical processing.
* **Uncertainties package:** For the propagation of uncertainties.
* **Custom facilities:** Unit conversion, data rebinning, interpolation, and weighted least squares solving.

### 2.3. Bundles of Inputs
To process multiple measurements with the same steps, `reductus` sends bundles of files between nodes:
* **Single parameters:** The module action operates on each input separately.
* **Multiple parameters:** All inputs are passed as a single list (e.g., for a "join" module).

### 2.4. Instrument and Module Definition
An instrument consists of a set of data types and computation modules. A module includes:
* Name, description, and version.
* Module action (the core function).
* Parameters (ID, label, type, description, and flags for optional/required or single/multiple).

### 2.5. Module Interface Language
Module interfaces are extracted from stylized documentation using ReStructured Text (RST). This allows:
* Automatic generation of tool tips in the UI.
* Creation of independent user manuals via Sphinx.
* Rendering of embedded equations using MathJax.

### 2.6. Serialization of the Diagram
A diagram is represented as a list of numbered nodes (containing the module, label, position, and control parameters) and a list of links (source node/parameter to target node/parameter).

## 3. Backend

The backend consists of a web server (HTTP) for static resources and a computation engine for remote procedure calls (RPC).

### 3.1. Computation Server
The server treats the dataflow diagram as a Directed Acyclic Graph (DAG). 

#### 3.1.1. Converting the Diagram to Computations
Nodes are arranged in topological order to ensure all input nodes are computed before their dependent nodes.

#### 3.1.2. Results and Source Caching
To ensure responsiveness, the server uses a Redis key-value store with a Least-Recently-Used (LRU) expiry algorithm.
* **Source Caching:** Raw data files are identified by URL and last-modified timestamp.
* **Step Caching:** Each calculation step is identified by a unique hash of its input values and the version number of the code. If a parameter or source file changes, the hash changes, triggering a recalculation of that step and all subsequent dependent steps.

#### 3.1.3. Data Provenance and Reproducibility
* **Templates:** The reduction template and parameters are stored within each exported file.
* **Stability:** NCNR data sources are referenced via Digital Object Identifiers (DOI).
* **Version Control:** The server source is managed via git. The specific git commit hash is stored with the template to allow exact reproduction of results.

#### 3.1.4. Statelessness
The computation engine maintains no state; the browser session holds the active template. This allows the engine to be restarted with zero impact on service continuity.

### 3.2. Server Configurations
1. **Simple Single-Computer:** Uses Python Flask to serve both static resources and RPC requests. Required for local file access or custom Python modules.
2. **Container-based:** Deployed via Docker and Docker-Compose (Web server, Python engine, and Redis cache containers).
3. **Scalable Production:** Static files served by Apache/nginx, forwarding RPC requests to a pool of Python engines (e.g., via uWSGI) sharing a Redis instance.

## 4. Web Interface

The interface is a JavaScript application (ECMAScript $\ge$ 5) utilizing the D3.js visualization library.

### 4.1. Dataflow Diagram
Users interact with the diagram to:
* Select modules to edit parameters.
* Click terminals to trigger and display calculation results.
* Export final reduced data.

### 4.2. Parameters Panel
Renders input fields based on the module definition. Enhanced interactions include:
* **Index type:** Clicking plot points to add them to a list.
* **Scale type:** Dragging a dataset on the plot to set a scaling factor.

### 4.3. Browser Caching
A local browser cache stores calculation results and file metadata to reduce the number of requests to the server during interactive adjustments.

### 4.4. Sessions and Persistence
As the server is stateless, persistence is handled locally:
* **Stashing:** Results can be saved in the browser's local persistent memory.
* **Filesystem:** Templates can be downloaded/uploaded as JSON. Exported data is saved as tab-delimited text files with the dataflow diagram in the header.
* **Sharing:** Because the reduced-data files contain the "recipe" (diagram) in the header, they can be shared via email for verification and reproduction.

## 5. Conclusions

The `reductus` system provides a flexible, scalable, and maintainable way to perform data reduction. By making the dataflow graph visible, it supports both novice users (who can treat it as a black box) and expert users (who can inspect and modify every step). It has successfully replaced legacy software for the three neutron reflectometry instruments at the NCNR.

<!-- Source: reductus: a stateless Python data-reduction service with a browser frontend. Removed journal headers, footers, page numbers, and personal email addresses. -->
