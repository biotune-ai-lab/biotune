from conch.open_clip_custom import create_model_from_pretrained
from conch.open_clip_custom import tokenize, get_tokenizer
from conch.downstream.zeroshot_path import zero_shot_classifier, run_mizero, run_zeroshot
import torch
from .data import read_slide, read_img
from dotenv import load_dotenv
import os

load_dotenv()

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
TOKEN = os.getenv('TOKEN')
def get_model():
    model, preprocess = create_model_from_pretrained('conch_ViT-B-16', "hf_hub:MahmoodLab/conch", hf_auth_token=TOKEN)
    model.eval()
    model.to(DEVICE)
    return model, preprocess


def get_image_embedding(model, preprocess, image_path, coords, dim, level):

    if image_path.endswith('.svs'):
        image = read_slide(image_path, coords, dim, level)
    else:
        image = read_img(image_path)
    image = preprocess(image).unsqueeze(0).to(DEVICE)

    with torch.inference_mode():
        image_embedings = model.encode_image(image)
    return image_embedings

def get_text_embedding(model, prompts):
    tokenizer = get_tokenizer()
    tokenized_prompts = tokenize(texts=prompts, tokenizer=tokenizer).to(DEVICE)

    with torch.inference_mode():
        text_embedings = model.encode_text(tokenized_prompts)
    return text_embedings

def get_similarity_score(model, image_embedings, text_embedings):
    with torch.inference_mode():
        sim_scores = (image_embedings @ text_embedings.T * model.logit_scale.exp()).softmax(dim=-1).cpu().numpy().squeeze()
    return sim_scores

