import datetime
import logging
import streamlit as st
import os
import yt_dlp
import mimetypes
from pathlib import Path
import re
from urllib.parse import urlparse, urlunparse

logging.basicConfig(level=logging.ERROR)

# -----------------------------
# Setup download folder in Downloads
# -----------------------------
downloads_path = Path.home() / "Downloads"
DOWNLOAD_DIR = downloads_path / "Facebook_Reels"
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
    """Remove query parameters and fragments from a Facebook URL."""
    parsed = urlparse(url.strip())
    clean = parsed._replace(query="", fragment="")
    return urlunparse(clean)

def is_valid_facebook_video_url(url: str) -> bool:
    """Check if URL looks like a valid Facebook Reels or Video link."""
    fb_video_pattern = re.compile(
        r'^(https?:\/\/)?([a-zA-Z0-9-]+\.)?facebook\.com\/(.*\/videos\/\d+|reel\/\d+)|^(https?:\/\/)?fb\.watch\/[A-Za-z0-9_-]+',
        re.IGNORECASE
    )
    return bool(fb_video_pattern.match(url.strip()))


# -----------------------------
# Video download function
# -----------------------------
def download_video(video_url, progress_callback):
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
        'paths': {'home': str(DOWNLOAD_DIR)},  # force save dir
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'logger': MyLogger(),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        file_path = ydl.prepare_filename(info)

    return file_path

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

urls_input = st.text_area("Video URLs (one per line)")

if st.button("Download Videos"):
    if not urls_input.strip():
        st.warning("Please enter at least one URL!")
    else:
        # Remove duplicates, validate, and clean
        seen = set()
        urls = []
        for u in urls_input.split("\n"):
            u = u.strip()
            if u:
                u = clean_facebook_url(u)  # auto-clean first
                if u not in seen:
                    if is_valid_facebook_video_url(u):
                        seen.add(u)
                        urls.append(u)
                    else:
                        st.warning(f"⚠️ Skipped invalid or non-video URL: {u}")

        total_videos = len(urls)
        if total_videos == 0:
            st.warning("No valid Facebook video URLs found!")
        else:
            video_rows = []
            for idx, url in enumerate(urls, start=1):
                cols = st.columns([3, 3, 2, 2])
                cols[0].markdown(f"<div style='white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width:250px;'>{url}</div>", unsafe_allow_html=True)
                progress_bar = cols[1].progress(0)
                status_text = cols[2].empty()
                status_text.text("Waiting...")
                download_btn_placeholder = cols[3].empty()
                video_rows.append({
                    "url": url,
                    "progress": progress_bar,
                    "status": status_text,
                    "download_btn": download_btn_placeholder
                })

            # Batch progress
            if total_videos > 1:
                batch_progress = st.progress(0)
                batch_status = st.empty()
            else:
                batch_progress = None
                batch_status = None

            # Download videos
            success_count = 0
            failed_count = 0

            with st.spinner("Downloading ..."):
                for row in video_rows:
                    def update_progress(p, row=row):
                        row["progress"].progress(p)
                        row["status"].text(f"{int(p*100)}%")

                    try:
                        row["status"].text("Downloading...")
                        file_path = download_video(row["url"], update_progress)
                        row["status"].text("Completed ✅")

                        # Show download button
                        mime_type, _ = mimetypes.guess_type(file_path)
                        row["download_btn"].download_button(
                            label="⬇ Download",
                            data=open(file_path, "rb"),
                            file_name=os.path.basename(file_path),
                            mime=mime_type or "application/octet-stream"
                        )
                        success_count += 1

                    except Exception as e:
                        logging.error(f"Failed to download {row['url']}: {e}")
                        row["status"].markdown("❌")
                        row["download_btn"].markdown("Failed",help="Something went wrong! Refresh browser and **Try Again!**")
                        failed_count += 1

                    # Update batch progress after each video
                    if total_videos > 1:
                        batch_progress.progress((success_count + failed_count) / total_videos)
                        batch_status.text(f"✅ {success_count} | ❌ {failed_count} | Total: {total_videos}")
            if success_count > 0:
                st.info(f"Videos are saved to: {DOWNLOAD_DIR}")

# Footer
st.write("---")
year = datetime.datetime.now().year
_, col, _ = st.columns([4, 2.5, 4])  # empty, center, empty
with col:
    st.caption(f"© {year} All rights reserved.")
