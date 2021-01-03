""" CLI script version of Jupyter Notebook

hit_finder.py

"""

import os
import pandas as pd

# Set some configuration variables
# In general, these should be explicit paths with no variables or homedir (~)
AIS_DIR = "/Users/pwang/data/vault"  # TODO
SAT_DIR = "/Users/pwang/data/vault/satellites_active"  # TODO

if not os.path.isdir(AIS_DIR) or not os.path.isdir(SAT_DIR):
    raise IOError("Invalid source data directory")

# The NORAD ID of the satellite we're interested in.
norad_id = 25544  # the ISS
start_time = pd.Timestamp("2008-12-31T00:00:01")  # TODO
end_time = pd.Timestamp("2009-02-01T00:00:00")    # TODO

from sathelpers import SatelliteDataStore
satdata = SatelliteDataStore(SAT_DIR)


(times, lats, lons, alts) = satdata.get_precomputed_tracks(norad_id, start=start_time,
        end=end_time)
# The longitudes in the pre-computed satellite tracks range from 0-360,
# but we need them in (-180,180) format.
mask = lons > 180.0
lons[mask] -= 360

# Now convert to a dict that can by passed in to the intersection calculation
sat = pd.DataFrame({"date_time": times.astype("<M8[s]"),
       "lat": lats, "lon": lons, "alt": alts})


ais = pd.read_hdf(os.path.join(AIS_DIR, "ais_2009.h5"))
ais.sort_values(by="date_time", inplace=True)
ais.info()

import sys
import intersect
intersect.PRINT_INFO=True

hits = intersect.compute_hits(sat, ais, start_time="2009-01-15", end_time="2009-01-23", workers=4)

