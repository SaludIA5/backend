"""Factories para generar datos de prueba usando Factory Boy."""

import factory
from faker import Faker

from app.databases.postgresql.models import Episode

fake = Faker()


class BaseFactory(factory.Factory):
    """Factory base con configuración común."""

    class Meta:
        abstract = True


# Ejemplos de factories para cuando tengas modelos
# Descomenta y adapta según tus modelos cuando los crees

# class UserFactory(BaseFactory):
#     """Factory para crear usuarios de prueba."""
#
#     class Meta:
#         model = User  # Reemplaza con tu modelo User
#
#     email = factory.LazyFunction(lambda: fake.email())
#     username = factory.LazyFunction(lambda: fake.user_name())
#     first_name = factory.LazyFunction(lambda: fake.first_name())
#     last_name = factory.LazyFunction(lambda: fake.last_name())
#     is_active = True
#     created_at = factory.LazyFunction(lambda: fake.date_time_this_year())


# Factories para datos sin modelo (para testing de APIs)
class UserDataFactory(BaseFactory):
    """Factory para generar datos de usuario de prueba."""

    class Meta:
        model = dict

    name = factory.LazyFunction(lambda: fake.name())
    email = factory.LazyFunction(lambda: fake.email())
    rut = factory.LazyFunction(
        lambda: f"{fake.random_int(min=10, max=25)}.{fake.random_int(min=100, max=999)}.{fake.random_int(min=100, max=999)}-{fake.random_element(elements=('1', '2', '3', '4', '5', '6', '7', '8', '9', 'k'))}"
    )
    password = factory.LazyFunction(lambda: fake.password(length=12))
    is_chief_doctor = False
    is_doctor = True


