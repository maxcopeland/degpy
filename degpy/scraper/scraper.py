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
import shutil

from degpy.session import Session


class Scraper:

    @staticmethod
    def crawl_files(path):
        """
        Utility to crawl datafiles with ncs or nev extension

        :param path:
        :return: tuple, (list of filepaths, total size of files in bytes)
        """
        data_files = []
        data_size = 0

        for root, dirs, files in os.walk(path):
            for file in files:
                if 'ncs' in file or 'nev' in file:
                    file_path = os.path.join(root, file)
                    data_files.append(file_path)
                    data_size += os.path.getsize(file_path)

        return data_files, (data_size / 1e9)

    @staticmethod
    def get_lfp_data(path):
        """
        Utility to crawl LFP datafiles

        :param path:
        :return: tuple, (list of filepaths, total size of files in bytes)
        """

        # Grabbing directories containing data files
        data_dirs = [x[0] for x in os.walk(path) if '-' in x[0].split('/')[-1]]

        for dir in data_dirs:
            sess = Session(dir)



    @staticmethod
    def move_files(root_path, dest_path):
        """

        :param root_path: str, relative path to root data directory
        :param dest_path: str, relative path to destination directory
        :return: None
        """

        for root, dirs, files in os.walk(root_path):
            for file in files:
                if 'ncs' in file or 'nev' in file:
                    src = os.path.join(root, file)

                    # Formatting filename to be concatenation
                    # of directories
                    name = src.replace('/', '_').split('data')[1][1:]
                    dst = os.path.join(dest_path, name)
                    shutil.copy(src, dst)
