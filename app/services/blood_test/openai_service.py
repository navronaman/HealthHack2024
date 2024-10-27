import openai
from config import Config

openai.api_key = Config.OPENAI_API_KEY

def analyze_text_with_openai(text):
    with open(r"app\templates\blood_test\blood_test_prompt.txt", "r") as prompt_file:
        prompt_template = prompt_file.read()
    
    full_prompt = prompt_template.format(text=text)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        result = response['choices'][0]['message']['content']
        return result
    except Exception as e:
        print("Error with OpenAI API:", e)
        return None

if __name__ == "__main__":
    test_text = """The patient's blood test results are as follows:
    1. Hemoglobin: 12.5 g/dL
    2. White Blood Cells: 8.2 x10^3/uL
    3. Platelets: 150 x10^3/uL
    - Hemoglobin levels are within normal range.
    - White blood cell count is slightly elevated.
    - Platelet count is normal."""
    
    result = analyze_text_with_openai(test_text)
    print(result)