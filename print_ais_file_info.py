""" Dumps some quick stats on each of the AIS hdf5 files. 

Usage:

    print_ais_file_info.py [ais_file.h5,..]

If no arguments are given, then looks for all files named like "ais_*.h5" 
in the current directory, and prints their information.

"""

import pandas as pd
import sys

def print_stats(filename):
    df = pd.read_hdf(filename)
    counts = df.shape[0]
    latmin = df["lat"].min()
    latmax = df["lat"].max()
    longmin = df["lon"].min()
    longmax = df["lon"].max()
    time_start = df["date_time"].min()
    time_end = df["date_time"].max()
    uniqmmsi = df["mmsi_id"].unique()
    print(f"[{filename}]  {counts:,} data points, {len(uniqmmsi)} uniq MMSI IDs")
    print(f"       Latitudes: {latmin} to {latmax}")
    print(f"     Longitutdes: {longmin} to {longmax}")
    print(f"      Timestamps: {time_start} to {time_end}")


if __name__ == "__main__":
    import glob
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = glob.glob("ais_*.h5")
    [print_stats(f) for f in files]

