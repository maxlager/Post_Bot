#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
DumpLoader created for dumping and loading, obviously
"""
import pickle


def dumper(file_name, variable):
    """
    Created for dumping lists to admin and blacklist files
    :param file_name:
    :param variable:
    :return: boolean variable
    """
    file = open("./%s" % (file_name), "wb")
    pickle.dump(variable, file)
    file.close()
    return True


def loader(file_name):
    """
    Created for loading lists from admin and blacklist files
    :param file_name:
    :return: a list of ID's in file
    """
    variable = []
    try:
        file = open("./%s" % (file_name), "rb")
        variable = pickle.load(file)
    except BaseException:  # We need to catch EOFError and OSError
        file = open("./%s" % (file_name), "w")
        file.close()
    return variable