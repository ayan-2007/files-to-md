import os
import tempfile
import streamlit as st

from utils import safe_filename, file_extension
from converters import (
    extract_pdf_to_markdown,
    txt_to_md_from_bytes,
    docx_to_md_from_bytes,
    html_to_md_from_bytes,
    rtf_to_md_from_bytes,
    epub_to_md_from_bytes
)

st.set_page_config(
    page_title="Markdown Forge Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 45%, #000 100%);
        color: white;
    }
    .hero {
        padding: 2rem 2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(168,85,247,0.16));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 24px 80px rgba(0,0,0,0.35);
        margin-bottom: 1.5rem;
    }
    .card {
        padding: 1.25rem;
        border-radius: 22px;
        background: rgba(15,23,42,0.72);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 12px 42px rgba(0,0,0,0.25);
    }
    .hint {
        color: #94a3b8;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>⚡ Markdown Forge Pro</h1>
    <p>Unique, polished, OCR-powered file-to-Markdown conversion for PDFs, images, and documents.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Settings")
    use_ocr = st.toggle("Enable OCR fallback for scanned PDFs", value=True)
    ocr_lang = st.text_input("OCR language", value="en")
    st.markdown("---")
    st.markdown("### Supported")
    st.write("PDF, TXT, DOCX, HTML, RTF, EPUB, PNG, JPG, JPEG, BMP, TIF, TIFF")
    st.markdown("### Note")
    st.caption("OCR is best deployed in Docker or a VM for PaddleOCR stability.")

col1, col2 = st.columns([1.05, 0.95], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload files")
    uploaded_files = st.file_uploader(
        "Drop files here",
        type=["pdf", "txt", "docx", "html", "htm", "rtf", "epub", "png", "jpg", "jpeg", "bmp", "tif", "tiff"],
        accept_multiple_files=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Workflow")
    st.write("1. Upload files")
    st.write("2. Convert with OCR fallback")
    st.write("3. Download Markdown")
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) queued.")
    if st.button("Convert to Markdown", use_container_width=True):
        results = []
        errors = []
        progress = st.progress(0)
        total = len(uploaded_files)

        for i, uploaded_file in enumerate(uploaded_files, start=1):
            try:
                name = uploaded_file.name
                ext = file_extension(name)
                data = uploaded_file.getvalue()

                if ext == ".pdf":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(data)
                        pdf_path = tmp.name
                    try:
                        md = extract_pdf_to_markdown(pdf_path, use_ocr=use_ocr, ocr_lang=ocr_lang)
                    finally:
                        os.remove(pdf_path)
                elif ext == ".txt":
                    md = txt_to_md_from_bytes(data)
                elif ext == ".docx":
                    md = docx_to_md_from_bytes(data)
                elif ext in [".html", ".htm"]:
                    md = html_to_md_from_bytes(data)
                elif ext == ".rtf":
                    md = rtf_to_md_from_bytes(data)
                elif ext == ".epub":
                    md = epub_to_md_from_bytes(data)
                elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]:
                    # Images are OCR'd too for best practical support
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(data)
                        img_path = tmp.name
                    try:
                        md = extract_pdf_to_markdown(img_path, use_ocr=True, ocr_lang=ocr_lang)  # fallback path
                    finally:
                        if os.path.exists(img_path):
                            os.remove(img_path)
                else:
                    raise ValueError(f"Unsupported file: {name}")

                out_name = safe_filename(os.path.splitext(name)[0]) + ".md"
                results.append((out_name, md))
            except Exception as e:
                errors.append(f"{uploaded_file.name}: {e}")

            progress.progress(i / total)

        if results:
            st.subheader("Downloads")
            for out_name, md in results:
                st.download_button(
                    label=f"Download {out_name}",
                    data=md.encode("utf-8"),
                    file_name=out_name,
                    mime="text/markdown",
                    use_container_width=True
                )
                with st.expander(f"Preview: {out_name}"):
                    st.code(md, language="markdown")

        if errors:
            st.error("Some files could not be converted.")
            for err in errors:
                st.write(err)
else:
    st.info("Upload files to start converting.")