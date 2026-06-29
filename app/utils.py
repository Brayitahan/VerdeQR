from flask import request
import random
import string
import os

def get_base_url():
    env_url = os.environ.get('BASE_URL')
    if env_url:
        return env_url.rstrip('/')
    forwarded_host = request.headers.get('X-Forwarded-Host')
    if forwarded_host:
        forwarded_proto = request.headers.get('X-Forwarded-Proto', 'https')
        return f"{forwarded_proto}://{forwarded_host}"
    original_host = request.headers.get('X-Original-Host')
    if original_host:
        return f"https://{original_host}"
    return request.host_url.rstrip('/')

def generar_token(longitud=6):
    return ''.join(random.choices(string.digits, k=longitud))

def determinar_genero(nombre):
    terminaciones_femeninas = ['a', 'ia', 'na', 'ina', 'ita', 'ela', 'isa', 'esa']
    excepciones_masculinas = ['juan', 'josue', 'matias', 'elias', 'tobias', 'lucas', 'tomas', 'nicolas', 'jesus']
    nombre_lower = nombre.lower()
    if nombre_lower in excepciones_masculinas:
        return 'masculino'
    for terminacion in terminaciones_femeninas:
        if nombre_lower.endswith(terminacion):
            return 'femenino'
    return 'masculino'

def obtener_avatar_predeterminado(nombre):
    genero = determinar_genero(nombre)
    if genero == 'femenino':
        return 'css/js/img/avatarf.jpg'
    else:
        return 'css/js/img/avatarm.jpg'
