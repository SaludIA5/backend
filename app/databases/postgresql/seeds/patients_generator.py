from faker import Faker
import random
from typing import List, Dict, Any


SEED_VALUE = 42 

def generate_patient_data(num_patients: int = 115) -> List[Dict[str, Any]]:
    """
    Genera una lista de diccionarios con datos falsos de paciente, 
    asegurando que el RUT no tenga puntos ni guiones.
    """
    
    Faker.seed(SEED_VALUE)
    random.seed(SEED_VALUE)
    
    fake = Faker('es_ES') 
    
    users = []
    ruts_generados = set()
    
    for i in range(num_patients):
        
        while True:

            rut_base = random.randint(5_000_000, 25_000_000) 
            rut_digito = random.choice('0123456789K')
            
            rut_final = str(rut_base) + rut_digito
            
            if rut_final not in ruts_generados:
                ruts_generados.add(rut_final)
                break

        gender = random.choice(['Masculino', 'Femenino', 'No descrito'])
        
        if gender == 'Masculino':
            primer_nombre = fake.first_name_male()
        elif gender == 'Femenino':
            primer_nombre = fake.first_name_female()
        else:
            primer_nombre = random.choice([fake.first_name_male(), fake.first_name_female()])
        
        primer_apellido = fake.last_name()
        segundo_apellido = fake.last_name()
            
        users.append({
            "name": f'{primer_nombre} {primer_apellido} {segundo_apellido}',
            "rut": rut_final,
            "age": random.randint(18, 95),
            "gender": gender,
            "active": fake.boolean(),
        })
        
    return users

if __name__ == "__main__":
    print(generate_patient_data(115))