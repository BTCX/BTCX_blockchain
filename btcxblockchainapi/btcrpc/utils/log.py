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


def log_info(log_instance, informative_string, info_to_log = None):
    if(info_to_log):
        print(informative_string + ":")
        print(info_to_log)
        log_instance.info(informative_string + ":")
        log_instance.info(info_to_log)
    else:
        print(informative_string)
        log_instance.info(informative_string)


def log_error(log_instance, informative_error_string, error_info_to_log=None):
    if (error_info_to_log):
        print(informative_error_string + ":")
        print(error_info_to_log)
        log_instance.error(informative_error_string + ":")
        log_instance.error(error_info_to_log)
    else:
        print(informative_error_string)
        log_instance.error(informative_error_string)