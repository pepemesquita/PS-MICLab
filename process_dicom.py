import os
import warnings
import json
from numpy import ndarray
from torchxrayvision.utils import normalize
import pydicom
import torch
from torchvision import transforms

def read_xray_dcm(path: os.PathLike) -> ndarray:
    """Read a DICOM file and convert it to a numpy array.

    Args:
        path (PathLike): Path to the DICOM file.

    Returns:
        ndarray: 2D numpy array for the DICOM image scaled between -1024, 1024.
    """
    try:
        import pydicom
    except ImportError:
        raise Exception("Missing Package Pydicom. Try installing it by running `pip install pydicom`.")

    # Get the pixel array
    ds = pydicom.dcmread(path, force=True)

    # We have not tested RGB, YBR_FULL, or YBR_FULL_422 yet.
    if ds.PhotometricInterpretation not in ['MONOCHROME1', 'MONOCHROME2']:
        raise NotImplementedError(f'PhotometricInterpretation `{ds.PhotometricInterpretation}` is not yet supported.')

    data = ds.pixel_array
    
    # LUT for human friendly view
    data = pydicom.pixel_data_handlers.util.apply_voi_lut(data, ds, index=0)

    # `MONOCHROME1` have an inverted view; Bones are black; background is white
    if ds.PhotometricInterpretation == "MONOCHROME1":
        warnings.warn(f"Converting MONOCHROME1 to MONOCHROME2 interpretation for file: {path}. Can be avoided by setting `fix_monochrome=False`")
        data = data.max() - data

    # Normalize data to [-1024, 1024]
    data = normalize(data, data.max())
    return data

def classify_image(image: ndarray) -> dict:
    """Classify an image and return results as a dictionary.
    
    Args:
        image (ndarray): 2D numpy array for the DICOM image.
    
    Returns:
        dict: Classification results including predicted class and probabilities.
    """
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),  
        transforms.Grayscale(num_output_channels=3), 
        transforms.ToTensor(),  
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
    ])
    
    image_pil = transforms.ToPILImage()(image)
    image_tensor = transform(image_pil).unsqueeze(0) 

    with torch.no_grad():
        output = model(image_tensor)

    predicted_probabilities = torch.nn.functional.softmax(output, dim=1).numpy().flatten()
    predicted_class = predicted_probabilities.argmax()

    return {
        "predicted_class": int(predicted_class),
        "predicted_probabilities": predicted_probabilities.tolist()
    }

def classify_all_dicoms(directory: str) -> dict:
    """Classify all DICOM files in the given directory and return results as a dictionary.

    Args:
        directory (str): Path to the directory containing DICOM files.
    
    Returns:
        dict: Classification results with filenames as keys and results as values.
    """
    results = {}
    
    if not os.path.exists(directory):
        print(f"Diretório não encontrado: {directory}")
        return results
    
    print(f"Procurando arquivos DICOM em: {directory}")
    for root, dirs, files in os.walk(directory):
        print(f"Explorando diretório: {root}")
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_path = os.path.join(root, file)
                print(f"Classificando arquivo: {dicom_path}")
                try:
                    image = read_xray_dcm(dicom_path)
                    result = classify_image(image)
                    results[dicom_path] = result
                except Exception as e:
                    print(f"Erro ao processar {dicom_path}: {e}")
    
    return results

def save_results_to_json(results: dict, output_file: str):
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

# Diretório contendo os arquivos DICOM
DICOM_DIRECTORY = "data\dicoms"

# Caminho para o arquivo JSON de saída
OUTPUT_JSON_FILE = "classification_results.json"

print("Iniciando a classificação dos arquivos DICOM...")
results = classify_all_dicoms(DICOM_DIRECTORY)
save_results_to_json(results, OUTPUT_JSON_FILE)
print(f"Resultados salvos em: {OUTPUT_JSON_FILE}")