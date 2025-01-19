import os
from pathlib import Path

import timm
import torch
from fastapi import FastAPI
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from timm.layers import SwiGLUPacked

from get_similar_image import find_most_similar_image, save_image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class Model:
    def __init__(self):
        model = timm.create_model(
            "hf-hub:paige-ai/Virchow2",
            pretrained=True,
            mlp_layer=SwiGLUPacked,
            act_layer=torch.nn.SiLU,
        )
        model = model.eval()
        self.model = model.to(DEVICE)

        self.transforms = create_transform(
            **resolve_data_config(model.pretrained_cfg, model=model)
        )

    def process(self, filename: str | Path, tmp_dir: str | Path = "/data/tmp") -> str:
        best_image, best_similarity = find_most_similar_image(
            filename, self.model, self.transforms
        )

        save_image(
            best_image, os.path.join("/data/tmp/", "most_similar_image_virchow.png")
        )

        response = f"Best image: {best_image}, Similarity: {best_similarity}"

        return response


model = Model()


app = FastAPI()


@app.get("/")
def read_root():
    return "send a GET request to /process/{image_filename} to run inference on the image at $TEMP_directory/`image_filename`"


@app.get("/process/{image_filename}")
def process(image_filename: str):
    image_path = f"/data/tmp/{image_filename}"
    return model.process(image_path)
