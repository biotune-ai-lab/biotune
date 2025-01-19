from fastapi import FastAPI

from classify_cancer import get_cancer_subtype

app = FastAPI()


@app.get("/")
def read_root():
    return "send a GET request to /process/{image_filename} to get the CONCH classification of the image at $TEMP_directory/`image_filename`"


@app.get("/process/{image_filename}")
def process(image_filename: str):
    image_path = f"/data/tmp/{image_filename}"
    return get_cancer_subtype(image_path)
