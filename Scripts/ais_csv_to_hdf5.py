""" This script converts AIS information in CSV format into HDF5 files,
for faster lookup and intersection by the satellite intersection logic.
"""

import os
import numpy as np
import pandas as pd
import time

# This is the root directory that contains subdirectories named
# after the pattern:
#
#   Zone[01..03]_[2015, 2016, 2017]_01/
#   Zone10_[2009..2014]/
# 
# In each directory there should be a Broadcast.csv file.
datadir = "/data/Cleaned_AIS"

def my_read_csv(filename):
    """ Read a dataframe with the appropriate default options """
    return pd.read_csv(filename, usecols=["mmsi_id", "date_time", "lat", "lon"],
                  parse_dates=[1], dtype={"lat": np.float32, "lon": np.float32})

for year in (2015, 2016, 2017):
    start = time.time()
    files = [os.path.join(datadir, f"Zone0{zone}_{year}_01/Broadcast.csv") for zone in (1,2,3)]
    df = pd.concat(map(my_read_csv, files), ignore_index=True)
    loadtime = time.time() - start
    start = time.time()

    df.sort_values(["mmsi_id", "date_time"], inplace=True)
    sorttime = time.time() - start
    start = time.time()
    df.to_hdf("ais_%d.h5"%year, "ais", complevel=3)
    print("[%d] Load: %d s, Sort: %ds, Write: %ds" % (year, loadtime, sorttime, time.time()-start))

for year in range(2009, 2015):
    start = time.time()
    df = my_read_csv(os.path.join(datadir, f"Zone10_{year}_01/Broadcast.csv"))
    loadtime = time.time() - start
    start = time.time()

    df.sort_values(["mmsi_id", "date_time"], inplace=True)
    sorttime = time.time() - start
    start = time.time()
    df.to_hdf("ais_%d.h5"%year, "ais", complevel=3)
    print("[%d] Load: %ds, Sort: %ds, Write: %ds" % (year, loadtime, sorttime, time.time()-start))

