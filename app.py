"""
app.py
------
Streamlit UI for the E-Commerce Image Fixer.
Run locally:  streamlit run app.py
Deploy free:  push this repo to GitHub, then deploy on streamlit.io/cloud.
"""

import io
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image

from image_fixer import SUPPORTED_EXTS, process_image

st.set_page_config(page_title="E-Commerce Image Fixer", page_icon="🖼️", layout="wide")

st.title("🖼️ E-Commerce Image Fixer")
st.caption("Raw phone photos in → clean studio-white product shots out.")

with st.sidebar:
    st.header("Settings")
    canvas_size = st.slider("Canvas size (px)", 800, 3000, 1600, step=100)
    padding = st.slider("Padding around product", 0.0, 0.30, 0.10, step=0.02)
    st.markdown("---")
    st.markdown(
        "**How it works**\n"
        "1. AI segmentation removes the background\n"
        "2. Product is sharpened and contrast-boosted\n"
        "3. Cropped tight and centered on a white canvas\n\n"
        "No manual masking, no studio, no green screen."
    )

uploaded_files = st.file_uploader(
    "Upload product photos (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

run = st.button("Fix images", type="primary", disabled=not uploaded_files)

if run:
    results = []
    progress = st.progress(0.0, text="Starting...")

    for i, uploaded in enumerate(uploaded_files):
        if Path(uploaded.name).suffix.lower() not in SUPPORTED_EXTS:
            continue
        progress.progress(i / len(uploaded_files), text=f"Processing {uploaded.name}...")
        try:
            original = Image.open(uploaded)
            fixed = process_image(original, canvas_size=canvas_size, padding_ratio=padding)
            results.append((uploaded.name, original, fixed))
        except Exception as exc:
            st.error(f"Failed on {uploaded.name}: {exc}")

    progress.progress(1.0, text="Done")
    st.success(f"Fixed {len(results)} image(s).")

    for name, original, fixed in results:
        col1, col2 = st.columns(2)
        with col1:
            st.image(original, caption=f"Before — {name}", use_container_width=True)
        with col2:
            st.image(fixed, caption="After — studio white background", use_container_width=True)

    if results:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for name, _, fixed in results:
                img_bytes = io.BytesIO()
                fixed.save(img_bytes, format="JPEG", quality=95)
                zf.writestr(f"{Path(name).stem}_studio.jpg", img_bytes.getvalue())
        zip_buffer.seek(0)

        st.download_button(
            "⬇️ Download all as ZIP",
            data=zip_buffer,
            file_name="studio_photos.zip",
            mime="application/zip",
        )
else:
    st.info("Upload one or more product photos and click **Fix images** to begin.")
