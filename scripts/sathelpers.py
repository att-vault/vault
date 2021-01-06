#!/usr/bin/env python 

from datetime import datetime, timedelta
import hashlib
import itertools
import os
import sys

# Force this to single thread
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import numpy as np
import pandas as pd
import pytz
from tables import Atom, CArray, Filters, open_file

from skyfield import api
from skyfield.sgp4lib import EarthSatellite
from skyfield.framelib import itrs

def get_el_number(tle1, tle2):
    return EarthSatellite(tle1.decode(), tle2.decode()).model.elnum

def tle_dataframe(records):
    """
    Return a pandas dataframe containing TLE records which are ordered by epoch and secondly
    element number
    """
    frame = pd.DataFrame.from_records(records, columns=["epoch", "norad_id", "tle1", "tle2"])

    elnum = np.array((get_el_number(tle1, tle2) for tle1, tle2 in zip(frame["tle1"], frame["tle2"])))

    frame["elnum"] = elnum
    frame.sort_values(["epoch", "elnum"])
    return frame


def get_all_tles(h5path: str, norad_id: int):
    """
    Return a pandas DataFrame, where rows correspond to a TLE

    (
        epoch_time: float,
        norad_id: int,
        tle_line_1: bytes,
        tle_line_2: bytes
    )
    """
    h5ro = open_file(h5path, mode="r")
    records = h5ro.root.tle_sorted.read_where("norad_id=={}".format(norad_id))
    h5ro.close()
    # Sort records based on time (should alredy be sorted, but hey)
    return tle_dataframe(sorted(records, key=lambda row: row[0]))

def get_all_ids(h5path: str) -> list:
    """
    Get all Norad ID that are present in this dataset in ascending order.
    """
    h5ro = open_file(h5path, mode="r")
    results = set(h5ro.root.tle_sorted.cols.norad_id)
    h5ro.close()
    return list(sorted(results))

# Presently we will only extrapolate +- one week from a given TLE's epoch
# This was chosen because we can't determine events such as launches/deorbits
# on the dataset that has been reduced to match the AIS data windows.
max_extrap = timedelta(days=7).total_seconds()

def floor_to_nearest_min(epoch_s: float):
    return int(60.0 * np.floor(epoch_s / 60.0))



