"""Factories para generar datos de prueba usando Factory Boy."""

import factory
from faker import Faker

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

    email = factory.LazyFunction(lambda: fake.email())
    username = factory.LazyFunction(lambda: fake.user_name())
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    password = factory.LazyFunction(lambda: fake.password(length=12))
    is_active = True
