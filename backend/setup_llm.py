import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoConfig

def setup_llm(model_id="meta-llama/Llama-3.2-1B-Instruct", torch_dtype=torch.bfloat16, device_map="auto"):
    print("Ensure you have logged into huggingface-cli (with a token) before accessing gated models.")

        # Test access to the model
    print("Checking access to the model...")
    try:
        config = AutoConfig.from_pretrained(model_id)
        print(f"Successfully accessed model configuration for {model_id}")
    except Exception as e:
        print(f"Error accessing model configuration for {model_id}: {e}")
        return None

    # Download the model and tokenizer
    print("Downloading model and tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch_dtype, device_map=device_map)
    except Exception as e:
        print(f"Error downloading model or tokenizer: {e}")
        return None

    # Initialize pipeline
    print("Initializing text-generation pipeline...")
    try:
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            pad_token_id=tokenizer.pad_token_id,
            torch_dtype=torch_dtype,
            device_map=device_map,
            #pad_token_id=tokenizer.eos_token_id  # Explicitly set pad_token_id
        )
        print("Setup complete. The pipeline is ready to use!")
        return pipe
    except Exception as e:
        print(f"Error initializing text-generation pipeline: {e}")
        return None