import requests
import zipfile
import os
import subprocess
from flask import Flask, send_from_directory

# Initialize Flask app
app = Flask(__name__)

# Function to download ROM from a URL
def download_rom(url, output_path):
    try:
        print(f"Downloading ROM from {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded ROM to {output_path}")
            return output_path
        else:
            print(f"Failed to download ROM. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading ROM: {e}")
        return None

# Function to extract ZIP file
def extract_payload(zip_path, extract_to):
    try:
        print(f"Extracting {zip_path} to {extract_to}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extracted to {extract_to}")
        return extract_to
    except Exception as e:
        print(f"Error extracting ZIP: {e}")
        return None

# Function to extract payload.bin using payload-dumper-go
def extract_payload_bin(payload_path, output_dir):
    try:
        print(f"Extracting payload.bin to {output_dir}...")
        subprocess.run(['./payload-dumper-go', '-o', output_dir, payload_path], check=True)
        print(f"Extracted images to {output_dir}")
        return output_dir
    except Exception as e:
        print(f"Error extracting payload.bin: {e}")
        return None

# Flask route to list extracted files
@app.route('/')
def list_files():
    images_dir = 'extracted_images'
    if not os.path.exists(images_dir):
        return "No images extracted yet. Run the script first."
    files = os.listdir(images_dir)
    links = ''.join(f'<li><a href="/download/{f}">{f}</a></li>' for f in files if f.endswith('.img'))
    return f'<h1>Extracted Images</h1><ul>{links}</ul>'

# Flask route to download a file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('extracted_images', filename)

# Main function to run the process
if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('extracted', exist_ok=True)
    os.makedirs('extracted_images', exist_ok=True)

    # Get ROM URL from user
    rom_url = input("Enter the ROM URL: ")
    rom_path = 'rom.zip'
    extract_dir = 'extracted'
    images_dir = 'extracted_images'

    # Download and extract
    if download_rom(rom_url, rom_path):
        if extract_payload(rom_path, extract_dir):
            # Check for payload.bin
            payload_path = os.path.join(extract_dir, 'payload.bin')
            if os.path.exists(payload_path):
                extract_payload_bin(payload_path, images_dir)
            else:
                print("No payload.bin found. Copying any .img files if present.")
                # Copy any .img files directly to images_dir
                for f in os.listdir(extract_dir):
                    if f.endswith('.img'):
                        os.rename(os.path.join(extract_dir, f), os.path.join(images_dir, f))
        else:
            print("Extraction failed. Check the ZIP file.")
    else:
        print("Download failed. Check the URL.")

    # Start the web server
    print("Starting web server at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)