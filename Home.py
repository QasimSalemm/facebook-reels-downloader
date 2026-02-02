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
import zipfile
import io

# -----------------------------
# Initialize session state for urls and download status
# -----------------------------
if "urls_input" not in st.session_state:
    st.session_state["urls_input"] = ""
if "download_queue" not in st.session_state:
    st.session_state["download_queue"] = []
if "is_processing" not in st.session_state:
    st.session_state["is_processing"] = False
if "prepared_zip_data" not in st.session_state:
    st.session_state["prepared_zip_data"] = None
if "ready_to_download_files" not in st.session_state:
    st.session_state["ready_to_download_files"] = {}

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

#This now matches:

#www.facebook.com
#m.facebook.com
#web.facebook.com
#fb.watch/...

def is_valid_facebook_video_url(url: str) -> bool:
    """Validates if a URL is a known Facebook video or reel format."""
    fb_video_pattern = re.compile(
        r'^(https?://)?'                                # optional http/https
        r'([a-z0-9-]+\.)?'                              # optional subdomain (www, m, web, l, etc.)
        r'(facebook\.com|fb\.watch|fb\.me)/'            # main domains
        r'('
        r'[^ ]*/videos/\d+[^ ]*|'                       # /videos/123...
        r'reel/\d+[^ ]*|'                               # /reel/123...
        r'watch/\?v=\d+[^ ]*|'                          # /watch/?v=123...
        r'story\.php\?story_fbid=\d+[^ ]*|'             # story.php?story_fbid=...
        r'share/r/[A-Za-z0-9_-]+/?|'                    # /share/r/...
        r'[A-Za-z0-9_-]+/?'                             # fb.watch/abc123 or fb.me/abc123
        r')',
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
# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="Facebook Video & Reels Downloader",
    page_icon="images/facebook_downloader.png",
    layout="wide"
)

# --- Header Section ---
st.title("Facebook Video & Reels Downloader")
st.markdown("Download Facebook videos and reels quickly and easily.")


# -----------------------------
# Handle Utility Actions (Reset/Clear)
# -----------------------------
if st.session_state.get("trigger_reset"):
    st.session_state["urls_input"] = ""
    st.session_state["download_queue"] = []
    st.session_state["is_processing"] = False
    st.session_state["prepared_zip_data"] = None
    st.session_state["ready_to_download_files"] = {}
    del st.session_state["trigger_reset"]
    st.rerun()

if st.session_state.get("trigger_clear"):
    st.session_state["download_queue"] = []
    st.session_state["prepared_zip_data"] = None
    st.session_state["ready_to_download_files"] = {}
    del st.session_state["trigger_clear"]
    st.rerun()

# --- Main Section ---
# Clipboard Button clearly positioned above the text area
clipboard_content = clipboard_component.paste_component(
    "📋 Paste from Clipboard",
    key="paste_clipboard",
    width="100%", 
    styles={},
)

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
# URL Input Area
urls_input = st.text_area(
    "Enter Facebook Video/Reel URLs (One per line):",
    key="urls_input",
    height=200,
    placeholder="https://www.facebook.com/reel/..."
)

# Start Processing Button
if st.button("Start Processing", type="primary", use_container_width=True, disabled=st.session_state["is_processing"]):
    if not urls_input.strip():
        st.toast("⚠️ Please enter at least one URL!", icon="⚠️")
    else:
        seen = set()
        st.session_state["download_queue"] = []
        
        # Simple validation toast
        st.toast("Processing URLs...", icon="⏳")
        
        count_added = 0
        for u in urls_input.split("\n"):
            u = u.strip()
            if u:
                u = clean_facebook_url(u)
                if u not in seen:
                    if is_valid_facebook_video_url(u):
                        seen.add(u)
                        st.session_state["download_queue"].append({"url": u, "status": "waiting", "file_path": None, "progress": 0})
                        count_added += 1
                    else:
                        # Optional: could show warnings regarding skips
                        pass
        
        if not st.session_state["download_queue"]:
            st.toast("No valid Facebook video URLs found!", icon="🚫")
        else:
            st.session_state["is_processing"] = True
            st.rerun()


