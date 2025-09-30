import datetime
import time
import logging
import streamlit as st
import os
import yt_dlp
import mimetypes
from pathlib import Path
import re
from urllib.parse import urlparse, urlunparse
import clipboard_component

# -----------------------------
# Initialize session state for urls and download status
# -----------------------------
if "urls_input" not in st.session_state:
    st.session_state["urls_input"] = ""
if "download_queue" not in st.session_state:
    st.session_state["download_queue"] = []
if "is_processing" not in st.session_state:
    st.session_state["is_processing"] = False

logging.basicConfig(level=logging.ERROR)

# -----------------------------
# Setup download folder in Downloads
# -----------------------------
downloads_path = Path.home() / "Downloads"
DOWNLOAD_DIR = downloads_path
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -----------------------------
# Logger for yt_dlp to suppress output
# -----------------------------
class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

# -----------------------------
# URL cleaning and validation
# -----------------------------
def clean_facebook_url(url: str) -> str:
    """Cleans Facebook URL to its base form."""
    parsed = urlparse(url.strip())
    clean = parsed._replace(query="", fragment="")
    return urlunparse(clean)

def is_valid_facebook_video_url(url: str) -> bool:
    """Validates if a URL is a known Facebook video or reel format."""
    # fb_video_pattern = re.compile(
    #     r'^(https?:\/\/)?([a-zA-Z0-9-]+\.)?(facebook\.com\/(.*\/videos\/\d+|reel\/\d+)|fb\.watch\/[A-Za-z0-9_-]+)',
    #     re.IGNORECASE
    # )
    fb_video_pattern = re.compile(
    r'(https?://)?(www\.|m\.)?(facebook\.com/.*/videos/\d+|facebook\.com/reel/\d+|fb\.watch/[A-Za-z0-9_-]+)',
    re.IGNORECASE
    )
    return bool(fb_video_pattern.match(url.strip()))

