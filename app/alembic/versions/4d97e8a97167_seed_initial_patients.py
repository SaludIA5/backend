"""seed_initial_patients

Revision ID: 4d97e8a97167
Revises: ed14b6831ae5
Create Date: 2025-10-15 18:41:06.495139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean
from app.databases.postgresql.seeds.patients_generator import generate_patient_data 

revision: str = '4d97e8a97167'
down_revision: Union[str, Sequence[str], None] = 'ed14b6831ae5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def define_patients_table():
    return table(
        'patients',
        column('name', String(50)),
        column('rut', String(20)),
        column('age', Integer),
        column('gender', String(1)),
        column('active', Boolean),
    )

def upgrade():

    patients_table = define_patients_table()
    NUM_PATIENTS = 115
    seed_data = generate_patient_data(NUM_PATIENTS)
    op.bulk_insert(patients_table, seed_data)


def downgrade():

    NUM_PATIENTS = 115
    ruts_to_delete = [data['rut'] for data in generate_patient_data(NUM_PATIENTS)]
    
    patients_table = define_patients_table()
    op.execute(
        patients_table.delete().where(
            patients_table.c.rut.in_(ruts_to_delete)
        )
    )
