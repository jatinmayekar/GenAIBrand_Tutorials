import google.generativeai as genai
import pandas as pd
from collections import defaultdict
import time
import os
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

# Setup Google API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # Make sure to set your API key
genai.configure(api_key=GOOGLE_API_KEY)

def generate_responses(prompt: str, num_samples: int = 3) -> Dict[str, List[str]]:
    """
    Generate multiple responses for different parameter combinations and compare them.
    """
    # Test configurations
    configs = [
        {"temp": 0.0, "top_k": 1, "top_p": 1.0},    # Most deterministic
        {"temp": 0.0, "top_k": 40, "top_p": 0.95},  # Similar to default
        {"temp": 0.7, "top_k": 40, "top_p": 0.95},  # More random
        {"temp": 1.0, "top_k": 1000, "top_p": 1.0}  # Most random
    ]
    
    results = defaultdict(list)
    
    for config in configs:
        # Create model instance with specific configuration
        model = genai.GenerativeModel(
            'gemini-1.5-flash-001',
            generation_config=genai.GenerationConfig(
                temperature=config["temp"],
                top_k=config["top_k"],
                top_p=config["top_p"]
            )
        )
        
        print(f"\nTesting configuration: Temperature={config['temp']}, "
              f"Top-k={config['top_k']}, Top-p={config['top_p']}")
        
        # Generate multiple samples for this configuration
        for i in range(num_samples):
            try:
                response = model.generate_content(prompt)
                output = response.text.strip()
                config_key = f"temp={config['temp']}_topk={config['top_k']}_topp={config['top_p']}"
                results[config_key].append(output)
                print(f"Sample {i+1}: {output[:100]}...")  # Print first 100 chars
                time.sleep(1)  # Avoid rate limiting
                
            except Exception as e:
                print(f"Error generating response: {str(e)}")
                continue
    
    return results

def analyze_outputs(results: Dict[str, List[str]]):
    """
    Analyze the uniqueness of outputs for each configuration.
    """
    analysis = []
    
    for config_key, outputs in results.items():
        unique_outputs = len(set(outputs))
        params = dict(param.split('=') for param in config_key.split('_'))
        
        analysis.append({
            'Configuration': config_key,
            'Temperature': params['temp'],
            'Top_k': params['topk'],
            'Top_p': params['topp'],
            'Total_Samples': len(outputs),
            'Unique_Outputs': unique_outputs,
            'Is_Deterministic': unique_outputs == 1,
            'Outputs': outputs
        })
    
    return pd.DataFrame(analysis)

# Test the script
prompt = "Write a one-sentence story about a cat who goes on an adventure."

print("Generating responses with different parameter combinations...")
results = generate_responses(prompt, num_samples=3)

print("\nAnalyzing results...")
analysis_df = analyze_outputs(results)

# Display results
print("\nAnalysis Results:")
print(analysis_df[['Configuration', 'Total_Samples', 'Unique_Outputs', 'Is_Deterministic']])

# Show actual outputs for comparison
print("\nDetailed Output Comparison:")
for config, outputs in results.items():
    print(f"\nConfiguration: {config}")
    for i, output in enumerate(outputs, 1):
        print(f"Sample {i}: {output}")