class PredictionDataFactory(BaseFactory):
    """Factory para generar datos de predicción de episodios médicos."""

    class Meta:
        model = dict

    # Model selection
    model_type = "random_forest"

    # Episode data
    tipo = "SIN ALERTA"
    tipo_alerta_ugcc = "SIN ALERTA"
    triage = factory.LazyFunction(lambda: fake.random_int(min=1, max=5))

    # Antecedentes médicos
    antecedentes_cardiaco = factory.LazyFunction(lambda: fake.boolean())
    antecedentes_diabetes = factory.LazyFunction(lambda: fake.boolean())
    antecedentes_hipertension = factory.LazyFunction(lambda: fake.boolean())

    # Signos vitales
    presion_sistolica = factory.LazyFunction(lambda: fake.random_int(min=90, max=180))
    presion_diastolica = factory.LazyFunction(lambda: fake.random_int(min=60, max=120))
    presion_media = factory.LazyFunction(lambda: fake.random_int(min=70, max=140))
    temperatura_c = factory.LazyFunction(
        lambda: round(fake.random.uniform(35.0, 39.0), 1)
    )
    saturacion_o2 = factory.LazyFunction(lambda: fake.random_int(min=85, max=100))
    frecuencia_cardiaca = factory.LazyFunction(lambda: fake.random_int(min=50, max=150))
    frecuencia_respiratoria = factory.LazyFunction(
        lambda: fake.random_int(min=12, max=30)
    )

    # Scores y escalas
    glasgow_score = factory.LazyFunction(lambda: fake.random_int(min=3, max=15))
    tipo_cama = factory.LazyFunction(
        lambda: fake.random_element(elements=["UCI", "UTI", "INTERMEDIO"])
    )

    # Soporte respiratorio
    fio2 = factory.LazyFunction(lambda: round(fake.random.uniform(0.21, 1.0), 2))
    fio2_ge_50 = factory.LazyFunction(lambda: fake.boolean())
    ventilacion_mecanica = factory.LazyFunction(lambda: fake.boolean())

    # Procedimientos
    cirugia_realizada = factory.LazyFunction(lambda: fake.boolean())
    cirugia_mismo_dia_ingreso = factory.LazyFunction(lambda: fake.boolean())
    hemodinamia = factory.LazyFunction(lambda: fake.boolean())
    hemodinamia_mismo_dia_ingreso = factory.LazyFunction(lambda: fake.boolean())
    endoscopia = factory.LazyFunction(lambda: fake.boolean())
    endoscopia_mismo_dia_ingreso = factory.LazyFunction(lambda: fake.boolean())
    dialisis = factory.LazyFunction(lambda: fake.boolean())
    trombolisis = factory.LazyFunction(lambda: fake.boolean())
    trombolisis_mismo_dia_ingreso = factory.LazyFunction(lambda: fake.boolean())

    # Laboratorios
    pcr = factory.LazyFunction(lambda: round(fake.random.uniform(0.5, 30.0), 2))
    hemoglobina = factory.LazyFunction(lambda: round(fake.random.uniform(8.0, 18.0), 1))
    creatinina = factory.LazyFunction(lambda: round(fake.random.uniform(0.5, 3.0), 2))
    nitrogeno_ureico = factory.LazyFunction(
        lambda: round(fake.random.uniform(10.0, 50.0), 2)
    )
    sodio = factory.LazyFunction(lambda: round(fake.random.uniform(130.0, 150.0), 2))
    potasio = factory.LazyFunction(lambda: round(fake.random.uniform(3.0, 6.0), 2))

    # Otros
    dreo = factory.LazyFunction(lambda: fake.boolean())
    troponinas_alteradas = factory.LazyFunction(lambda: fake.boolean())
    ecg_alterado = factory.LazyFunction(lambda: fake.boolean())
    rnm_protocolo_stroke = factory.LazyFunction(lambda: fake.boolean())
    dva = factory.LazyFunction(lambda: fake.boolean())
    transfusiones = factory.LazyFunction(lambda: fake.boolean())
    compromiso_conciencia = factory.LazyFunction(lambda: fake.boolean())

    @classmethod
    def build_complete(cls, **kwargs):
        """Build prediction data with all fields populated."""
        return cls.build(**kwargs)

    @classmethod
    def build_deterministic(cls, **kwargs):
        """Build deterministic prediction data for consistency tests."""
        return {
            "model_type": "random_forest",
            "tipo": "SIN ALERTA",
            "tipo_alerta_ugcc": "SIN ALERTA",
            "triage": 3,
            "antecedentes_cardiaco": True,
            "antecedentes_diabetes": False,
            "antecedentes_hipertension": True,
            "presion_sistolica": 160,
            "presion_diastolica": 95,
            "presion_media": 140,
            "temperatura_c": 36.5,
            "saturacion_o2": 97,
            "frecuencia_cardiaca": 104,
            "frecuencia_respiratoria": 27,
            "tipo_cama": "UCI",
            "glasgow_score": 14,
            "fio2": 0.21,
            "fio2_ge_50": False,
            "ventilacion_mecanica": False,
            "cirugia_realizada": False,
            "cirugia_mismo_dia_ingreso": False,
            "hemodinamia": False,
            "hemodinamia_mismo_dia_ingreso": False,
            "endoscopia": False,
            "endoscopia_mismo_dia_ingreso": False,
            "dialisis": False,
            "trombolisis": False,
            "trombolisis_mismo_dia_ingreso": False,
            "pcr": 17.51,
            "hemoglobina": 13.1,
            "creatinina": 0.92,
            "nitrogeno_ureico": 31.0,
            "sodio": 139.0,
            "potasio": 4.5,
            "dreo": False,
            "troponinas_alteradas": False,
            "ecg_alterado": False,
            "rnm_protocolo_stroke": False,
            "dva": False,
            "transfusiones": False,
            "compromiso_conciencia": False,
            **kwargs,
        }


class EpisodeFactory(BaseFactory):
    """Factory para generar episodios médicos de prueba."""

    class Meta:
        model = Episode

    id = factory.Sequence(lambda n: n + 1)
    numero_episodio = factory.LazyFunction(lambda: fake.uuid4())
    patient_id = factory.Sequence(lambda n: n + 1)
    fecha_estabilizacion = factory.LazyFunction(lambda: fake.date_this_year())
    fecha_alta = factory.LazyFunction(lambda: fake.date_this_year())
    validacion = factory.LazyFunction(
        lambda: fake.random_element(["VALIDADO", "PENDIENTE"])
    )
    tipo = factory.LazyFunction(lambda: fake.random_element(["URGENTE", "NORMAL"]))
    tipo_alerta_ugcc = factory.LazyFunction(
        lambda: fake.random_element(["SIN ALERTA", "ALERTA"])
    )
    fecha_ingreso = factory.LazyFunction(lambda: fake.date_this_year())
    mes_ingreso = factory.LazyFunction(lambda: fake.random_int(min=1, max=12))
    fecha_egreso = factory.LazyFunction(lambda: fake.date_this_year())
    mes_egreso = factory.LazyFunction(lambda: fake.random_int(min=1, max=12))
    centro = factory.LazyFunction(lambda: fake.company())
