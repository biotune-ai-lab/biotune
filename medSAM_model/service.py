from fastapi import FastAPI

from segment_image import load_and_segment

app = FastAPI()


@app.get("/")
def read_root():
    return "send a GET request to /process/{image_filename} to run inference on the image at $TEMP_directory/`image_filename`"


@app.get("/process/{image_filename}")
def process(image_filename: str):
    image_path = f"/data/tmp/{image_filename}"
    output_dir = "/data/tmp"
    output_path = load_and_segment(file_path=image_path, output_dir=output_dir)
    return {"output_path": output_path}
