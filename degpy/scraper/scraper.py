"""
This module contains utilities to scrape degu ephys data of the following structure

data
    080602
        080602_ps01_160614
            2016-06-14_09-39-10
                LFP1.ncs
                LFP2.ncs
                E1.ncs


TODO:
"""

import os

from degpy.session import Session


class Scraper:

    @staticmethod
    def scrape(path):
        """
        :param path:
        :return:
        """
        data_files = []
        data_size = 0

        for root, dirs, files in os.walk(path):
            for file in files:
                if 'ncs' in file:
                    file_path = os.path.join(root, file)
                    data_files.append(file_path)
                    data_size += os.path.getsize(file_path)

        return data_files, (data_size / 1e9)


