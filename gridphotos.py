import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import streamlit as st
import zipfile

# Konfigurasi halaman Streamlit
st.set_page_config("Sukses Jaya - Create Photos")

# Load database
database = pd.read_json("Database.json")

# Upload file Excel pengguna
file_upload = st.file_uploader("Upload File")
if file_upload:
    file_user = pd.read_excel(file_upload)
else:
    st.warning("Please upload your Excel file.")
    st.stop()

# Dropdown untuk memilih harga
selectprice = st.selectbox(
    "Select", options=['Harga Under', 'HargaJualLusin', 'HargaJualKoli', 'HargaJualSpecial']
)

# Filter data berdasarkan ItemCode di file pengguna
selected_df = database[database['ItemCode'].isin(file_user['ItemCode'])]

st.dataframe(selected_df)

# Load font
font_path = "./Poppins-Medium.ttf"
font = ImageFont.truetype(font_path, size=25)

# Fungsi membungkus teks agar pas dengan lebar tertentu
def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)  # Menggunakan getbbox() untuk mendapatkan ukuran
        width = bbox[2] - bbox[0]  # Ambil lebar dari bounding box

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

# Fungsi untuk menambahkan gambar ke template (landscape)
def add_image(img_url, row):
    colour = "white" if selectprice == 'Harga Under' else "orange" if selectprice == 'HargaJualLusin' else "yellow" if selectprice == 'HargaJualKoli' else "green"
    height = 600  # Menurunkan tinggi untuk layout landscape
    width = 1200  # Lebar lebih besar untuk landscape
    template = Image.new("RGB", (width, height), colour)

    draw = ImageDraw.Draw(template)
    draw.rectangle([0, 0, template.width // 2, template.height], fill="white")  # Bagian kanan untuk teks
    
    try:
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img = img.resize((600, 600))  # Sesuaikan ukuran gambar
        
        # Paste gambar di kiri
        template.paste(img, (0, 0))
    except Exception as e:
        st.error(f"Error loading image: {e}")

    return template

# Fungsi untuk menambahkan teks ke gambar (di kanan)
def add_text(template, draw, row, font, selectprice):
    item_code = row['ItemCode']
    item_name = row['ItemName']
    harga_jual = f"Rp. {row[selectprice]:,} / {row['InventoryUoM']}"
    ctn = f"Isi Karton: {int(row['IsiCtn'])} {row['InventoryUoM']}" if pd.notna(row['IsiCtn']) else "N/A"
    text_x = 620  # Mulai teks di sisi kanan gambar
    text_y = 50   # Start posisi teks di atas

    lines_item_code = wrap_text(f"{item_code}", font, template.width // 2 - 40)
    lines_item_name = wrap_text(f"{item_name}", font, template.width // 2 - 40)
    lines_harga_jual = wrap_text(harga_jual, font, template.width // 2 - 40)
    lines_ctn = wrap_text(ctn, font, template.width // 2 - 40)

    y_offset = text_y
    for line in lines_item_code + lines_item_name + lines_harga_jual + lines_ctn:
        draw.text((text_x, y_offset), line, font=font, fill="black")
        y_offset += 40

# Dictionary untuk mengelompokkan gambar berdasarkan kategori
category_dict = {}
image_paths = []
# Iterasi untuk setiap baris pada selected_df
for index, row in selected_df.iterrows():
    img_template = add_image(row['Link'], row)
    draw = ImageDraw.Draw(img_template)
    add_text(img_template, draw, row, font, selectprice)

    buf = BytesIO()
    img_template.save(buf, format="JPEG")
    buf.seek(0)
    
    file_name = f"{row['ItemCode']}.jpg"
    image_paths.append((file_name, buf.getvalue()))
    category = row['Kategori']

    # Tambahkan gambar ke kategori yang sesuai
    if category not in category_dict:
        category_dict[category] = []
    category_dict[category].append((file_name, buf.getvalue()))
    st.image(buf)

if image_paths:
    st.image(image_paths[0][1], use_column_width=True)

# Membuat ZIP file dengan struktur folder berdasarkan kategori
zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zipf:
    for category, files in category_dict.items():
        for file_name, image_data in files:
            file_path = f"{category}/{file_name}"  # Menyimpan gambar dalam folder kategori
            zipf.writestr(file_path, image_data)

zip_buffer.seek(0)

# Tombol download ZIP
st.download_button(
    label="Download ZIP",
    data=zip_buffer,
    file_name="Ready_to_Upload.zip",
    mime="application/zip"
)
