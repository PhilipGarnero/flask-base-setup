# -*- coding: utf8 -*-

from __future__ import unicode_literals
import os
import sys
import codecs
import yaml
import json


def get_config_file(base_path):
    """Determine the configuration file to use."""
    config_files = [
        base_path + '/config.yml',
        'config.yml'
    ]
    for config_file in config_files:
        if os.path.isfile(config_file):
            return config_file
    return None


def read_config(base_path='', verbose=False):

    # Locate the config file to use
    config_file = get_config_file(base_path)
    if not config_file:
        print 'Missing configuration file'
        sys.exit(1)
    if verbose:
        print 'Using configuration file: %s' % config_file

    # Open and read the config file
    with codecs.open(config_file, 'r', 'utf8') as file_handler:
        conf = yaml.load(file_handler)
    if conf is None:
        conf = {}
    if verbose:
        print json.dumps(conf, sort_keys=True,
                         indent=4, separators=(',', ': '))

    return conf
