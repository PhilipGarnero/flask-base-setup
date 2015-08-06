# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging


def setup_loggers(app):
    config = app.config['LOGGERS']
    app.logger.setLevel(logging.DEBUG)
    for logger_name, logger_config in config.iteritems():
        handler = None
        if logger_name == 'syslog':
            handler = _get_syslog_handler(logger_config)
        elif logger_name == 'stdout':
            handler = _get_stdout_handler(logger_config)
        elif logger_name == 'file':
            handler = _get_file_handler(logger_config)

        if handler:
            handler.setLevel(getattr(logging, logger_config['level'].upper()))
            app.logger.addHandler(handler)


def _get_syslog_handler(logger_config):
    """Get a syslog handler.

    If 'device' is set it will use this device as syslog address,
    otherwise it will send to 'host':'port' using either TCP or UDP as
    defined in 'transport'.
    """
    from logging.handlers import SysLogHandler
    from socket import SOCK_DGRAM, SOCK_STREAM
    if logger_config.get('device', False):
        return SysLogHandler(address=logger_config['device'])
    address = (logger_config['host'], logger_config['port'])
    socktype = SOCK_STREAM
    if logger_config['transport'] == 'UDP':
        socktype = SOCK_DGRAM
    handler = SysLogHandler(
        address=address,
        socktype=socktype,
        facility=SysLogHandler.LOG_USER
    )
    return handler


def _get_stdout_handler(logger_config):
    from logging import StreamHandler
    from sys import stdout
    handler = StreamHandler(stream=stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    return handler


def _get_file_handler(logger_config):
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(
        filename=logger_config['file_name'],
        maxBytes=logger_config['max_bytes'],
        backupCount=logger_config['backups']
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    return handler