# -----------------------------
# Video download function
# -----------------------------
def download_video(video_url, progress_callback):
    """Downloads a video and returns its local path."""
    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                progress = downloaded_bytes / total_bytes
                progress_callback(progress)
        elif d['status'] == 'finished':
            progress_callback(1.0)

    ydl_opts = {
        'format': 'best',
        'outtmpl': str(DOWNLOAD_DIR / '%(title).50s_%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'logger': MyLogger(),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        if not Path(file_path).suffix:
            file_path = f"{file_path}.{info.get('ext', 'mp4')}"

        return file_path
    except Exception as e:
        logging.error(f"Failed to download {video_url}: {e}")
        return None

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Facebook Reels Downloader - Save Videos in HD Free",
    page_icon="images/facebook_downloader.png",
)

st.title("Download Facebook Reels Videos Online in HD Quality")
st.write("Fast and free Facebook Reels Downloader. Save Reels videos in HD directly to your device. No watermark, no signup - just paste the link and download instantly.")
st.divider()

# -----------------------------
# Clipboard + Refresh Buttons
# -----------------------------
_, col1, col2 = st.columns([5, 1.2, 1.2])

with col1:
    clipboard_content = clipboard_component.paste_component(
        "📋 Get URL",
        styles={
            "borderColor": "mediumSlateBlue",
            "hoverBackgroundColor": "#1E2429",
            "backgroundColor": "#2C3137",
            "textColor": "white",
            "borderRadius": "6px",
            "padding": "6px 12px",
        },
    )

with col2:
    if st.button("🔄 Refresh", help="This will clear all data & refresh page."):
        st.session_state["urls_input"] = ""
        st.session_state["download_queue"] = []
        st.session_state["is_processing"] = False
        st.rerun()

# -----------------------------
# Handle Clipboard Content
# -----------------------------
if clipboard_content:
    potential_urls = re.split(r'[\s\n]+', clipboard_content.strip())
    existing_links = set(
        line.strip()
        for line in st.session_state["urls_input"].splitlines()
        if line.strip()
    )
    added_count = 0
    for url in potential_urls:
        url = clean_facebook_url(url)
        if is_valid_facebook_video_url(url) and url not in existing_links:
            if st.session_state["urls_input"]:
                st.session_state["urls_input"] += "\n" + url
            else:
                st.session_state["urls_input"] = url
            existing_links.add(url)
            added_count += 1

    if added_count > 0:
        st.success(f"✅ Added {added_count} URL(s) from clipboard!")
    else:
        st.warning("⚠️ No new valid Facebook video URLs found in clipboard.")

# -----------------------------
# Text area
# -----------------------------
urls_input = st.text_area(
    "Video URLs (one per line)",
    key="urls_input",
    height=150
)

# -----------------------------
# Main download logic
# -----------------------------
if st.button("Start Processing", disabled=st.session_state["is_processing"]):
    if not urls_input.strip():
        st.warning("Please enter at least one URL!")
    else:
        seen = set()
        st.session_state["download_queue"] = []
        for u in urls_input.split("\n"):
            u = u.strip()
            if u:
                u = clean_facebook_url(u)
                if u not in seen:
                    if is_valid_facebook_video_url(u):
                        seen.add(u)
                        st.session_state["download_queue"].append({"url": u, "status": "waiting", "file_path": None, "progress": 0})
                    else:
                        st.warning(f"⚠️ Skipped invalid or non-video URL: {u}")
        
        if not st.session_state["download_queue"]:
            st.warning("No valid Facebook video URLs found!")
        else:
            st.session_state["is_processing"] = True
            st.rerun()

# Display download status and start downloads
if st.session_state["download_queue"]:
    for idx, video in enumerate(st.session_state["download_queue"]):
        video_url = video["url"]
        
        cols = st.columns([2.5, 2.5, 1.5, 1.5])
        
        # Column 1: Link
        cols[0].markdown(
            f"<div style='white-space: nowrap; overflow: hidden; "
            f"text-overflow: ellipsis; max-width:250px;'>{video_url}</div>",
            unsafe_allow_html=True
        )

        # Handle different download statuses
        if video["status"] == "waiting":
            cols[1].progress(0.0)
            cols[2].text("waiting...")
            cols[3].text("- - - - - - - - - - -")
        elif video["status"] == "downloading":
            cols[1].progress(video.get("progress", 0.0), text=f"{int(video.get('progress', 0.0)*100)}%")
            cols[2].text("downloading...")
            cols[3].text("- - - - - - - - - - -")
        elif video["status"] == "success":
            cols[1].progress(1.0)
            cols[2].markdown("✅ Success")
            file_path = video["file_path"]
            if file_path and os.path.exists(file_path):
                mime_type, _ = mimetypes.guess_type(file_path)
                with open(file_path, "rb") as f:
                    video_data = f.read()
                cols[3].download_button(
                    label="Download",
                    data=video_data,
                    file_name=os.path.basename(file_path),
                    mime=mime_type or "application/octet-stream",
                    key=f"download_{idx}"
                )
        elif video["status"] == "failed":
            cols[1].progress(0)
            cols[2].markdown("❌ Failed")
            if cols[3].button("Try Again", key=f"retry_{idx}"):
                st.session_state["download_queue"][idx]["status"] = "waiting"
                st.session_state["is_processing"] = True
                st.rerun()

    # Process next video in the queue if one is not already downloading
    if st.session_state["is_processing"]:
        next_video_to_process = None
        for idx, video in enumerate(st.session_state["download_queue"]):
            if video["status"] == "waiting":
                next_video_to_process = idx
                break
        
        if next_video_to_process is not None:
            with st.spinner(f"Downloading video: {next_video_to_process + 1}"):
                st.session_state["download_queue"][next_video_to_process]["status"] = "downloading"
                video_url_to_download = st.session_state["download_queue"][next_video_to_process]["url"]
                
                # A hack to pass progress updates back to the session state
                class ProgressWrapper:
                    def __init__(self, idx):
                        self.idx = idx
                    def __call__(self, p):
                        st.session_state["download_queue"][self.idx]["progress"] = p
                        time.sleep(0.01) # Small sleep to allow UI to update
                        
                file_path = download_video(video_url_to_download, ProgressWrapper(next_video_to_process))
                
                if file_path:
                    st.session_state["download_queue"][next_video_to_process]["status"] = "success"
                    st.session_state["download_queue"][next_video_to_process]["file_path"] = file_path
                else:
                    st.session_state["download_queue"][next_video_to_process]["status"] = "failed"
                
                st.rerun()
        else:
            st.session_state["is_processing"] = False
            st.success("All videos have been processed!")
            st.rerun()

    if any(v['status'] == "success" for v in st.session_state["download_queue"]):
        st.info(f"Downloads are saved to: {DOWNLOAD_DIR}")

# -----------------------------
# Footer
# -----------------------------
st.write("---")
year = datetime.datetime.now().year
_, col, _ = st.columns([4, 2.5, 2])
with col:
    st.caption(f"© {year} All rights reserved.")
