import os
import requests

ORTHANC_URL = "http://localhost:8042/instances"
ORTHANC_USERNAME = "orthanc"
ORTHANC_PASSWORD = "orthanc"

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

def upload_all_dicoms(directory):
    if not os.path.exists(directory):
        print(f"Diretório não encontrado: {directory}")
        return
    
    print(f"Procurando arquivos DICOM em: {directory}")  # Mensagem de depuração
    for root, dirs, files in os.walk(directory):
        print(f"Explorando diretório: {root}")  # Mensagem de depuração
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_path = os.path.join(root, file)
                upload_dicom(dicom_path)

DICOM_DIRECTORY = "data/dicoms"

print("Iniciando o upload dos arquivos DICOM...")  # Mensagem de depuração
upload_all_dicoms(DICOM_DIRECTORY)
