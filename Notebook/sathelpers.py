from datetime import datetime
from tables import open_file, Array
import numpy as np


class SatelliteDataStore:
    def __init__(self, h5_node):
            self.node = h5_node

    def _norad_id_to_node(self, norad_id: int) -> str:
        return "s" + str(norad_id)

    def get_norad_ids(self):
        """
        Get a set containing all the norad ids that are contained by this archive.
        """
        return list(sorted(int(k.replace("s", "")) for k in dir(self.node) if not k.startswith("_")))

    def _get_norad_node(self, norad_id: int):
        name = self._norad_id_to_node(norad_id)
        assert hasattr(self.node, name), "No Data for satellite with norad ID: %i" % norad_id
        return getattr(self.node, name)

    def get_timespan(self, norad_id: int):
	"""
	Get the minimum and maximum epoch timestamp for a given `norad_id`
        """
        node = self._get_norad_node(norad_id)
        times = node[0, :]
        first = datetime.utcfromtimestamp(float(times.min()))
        last = datetime.utcfromtimestamp(float(times.max()))
        return first, last

    def put_precomputed_tracks(self, norad_id: int, data: np.array):
	"""
	Add the track for `norad_id`
	"""
        name = self._norad_id_to_node(norad_id)
        Array(self.node, name, data, title="Data for satellite with norad id: %s" % norad_id)

    def get_precomputed_tracks(self, norad_id: int, start: datetime, end: datetime):
        """
        Return telemetry for the satellite with a given `norad_id` from `start` to `end` datetimes.
        The array returned will have a size (4,n) where `n` corresponds to the
        number of integer minutes between the starting points of the two times.

        times, lats, longs, dist = get_precomputed_tracks(...)

        This returns an array:
        @returns np.array (4, times)
        """
        dataz = self._get_norad_node(norad_id)[:]

        start_index = np.searchsorted(dataz[0, :], start.timestamp())
        end_index   = np.searchsorted(dataz[0, :], end.timestamp())
        return dataz[:, start_index: end_index]
