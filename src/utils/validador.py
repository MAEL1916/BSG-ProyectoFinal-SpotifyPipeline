import json
import logging
import pandas

logging.basicConfig(level=logging.INFO)

def cargar_schema(capa):
    try:
        ruta = f"data_contracts/schemas/{capa}_schema.json"
        with open(ruta, 'r') as f:
            schema = json.load(f)
        
        logging.info(f'Schema {capa} cargado correctamente')
        return schema
        
    except Exception as e:
        logging.error(f"Error en cargar_schema: {str(e)}")
        return None


def validar_columnas(df, schema):
    try:
        campos_esperados = [field['name'] for field in schema['fields']]
        columnas_df = df.columns.tolist()
        
        faltantes = [col for col in campos_esperados if col not in columnas_df]
        
        if faltantes:
            logging.error(f"Columnas faltantes: {faltantes}")
            return False
        
        logging.info("Validación de columnas exitosa")
        return True
        
    except Exception as e:
        logging.error(f"Error en validar_columnas: {str(e)}")
        return False


# TODO: mejorar esto
def validar_tipos(df, schema):
    '''
    Valida tipos de datos básicos
    '''
    try:
        for field in schema["fields"]:
            nombre = field['name']
            tipo = field['type']
            
            if nombre not in df.columns:
                continue
            
            if tipo == 'integer':
                if not pandas.api.types.is_numeric_dtype(df[nombre]):
                    logging.error(f"Columna {nombre} no es numérica")
                    return False
            
            elif tipo == "string":
                if not pandas.api.types.is_string_dtype(df[nombre]) and not pandas.api.types.is_object_dtype(df[nombre]):
                    logging.error(f'Columna {nombre} no es string')
                    return False
        
        logging.info("Validación de tipos exitosa")
        return True
        
    except Exception as e:
        logging.error(f"Error en validar_tipos: {str(e)}")
        return False


def validar_datos(df, capa):
    try:
        schema = cargar_schema(capa)
        
        if not schema:
            return False
        if not validar_columnas(df, schema):
            return False
        
        if not validar_tipos(df, schema):
            return False
        
        logging.info(f"Validación completa de capa {capa} exitosa")
        return True
        
    except Exception as e:
        logging.error(f"Error en validar_datos: {str(e)}")
        return False