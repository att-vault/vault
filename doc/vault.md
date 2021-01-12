<!-- pandoc --template=GitHub.html5 --self-contained vault.md -o  /tmp/deployments.html -->
<!-- GitHub.html5 template from git@github.com:tajmone/pandoc-goodies.git -->

## AT&T Vault Deployment Index

### EDA

* Viewing AIS: Basic rendering of location data from sets of AIS pings.  ([PDF](https://github.com/att-vault/vault/blob/main/doc/Viewing_AIS.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Viewing_AIS.ipynb),
[Runnable NB](https://viewing-ais.anaconda.hitsandholes.com/),
[Live app](https://dashboards.anaconda.hitsandholes.com/Viewing_AIS))

<center><img width=600 src="https://vault-data-minimal.s3.us-east-2.amazonaws.com/screenshots/Viewing_AIS.png">
</img></center>


* Viewing AIS Categorical: Breakdown of AIS location data by vessel type. ([PDF](https://github.com/att-vault/vault/blob/main/doc/Viewing_AIS_Categorical.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Viewing_AIS_Categorical.ipynb),
[Runnable NB](https://viewing-ais-categorical.anaconda.hitsandholes.com),
[Live app](https://dashboards.anaconda.hitsandholes.com/Viewing_AIS_Categorical))

<center><img width=600 src="https://vault-data-minimal.s3.us-east-2.amazonaws.com/screenshots/Viewing_AIS_Categorical.png">
</img></center>


* Viewing TLEs: Basic rendering of earth-centered satellite location at epoch time from sets of TLEs. ([PDF](https://github.com/att-vault/vault/blob/main/doc/Viewing_TLEs.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Viewing_TLEs.ipynb),
[Runnable NB](https://viewing-tles.anaconda.hitsandholes.com/),
[Live app](https://dashboards.anaconda.hitsandholes.com/Viewing_TLEs))

<center><img width=600 src="https://vault-data-minimal.s3.us-east-2.amazonaws.com/screenshots/Viewing_TLEs.png">
</img></center>


### Data Exploration

* Viewing AIS Gaps: Visualizing unusually large gaps between AIS pings. ([PDF](https://github.com/att-vault/vault/blob/main/doc/Viewing_AIS_Gaps.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Viewing_AIS_Gaps.ipynb),
[Runnable NB](https://viewing-ais-gaps.anaconda.hitsandholes.com))

<center><img width=600 src="https://vault-data-minimal.s3.us-east-2.amazonaws.com/screenshots/Viewing_AIS_Gaps.png">
</img></center>


* Viewing Tracks: Visualizing computed satellite tracks (derived from TLE records).  ([PDF](https://github.com/att-vault/vault/blob/main/doc/Viewing_Tracks.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Viewing_Tracks.ipynb),
[Runnable NB](https://viewing-tracks.anaconda.hitsandholes.com),
[Live app](https://viewing-tracks-dashboard.anaconda.hitsandholes.com/Viewing_Tracks))

<center><img width=600 src="https://vault-data-minimal.s3.us-east-2.amazonaws.com/screenshots/Viewing_Tracks.png">
</img></center>


### Solution to Satellite Visibility Challenge Problem

* Hit Dashboard: End-user app for showing tracks and vessels viewable by a satellite over a date/time range. ([PDF](https://github.com/att-vault/vault/blob/main/doc/Hit_Dashboard.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Hit_Dashboard.ipynb),
[Runnable NB](https://hit-dashboard.anaconda.hitsandholes.com),
[Live app](https://dashboards.anaconda.hitsandholes.com/Hit_Dashboard))

<center><img width=600 src="https://vault-data-minimal.s3.us-east-2.amazonaws.com/screenshots/Hit_Dashboard.png">
</img></center>

* Hit_Finder: Notebook for calculating vessels viewable by a satellite over a date/time range. ([PDF](https://github.com/att-vault/vault/blob/main/doc/Hit_Finder.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/Hit_Finder.ipynb))

### Machine learning / Analysis use cases

* DOD_anomaly: Case study provided by H2O for Pinnacle Use Case: Classify Suspicious Activity from AIS Data. ([PDF](https://github.com/att-vault/vault/blob/main/doc/DOD_anomaly.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/DOD_anomaly.ipynb))

* PrepareDataForMachineLearning: Curate and Prepare Data for various Pinnacle Use cases. ([PDF](https://github.com/att-vault/vault/blob/main/doc/PrepareDataForMachineLearning.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/PrepareDataForMachineLearning.ipynb))

* AIS_Analyze_Vessel_Cluster: EDA, Stats, K-Means clustering, Plots for a given vessel. ([PDF](https://github.com/att-vault/vault/blob/main/doc/AIS_Analyze_Vessel_Cluster.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/AIS_Analyze_Vessel_Cluster.ipynb))

* AIS_Anomaly_Detection: Collect stats and flag anomalous vessel coordinates. ([PDF](https://github.com/att-vault/vault/blob/main/doc/AIS_Anomaly_Detection.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/AIS_Anomaly_Detection.ipynb))


### Data preparation

These files start with raw data and create cleaned/consolidated/computed data for use in the other categories. Many of these rely on scripts in `scripts/`, where you can see the detailed computations involved.

- AIS_Parser: Parse the 2015-2017 flat csv files and transform data into Vessel, Broadcast, and Voyage files to be uniform with the GDB Exported Data. ([IPYNB](https://github.com/att-vault/vault/blob/main/AIS_Parser.ipynb))
- AIS_Validation: Combine all vessels' data and generate clean consolidated files. ([PDF](https://github.com/att-vault/vault/blob/main/doc/AIS_Validation.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/AIS_Validation.ipynb))
- TLE_Parser: Validate or correct the TLE data, producing gridded data for ingestion into the compute engine. ([PDF](https://github.com/att-vault/vault/blob/main/doc/TLE_Parser.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/TLE_Parser.ipynb))
- TLE_precompute_checks: Various sanity checks on the TLE data. ([PDF](https://github.com/att-vault/vault/blob/main/doc/TLE_precompute_checks.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/TLE_precompute_checks.ipynb))
- TLE_to_pytables: Converting TLE data into h5 format. ([PDF](https://github.com/att-vault/vault/blob/main/doc/TLE_to_pytables.pdf),
[IPYNB](https://github.com/att-vault/vault/blob/main/TLE_to_pytables.ipynb))