class TLEManager:
    """
    This class is responsible for determining when and which TLE's are
    valid/useful for a particular period in time. It additionally has
    methods for computing Lat/Long/Dist data based on the windows it
    computes
    """
    def __init__(self, h5path: str, norad_id: int):
        self.records = get_all_tles(h5path, norad_id)
        self._ts = api.load.timescale()

    def get_known_timespan(self):
        """
        Return datetimes corresponding to the first and last TLE epoch values
        in our record set
        """
        times = self.get_tle_times()
        return times[0], times[-1]

    def get_tle_times(self):
        return self.records.epoch.to_numpy()

    def get_compute_windows(self):
        """
        Calculate the windows over which all of the TLE's for this identifier are
        valid. When used on a dataset pruned down for the AIS valid time periods,
        this will automatically

        [
          (start_epoch, end_epoch, tle1, tle2)
            ...
          (start_epoch, end_epoch, tle1, tle2)
        ]
        """
        times = self.get_tle_times()
        ntle = times.shape[0]

        windows = []
        for i in range(ntle):
            # For each TLE there is a window of time around that we will use to
            # pre-compute the position of the satellite.

            # Logic for window starting
            if i == 0:
                # Handle the first record, no TLE before, so start centered on it
                start = times[0]
            else:
                # If the time since the last TLE has been more than `max_extrap`
                # then start this window that far back
                # Otherwise this window starts halfway between this and the last
                # TLE to minimize the projection error
                halfway_to_last = (times[i-1] + times[i]) /2
                two_weeks_back = times[i] - max_extrap
                start = max(halfway_to_last, two_weeks_back)

            # Logic for window ending
            if i == ntle-1:
                # Handle the last record. Do not project past it
                end = times[-1]
            else:
                # If the time between this TLE and the next is more than two weeks
                # project forward at most two weeks time, then close the window
                halfway_to_next = (times[i] + times[i+1]) / 2
                two_weeks_forward = times[i] + max_extrap

                end = min(halfway_to_next, two_weeks_forward)

            start = floor_to_nearest_min(start)
            end = floor_to_nearest_min(end)

            window_length = end - start
            if window_length <= 60:
                print("Warning: Very short window being ignored: %f seconds" % window_length)
                continue

            windows.append((start, end, self.records.tle1[i], self.records.tle2[i]))

        return windows

    def _epoch_to_julian(self, time: float) -> float:
        """
        Convert an epoch float timestamp to a julian year float timestamp
        """
        return self._ts.from_datetime(datetime.utcfromtimestamp(time).replace(tzinfo=pytz.utc)).tt

    def compute_lat_long_dist(self, start_epoch: int, end_epoch: int, tle1, tle2):
        """
        Given the parameters of a TLE window.

        Compute four np.array instances:
         * times (n,)  - Epoch times (spaced by ~1 minute) that span the start to end specified
         * lats (n,)   - Latitude in degrees
         * longs (n,)  - Longitude in degrees
         * radius (n,) - The distance from the COM of Earth in kilometers
        """
        assert end_epoch - start_epoch > 60, "Start: %f End: %f" % (start_epoch, end_epoch)

        # Convert the start and end into julian
        start_time_j = self._epoch_to_julian(floor_to_nearest_min(start_epoch))
        end_time_j = self._epoch_to_julian(floor_to_nearest_min(end_epoch))

        # Compute the number of steps we will take between the start and stop
        n_time_steps = int( round((end_epoch - start_epoch) / 60) )

        # Create matching epoch/julian times spans
        julian_times = self._ts.tt_jd(np.linspace(start_time_j, end_time_j, n_time_steps))
        epoch_times = np.linspace(start_epoch, end_epoch, n_time_steps)

        # Do the actual satellite propagation math
        sat = EarthSatellite(tle1.decode(), tle2.decode())
        lats, longs, dists = sat.at(julian_times).frame_latlon(itrs)

        # return the times, lats, longs, and distances in the units specified
        return epoch_times, lats.degrees, (longs.degrees + 180) % 360 - 180, dists.km

    def compute_tlla_sequence(self):
        """
        For each of the TLE windows this instance represents generate and concatenate
        an array of the values returned by `compute_lat_long_dist`.

        The returned array will have shape (4,n) where n is the number of minutes
        covered by TLE's in this set.

        NB: the times spanned may have large gaps, but are guaranteed to be monotonically
        increasing

        Returns None if there are no datapoints for this object.
        """
        # Determine all the windows to do our TLE math over.
        windows = self.get_compute_windows()

        if not windows:
            return None

        # Perform the propagation math, and concatenate the arrays to return a block
        to_concat = []
        for start, end, tle1, tle2 in windows:
            tlla = self.compute_lat_long_dist(start, end, tle1, tle2)
            tlla = np.vstack(tlla)
            to_concat.append(tlla)

        return np.hstack(to_concat)


