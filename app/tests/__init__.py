# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import print_function

from flask_script import Command, Option, Group
import unittest
import logging
import sys

from raven.middleware import Sentry

from .test_files import load_json


class Tests(Command):
    """Discovers and runs tests"""
    def __init__(self, app, db, cel):
        self.app = app
        self.db = db
        self.cel = cel
        self.loader = unittest.TestLoader()

    def change_configuration(self):
        self.app.debug = True
        self.app.secret_key = "secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        self.app.config["SENTRY"] = None
        self.app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
        self.cel.conf.CELERY_ALWAYS_EAGER = True
        self.cel.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
        self.cel.conf.BROKER_BACKEND = "memory"
        self.cel.conf.CELERY_RESULT_BACKEND = ('cache+memcached'
                                               '://127.0.0.1:11211/')
        self.cel.conf.CELERYD_HIJACK_ROOT_LOGGER = False

        if isinstance(self.app.wsgi_app, Sentry):
            self.app.wsgi_app = self.app.wsgi_app.application

    def get_options(self):
        return [
            Option('-d', '--directory', dest='directory', default='app',
                   help="directory in which tests should be discovered"),
            Option('-l', '--limit', dest='limit', nargs='+', default=None,
                   help="dotted path to a test module, class or function"),
            Option('-f', '--failfast', dest='failfast', action='store_true',
                   help="if enabled, will stop the tests on first fail"),
            Group(
                Option('-q', '--quiet', dest='quiet', action='store_true'),
                Option('-v', '--verbose', dest='verbose', action='store_true'),
                exclusive=True, required=False),
            Group(
                Option('-V', '--very-verbose', dest='very_verbose',
                       action='store_true'),
                Option('-Q', '--very-quiet', dest='very_quiet',
                       action='store_true'),
                exclusive=True, required=False),
        ]

    def run(self, directory, limit, failfast=False,
            verbose=False, quiet=False, very_verbose=False, very_quiet=False):
        self.change_configuration()

        if limit:
            try:
                tests = self.loader.loadTestsFromNames(limit)
            except (ImportError, AttributeError):
                print("Couldn't find test{1} {0}.".format(", ".join(limit),
                      "s" if len(limit) > 1 else ""))
                return
        else:
            tests = self.loader.discover(directory, top_level_dir="app/tests")

        if very_verbose:
            logging_level = logging.DEBUG
        elif very_quiet:
            logging_level = logging.CRITICAL
            import warnings
            # We prevent warnings from printing (i.e. sqlachemy warnings)
            warnings.simplefilter("ignore")
        else:
            logging_level = logging.ERROR

        if verbose:
            verbosity = 2
        elif quiet:
            verbosity = 0
        else:
            verbosity = 1

        stream = logging.StreamHandler(sys.stdout)
        logging.root.addHandler(stream)
        logging.root.setLevel(logging_level)
        stream.setLevel(logging_level)
        self.app._logger = logging.root
        self.app.logger_name = logging.root.name
        test_runner = unittest.runner.TextTestRunner(
            verbosity=verbosity,
            failfast=failfast
        )
        r = not test_runner.run(tests).wasSuccessful()
        sys.exit(r)
