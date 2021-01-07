""" Command-line script to compute visibility of vessels for a satellite.

For a notebook version, see Hit_Finder.ipynb

This notebook can also run in a "validation" mode, where it uses an
alternative (slower) algorithm to verify each "hit" it found.
"""

import os
import pandas as pd
import time

import intersect
from sathelpers import SatelliteDataStore

# Set some configuration variables
# In general, these should be explicit paths with no variables or homedir (~)
AIS_DIR = "./data/ais"  # TODO
SAT_DIR = "./data/satellites"  # TODO

# The years for which we have data
VALID_YEARS = list(range(2009,2018))

def load_ais_for_times(start_time, end_time, use_interpolation=True):
    years = list(pd.date_range(start_time, end_time, freq="AS").year)
    if start_time.year not in years:
        years.insert(0, start_time.year)
    years = sorted(set(years) & set(VALID_YEARS))  # filter out years for which we don't have data

    all_ais = []
    for year in years:
        if use_interpolation:
            suffix = "h5"
        else:
            suffix = "interp.h5"
        ais = pd.read_hdf(os.path.join(AIS_DIR, f"ais_{year}.{suffix}"))
        ais.sort_values(by="date_time", inplace=True)
        all_ais.append(ais)
    
    return pd.concat(all_ais)

def compute_visibility(norad_id, start_time, end_time, 
        use_interpolation = True, use_half_earth_FOV = False, workers=None,
        print_info = True):
    """
    start_time, end_time:  Anything that can be cast into a SpatialPandas
    """

    satdata = SatelliteDataStore(SAT_DIR)
    sat = satdata.get_precomputed_df(norad_id, start=start_time, end=end_time)

    s = time.time()
    ais = load_ais_for_times(start_time, end_time, use_interpolation)
    if print_info:
        print(f"Loaded {len(ais):,} points in", time.time()-s, "seconds")
        print(ais.info())
    
    s = time.time()
    hits = intersect.compute_hits(sat, ais, start_time, end_time, 
                assume_half_earth = use_half_earth_FOV,
                workers = workers)  # Use as many cores as possible, up to 32
    if print_info:
        print(f"Found {len(hits):,} hits in ", time.time()-s, "seconds")
    return hits

def find_sats(mmsi, start_time, end_time):
    """ Find all satellites that could have seen the given vessel between start_time and end_time
    """
    sds = SatelliteDataStore(SAT_DIR)
    ids = sds.get_norad_ids()
    print("Found", len(ids), "satellites")

    s = time.time()
    ais = load_ais_for_times(start_time, end_time, use_interpolation=True)
    if len(ais) > 0:
        ais = ais[ais["mmsi_id"] == mmsi]
    print(f"Loaded {len(ais):,} points in", time.time()-s, "seconds")
    print(ais.info())

    import tqdm
    vis_sat = []
    for s_id in tqdm.tqdm(ids):
        sat = sds.get_precomputed_df(s_id, start=start_time, end=end_time)
        if len(sat) == 0:
            continue
        hits = intersect.compute_hits(sat, ais, start_time, end_time, 
                assume_half_earth = False,
                workers = None)
        if len(hits) > 0:
            vis_sat.append(s_id)
    print("Found", len(vis_sat), "satellites")

def main():
    import argparse
    import os, sys, time

    parser = argparse.ArgumentParser()
    parser.add_argument("norad_id", help="the satellite's NORAD ID", type=int)
    parser.add_argument("-s", "--satdata", help="the directory containing precomputed satellite data")
    parser.add_argument("-a", "--aisdata", help="the directory containing AIS HDF5 files, both *.h5 and *.interp.h5")

    parser.add_argument("--half-earth", help="use the half-earth FOV assumption", default=False, type=bool)
    parser.add_argument("--start", help="Starting datetime, as a string that can be converted into a "
                        "pandas.Timestamp; e.g '2008-12-31T09:32:12'. If none is provided, then start "
                        "at the beginning of available AIS data.", default=None)
    parser.add_argument("--end", help="Ending datetime, as a string that can be converted into a "
                        "pandas.Timestamp; e.g '2008-12-31T09:32:12'. If none is provided, then end "
                        "at the end of available AIS data.", default=None)
    parser.add_argument("-o", "--output", help="Write output to CSV", default=None)

#    parser.add_argument("--validate", help="Run validation on each computed visible datapoint. (Warning: takes a long time; "
#                        "provide narrower time windows to accelerate the process.")

    parser.add_argument("-w", "--workers", help="Number of workers to use. By default, uses all available on machine",
                        default=None)

    args = vars(parser.parse_args())
    norad_id = args["norad_id"]

    global SAT_DIR, AIS_DIR
    SAT_DIR = args.get("satdata", "./data/sat")
    AIS_DIR = args.get("aisdata", "./data/ais")

    if not os.path.isdir(AIS_DIR) or not os.path.isdir(SAT_DIR):
        raise IOError("Invalid source data directory")

    start_time = pd.Timestamp(args.get("start", "2008-12-31T00:00:01"))
    end_time = pd.Timestamp(args.get("end", "2009-02-01T00:00:00"))

    intersect.PRINT_INFO = True

    hits = compute_visibility(norad_id, start_time, end_time,
            use_half_earth_FOV=args.get("half-earth", False), workers=args["workers"])
    
    if args["output"]:
        hits.to_csv(args["output"])
    return hits

if __name__ == "__main__":
    hits = main()
