from utils.conch_utils import get_model, get_image_embedding, get_text_embedding, get_similarity_score
import json
import numpy as np
import argparse 
import os

def generate_combinations(cancer_data="conch_model/data/TCGA-A7-A0DB-01Z-00-DX2.6C6A5F9C-294F-4A86-A0F1-B68D4729B535.svs"):
    descriptions = []
    
    for cancer in cancer_data["cancers"]:
        organ = cancer["organ"]
        
        # Loop through each cancer type
        for cancer_type in cancer["types"]:
            type_name = cancer_type["type"]
            # If there are subtypes, generate combinations
            if "subtypes" in cancer_type:
                for subtype in cancer_type["subtypes"]:
                    description = f"An H&E image of invasive {type_name.lower()} cancer in {organ.lower()}, subtype {subtype}."
                    descriptions.append(description)
    
    return descriptions

def get_cancer_subtype(image_path):
    with open('params/cancer.json', 'r') as file:
        cancer_data = json.load(file)
    
    prompts = generate_combinations(cancer_data)
    prompts += ["The image does not contain cancer.", "Other"]

    model, preprocess = get_model()
    
    image_embeddings = get_image_embedding(model, preprocess, image_path, (2500, 12500), (512, 512), 1)
    text_embeddings = get_text_embedding(model, prompts)
    print(image_embeddings.shape, text_embeddings.shape)
    sim_scores = get_similarity_score(model,image_embeddings, text_embeddings)
    print(sim_scores.shape)

    # Print prompts in order of probability
    sorted_indices = np.argsort(sim_scores)[::-1]
    preds = "\n".join([f"{prompts[idx]} with probability: {sim_scores[idx]}" for i, idx in enumerate(sorted_indices) if i<3])
    return preds

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--image_path", type=str, required=True)
    args = argparser.parse_args()

    print(get_cancer_subtype(args.image_path))