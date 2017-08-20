import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app import models

app = create_app(config_name=os.getenv('APP_SETTINGS'))
# app = create_app(config_name="development")
migrate = Migrate(app, db)
# create an instance of class that will handle our commands
manager = Manager(app)

# Define the migration command to always be preceded by the word "db"
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
