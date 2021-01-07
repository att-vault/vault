# Metadata

- *AIS_categories.csv*: This file defines the [AIS vessel type
fields](https://api.vtexplorer.com/docs/ref-aistypes.html) using
information from
[fisheries.noaa.gov](https://www.fisheries.noaa.gov/inport/item/54208). In
addition to the official types, 21 condensed categories are defined in
order to generate meaningful categorical plots.
- *UCS-Satellite-Database-8-1-2020.txt*: The is a snapshot of [this
  CSV](https://www.ucsusa.org/sites/default/files/2020-10/UCS-Satellite-Database-8-1-2020.txt)
  file from [ucsusa.org](https://www.ucsusa.org/) which provides
  metadata for a large number of satellites, including their NORAD ids.
- *Vessel.csv*:  This file contains AIS metadata of sea vessels by their AIS `mmsi_id`.
- norad_id_active.txt: Used to determine precomputation in `scripts/build_index_parallel.sh`
- norad_id_all.txt:   Used to determine precomputation in `scripts/build_index_parallel.sh`