import os
import google.generativeai as genai
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Configure API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def test_parameters_and_save(prompts, output_file):
    """Test different parameter combinations and save results to CSV"""
    
    # Test configurations
    configs = [
        {"temp": 0.0, "top_k": 1, "top_p": 0.1},    # Most restrictive
        {"temp": 0.0, "top_k": 1, "top_p": 1.0},    # Original deterministic
        {"temp": 0.1, "top_k": 1, "top_p": 0.1},    # Slightly random
        {"temp": 0.0, "top_k": 40, "top_p": 0.1},   # Higher top_k
    ]
    
    # Prepare CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Timestamp',
            'Prompt',
            'Temperature',
            'Top_k',
            'Top_p',
            'Sample_Number',
            'Output',
            'Is_Deterministic',
            'Output_Length'
        ])
        
        for prompt in prompts:
            print(f"\n\nTesting prompt: {prompt}\n")
            
            for config in configs:
                print(f"\nConfiguration:")
                print(f"Temperature: {config['temp']}")
                print(f"Top-k: {config['top_k']}")
                print(f"Top-p: {config['top_p']}")
                print("-" * 50)
                
                model = genai.GenerativeModel(
                    'gemini-1.5-flash-001',
                    generation_config=genai.GenerationConfig(
                        temperature=config['temp'],
                        top_k=config['top_k'],
                        top_p=config['top_p']
                    )
                )
                
                # Generate 3 samples
                outputs = []
                for i in range(3):
                    try:
                        response = model.generate_content(prompt)
                        output = response.text.strip()
                        outputs.append(output)
                        print(f"\nSample {i+1}:")
                        print(output)
                        
                        # Save to CSV
                        writer.writerow([
                            datetime.now().isoformat(),
                            prompt,
                            config['temp'],
                            config['top_k'],
                            config['top_p'],
                            i+1,
                            output,
                            len(set(outputs)) == 1 if len(outputs) == 3 else "N/A",
                            len(output)
                        ])
                        
                        time.sleep(6)
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        writer.writerow([
                            datetime.now().isoformat(),
                            prompt,
                            config['temp'],
                            config['top_k'],
                            config['top_p'],
                            i+1,
                            f"ERROR: {str(e)}",
                            "N/A",
                            0
                        ])
                
                is_deterministic = len(set(outputs)) == 1
                print(f"\nDeterministic: {is_deterministic}")

def analyze_results(csv_file):
    """Analyze the results from the CSV file"""
    import pandas as pd
    
    df = pd.read_csv(csv_file)
    
    # Calculate statistics
    analysis = df.groupby(['Prompt', 'Temperature', 'Top_k', 'Top_p']).agg({
        'Is_Deterministic': 'first',
        'Output_Length': ['mean', 'std'],
    }).round(2)
    
    # Save analysis
    analysis_file = csv_file.replace('.csv', '_analysis.csv')
    analysis.to_csv(analysis_file)
    print(f"\nAnalysis saved to {analysis_file}")
    return analysis

if __name__ == "__main__":
    # Test prompts
    prompts = [
        "Write a one-sentence story about a cat who goes on an adventure.",
        "What is 2+2? Explain in one sentence.",
        "Generate a creative name for a new technology startup.",
        "Write a haiku about the moon."
    ]
    
    # Output filename with timestamp
    output_file = f'llm_parameter_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    print("Starting parameter test...")
    test_parameters_and_save(prompts, output_file)
    
    print("\nAnalyzing results...")
    analysis = analyze_results(output_file)
    print("\nAnalysis Summary:")
    print(analysis)