import timm
import torch
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from timm.layers import SwiGLUPacked
import openslide
import PIL.Image
import os
import argparse

DATA_PATH = "/data/tcga-brca"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def read_slide(img, coords = (0,0), dim=(512, 512), level=1):
    slide = openslide.open_slide(img)
    width, height = slide.dimensions
    image = slide.read_region(coords, level, dim)
    
    return image

def read_img(img):
    return PIL.Image.open(img)

def list_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def get_embedding(model, image):
    with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.float16):
        output = model(image)
    class_token = output[:, 0]
    patch_tokens = output[:, 5:]
    embedding = torch.cat([class_token, patch_tokens.mean(1)], dim=-1)
    embedding = embedding.to(torch.float16)
    return embedding

def find_most_similar_image(org_image, model, transforms, coords = (0,0), dim=(512, 512), level=1):
    org_image = transforms(org_image).unsqueeze(0).to(DEVICE)
    org_embedding = get_embedding(model, org_image)

    best_similarity = 0
    for f in list_all_files(DATA_PATH):
        if not f.endswith(".svs"):
            image = read_img(f)
        else:
            image = read_slide(f, coords, dim, level).convert("RGB")
        
        image = transforms(image).unsqueeze(0).to(DEVICE)
        embedding = get_embedding(model, image)
        similarity = torch.nn.functional.cosine_similarity(org_embedding, embedding)

        if similarity > best_similarity:
            best_similarity = similarity
            best_image = f

    return best_image, best_similarity

def save_image(image_path, output_path):
  if not best_image.endswith(".svs"):
    image = read_img(image_path)
  else:
    image = read_slide(best_image)
  image.save(output_path)
    

if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-i","--image", type=str, required=True)
  args = argparser.parse_args()

  model = timm.create_model("hf-hub:paige-ai/Virchow2", pretrained=True, mlp_layer=SwiGLUPacked, act_layer=torch.nn.SiLU)
  model = model.eval()
  model = model.to(DEVICE)

  transforms = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))
  org_image = read_slide(args.image, (2500, 12500), (512, 512), 1).convert("RGB")
  best_image, best_similarity = find_most_similar_image(org_image, model, transforms, (2500, 12500), (512, 512), 1)

  print(f"Best image: {best_image}, Similarity: {best_similarity}")
  save_image(best_image, os.path.join("/data/tmp/","most_similar_image_virchow.png"))

  
  



