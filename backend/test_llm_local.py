from backend.setup_llm import setup_llm

# Step 1: Load the LLM pipeline
print("Initializing the LLM pipeline...")
llm_pipeline = setup_llm()

if not llm_pipeline:
    print("Failed to initialize the pipeline. Exiting.")
else:
    print("Pipeline initialized. Ready for input!")

    # Step 2: Initialize conversation history
    conversation_history = [
        {"role": "system", "content": "You are a pirate chatbot. Respond in pirate speak in 50 words or less. Make controversial statements."},
    ]
    
    # Step 3: Accept new inputs dynamically
    while True:
        input_text = input("Enter your text (or type 'exit' to quit): ")
        if input_text.lower() == "exit":
            print("Exiting...")
            break

        # Append the user's input to the conversation history
        conversation_history.append({"role": "user", "content": input_text})

        # Generate a reply
        try:
            response = llm_pipeline(
                conversation_history, 
                truncation=True, # Works like max_length, in this case prevents exceeding the max context window of the model - this is good for robustness
                num_return_sequences=1, # Sets the number of responses e.g. top 1 responses, top 3, etc. In the case of a chatbot, we only need 1
                # Set do_sample=False if you want deterministic, predictable outputs (e.g., summarization or single-answer tasks).
                # Set do_sample=True if you want creative, diverse responses (e.g., storytelling, open-ended chat) - the model then samples tokens from a PD curve rather than taking the most likely responses
                do_sample=True,
                top_p=0.9, # Assigns probability distribution to token selection i.e. scales the creativity of the response by selecting more tokens on the PD curve - works in tandem with do_sample=True, the lower the figure only the deterministic tokens are selected, and the higher the figure more creative tokens are selected as well (between the range 0<n<=1)
                temperature=1.0, # Higher the value, more it smooths the PD curve i.e. increases chances for more creative tokens to be selected 
                max_new_tokens=256,
            )
            
            # Extract and print the generated response
            reply = response[0]['generated_text']
            print("Generated Reply:", reply)

            # Add the assistant's reply to the conversation history
            conversation_history.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"Error during text generation: {e}")