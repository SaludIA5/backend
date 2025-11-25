from sqlalchemy.orm import declarative_base

Base = declarative_base()


from app.databases.postgresql.models.patient import Patient
from app.databases.postgresql.models.user import User
from app.databases.postgresql.models.episode import Episode
from app.databases.postgresql.models.diagnostic import Diagnostic
from app.databases.postgresql.models.user_episodes_validations import UserEpisodeValidation
from app.databases.postgresql.models.episode_user import episode_user
from app.databases.postgresql.models.model_versions import ModelVersion
from app.databases.postgresql.models.doctor_summary import DoctorSummary    
