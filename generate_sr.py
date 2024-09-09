import os
import json
import pydicom
import requests
from pydicom.uid import generate_uid

ORTHANC_URL = "http://localhost:8042/instances"
ORTHANC_USERNAME = "orthanc"
ORTHANC_PASSWORD = "orthanc"

def create_dicom_sr(original_dicom_path, result_data, output_sr_path):
    # Carregar o DICOM original para obter metadados
    original_dicom = pydicom.dcmread(original_dicom_path)
    
    # Criar um novo DICOM SR
    ds = pydicom.Dataset()
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.120.1'  # DICOM SR SOP Class UID
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    # Copiar metadados do DICOM original
    ds.PatientID = original_dicom.PatientID
    ds.PatientName = original_dicom.PatientName
    ds.StudyInstanceUID = original_dicom.StudyInstanceUID
    ds.SeriesInstanceUID = original_dicom.SeriesInstanceUID
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.120.1'
    
    # Adicionar informações do Structured Report
    ds.add_new(0x00080060, 'CS', 'SR')  # Modality
    ds.add_new(0x00080018, 'UI', ds.SOPInstanceUID)  # SOP Instance UID
    ds.add_new(0x00400001, 'AE', 'Structured Report')  # Scheduled Procedure Step ID
    ds.add_new(0x0040A730, 'LO', 'Classification Results')  # Content Template Sequence
    ds.add_new(0x0040A731, 'ST', 'Classification Results')  # Structured Report Content
    
    # Adicionar resultado previsto e probabilidades
    result_description = (
        f"Predicted Class: {result_data['predicted_class']}\n"
        f"Predicted Probabilities: {', '.join(map(str, result_data['predicted_probabilities']))}"
    )
    ds.add_new(0x0040A730, 'ST', result_description)  # '0x0040A730' é um exemplo, ajuste conforme necessário

    # Salvar o DICOM SR
    ds.save_as(output_sr_path)

def upload_dicom(dicom_path):
    print(f"Tentando enviar: {dicom_path}")  # Mensagem de depuração
    try:
        with open(dicom_path, 'rb') as f:
            dicom_data = f.read()
        
        response = requests.post(
            ORTHANC_URL,
            data=dicom_data,
            headers={"Content-Type": "application/dicom"},
            auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD)
        )

        if response.status_code == 200:
            print(f"Upload bem-sucedido para {dicom_path}")
        else:
            print(f"Erro no upload de {dicom_path}: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Erro ao tentar enviar {dicom_path}: {e}")

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_all_dicom_files(input_dir, output_dir, json_path):
    # Carregar os resultados da classificação do JSON
    with open(json_path, 'r') as f:
        results = json.load(f)
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.dcm'):
                original_dicom_path = os.path.join(root, file)
                
                # Obter o resultado da classificação do JSON
                json_path_key = os.path.relpath(original_dicom_path, input_dir).replace('\\', '/')
                result_data = results.get(json_path_key, {'predicted_class': 'Unknown', 'predicted_probabilities': []})
                
                # Obter os metadados do DICOM original
                dicom = pydicom.dcmread(original_dicom_path)
                patient_id = dicom.PatientID
                patient_name = dicom.PatientName
                study_instance_uid = dicom.StudyInstanceUID
                series_instance_uid = dicom.SeriesInstanceUID
                
                # Criar estrutura de diretórios, mas não ta indo...
                patient_dir = os.path.join(output_dir, patient_id)
                study_dir = os.path.join(patient_dir, study_instance_uid)
                series_dir = os.path.join(study_dir, series_instance_uid)
                
                ensure_directory_exists(series_dir)
                
                # Criar DICOM SR
                output_sr_path = os.path.join(series_dir, file.replace('.dcm', '_sr.dcm'))
                create_dicom_sr(original_dicom_path, result_data, output_sr_path)
                
                # Enviar para PACS
                upload_dicom(output_sr_path)

input_dir = 'data/dicoms'
output_dir = 'data/dicoms_sr'
json_path = 'data/classification_results.json'

print("Iniciando o processamento e upload dos arquivos DICOM...")  # Mensagem de depuração
process_all_dicom_files(input_dir, output_dir, json_path)
