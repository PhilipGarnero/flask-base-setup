# -*- coding: utf8 -*-

from __future__ import unicode_literals
import importlib
import pkgutil
import sqlite3
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from celery import Celery
from sqlalchemy.engine import Engine
from sqlalchemy import event
from raven import Client
from raven.contrib.flask import Sentry
from raven.contrib.celery import register_signal

from app.config import read_config
from app.logs import setup_loggers

db = SQLAlchemy(session_options={"autoflush": False})
migrate = Migrate()
cel = Celery('app', include=["app.tasks"])
login_manager = LoginManager()
sentry = Sentry()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def _create_app(config):
    app = Flask(__name__)
    app.config = dict(app.config.items() + config.items())
    app.debug = app.config.pop("DEBUG", False)
    app.secret_key = app.config.pop("SECRET", False)
    cel.conf.update(app.config.get("CELERY_CONF", {}))
    if not app.debug and app.config.get('LOGGERS', False):
        setup_loggers(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    if app.config.get('SENTRY', None):
        sentry.init_app(app, dsn=app.config.get('SENTRY'))
        register_signal(Client(dsn=app.config.get('SENTRY')))
    return app

config = read_config()
app = _create_app(config)


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, unicode) or isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if not name.startswith("_"):
            full_name = package.__name__ + '.' + name
            if any((x in package.__name__ for x in ("models", "views",
                                                    "tasks",))):
                results[full_name] = importlib.import_module(full_name)
            elif any((x in name for x in ("models", "views",))):
                results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(import_submodules(full_name))
    return results

import_submodules(__name__)
