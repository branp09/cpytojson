from flask import Flask,jsonify , request
import sys 
sys.path.append("..")

from lib.cpybk import copybook
from lib.cpybk.field_group import FieldGroup
from lib.cpybk.field import Field
from werkzeug.datastructures.file_storage import FileStorage
from tempfile import _TemporaryFileWrapper

import os
import tempfile
import os
import re

app = Flask(__name__)

def generar_cobol_json( field , nivel=1 , json_cob = {},data_rs="",tupla=()):
  current_level = json_cob
  
  if type(field) == FieldGroup:    
    partes = field.name.split("_")
    if not partes[-1].isdigit(): 
      field_json = {}
      current_level[field.name] = field_json
      if field.repeat > 1: 
        current_level[field.name]["datatype"] = "array"
        current_level[field.name]["length"] = field.repeat
      else:
        current_level[field.name]["datatype"] = "object"
      generar_cobol_json(field.children, nivel + 1, field_json,data_rs,tupla)

  if type(field) == Field:
    partes = field.name.split("_")
    if not partes[-1].isdigit(): 
      if field.datatype == 'decimal':
        current_level[field.name] = {"length": str(field.length), "datatype": field.datatype,"precision":field.precision}
      else:
        current_level[field.name] = {"length": str(field.length), "datatype": field.datatype,"pos_ini":field.start_pos,"pos_fin": (field.start_pos) + field.length}
        
      descripcion = [clave for clave, valor in tupla if valor == field.name]
        
      if descripcion:
        current_level[field.name]["descripcion"] = descripcion[0]

      if data_rs != "" :
        current_level[field.name]["example"] = data_rs[field.start_pos:(field.start_pos + field.length) ]
      
  if type(field) == list:
    for child in field :
      generar_cobol_json(child,nivel,json_cob,data_rs,tupla)
  
  return json_cob

def readFile(file_cpy) -> list[str]:
  str_file: list
  with open(file_cpy, 'r', encoding='utf-8') as base_file:
    str_file = base_file.readlines()
  return str_file

def extraer_cadena(linea):
    pos_pic = linea.find("PIC")
    if pos_pic == -1:
        return None
    
    match_num = re.search(r'\d+', linea[:pos_pic])
    
    if not match_num:
      return None
    
    pos_num = match_num.span()[1]
    nueva_pos = (pos_num + 2 )
    subcadena = linea[max(0, nueva_pos):pos_pic]
    return subcadena.strip()

def generar_tuplas(array_texto):
    tuplas = []
    for i in range(len(array_texto)):
      if array_texto[i].strip().startswith("*") and not array_texto[i].strip().endswith(".") :
        descripcion = array_texto[i].strip().lstrip("*").strip()
        if i + 1 < len(array_texto) and  'PIC' in array_texto[i+1].strip() :
          tuplas.append((descripcion, extraer_cadena(array_texto[i + 1])))  # Crea la tupla
    return tuplas

def limpiar_archivo_contenido(base_file):
    
    temp_file: _TemporaryFileWrapper

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
    for linea in base_file:
      if '*' not in linea and '' not in linea:
          last_char_paren = linea.rfind(").")
          if last_char_paren != -1:
              linea_limpia = linea[:last_char_paren + len(").")].rstrip() + '\n'     
          else:
              last_char_point = linea.rfind(".")
              if last_char_point != -1:
                linea_limpia = linea[:last_char_point + len(".")].rstrip() + '\n'    
              else:
                linea_limpia = linea.rstrip() + '\n'
          temp_file.write(linea_limpia)

    temp_file.close()
    return temp_file.name

def cobolToJson(file_cpy: FileStorage,file_data):

  data = file_data.read().decode('utf-8')
  lines = file_cpy.readlines()
  lines_as_strings = [line.decode('utf-8') for line in lines]
  tupla_desc = generar_tuplas(lines_as_strings)
  temp_file_path = limpiar_archivo_contenido(lines_as_strings)
  
  json_cobol = {"metadata":{},"cobolReg":{}}
  
  root_copy = copybook.parse_file(temp_file_path)
  list_of_fields = root_copy.flatten()
  regProgram = list_of_fields[0]
  json_cobol["metadata"]["lengthTotal"] = regProgram.get_total_length()
  
  if type(list_of_fields) == list: 
    json_cobol["cobolReg"][regProgram.name] = {}
    if type(regProgram) == FieldGroup:
      generar_cobol_json(regProgram.children,0,json_cob=json_cobol["cobolReg"][regProgram.name],data_rs=data,tupla=tupla_desc)
  os.remove(temp_file_path)
  return json_cobol

@app.route('/components/cpy/toJson', methods=['GET'])
def convertCpyToJson():

  if 'file_cpy' not in request.files:
    return jsonify({"error": "CPY OBLIGATORIO"}), 400
  
  file_cpy: FileStorage

  file_cpy = request.files['file_cpy']
  file_data = request.files['data']
  
  if file_cpy.filename == '':
    return jsonify({"error": "Archivo no seleccionado"}), 400

  try:
    json_cobol = cobolToJson(file_cpy,file_data)
    return jsonify(json_cobol), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'cpy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)