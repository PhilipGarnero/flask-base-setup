# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

from flask_script import Shell, Manager
from flask_migrate import MigrateCommand

from app import app, db, cel
from app import models
from app.tests import Tests
from app.config import read_config


manager = Manager(app)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, models=models)


@manager.command
def getconfig():
    """Gives information about the configuration file used."""
    read_config(verbose=True)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('test', Tests(app, db, cel))

if __name__ == '__main__':
    manager.run()
