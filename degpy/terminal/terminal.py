from __future__ import division

import os
import warnings

import numpy as np
import pandas as pd

from scipy.signal import welch
from scipy.integrate import simps

from degpy.neuralynx_io import read_records, parse_header, check_ncs_records, read_header


class Terminal:
    """
    Instantiate the Channel object
    Then run .load_ncs_data()
    """

    # Standard variables per Neuralynx file formatting
    _header_length=16*1024
    _ncs_samples_per_record=512
    _volt_scaling= (1, u'V')
    _millivolt_scaling = (10000, u'mV')
    _microvolt_scaling=(1000000, u'µV')

    def __init__(self, file_path, events, event_timestamps):
        """
        TODO: Add _load_ncs() arguments to instance attributes?
        """
        self.file_path = file_path
        self.events = events
        self.event_timestamps = event_timestamps
        
        # Load in data
        self._load_data()

        # Load target vector
        self.target = self._get_exposure_vec()

        self.encoded_target = self._get_encoded_labels()



    def _get_data_record(file_path):
        if file_path.split(".")[1] == "ncs":
            return np.dtype([('TimeStamp',       np.uint64),       # Cheetah timestamp for this record. This corresponds to
                                                                    # the sample time for the first data point in the Samples
                                                                    # array. This value is in microseconds.
                            ('ChannelNumber',   np.uint32),       # The channel number for this record. This is NOT the A/D
                                                                    # channel number
                            ('SampleFreq',      np.uint32),       # The sampling frequency (Hz) for the data stored in the
                                                                    # Samples Field in this record
                            ('NumValidSamples', np.uint32),       # Number of values in Samples containing valid data
                            ('Samples',         np.int16, Terminal._ncs_samples_per_record)])  # Data points for this record. Cheetah
                                                                                        # currently supports 512 data points per
                                                                                        # record. At this time, the Samples
                                                                                        # array is a [512] array.
        elif file_path.split(".")[1] == "nse":
            return np.dtype([('TimeStamp',  np.uint64),       # Cheetah timestamp for this record in microseconds.
                            ('ScNumber',   np.uint32),       # The spike acquisition entity number for this record. 
                                                                # This is NOT the A/D channel number.
                            ('CellNumber', np.uint32),       # The classified cell number for this record. If no cells 
                                                                # have been classified, this number will be zero.
                            ('Params',     np.uint32, 8),    # Array of selected feature data for this spike channel. Cheetah
                                                                # currently allows eight (8) selected features, so this array is fixed
                                                                # at length eight.
                            ('Data',       np.int, (32, 1))  # Data points for this record. Cheetah currently supports 32 points per
                                                                # spike record. The array is organized as [DATAPOINTS, CHANNEL]. At this 
                                                                # time, the Data array is a [32, 1] array.
        ])
        elif file_path.split(".")[1] == "nst":
            NST_RECORD = np.dtype([('TimeStamp',  np.uint64),       # Cheetah timestamp for this record in microseconds.
                                ('ScNumber',   np.uint32),       # The spike acquisition entity number for this record. 
                                                                    # This is NOT the A/D channel number.
                                ('CellNumber', np.uint32),       # The classified cell number for this record. If no cells 
                                                                    # have been classified, this number will be zero.
                                ('Params',     np.uint32, 8),    # Array of selected feature data for this spike channel. Cheetah
                                                                    # currently allows eight (8) selected features, so this array is fixed
                                                                    # at length eight.
                                ('Data',       np.int, (32, 2))  # Data points for this record. Cheetah currently supports 32 points per
                                                                    # spike record. The array is organized as [DATAPOINTS, CHANNEL]. At this 
                                                                    # time, the Data array is a [32, 2] array.
            ])

        elif file_path.split(".")[1] == "ntt":
            return np.dtype([('TimeStamp',  np.uint64),       # Cheetah timestamp for this record in microseconds.
                            ('ScNumber',   np.uint32),       # The spike acquisition entity number for this record. 
                                                                # This is NOT the A/D channel number.
                            ('CellNumber', np.uint32),       # The classified cell number for this record. If no cells 
                                                                # have been classified, this number will be zero.
                            ('Params',     np.uint32, 8),    # Array of selected feature data for this spike channel. Cheetah
                                                                # currently allows eight (8) selected features, so this array is fixed
                                                                # at length eight.
                            ('Data',       np.int, (32, 4))  # Data points for this record. Cheetah currently supports 32 points per
                                                                # spike record. The array is organized as [DATAPOINTS, CHANNEL]. At this 
                                                                # time, the Data array is a [32, 4] array.
        ])
        else:
            raise FileNotFoundError("file '{}' does not contain .ncs, .nse, .nst, or .ntt extension")

    def _load_data(self):

        if self.file_path.split(".")[1] == "ncs":
            return self._load_ncs()
        
        elif (self.file_path.split(".")[1] == 'ntt') or (self.file_path.split(".")[1] == "nse"):
            raise NotImplementedError("Still working on ntt and nse data load utility")


    def _load_ncs(self, load_time=True, rescale_data=True, signal_scaling=_microvolt_scaling):
        """

        input
        -----
        signal_scaling = Terminal.MICROVOLT_SCALING, Terminal.MILLIVOLT_SCALING, or Terminal.VOLT_SCALING
            #TODO: change how signal_scaling is input (class variable, etc?)
        """
        # Load the given file as a Neuralynx .ncs continuous acquisition file and extract the contents
        file_path = os.path.abspath(self.file_path)
        data_record = Terminal._get_data_record(file_path)
        with open(file_path, 'rb') as fid:
            raw_header = read_header(fid)
            records = read_records(fid, data_record)

        header = parse_header(raw_header)
        check_ncs_records(records)

        # Reshape (and rescale, if requested) the data into a 1D array
        data = records['Samples'].ravel()
        #data = records['Samples'].reshape((NCS_SAMPLES_PER_RECORD * len(records), 1))
        if rescale_data:
            try:
                # ADBitVolts specifies the conversion factor between the ADC counts and volts
                data = data.astype(np.float64) * (np.float64(header['ADBitVolts']) * signal_scaling[0])
            except KeyError:
                warnings.warn('Unable to rescale data, no ADBitVolts value specified in header')
                rescale_data = False

        # Pack the extracted data to instance variables
        self.file_path = file_path
        self.raw_header = raw_header
        self.header = header
        self.data = data
        self.data_units = signal_scaling[1] if rescale_data else 'ADC counts'
        self.sampling_rate = records['SampleFreq'][0]
        self.channel_number = records['ChannelNumber'][0]
        self.timestamp = records['TimeStamp']
        #TODO: Ask Nathan if below is a fair means of getting timestamp same length as signal data
        self.timestamp_expanded = np.linspace(self.timestamp.min(), self.timestamp.max(), len(self.data))


    def get_dataframe(self):
        """
        Function to return pandas dataframe from ncs data and event data

        :return: pandas dataframe
        """

        # Creating event mapping, of float to event so nan's are
        # easily replaced, then mapping is used to fill event strings
        event_map = {}
        for i in range(len(self.events)):
            event_map[float(i)] = self.events[i]

        # Creating dataframe
        df = pd.DataFrame({'timestamp': self.timestamp_expanded, 'data': self.data})
        df['exposure'] = np.nan * len(df)

        # TODO: Validate removing last event timestamp works
        event_ts = self.event_timestamps[:-1]

        for i, ts in enumerate(event_ts):
            # TODO: last value from argmax op is 0. Delete last value?
            ix = np.argmax(df['timestamp'].values > ts)
            df.at[ix, 'exposure'] = float(i)

        df['exposure'] = df['exposure'].fillna(method='ffill').map(event_map)

        # Adding degunum to dataframe
        df['degu_id'] = [self.header['FileName'].split('\\')[2].split('_')[0]] * len(df)

        return df


    def _get_exposure_vec(self):

        event_map = {}

        for i in range(len(self.events)):
            event_map[float(i)] = self.events[i]

        exposures = pd.Series([np.nan] * len(self.data))

        # TODO: Validate removing last event timestamp works
        event_ts = self.event_timestamps[:-1]

        for i, ts in enumerate(event_ts):
            # TODO: last value from argmax op is 0. Delete last value?
            ix = np.argmax(self.timestamp_expanded > ts)
            exposures[ix] = float(i)

        exposures = exposures.fillna(method='ffill').map(event_map)

        return exposures.values


    def _get_encoded_labels(self):

        stack = []
        end_states = []
        encoded_labels = []

        for lab in self.target:
            if lab[-1] in '1234567890':
                lab += 'i'

            if lab[:-1] not in stack:

                if lab[-1] == 's' or lab[-1] == 'i':
                    stack.append(lab[:-1])
                    try:
                        end_states.pop()
                    except IndexError:
                        pass

            if lab[:-1] not in end_states:
                if lab[-1] == 'e' or lab[-1] == 'o':
                    end_states.append(lab[:-1])
                    stack.pop()

            encoded_labels.append("-".join(stack))

        return encoded_labels


    def get_target_binary_matrix(self):

        cols = []
        target_cols = pd.Series(self.encoded_target).unique()

        for i, lab in enumerate(self.encoded_target):
            exposures = lab.split('-')
            #     if '' not in exposures:
            #         for exp in exposures:
            #             target_binary.loc[i, exp] = 1
            #     if i % 10000 == 0:
            #         print(i)
            row = []
            for col in target_cols:
                if col in exposures:
                    row.append(1)
                else:
                    row.append(0)
            cols.append(row)

        target_binary_matrix = np.array(cols)

        return target_cols, target_binary_matrix



    def bandpower(self, band, exposure, window_sec=None, relative=False):
        """Compute the average power of the signal x in a specific frequency band.

        Parameters
        ----------
        band : list
            Lower and upper frequencies of the band of interest.
        exposure : str
            name of exposure for analysis. by default, all exposures are analyzed
        window_sec : float
            Length of each window in seconds.
            If None, window_sec = (1 / min(band)) * 2
        relative : boolean
            If True, return the relative power (= divided by the total power of the signal).
            If False (default), return the absolute power.

        Return
        ------
        bp : float
            Absolute or relative band power.
        """
        band = np.asarray(band)
        low, high = band
        start_event = exposure + "s"
        end_event = exposure + "e"

        # Pulling out event timestamp
        start_event_ts = self.event_timestamps[np.where(self.events == start_event)]
        end_event_ts = self.event_timestamps[np.where(self.events == end_event)]

        # Finding index of timestamp for slicing sample
        # TODO: Timestamps to exactly match. ie:
        # Start event ts:  [2460552980]
        # Start event ts (from expanded):  2460553356.988559
        # end event ts:  [2647660347]
        # end event ts (from expanded):  2647660720.174286

        start_event_data_idx = np.argmax(self.timestamp_expanded > start_event_ts)
        end_event_data_idx = np.argmin(self.timestamp_expanded < end_event_ts)

        data = self.data[start_event_data_idx:end_event_data_idx]

        # Define window length
        if window_sec is not None:
            nperseg = window_sec * self.sampling_rate
        else:
            nperseg = (2 / low) * self.sampling_rate

        # Compute the modified periodogram (Welch)
        freqs, psd = welch(data, self.sampling_rate, nperseg=nperseg)

        # Frequency resolution
        freq_res = freqs[1] - freqs[0]

        # Find closest indices of band in frequency vector
        idx_band = np.logical_and(freqs >= low, freqs <= high)

        # Integral approximation of the spectrum using Simpson's rule.
        bp = simps(psd[idx_band], dx=freq_res)

        if relative:
            bp /= simps(psd, dx=freq_res)
        return bp

    def bandpower_splits(self, band, window_sec=None, relative=False):
        
        # Get list of exposure types 
        # e.g. ['r1', 'b1', ...]
        exposures = []
        for e in self.events:
            if e[-1] == 's':
                exposures.append(e[:-1])

        bp_dict = {}
        for i in range(len(exposures)):
            bp_dict[exposures[i]] = self.bandpower(band, exposures[i])

        return bp_dict

# exposures = ['Starting Recording', 'r1s', 'r1e', 'b1s', 'b1e', 'b2s', 'b2e',
                #    'b3s', 's1', 's1o', 's2', 's2o', 'b3e', 'b4s', 's1', 's1o', 's2',
                #    's2o', 'b4e', 'b5s', 's1', 's2', 's1o', 's2o', 'b5e', 'b6s', 's1',
                #    's2', 's1o', 's2o', 'b6e', 'b7s', 'o1', 'o1o', 'o2', 'o2o', 'b7e',
                #    'b8s', 'o1', 'o1o', 'o2', 'o2o', 'b8e', 'b9s', 'o1', 'o2', 'o1o',
                #    'o2o', 'b9e', 'b10s', 'o1', 'o2', 'o1o', 'o2o', 'b10e', 'b11s',
                #    'b11e', 'b12s', 'b12e', 'r2s', 'r2e', 'Stopping Recording'],
                #   dtype='<U18')
