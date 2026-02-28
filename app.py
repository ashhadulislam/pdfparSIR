import streamlit as st
import fitz
import numpy as np
import cv2
import tempfile
import zipfile
import os
from io import BytesIO
from PIL import Image

NUM_COLS = 3
NUM_ROWS = 10
DPI = 300

# ----------------------------------
# Convert PDF page to image
# ----------------------------------
def pdf_page_to_image(doc, page_number, dpi=300):
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=matrix)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)

    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img


# ----------------------------------
# Extract cards
# ----------------------------------
def extract_cards(doc, start_page, end_page,
                  top_margin, bottom_margin,
                  left_margin, right_margin):

    temp_dir = tempfile.mkdtemp()

    for page_number in range(start_page - 1, end_page):

        img = pdf_page_to_image(doc, page_number, DPI)
        h, w = img.shape[:2]

        cropped = img[
            top_margin : h - bottom_margin,
            left_margin : w - right_margin
        ]

        usable_h, usable_w = cropped.shape[:2]

        col_width = usable_w // NUM_COLS
        row_height = usable_h // NUM_ROWS

        card_count = 0

        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):

                x1 = col * col_width
                x2 = (col + 1) * col_width
                y1 = row * row_height
                y2 = (row + 1) * row_height

                card = cropped[y1:y2, x1:x2]

                filename = f"page_{page_number+1}_card_{card_count}.png"
                cv2.imwrite(os.path.join(temp_dir, filename), card)

                card_count += 1

    return temp_dir


# ----------------------------------
# Draw margin lines for preview
# ----------------------------------
def draw_guides(img, top, bottom, left, right):
    preview = img.copy()
    h, w = preview.shape[:2]

    # Top line
    cv2.line(preview, (0, top), (w, top), (0, 0, 255), 3)
    # Bottom line
    cv2.line(preview, (0, h-bottom), (w, h-bottom), (0, 0, 255), 3)
    # Left line
    cv2.line(preview, (left, 0), (left, h), (255, 0, 0), 3)
    # Right line
    cv2.line(preview, (w-right, 0), (w-right, h), (255, 0, 0), 3)

    return preview


# ----------------------------------
# Streamlit UI
# ----------------------------------

st.title("📄 Electoral Roll Name Card Extractor")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    doc = fitz.open(pdf_path)

    total_pages = len(doc)
    st.write(f"Total Pages: {total_pages}")

    start_page = st.number_input("Start Page", 1, total_pages, 1)
    end_page = st.number_input("End Page", 1, total_pages, 1)

    preview_page = st.slider("Preview Page", 1, total_pages, start_page)

    img = pdf_page_to_image(doc, preview_page - 1, DPI)

    h, w = img.shape[:2]

    st.subheader("Adjust Margins")

    top_margin = st.slider("Top Margin", 0, h//2, 120)
    bottom_margin = st.slider("Bottom Margin", 0, h//2, 100)
    left_margin = st.slider("Left Margin", 0, w//2, 60)
    right_margin = st.slider("Right Margin", 0, w//2, 60)

    preview_with_guides = draw_guides(
        img,
        top_margin,
        bottom_margin,
        left_margin,
        right_margin
    )

    st.image(preview_with_guides, channels="BGR", use_container_width=True)

    if st.button("Download Name Cards"):

        temp_dir = extract_cards(
            doc,
            start_page,
            end_page,
            top_margin,
            bottom_margin,
            left_margin,
            right_margin
        )

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file in os.listdir(temp_dir):
                zipf.write(
                    os.path.join(temp_dir, file),
                    arcname=file
                )

        st.download_button(
            label="Download ZIP",
            data=zip_buffer.getvalue(),
            file_name="name_cards.zip",
            mime="application/zip"
        )

    doc.close()