class SatelliteDataStore:
    def __init__(self, root_folder):
        assert os.path.exists(root_folder)
        self.root_folder = root_folder
        # Store a reference to file handles so we can close them, if requested.
        # key is (norad_id, file_mode) where file_mode is "r", "w", etc.
        self._handles = {}

    def _norad_id_to_path(self, norad_id: int) -> str:
        hsh = hashlib.md5(str(norad_id).encode("ascii")).hexdigest()
        return os.path.join(self.root_folder, hsh[0:2], hsh[2:4], str(norad_id) + ".h5")

    def get_norad_ids(self):
        """
        Get a set containing all the norad ids that are contained by this archive.
        """
        ids = []
        for root, dirs, files in os.walk(self.root_folder):
            ids += list(int(os.path.splitext(f)[0]) for f in files)
        return ids  

    def get_timespan(self, norad_id: int):
        """
        Get the minimum and maximum epoch timestamp for a given `norad_id`
        """
        times = self._get_array(norad_id)[0, :]
        first = datetime.utcfromtimestamp(float(times.min()))
        last = datetime.utcfromtimestamp(float(times.max()))
        return first, last

    def _open_file_for_id(self, norad_id: int, mode: str):
        path_to_file = self._norad_id_to_path(norad_id)
        try:
            os.makedirs(os.path.split(path_to_file)[0])
        except FileExistsError as e:
            pass
        
        return self._handles.setdefault((norad_id, mode), open_file(path_to_file, mode))

        return open_file(path_to_file, mode, filters=Filters(complevel=5, complib='blosc'))

    def _close(self, norad_id, mode: str):
        """ Closes any open file handles for the given norad_id. If no ID is
        given, then attempts to close all open file handles.
        """
        key = (norad_id, mode)
        if key in self._handles:
            self._handles[key].close()
            del self._handles[key]

    def _get_array(self, norad_id):
        return getattr(self._open_file_for_id(norad_id, "r").root, "s%d" % norad_id)    

    def put_precomputed_tracks(self, norad_id: int, data: np.array):
        """
        Add the track for `norad_id`
        """
        f = self._open_file_for_id(norad_id, "w")
        new_array = CArray(
            f.root,
            "s%d" % norad_id, 
            atom=Atom.from_dtype(data.dtype),
            shape=data.shape,
            title="Data for satellite with norad id: %s" % norad_id)
        new_array[:] = data
        return new_array

    def get_precomputed_tracks(self, norad_id: int, start: datetime, end: datetime):
        """
        Return telemetry for the satellite with a given `norad_id` from `start` to `end` datetimes.
        The array returned will have a size (4,n) where `n` corresponds to the
        number of integer minutes between the starting points of the two times.

        times, lats, longs, dist = get_precomputed_tracks( ... )

        **times** are in floating-point seconds since UNIX epoch
        **dist** is distance from Center of Earth, in meters
        **longs** is longitude, between 0 and 360

        This returns an array:
        @returns np.array (4, times)
        """
        
        array_node = self._get_array(norad_id)
        times = array_node[0, :]
        start_index = np.searchsorted(times, start.timestamp())
        end_index   = np.searchsorted(times, end.timestamp())
        
        dataz = array_node[:, start_index: end_index]

        # close the file
        self._close(norad_id, "r")

        # Pull out duplicate timestamps if any exist
        _, indices = np.unique(dataz[0, :], return_index=True)
        return dataz[:, indices]

    def get_precomputed_df(self, norad_id: int, start: datetime, end: datetime):
        """Returns a DataFrame version of get_precomputed_tracks"""
        times, lats, longs, dist = self.get_precomputed_tracks(norad_id, start, end)
        return pd.DataFrame({"date_time": times.astype("<M8[s]"),
            "lat": lats, "lon": longs, "alt": dist})


if __name__ == "__main__":
    import argparse

    usage = """
    A tool to run precomute the propagations of satellites from an index file.

    Usage:
       List the cached norad ID's:
         python sathelpers.py --inputH5 /data/Indexed_TLE/reduced.h5 --listIDs

       Compute the track for a satellite and store it in the index:
         python sathelpers.py --inputH5 /data/Indexed_TLE/reduced.h5 --noradID 5
    
    This is specifically desgigned to be invoked by gnu parallel ala the script
    `build_index_parallel.sh` found in this same directory.
    """
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inputH5", default="/data/Indexed_TLE/reduced.h5")
    parser.add_argument("--indexDirectory", default="/data/Indexed_TLE/index")
    parser.add_argument("--listIDs", default=False, action="store_true")
    parser.add_argument("--noradID", type=int)
    
    args = parser.parse_args()
    data_store = SatelliteDataStore(args.indexDirectory)

    if (args.listIDs):
        for i in data_store.get_norad_ids():
            print(i)
        sys.exit(0)

    if int(args.noradID) in data_store.get_norad_ids():
        print("%s is already in the index. Skipping" % args.noradID)
        sys.exit(0)
    
    track_data = TLEManager(args.inputH5, args.noradID).compute_tlla_sequence()
    if track_data is None:
        print("No data for noradID: %i" % args.noradID)
    else:
        carray = data_store.put_precomputed_tracks(args.noradID, track_data)
        print("Completed compute for noradID: %i %s %s" % (args.noradID, carray.shape, carray.dtype))
