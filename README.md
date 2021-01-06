# ATT Vault Tech Scenario

This repository contains the draft code used to explore and analyze the data in the 12/2020 "Technical Scenario" document for VAULT. It is organized into a set of [Jupyter notebooks](https://jupyter.org), falling into the following categories:

1. EDA/Data exploration (Viewing_*.ipynb)
  * These files start with raw data where possible, with a goal of revealing it as it is, with as little cleanup as possible, so that same process can be applied to new data. These are primarily self contained, not relying on external scripts or modules in this repository (just packages in the Python environment installed)
2. Machine Learning Use cases
  * DOD_anomaly.ipynb - Case study provided by H2O for Pinnacle Use Case: Classify Suspicious Activity from AIS Data
  * PrepareDataForMachineLearning.ipynb - Curate and Prepare Data for various Pinnacle Use cases.
3. Data preparation (AIS*, TLE*)
  * These files start with raw data and create cleaned/consolidated/computed data for use in the other categories. Many of these use scripts in `scripts/`.
4. Production (Hit_*; really prototypes of production)
  * These files start with processed/prepared data, and approximate an end-user task (e.g. hit detection).

## Data

These notebooks and scripts expect files to be in a `data/` subdirectory of this directory. The data can be obtained from att-vault-corpus on S3.

## Documentation

PDF versions of the main notebooks used are in the `doc/` subdirectory of this directory, along with other documentation.

## Deliverables Checklist:
1. Public GitHub – All code/doc/Instructions
  * Main Instruction Index Page: https://github.com/att-vault/vault/blob/main/README.md
  * Main Repos: https://github.com/att-vault/vault
  * API Repos: https://github.com/att-vault/vault-apis
2. Public Vault-data-corpus on S3: http://..........
  * Satellite Data - Contains all TLE related data snapshots from various EDA/Curation processes
  * Vessel Data - Contains all AIS related data snapshots from various EDA/Curation processes
  * Docker Images - Contains latest Docker images for API and Interactive UI App; but you can also use our Jenkins pipeline to build and deploy new Docker images as well.


## Further reading

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