# --- Download Queue Display ---
if st.session_state["download_queue"]:
    st.subheader(f"Queue ({len(st.session_state['download_queue'])})")
    
    # Create placeholders for progress bars so they can be updated during download
    progress_placeholders = {}

    for idx, video in enumerate(st.session_state["download_queue"]):
        status = video["status"]
        
        # Use a boxed container for each row
        with st.container(border=True):
            # Adjusted for better mobile visibility: Index(0.4), URL(3.0), Progress/Status(2.0), Save(1.2)
            q_cols = st.columns([0.4, 3.0, 2.0, 1.2], vertical_alignment="center")
            
            with q_cols[0]:
                st.markdown(f"**{idx+1}.**")
                
            with q_cols[1]:
                # Aggressive truncation
                display_url = video["url"]
                if len(display_url) > 18:
                    display_url = f"{display_url[:15]}..."
                st.markdown(f"`{display_url}`", help=video["url"])
                
            with q_cols[2]:
                # Dynamic area for status/progress
                progress_placeholders[idx] = st.empty()
                with progress_placeholders[idx]:
                    if status == "waiting":
                        st.caption("Waiting...")
                    elif status == "downloading":
                        st.progress(video.get("progress", 0.0))
                    elif status == "success":
                        st.markdown(":green[**Ready**]", help="Click to download.")
                    elif status == "failed":
                        st.markdown(":red[**Error**]", help="Check the URL and try again.")
            
            with q_cols[3]:
                if status == "success":
                    file_path = video["file_path"]
                    if file_path and os.path.exists(file_path):
                        # Check if this file is already prepared
                        if idx in st.session_state["ready_to_download_files"]:
                            # Show the actual download button
                            file_data = st.session_state["ready_to_download_files"][idx]
                            mime_type, _ = mimetypes.guess_type(file_path)
                            st.download_button(
                                label="💾 Download Now",
                                data=file_data,
                                file_name=os.path.basename(file_path),
                                mime=mime_type or "application/octet-stream",
                                key=f"download_{idx}",
                                use_container_width=True
                            )
                        else:
                            # Show prepare button
                            if st.button("☁️ Prepare Download", key=f"prepare_{idx}", use_container_width=True):
                                # Show immediate feedback in the status column
                                progress_placeholders[idx].info("⏳ Preparing...")
                                st.toast(f"📁 Reading video {idx+1}...", icon="⏳")
                                
                                try:
                                    with open(file_path, "rb") as f:
                                        video_data = f.read()
                                    st.session_state["ready_to_download_files"][idx] = video_data
                                    st.toast(f"✅ Video {idx+1} ready to download!", icon="✅")
                                    st.rerun()
                                except Exception as e:
                                    st.error("❌ Failed to prepare file")
                                    st.toast(f"❌ Error: {str(e)}", icon="❌")
                elif status == "failed":
                    if st.button("Retry", key=f"retry_{idx}", use_container_width=True):
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
            st.session_state["download_queue"][next_video_to_process]["status"] = "downloading"
            video_url_to_download = st.session_state["download_queue"][next_video_to_process]["url"]
            
            # Use the placeholder to show immediate processing
            placeholder = progress_placeholders[next_video_to_process]
            
            # A hack to pass progress updates back to the session state AND the placeholder
            class ProgressWrapper:
                def __init__(self, idx, ph):
                    self.idx = idx
                    self.ph = ph
                def __call__(self, p):
                    st.session_state["download_queue"][self.idx]["progress"] = p
                    # Update placeholder immediately for live feedback
                    self.ph.progress(p)
                    
            file_path = download_video(video_url_to_download, ProgressWrapper(next_video_to_process, placeholder))
            
            if file_path:
                st.session_state["download_queue"][next_video_to_process]["status"] = "success"
                st.session_state["download_queue"][next_video_to_process]["file_path"] = file_path
            else:
                st.session_state["download_queue"][next_video_to_process]["status"] = "failed"
            
            st.rerun()
        else:
            st.session_state["is_processing"] = False
            st.toast("✅ All videos processed!", icon="✅")
            st.rerun()

    if any(v['status'] == "success" for v in st.session_state["download_queue"]):
        st.info(f"Downloads are saved to: {DOWNLOAD_DIR}")
        
        # --- Save All Videos Button ---
        success_videos = [v for v in st.session_state["download_queue"] if v['status'] == "success" and v['file_path'] and os.path.exists(v['file_path'])]
        
        if success_videos:
            st.write("")
            
            # Check if ZIP is already prepared
            if st.session_state["prepared_zip_data"] is not None:
                # Show the actual download button
                st.download_button(
                    label="📥 Download All Videos (ZIP)",
                    data=st.session_state["prepared_zip_data"],
                    file_name=f"facebook_reels_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    key="download_all_zip_final",
                    use_container_width=True,
                    type="primary",
                    help="Download all finished videos in one ZIP file"
                )
            else:
                # Show prepare button
                if st.button("📦 Prepare ZIP Download", use_container_width=True, type="primary"):
                    st.toast(f"🗜️ Compressing {len(success_videos)} videos...", icon="⏳")
                    
                    # --- Generate ZIP in memory ---
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for v in success_videos:
                            file_path = v['file_path']
                            arcname = os.path.basename(file_path)
                            zip_file.write(file_path, arcname)
                    
                    zip_buffer.seek(0)
                    st.session_state["prepared_zip_data"] = zip_buffer.getvalue()
                    st.toast("✅ ZIP file ready to download!", icon="✅")
                    st.rerun()

# -----------------------------
# --- Utility Actions (Reset/Clear) at Bottom ---
st.divider()
cb1, cb2 = st.columns(2)
with cb1:
    if st.button("Reset App", use_container_width=True, help="Reset everything"):
        st.session_state["trigger_reset"] = True
        st.rerun()
with cb2:
    if st.button("Clear Results", use_container_width=True, help="Clear results list"):
        st.session_state["trigger_clear"] = True
        st.rerun()

# --- Footer ---
st.write("")
year = datetime.datetime.now().year
st.markdown(
    f"""
    <div style="text-align: center; color: gray; font-size: 0.8rem; margin-top: 50px;">
        © {year} All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
