"""seed admin user

Revision ID: 6839f4efda73
Revises: 04d4fde71b24
Create Date: 2025-11-14 00:24:50.200891

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Boolean, String, column, table

from app.databases.postgresql.seeds.admin_user_seed import generate_admin_user

# revision identifiers, used by Alembic.
revision: str = "6839f4efda73"
down_revision: Union[str, Sequence[str], None] = "04d4fde71b24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def define_users_table():
    return table(
        "users",
        column("name", String(120)),
        column("email", String(255)),
        column("rut", String(20)),
        column("hashed_password", String(255)),
        column("is_admin", Boolean),
        column("is_doctor", Boolean),
        column("is_chief_doctor", Boolean),
        column("turn", String(50)),
    )


def upgrade():
    users_table = define_users_table()
    admin_data = generate_admin_user()
    op.bulk_insert(users_table, [admin_data])


def downgrade():
    admin_data = generate_admin_user()
    users_table = define_users_table()
    op.execute(users_table.delete().where(users_table.c.email == admin_data["email"]))
