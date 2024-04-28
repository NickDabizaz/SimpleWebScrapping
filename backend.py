from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Import Flask CORS
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import re
import os

app = Flask(__name__)
CORS(app)  # Inisialisasi CORS pada aplikasi Flask

@app.route('/')
def index():
    # Mengirim file HTML ke browser
    return send_file('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    # Mendapatkan teks dari request POST
    text = request.json.get('text', '')

    # Melakukan operasi apa pun yang diperlukan pada teks di sini
    # Misalnya, mencetak teks di console
    print("Input teks:", text)

    url = "https://google-web-search1.p.rapidapi.com/"

    querystring = {"query":text,"limit":"20","related_keywords":"true"}

    headers = {
        "X-RapidAPI-Key": "a6d0ab3eddmshf9579f65231d358p1c78c3jsn90f68c469338",
        "X-RapidAPI-Host": "google-web-search1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())
    urls = []
    titles = []
    for result in response.json()['results']:
        urls.append(result['url'])
        titles.append(result['title'])

    for i, url in enumerate(urls):
        # Setel header permintaan
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Mengirim permintaan GET ke URL dengan header
        response = requests.get(url, headers=headers)

        # Memeriksa apakah permintaan berhasil
        if response.status_code == 200:
            # Parsing halaman HTML menggunakan BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Mengumpulkan semua teks dari halaman
            all_text = soup.get_text()
            
            # Menghapus karakter non-ASCII dari teks
            all_text_clean = re.sub(r'[^\x00-\x7F]+', '', all_text)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(200, 10, all_text_clean)
            
            # Membersihkan judul dari karakter yang tidak valid untuk nama file sistem
            cleaned_title = re.sub(r'[\\/*?:"<>|]', '', titles[i])
            
            # Membuat nama file PDF yang valid
            filename = cleaned_title + ".pdf"
            
            # Simpan file PDF di folder 'pdf_files'
            pdf_output_path = os.path.join('pdf_files', filename)
            pdf.output(pdf_output_path)
            
            print("File PDF berhasil dibuat:", pdf_output_path)
            
    # Mengirimkan respons ke frontend
    return jsonify({'message': 'Proses Web Scrapping Telah Selesai'})

if __name__ == '__main__':
    # Pastikan folder 'pdf_files' ada sebelum menjalankan aplikasi Flask
    os.makedirs('pdf_files', exist_ok=True)
    app.run(debug=True)
