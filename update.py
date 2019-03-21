import os

from alembic import command
from alembic.config import Config
from flask.cli import with_appcontext

from model.Media import storage
from shared import app, db


MIGRATION_DIR = "migrations"
EARLIEST_REVISION = "b38b893343b7"


def update_storage():
    storage.update()


def update_db():
    alembic_config = Config(os.path.join(MIGRATION_DIR, "alembic.ini"))
    alembic_config.set_main_option("script_location", MIGRATION_DIR)
    with app.app_context():
        if not db.engine.dialect.has_table(db.engine, "alembic_version"):
            # consider old databases lacking alembic support to have the earliest
            # revision
            command.stamp(config=alembic_config, revision=EARLIEST_REVISION)
            db.session.flush()
        command.upgrade(config=alembic_config, revision="head")
    db.session.commit()

if __name__ == "__main__":
    update_storage()
    update_db()
