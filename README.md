# AT&T Vault Tech Scenario

This repository contains the draft code used to explore and analyze the data in the 12/2020 "Technical Scenario" document for VAULT. It is organized into a set of [Jupyter notebooks](https://jupyter.org). Ideally, notebooks with interactive plots should be viewed "live", with a running Python server, so that the data can be fully explored interactively. PDF copies of most notebooks are provided for quick skimming or in case the notebook code or data is not available for running. 

## Notebooks

The notebooks fall into the following categories:

### EDA

These notebooks start with raw data where possible, with a goal of revealing it as it is, with as little cleanup as possible, so that same process can be applied to new data. These are primarily self contained, not relying on external scripts or modules in this repository (just packages in the Python environment installed).

- [Viewing_AIS](Viewing_AIS.ipynb): Basic rendering of location data from sets of AIS pings.
- [Viewing_AIS_Categorical](Viewing_AIS_Categorical.ipynb)): Breakdown of AIS location data by vessel type.
- [Viewing_TLEs](Viewing_TLEs.ipynb): Basic rendering of earth-centered satellite location at epoch time from sets of TLEs.

### Data exploration

These notebooks also focus on data, but on derived or computed values.

- [Viewing_AIS_Gaps](Viewing_AIS_Gaps.ipynb): Visualizing unusually large gaps between AIS pings.
- [Viewing_Tracks](Viewing_Tracks.ipynb): Visualizing conputed satellite tracks (derived from TLE records)

### Prototypes

These files start with processed/prepared data, and approximate an end-user task (e.g. hit detection).

- [Hit_Finder](Hit_Finder.ipynb): Notebook for calculating vessels viewable by a satellite over a date/time range
- [Hit_Dashboard](Hit_Dashboard.ipynb): End-user app for showing tracks and vessels viewable by a satellite over a date/time range

### Machine learning / Analysis use cases

- [DOD_anomaly](DOD_anomaly.ipynb): Case study provided by H2O for Pinnacle Use Case: Classify Suspicious Activity from AIS Data
- [PrepareDataForMachineLearning](PrepareDataForMachineLearning.ipynb): Curate and Prepare Data for various Pinnacle Use cases.
- [AIS_Analyze_Vessel_Cluster](AIS_Analyze_Vessel_Cluster.ipynb): EDA, Stats, K-Means clustering, Plots for a given vessel
- [AIS_Anomaly_Detection](AIS_Anomaly_Detection.ipynb): Collect stats and flag anomalous vessel coordinates


### Data preparation

These files start with raw data and create cleaned/consolidated/computed data for use in the other categories. Many of these use scripts in `scripts/`.

- [AIS_Parser](AIS_Parser.ipynb): Parse the 2015-2017 flat csv files and transform data into Vessel, Broadcast, and Voyage files to be uniform with the GDB Exported Data
- [AIS_Validation](AIS_Validation.ipynb): Combine all vessels' data and generate clean consolidated files
- [TLE_Parser](TLE_Parser.ipynb):  Validate or correct the TLE data, producing gridded data for ingestion into the compute engine
- [TLE_precompute_checks](TLE_precompute_checks.ipynb): Various sanity checks on the TLE data
- [TLE_to_pytables](TLE_to_pytables.ipynb): Converting TLE data into h5 format


## Data

These notebooks and scripts expect files to be in a `data/` subdirectory of this directory, which by default is a symbolic link to /data. You can obtain the files from [vault-data-corpus on S3](http://vault-data-corpus.s3-website.us-east-2.amazonaws.com/), and put them in /data on your own system (local or cloud) if you have access to /, or else put the data somewhere in your writable directories and update the ./data symlink to point to its location.

## Deliverables Checklist:
This page serves as the main instruction index. From here, you can navigate to various resources, deliverables, and documention specific to that process.
1. Public GitHub – All code/doc/Instructions
  * Main Repos: https://github.com/att-vault/vault
  * API Repos: https://github.com/att-vault/vault-apis
2. Public Vault-data-corpus on S3:  http://vault-data-corpus.s3-website.us-east-2.amazonaws.com/
  * Satellite Data - Contains all TLE related data snapshots from various EDA/Curation processes
  * Vessel Data - Contains all AIS related data snapshots from various EDA/Curation processes
  * Docker Images - Contains latest Docker images for API and Interactive UI App; but you can also use our Jenkins pipeline to build and deploy new Docker images as well.


## Background reading

DoD/government documents:
- [2020-09-30 Executive Summary: DoD Data](https://github.com/att-vault/vault/raw/jlstevens/hit_visualization/Doc/DOD-DATA-STRATEGY%20%26%20Executive%20Summary%2020201013.pdf)
- [2020-12-17 Technical Scenario](https://github.com/att-vault/vault/raw/jlstevens/hit_visualization/Doc/Technical%20Scenario.pdf)
- [2020-05-01 Space Force Data Management strategy](https://www.afcea.org/content/space-force-looks-next-generation-data-management)
- [2020-12-30 Example of an open data catalog](https://catalog.data.gov/dataset?organization=nasa-gov&q=space+force)
- [2020-12-30 Example of an open dataset](https://catalog.data.gov/dataset/near-earth-asteroid-tracking-v1-0)
- [2014-11-06 Open data standard 1.1](https://project-open-data.cio.gov/v1.1/schema)
- [2014-11-06 Open data standard 1.1 field Mappings](https://project-open-data.cio.gov/v1.1/metadata-resources/#field-mappings)

Data files:
- [Tech Scenario data files on S3](https://afdata.s3.us-gov-west-1.amazonaws.com/index.html)

General background:
- [Automatic Identification System (AIS)](https://en.wikipedia.org/wiki/Automatic_identification_system)
- [Maritime Mobile Service Identity (AIS vessel IDs)](https://en.wikipedia.org/wiki/Maritime_Mobile_Service_Identity)
- [Two-line Element Set (TLE)](https://en.wikipedia.org/wiki/Two-line_element_set)
- [Space Surveillance Network](https://en.wikipedia.org/wiki/United_States_Space_Surveillance_Network#Space_Surveillance_Network)
