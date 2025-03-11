import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class TinyLlamaInference:
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.device = "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(self.device)

    def generate_response(self, prompt, max_length=256):
        chat_prompt = f"### Instruction:\n{prompt}\n\n### Response:"
        
        inputs = self.tokenizer(chat_prompt, return_tensors="pt").to(self.device)
        output = self.model.generate(
            **inputs, 
            max_length=max_length, 
            do_sample=True,  # Greedy decoding
            temperature=0.7,  
            top_p=1.0,  
            eos_token_id=self.tokenizer.eos_token_id  
        )
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

# Test it
tiny_llama = TinyLlamaInference()
response = tiny_llama.generate_response("What is the capital of France?")
print(response)
 