from supabase import create_client, Client
from urllib.parse import quote
from dotenv import load_dotenv
import os
import streamlit as st
import uuid

# Load .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit App
st.set_page_config(page_title="Cloud File Storage", layout="centered")
st.title("📁 Cloud File Storage App")

uploaded_file = st.file_uploader("Upload a file", type=None)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
    
    try:
        supabase.storage.from_("uploads").upload(file_name, file_bytes)
        st.success(f"✅ File uploaded as {file_name}")
    except Exception as e:
        st.error(f"⚠ Upload failed: {str(e)}")

def list_files():
    try:
        files = supabase.storage.from_("uploads").list()
        return files
    except Exception as e:
        st.error(f"⚠ Could not fetch files: {str(e)}")
        return []

def delete_file(file_name):
    try:
        st.write(f"🧪 Deleting file: {file_name}")  # encode all special chars
        response = supabase.storage.from_("uploads").remove([file_name])
        if response.get('error'):
            st.error(f"⚠ Delete failed: {response['error']['message']}")
        else:
            st.success(f"🗑️ Deleted file: {file_name}")
            st.experimental_rerun()  # Refresh UI after delete
    except Exception as e:
        st.error(f"⚠ Exception on delete: {str(e)}")

def download_file(file_name):
    try:
        response = supabase.storage.from_("uploads").download(file_name)
        data = response.read()
        return data
    except Exception as e:
        st.error(f"⚠ Download failed: {str(e)}")
        return None

if st.button("🔄 Refresh Files List"):
    files = list_files()
    if files:
        st.write("📂 Files in storage:")
        for f in files:
            file_name = f.get('name', 'Unknown')
            col1, col2, col3 = st.columns([6,1,1])
            with col1:
                st.markdown(f"- {file_name}")
            with col2:
                if st.button("Download", key=f"download_{file_name}"):
                    file_data = download_file(file_name)
                    if file_data:
                        st.download_button(
                            label="Click to Save",
                            data=file_data,
                            file_name=file_name,
                            mime="application/octet-stream"
                        )
            with col3:
                if st.button("Delete", key=f"delete_{file_name}"):
                    delete_file(file_name)
                    # Force refresh or rerun so list updates after deletion
                    st.experimental_rerun()
    else:
        st.info("📭 No files found.")

    