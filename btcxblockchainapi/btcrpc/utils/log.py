import logging
import sys


def get_log(log_name):

    log = logging.getLogger(log_name)
    #check is already a singleTon
    if not len(log.handlers):
        log.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        log.addHandler(ch)
    return log


def get_file_logger(log_name, filename):

    log = logging.getLogger(log_name)
    #check is already a singleTon
    if not len(log.handlers):
        ch = logging.FileHandler(filename)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        log.addHandler(ch)
        log.setLevel(logging.DEBUG)
    return log