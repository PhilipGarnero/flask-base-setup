# -*- coding: utf8 -*-

from __future__ import unicode_literals

from flask import json
import os.path


def load_json(json_file, to_dict=True):
    if not json_file.endswith(".json"):
        json_file += ".json"
    json_file = os.path.join(os.path.dirname(__file__), json_file)

    with open(json_file) as f:
        data = f.read()

    if to_dict:
        data = json.loads(data)

    return data
