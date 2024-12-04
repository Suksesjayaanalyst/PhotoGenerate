import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Membuat gambar dengan ukuran 1200x800 dan background putih
img = Image.new('RGB', (1200, 800), color='white')
draw = ImageDraw.Draw(img)

# Menentukan font dan ukuran font
font = ImageFont.truetype("./Poppins-Medium.ttf", size=25)

# Data teks (dapat diubah oleh pengguna)
nama = "Valentio"
umur = "12"
status = "Kaya Raya"
deskripsi = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

# Data teks
text_data = [
    ("Nama", nama),
    ("Umur", umur),
    ("Status", status),
    ("Deskripsi", deskripsi),
]

# Posisi awal untuk menulis teks
x, y = 50, 50
line_height = 50
max_width = 1100  # Lebar maksimal untuk teks (sesuaikan dengan lebar gambar)

# Fungsi untuk menggambar teks dalam text box
def draw_text_with_box(draw, text, position, font, max_width):
    # Membungkus teks agar sesuai dengan lebar maksimal
    lines = []
    words = text.split(' ')
    line = ""

    for word in words:
        # Jika menambah kata melebihi lebar maksimal, lanjutkan ke baris berikutnya
        test_line = line + " " + word if line else word
        width, _ = draw.textsize(test_line, font=font)
        if width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    
    # Menulis teks dengan background biru
    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        draw.rectangle([position[0], position[1], position[0] + text_width + 20, position[1] + text_height + 20], fill="blue")
        draw.text((position[0] + 10, position[1] + 10), line, font=font, fill="white")
        position = (position[0], position[1] + text_height + 10)  # Update posisi y untuk baris berikutnya

    return position  # Mengembalikan posisi akhir setelah teks ditulis

# Menulis teks
for label, text in text_data:
    if label == "Deskripsi":
        # Deskripsi tidak perlu jarak tambahan setelahnya
        y = draw_text_with_box(draw, f"{label}: {text}", (x, y), font, max_width)[1]
    else:
        # Untuk keterangan lain, beri jarak antar keterangan
        y = draw_text_with_box(draw, f"{label}: {text}", (x, y), font, max_width)[1] + 30  # Tambahkan jarak tambahan setelah keterangan

# Menyimpan gambar ke dalam buffer
buffer = BytesIO()
img.save(buffer, format="PNG")
buffer.seek(0)

# Menampilkan gambar di Streamlit
st.image(buffer, use_column_width=True)
