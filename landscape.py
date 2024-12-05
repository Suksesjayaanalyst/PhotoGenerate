import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import streamlit as st
import textwrap
import zipfile

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
    "Select", options=['Harga Under', 'HargaJualLusin', 'HargaJualSpecial']
)

# Filter data berdasarkan ItemCode di file pengguna
selected_df = database[database['ItemCode'].isin(file_user['ItemCode'])]

st.dataframe(selected_df)

start = st.button("Start 1")

start2 = st.button("Start 2")

if start:
    
    font_path = "./Poppins-Regular.ttf"
    font_harga = ImageFont.truetype("./Poppins-SemiBold.ttf", size =26)
    font = ImageFont.truetype(font_path, size=26)
    font_harga = ImageFont.truetype("./Poppins-SemiBold.ttf", size =26)

    # Fungsi membungkus teks agar pas dengan lebar tertentu
    def wrap_text(text, font, max_width):
        # Pembungkusan teks menggunakan textwrap
        wrapped_text = textwrap.fill(text, width=max_width // (font.getbbox('a')[2] - font.getbbox('a')[0]))  # Perhitungan dengan ukuran karakter 'a'

        return wrapped_text.splitlines()

    def add_image(img_url, row):
        if selectprice == 'Harga Under':
            colour = (255, 255, 255)  # Putih
        elif selectprice == 'HargaJualLusin':
            colour = (250, 225, 135)  # Oranye
        elif selectprice == 'HargaJualSpecial':
            colour = (181,220,249)  # Hijau

        template = Image.new("RGBA", (1200, 800), colour)  # Menambahkan warna RGB pada background
        try:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img = img.resize((600, 600))
            image_y = (template.height - img.height) // 2
            template.paste(img, (20, image_y))
            if row['Kategori'] == 'AKSESORIS RAMBUT KAMINO':
                logo = "./logo-kamino-for-web-new.png"
                logo = Image.open(logo).convert("RGBA") 
                logo = logo.resize((300, 150))
                # Resize logo sesuai ukuran
                logo_x = (template.width - logo.width) // 2 + 300  # Posisikan logo di tengah
                template.paste(logo, (logo_x, 50), logo) 
            elif row['Kategori'] == 'LOLI & MOLI':
                logo = "./Lolimoli Logo-02.png"
                logo = Image.open(logo).convert("RGBA") 
                logo = logo.resize((200, 100))
                # Resize logo sesuai ukuran
                logo_x = (template.width - logo.width) // 2 + 300  # Posisikan logo di tengah
                template.paste(logo, (logo_x, 50), logo) 

            

        except Exception as e:
            st.error(f"Error loading image: {e}")

        return template


    def add_text(template, draw, row, font, selectprice):
        item_code = row['ItemCode']
        item_name = row['ItemName']
        harga_jual = f"Rp. {row[selectprice]:,} / {row['InventoryUoM']}"
        ctn = f"Isi Karton: {int(row['IsiCtn'])} {row['InventoryUoM']}" if pd.notna(row['IsiCtn']) else "N/A"

        # Wrap each line of text
        lines_item_code = wrap_text(f"{item_code}", font, max_width=450)  # Max width tetap
        lines_item_name = wrap_text(f"{item_name}", font, max_width=450)  # Max width tetap
        lines_harga_jual = wrap_text(harga_jual, font_harga, max_width=450)  # Max width tetap
        lines_ctn = wrap_text(ctn, font, max_width=450)  # Max width tetap
        
        # Menentukan lebar latar belakang tetap (300 piksel)
        background_width = 400
        background_margin = 20  # Jarak margin sekitar teks
        corner_radius = 15  # Radius untuk rounded rectangle
        x_position = 700  # Posisi X tetap untuk semua teks
        y_start = 200  # Posisi Y awal

        # Helper untuk menggambar teks dengan background
        def draw_text_with_background(lines, y_offset):
            for line in lines:

                if line in lines_harga_jual:
                    font = font_harga
                if line in lines_ctn:
                    font = current_font
                # Hitung ukuran teks
                text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:4]  # Menggunakan getbbox() untuk mendapatkan ukuran


                # Menggambar kotak dengan rounded corners, lebar tetap dan margin tetap
                rect_coords = [
                    (x_position - background_margin, y_offset),
                    (x_position + background_width + background_margin, y_offset + text_height + 2 * background_margin),
                ]
                
                # Gambar background (kotak dengan sudut membulat)
                draw.rounded_rectangle(
                    rect_coords,
                    fill=(242,242,242,255),  # Warna latar belakang
                    radius=corner_radius,  # Radius sudut
                )
                
                # Pusatkan teks secara horizontal dalam kotak
                text_x = x_position + (background_width - text_width) // 2  # Pusatkan horizontal di dalam background
                text_y = y_offset + background_margin  # Menjaga margin atas yang konsisten

                # Gambar teks pada posisi yang sudah dihitung
                draw.text((text_x, text_y), line, font=font, fill="black")

                # Perbarui posisi Y untuk baris berikutnya, tambahkan lebih banyak jarak antara baris
                y_offset += text_height + 2 * background_margin  # Menambah jarak lebih besar antar baris
            return y_offset  # Mengembalikan posisi Y terakhir



        # Gambar item_code
        y_offset = draw_text_with_background(lines_item_code, y_start)

        # Gambar item_name tepat di bawah item_code
        y_offset += 10  # Tambahkan jarak antar blok
        y_offset = draw_text_with_background(lines_item_name, y_offset)

        # Gambar harga_jual tepat di bawah item_name
        y_offset += 10  # Tambahkan jarak antar blok
        y_offset = draw_text_with_background(lines_harga_jual, y_offset)

        # Gambar ctn tepat di bawah harga_jual
        y_offset += 10  # Tambahkan jarak antar blok
        draw_text_with_background(lines_ctn, y_offset)


    category_dict = {}
    image_paths = []

    for index, row in selected_df.iterrows():
        img_template = add_image(row['Link'], row)
        draw = ImageDraw.Draw(img_template)
        add_text(img_template, draw, row, font, selectprice)

        buf = BytesIO()
        img_template.save(buf, format='PNG')

        buf.seek(0)
        file_name = f"{row['ItemCode']}.jpg"
        image_paths.append((file_name, buf.getvalue()))
        category = row['Kategori']
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append((file_name, buf.getvalue()))

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
    



