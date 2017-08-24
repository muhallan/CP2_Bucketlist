import os
import unittest
import coverage
# class for handling a set of commands
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app import models

# initialize the app with all its configurations
# app = create_app(config_name=os.getenv('APP_SETTINGS'))
app = create_app(config_name="development")
migrate = Migrate(app, db)
# create an instance of class that will handle our commands
manager = Manager(app)


# Define the migration command to always be preceded by the word "db"
# Usage: python manage.py db init
manager.add_command('db', MigrateCommand)

# define our command for testing called "test"
# Usage: python manage.py test
@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def cov():
    """Runs the unit tests with coverage."""
    cov = coverage.coverage(branch=True, include='app/*')
    cov.start()
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    cov.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    cov.erase()

@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()

@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()

if __name__ == '__main__':
    manager.run()
