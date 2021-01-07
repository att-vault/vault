""" Given a vessel MMSI ID and date/time range, find all satellites that
could have seen it.
"""

import pandas as pd
import time
import sys
import intersect

from sathelpers import SatelliteDataStore
import hit_finder

# Set some configuration variables
# In general, these should be explicit paths with no variables or homedir (~)
AIS_DIR = "./data/vessel data/Cleaned AIS/"
SAT_DIR = "./data/satellite data/index/"


def find_sats(mmsi, start_time, end_time):
    """ Find all satellites that could have seen the given vessel between start_time and end_time
    """
    sds = SatelliteDataStore(SAT_DIR)
    ids = sds.get_norad_ids()
    print("Found", len(ids), "satellites")

    s = time.time()
    #import ipdb;ipdb.set_trace()
    ais = hit_finder.load_ais_for_times(start_time, end_time, use_interpolation=True)
    if len(ais) > 0:
        ais = ais[ais["mmsi_id"] == mmsi]
        print(f"Loaded {len(ais):,} points in", time.time()-s, "seconds")
        print(ais.info())
    else:
        print("Found no AIS points; exiting.")
        sys.exit()

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
    
    return vis_sat


def main():
    import argparse
    import os, sys, time

    parser = argparse.ArgumentParser()
    parser.add_argument("mmsi", help="the vessel MMSI ID", type=int)

    parser.add_argument("-s", "--satdata", help="the directory containing precomputed satellite data")
    parser.add_argument("-a", "--aisdata", help="the directory containing AIS HDF5 files, both *.h5 and *.interp.h5")

    parser.add_argument("--half-earth", help="use the half-earth FOV assumption", default=False, type=bool)
    parser.add_argument("--start", help="Starting datetime, as a string that can be converted into a "
                        "pandas.Timestamp; e.g '2008-12-31T09:32:12'. If none is provided, then start "
                        "at the beginning of available AIS data.", default=None)
    parser.add_argument("--end", help="Ending datetime, as a string that can be converted into a "
                        "pandas.Timestamp; e.g '2008-12-31T09:32:12'. If none is provided, then end "
                        "at the end of available AIS data.", default=None)

    args = vars(parser.parse_args())
    mmsi = args["mmsi"]

    global SAT_DIR, AIS_DIR
    SAT_DIR = args.get("satdata", "./data/sat")
    AIS_DIR = args.get("aisdata", "./data/ais")
    hit_finder.SAT_DIR = SAT_DIR
    hit_finder.AIS_DIR = AIS_DIR

    if not os.path.isdir(AIS_DIR) or not os.path.isdir(SAT_DIR):
        raise IOError("Invalid source data directory")

    start_time = pd.Timestamp(args.get("start", "2008-12-31T00:00:01"))
    end_time = pd.Timestamp(args.get("end", "2009-02-01T00:00:00"))

    intersect.PRINT_INFO = False
    results = find_sats(mmsi, start_time, end_time)
    print("Found", len(results), "satellites")
    from pprint import pprint
    pprint(results)


if __name__ == "__main__":
    main()
