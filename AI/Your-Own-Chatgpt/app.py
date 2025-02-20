import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI

app = Flask(__name__)

# Load environment variables
load_dotenv()
azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
azure_oai_key = os.getenv("AZURE_OAI_KEY")
azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=azure_oai_endpoint,
    api_key=azure_oai_key,
    api_version="2024-02-15-preview"
)

# Create a system message
system_message = """I am a cloud enthusiast named Sky who helps people learn about cloud computing, with a focus on Azure Cloud services. 
        If no specific topic is mentioned, I will default to discussing Azure's core offerings and best practices. 
        I can provide explanations about Azure services, deployment strategies, pricing models, and tips for optimizing cloud performance. 
        Feel free to ask me any questions related to Azure Cloud, and I'll provide clear and informative answers to enhance your cloud journey.
        """

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    input_text = request.json.get('prompt')
    
    try:
        response = client.chat.completions.create(
            model=azure_oai_deployment,
            temperature=0.7,
            max_tokens=400,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": input_text}
            ]
        )
        generated_text = response.choices[0].message.content
        return jsonify({"response": generated_text})

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80',debug=True)
