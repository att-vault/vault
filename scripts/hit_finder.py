""" CLI script version of Jupyter Notebook

hit_finder.py

"""

import os
import pandas as pd
import time

import intersect
from sathelpers import SatelliteDataStore

# Set some configuration variables
# In general, these should be explicit paths with no variables or homedir (~)
AIS_DIR = "/Users/pwang/data/vault"  # TODO
SAT_DIR = "/Users/pwang/data/vault/satellites_active"  # TODO

# The years for which we have data
VALID_YEARS = list(range(2009,2018))

if not os.path.isdir(AIS_DIR) or not os.path.isdir(SAT_DIR):
    raise IOError("Invalid source data directory")

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
        use_interpolation = True,
        use_half_earth_FOV = False,
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
                workers = None)  # Use as many cores as possible, up to 32
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
    # The NORAD ID of the satellite we're interested in.
    norad_id = 25544  # the ISS
    start_time = pd.Timestamp("2008-12-31T00:00:01")
    end_time = pd.Timestamp("2009-02-01T00:00:00")
    return compute_visibility(norad_id, start_time, end_time)

if __name__ == "__main__":
    hits = main()
    #start_time = pd.Timestamp("2015-01-01T00:00:01")
    #end_time = pd.Timestamp("2015-01-05T00:00:00")
    #find_sats(43676060, start_time, end_time)
