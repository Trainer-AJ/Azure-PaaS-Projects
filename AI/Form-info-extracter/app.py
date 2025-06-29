import os
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
import pyodbc
import traceback

# Load environment variables
load_dotenv()
form_endpoint = os.getenv('FORM_ENDPOINT', '').strip('"\'')
form_key = os.getenv('FORM_KEY', '').strip('"\'')
model_id = os.getenv('MODEL_ID', '').strip('"\'')

app = Flask(__name__)

HTML_FORM = '''
<!doctype html>
<title>Custom Form Recognizer</title>
<h2>Upload a JPG Form</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=formfile accept="image/jpeg">
  <input type=submit value=Upload>
</form>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
{% if results %}
  <h3>Extracted Information:</h3>
  <ul>
  {% for field in results %}
    <li>{{ field }}</li>
  {% endfor %}
  </ul>
{% endif %}
'''

def save_to_mssql(form_type, fields):
    print(f"save_to_mssql called with form_type={form_type}, fields={fields}")
    server = os.getenv('SQL_SERVER', '').strip('"\'')
    database = os.getenv('SQL_DATABASE', '').strip('"\'')
    username = os.getenv('SQL_USER', '').strip('"\'')
    password = os.getenv('SQL_PASSWORD', '').strip('"\'')
    if not all([server, database, username, password]):
        print("Missing SQL credentials.")
        return
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    try:
        print(f"Connecting to DB with: {conn_str}")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        if not fields:
            print("No fields to insert!")
        for name, field in fields.items():
            print(f"Inserting: {form_type}, {name}, {field.label_data.text if field.label_data else name}, {field.value}, {field.confidence}")
            cursor.execute('''
                INSERT INTO ExtractedFields (form_type, field_name, field_label, field_value, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', form_type, name, field.label_data.text if field.label_data else name, str(field.value), field.confidence)
        cursor.close()
        conn.close()
        print("DB insert complete.")
    except Exception as e:
        print(f"DB error: {e}")
        traceback.print_exc()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    error = None
    results = None
    if not model_id:
        error = "MODEL_ID is not set. Please check your environment variables!"
        return render_template_string(HTML_FORM, error=error, results=results)
    if request.method == 'POST':
        file = request.files.get('formfile')
        if not file or file.filename == '':
            error = 'No file selected! Please upload a JPG image.'
        elif not file.filename.lower().endswith('.jpg'):
            error = 'Only JPG images are supported! Try again with a .jpg file.'
        else:
            try:
                form_recognizer_client = FormRecognizerClient(form_endpoint, AzureKeyCredential(form_key))
                poller = form_recognizer_client.begin_recognize_custom_forms(
                    model_id=model_id, form=file
                )
                result = poller.result()
                results = []
                for recognized_form in result:
                    results.append(f"Form type: {recognized_form.form_type}")
                    save_to_mssql(recognized_form.form_type, recognized_form.fields)
                    for name, field in recognized_form.fields.items():
                        results.append(f"Field '{name}' (label: '{field.label_data.text if field.label_data else name}') "
                                       f"= '{field.value}' (confidence: {field.confidence})")
                if not results:
                    error = "Oops! I couldn't find any information in your form. Try another image? 🦄"
            except Exception as ex:
                error = f"Yikes! Something went wrong: {str(ex)} 😅 Try a different image or check your model!"
    return render_template_string(HTML_FORM, error=error, results=results)

if __name__ == '__main__':
    app.run(debug=True)