if start2:
    font_path = "./Poppins-Regular.ttf"
    font_harga = ImageFont.truetype("./Poppins-SemiBold.ttf", size =20)
    current_font = ImageFont.truetype(font_path, size=20)
    font = ImageFont.truetype(font_path, size=20)
    if selectprice == 'Harga Under':
            colour = (242, 242, 242)  # Putih
    elif selectprice == 'HargaJualLusin':
        colour = (250, 225, 135)  # Oranye
    elif selectprice == 'HargaJualSpecial':
        colour = (154,210,172)  # Hijau

    def wrap_text(text, font, max_width):
        # Pembungkusan teks menggunakan textwrap
        wrapped_text = textwrap.fill(text, width=max_width // (font.getbbox('a')[2] - font.getbbox('a')[0]))  # Perhitungan dengan ukuran karakter 'a'

        return wrapped_text.splitlines()

    
    def add_image(img_url, row):
        

        template = Image.new("RGBA", (800, 1200), "white")  # Menambahkan warna RGB pada background


        try:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img = img.resize ((750,750))
            image_x = (template.width - img.width) // 2
            image_y = 25
            if row['Kategori'] == 'AKSESORIS RAMBUT KAMINO':
                image_y = 100
                logo = "./logo-kamino-for-web-new.png"
                logo = Image.open(logo).convert("RGBA") 
                logo = logo.resize((200, 100))
                logo_x = (template.width - logo.width) // 2
                template.paste(logo,(logo_x, 0), logo)

            if row['Kategori'] == 'LOLI & MOLI':
                image_y = 100
                logo = "./Lolimoli Logo-02.png"
                logo = Image.open(logo).convert("RGBA") 
                logo = logo.resize((150, 75))
                logo_x = (template.width - logo.width) // 2
                template.paste(logo,(logo_x, 15), logo)
            template.paste(img, (image_x, image_y))

        except Exception as e:
            st.error(f"Error loadingimage: {e}")

        return template
    
    def add_text(template, draw, row, font, selectprice):
        item_code = row['ItemCode']
        item_name = row['ItemName']
        harga_jual = f"Rp. {row[selectprice]:,} / {row['InventoryUoM']}"
        ctn = f"Isi Karton: {int(row['IsiCtn'])} {row['InventoryUoM']}" if pd.notna(row['IsiCtn']) else "N/A"

        # Wrap each line of text
        lines_item_code = wrap_text(f"{item_code}", font, max_width=450)
        lines_item_name = wrap_text(f"{item_name}", font, max_width=450)
        lines_harga_jual = wrap_text(harga_jual, font, max_width=450)
        lines_ctn = wrap_text(ctn, font, max_width=450)

        # Gabungkan semua teks untuk menghitung tinggi total
        all_lines = lines_item_code + lines_item_name + lines_harga_jual + lines_ctn

        

        # Konfigurasi latar belakang
        background_width = 735
        background_margin = 10  # Margin sekitar teks
        corner_radius = 15  # Radius untuk rounded rectangle
        x_position = 32.5  # Posisi X tetap
        y_start = 825  # Posisi Y awal
        if row['Kategori'] in (['AKSESORIS RAMBUT KAMINO', 'LOLI & MOLI']):
            y_start = 900

        # Hitung tinggi total teks dan latar belakang
        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in all_lines)
        total_height = total_text_height + (len(all_lines) + 1) * 2 * background_margin  # Tambahkan margin antar baris

        # Gambar latar belakang
        rect_coords = [
            (x_position - background_margin, y_start),
            (x_position + background_width + background_margin, y_start + total_height),
        ]
        draw.rounded_rectangle(
            rect_coords,
            fill=colour,  # Warna latar belakang
            radius=corner_radius,  # Radius sudut
        )

        # Gambar semua teks di atas latar belakang
        y_offset = y_start + background_margin
        for line in all_lines:
            if line in lines_item_code:
                font = font_harga
            elif line in lines_item_name:
                font = current_font
            elif line in lines_harga_jual:
                font = font_harga
            elif line in lines_ctn:
                font = current_font
                
            text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:4]

            # Pusatkan teks secara horizontal dalam latar belakang
            text_x = x_position + (background_width - text_width) // 2
            draw.text((text_x, y_offset), line, font=font, fill="black")

            # Perbarui posisi Y untuk baris berikutnya
            y_offset += text_height + 2 * background_margin



    category_dict = {}
    image_paths = []

    for index, row in selected_df.iterrows():
        img_template = add_image(row['Link'], row)
        draw = ImageDraw.Draw(img_template)
        add_text(img_template, draw, row, font, selectprice)
        

        buf = BytesIO()
        img_template.save(buf, format='PNG')
        buf.seek(0)
        file_name = f"{row['ItemCode']}.jpg"
        image_paths.append((file_name, buf.getvalue()))
        category = row['Kategori']
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append((file_name, buf.getvalue()))

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