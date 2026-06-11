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
    epub_to_md_from_bytes,
    image_to_md_from_bytes
)

st.set_page_config(
    page_title="Markdown Forge Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    /* Premium Font overrides */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
    }
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Ambient Background */
    .stApp {
        background: radial-gradient(circle at top left, #080b11 0%, #02040a 60%, #000000 100%) !important;
        color: #e2e8f0 !important;
    }

    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes glowPulse {
        0% { box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 4px 25px rgba(168, 85, 247, 0.5); }
        100% { box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); }
    }

    /* Hero Section Card */
    .hero {
        padding: 3rem 2rem;
        border-radius: 28px;
        background: linear-gradient(-45deg, rgba(79, 70, 229, 0.2) 0%, rgba(147, 51, 234, 0.15) 35%, rgba(59, 130, 246, 0.15) 70%, rgba(99, 102, 241, 0.1) 100%);
        background-size: 400% 400%;
        animation: gradientShift 10s ease infinite, fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    .hero h1 {
        font-size: 3.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #6366f1, #a855f7, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.04em;
    }
    .hero p {
        color: #94a3b8;
        font-size: 1.15rem;
        font-weight: 300;
        max-width: 700px;
        margin: 0 auto;
    }

    /* Glassmorphic Content Cards */
    .card {
        padding: 2rem;
        border-radius: 24px;
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .card:hover {
        transform: translateY(-5px);
        border-color: rgba(168, 85, 247, 0.25);
        box-shadow: 0 20px 45px rgba(168, 85, 247, 0.12);
    }
    .hint {
        color: #64748b;
        font-size: 0.9rem;
    }

    /* Sidebar Enhancements */
    section[data-testid="stSidebar"] {
        background-color: #02040a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* File Uploader Custom Aesthetics */
    div[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.3) !important;
        border: 2px dashed rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.5) !important;
        background: rgba(99, 102, 241, 0.03) !important;
    }

    /* Streamlit Primary Button Overrides */
    div.stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
        animation: glowPulse 4s infinite;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
        background: linear-gradient(90deg, #5c53ef 0%, #8b5cf6 100%) !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Streamlit Download Button Overrides */
    div.stDownloadButton > button {
        background: linear-gradient(90deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
        background: linear-gradient(90deg, #0f9f72 0%, #10c98e 100%) !important;
    }
</style>


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
                    md = image_to_md_from_bytes(data, ocr_lang=ocr_lang)
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