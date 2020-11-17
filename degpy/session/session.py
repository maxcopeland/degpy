import os
import numpy as np

from degpy.neuralynx_io import load_ncs, load_nev
from degpy.terminal import Terminal


class Session:


    def __init__(self, session_path):
        self.session_path = os.path.abspath(session_path)
        self.events_file = self._get_eventsfile()
        self.data_files = self._get_datafiles()
        self.header = None
        self.records = None
        self.timestamps = None
        self.events = None

        # Read in events data to null attributes
        self._get_events_data()


    def __repr__(self):
        #TODO: Return header from events and list of data files?
        lst = ["{}: {}".format(key, val) for key, val in self.header.items()]
        return "\n".join(lst)


    def _get_eventsfile(self):
        """
        Returns events file from given session_path

        #TODO: Raise error if multiple events files?
        """
        for file in os.listdir(self.session_path):
            if file.split(".")[1] == "nev":
                return file
        raise FileNotFoundError("No events file found with extension .nev")


    def _get_datafiles(self):
        """

        """
        files = []
        for file in os.listdir(self.session_path):
            # if (file.split(".")[1] == "ncs" or
            #     file.split(".")[1] == "nse" or
            #     file.split(".")[1] == "ntt"):
            files.append(file)
        if len(files) == 0:
            raise FileNotFoundError("No data files found with extensions .ncs, .ntt, or .nse")
        else:
            return files


    def _get_events_data(self):
        events_file = self._get_eventsfile()
        events_data = load_nev(os.path.join(self.session_path, events_file))
        self.header = events_data['header']
        self.records = events_data['records']
        self.timestamps = events_data['events']['TimeStamp']
        self.events = [x.decode('utf8') for x in events_data['events']['EventString']]
        self.events = np.array(self.events)

    
    def get_terminal(self, file):
        if file not in self.data_files:
            raise FileNotFoundError("'{}' does not exist in directory '{}'".format(file, self.session_path))
        
        return Terminal(os.path.join(self.session_path, file), self.events, self.timestamps)


