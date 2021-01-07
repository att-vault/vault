# AT&T Vault Tech Scenario

This repository contains the draft code used to explore and analyze the data in the 12/2020 "Technical Scenario" document for VAULT. It is organized into a set of [Jupyter notebooks](https://jupyter.org) runnable on any Linux or Mac system. For notebooks without interactive plots, the notebook is provided with output embedded directly into it, so that the results can be seen without having to set up and execute the code. Notebooks without output included are meant to be viewed "live", with a running Python server, so that the data can be fully explored interactively. PDF copies of all notebooks are provided for quick skimming or in case the notebook code or data is not available for running. Where appropriate, you can also visit a [deployed version](http://bit.ly/attvault) of the code.

## Notebooks

The notebooks fall into the following categories:

### EDA

These notebooks start with raw data where possible, with a goal of revealing it as it is, with as little cleanup as possible, so that same process can be applied to new data. These are primarily self contained, not relying on external scripts or modules in this repository (just packages in the Python environment installed).

- [Viewing_AIS](Viewing_AIS.ipynb): Basic rendering of location data from sets of AIS pings. [(PDF)](doc/Viewing_AIS.pdf)
- [Viewing_AIS_Categorical](Viewing_AIS_Categorical.ipynb): Breakdown of AIS location data by vessel type. [(PDF)](doc/Viewing_AIS_Categorical.pdf)
- [Viewing_TLEs](Viewing_TLEs.ipynb): Basic rendering of earth-centered satellite location at epoch time from sets of TLEs. [(PDF)](doc/Viewing_TLEs.pdf)

### Data exploration

These notebooks also focus on data, but on derived or computed values.

- [Viewing_AIS_Gaps](Viewing_AIS_Gaps.ipynb): Visualizing unusually large gaps between AIS pings. [(PDF)](doc/Viewing_AIS_Gaps.pdf)
- [Viewing_Tracks](Viewing_Tracks.ipynb): Visualizing computed satellite tracks (derived from TLE records). [(PDF)](doc/Viewing_Tracks.pdf)

### Prototypes

These files start with processed/prepared data, and approximate an end-user task (e.g. hit detection).

- [Hit_Finder](Hit_Finder.ipynb): Notebook for calculating vessels viewable by a satellite over a date/time range. [(PDF)](doc/Hit_Finder.pdf)
- [Hit_Dashboard](Hit_Dashboard.ipynb): End-user app for showing tracks and vessels viewable by a satellite over a date/time range. [(PDF)](doc/Hit_Dashboard.pdf)

### Machine learning / Analysis use cases

- [DOD_anomaly](DOD_anomaly.ipynb): Case study provided by H2O for Pinnacle Use Case: Classify Suspicious Activity from AIS Data. [(PDF)](doc/DOD_anomaly.pdf)
- [PrepareDataForMachineLearning](PrepareDataForMachineLearning.ipynb): Curate and Prepare Data for various Pinnacle Use cases. [(PDF)](doc/PrepareDataForMachineLearning.pdf)
- [AIS_Analyze_Vessel_Cluster](AIS_Analyze_Vessel_Cluster.ipynb): EDA, Stats, K-Means clustering, Plots for a given vessel. [(PDF)](doc/AIS_Analyze_Vessel_Cluster.pdf)
- [AIS_Anomaly_Detection](AIS_Anomaly_Detection.ipynb): Collect stats and flag anomalous vessel coordinates. [(PDF)](doc/AIS_Anomaly_Detection.pdf)


### Data preparation

These files start with raw data and create cleaned/consolidated/computed data for use in the other categories. Many of these rely on scripts in `scripts/`, where you can see the detailed computations involved.

- [AIS_Parser](AIS_Parser.ipynb): Parse the 2015-2017 flat csv files and transform data into Vessel, Broadcast, and Voyage files to be uniform with the GDB Exported Data. [(PDF)](AIS_Parser.ipynb)
- [AIS_Validation](AIS_Validation.ipynb): Combine all vessels' data and generate clean consolidated files. [(PDF)](AIS_Validation.ipynb)
- [TLE_Parser](TLE_Parser.ipynb):  Validate or correct the TLE data, producing gridded data for ingestion into the compute engine. [(PDF)](TLE_Parser.ipynb)
- [TLE_precompute_checks](TLE_precompute_checks.ipynb): Various sanity checks on the TLE data. [(PDF)](TLE_precompute_checks.ipynb)
- [TLE_to_pytables](TLE_to_pytables.ipynb): Converting TLE data into h5 format. [(PDF)](TLE_to_pytables.ipynb)

## Data

These notebooks and scripts expect the underlying data files to be in a `data/` subdirectory of this directory, which by default is a symbolic link to `/data`. You can copy the files from [vault-data-corpus on S3](http://vault-data-corpus.s3-website.us-east-2.amazonaws.com/), putting them in `/data` on your own system (local or cloud) if you have access to `/`, or else put the data somewhere in your writable directories and update the `./data` symlink to point to its location. E.g.:

```
> cd /data
> pip install awscli
> aws s3 sync s3://vault-data-minimal data --no-sign-request
```

Note that there are a lot of files involved and downloading is likely to take some time. Downloading to an EC2 instance is typically faster than to a home system.

## Running the code

Starting from a laptop or cloud instance:
1. install and activate [miniconda](https://conda.io/miniconda.html]
2. Unpack this .zip file or clone `git@github.com:att-vault/vault.git`
3. cd `vault`
4. `conda install anaconda-project`
5. `anaconda-project run` (to launch the apps) or `anaconda-project run Viewing_AIS` (or another notebook's name) to launch that notebook.

anaconda-project will download the OSS packages needed, activate an appropriate environment, and then launch the indicated command in that environment. On a local system, a tab will then normally open in your web browser for you to use; on a remote system you can use the URL that is printed as a starting point for setting up a tunnel to your local system.

## Deliverables Checklist:

This page serves as the main instruction index. From here, you can navigate to various resources, deliverables, and documention specific to that process.
1. Public GitHub – All code/doc/Instructions
  * Main Repos: https://github.com/att-vault/vault
  * API Repos: https://github.com/att-vault/vault-apis
2. Public vault-data-corpus on S3:  http://vault-data-corpus.s3-website.us-east-2.amazonaws.com/ (a subset of which is provided at vault-data-minimal, sufficient for running the code)
  * Satellite Data - Contains all TLE related data snapshots from various EDA/Curation processes
  * Vessel Data - Contains all AIS related data snapshots from various EDA/Curation processes
  * Docker Images - Contains latest Docker images for API and Interactive UI App; but you can also use our Jenkins pipeline to build and deploy new Docker images as well.
3. Deployed apps at http://bit.ly/attvault , though these will be taken down at some point after the demo presentation.


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
