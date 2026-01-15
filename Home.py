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
        return Nonepy

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

# --- Custom CSS for Premium UI ---
st.markdown("""
    <style>
    /* Main Background & Font */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    h1 {
        font-weight: 700 !important;
        background: -webkit-linear-gradient(45deg, #4267B2, #1877F2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.5rem;
    }
    
    /* Input Areas */
    .stTextArea textarea {
        background-color: #161b22;
        border: 1px solid #30363d;
        color: #e6edf3;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #1877F2;
        box-shadow: 0 0 0 1px #1877F2;
    }

    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stBaseButton-secondary"] {
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #c9d1d9;
    }
    div[data-testid="stBaseButton-secondary"]:hover {
        border-color: #8b949e;
        color: white;
    }
    
    /* Card/Container Styling */
    div[data-testid="stExpander"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #1877F2;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #8b949e;
        padding-top: 3rem;
        padding-bottom: 2rem;
        font-size: 0.85rem;
        border-top: 1px solid #30363d;
        margin-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
col_head1, col_head2 = st.columns([3, 1], vertical_alignment="bottom")
with col_head1:
    st.title("FB Reels Downloader")
    st.markdown("🚀 **Fast, High-Quality, and Free.** Download Facebook videos and reels instantly.")

with col_head2:
    with st.expander("ℹ️ **How to Use**"):
        st.markdown("""
        1. **Copy Link**: Go to Facebook and copy the link of the video/reel.
        2. **Paste**: Paste the link in the box below or use the 'Paste' button.
        3. **Start**: Click **Start Processing**.
        4. **Download**: Click **Save** when ready.
        """)

st.divider()

# --- Control Section ---
# Removed redundant container init

# Better responsiveness: 
# On mobile check we can't detect, but we can arrange columns smartly.
# Let's keep a main layout but maybe move actions.

# Actually, for better UX, let's put the Input and Action in the same block or cleaner columns.
col_input, col_actions = st.columns([3, 1.2], gap="large")

with col_actions:
    st.markdown("### Actions")
    
    # Clipboard Tool
    clipboard_content = clipboard_component.paste_component(
        "📋 Paste from Clipboard",
        key="paste_clipboard",
        width="100%", 
        styles={},
    )
    
    st.write("") # Spacer
    
    # Refresh/Clear
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🔄 Reset", use_container_width=True, help="Reset everything"):
            st.session_state["urls_input"] = ""
            st.session_state["download_queue"] = []
            st.session_state["is_processing"] = False
            st.rerun()
    with col_act2:
        if st.button("🧹 Clear", use_container_width=True, help="Clear results list"):
            st.session_state["download_queue"] = []
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
# -----------------------------
with col_input:
    # Text area
    urls_input = st.text_area(
        "Enter Facebook Video/Reel URLs (One per line):",
        key="urls_input",
        height=180,
        placeholder="https://www.facebook.com/reel/..."
    )

    if st.button("🚀 Start Processing", type="primary", use_container_width=True, disabled=st.session_state["is_processing"]):
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
# --- Download Queue Display ---
if st.session_state["download_queue"]:
    st.write("---") # Visual separator
    st.subheader(f"📥 Download Queue ({len(st.session_state['download_queue'])})")
    
    for idx, video in enumerate(st.session_state["download_queue"]):
        # Create a card-like container
        with st.container():
            video_url = video["url"]
            
            # Responsive Card Layout
            # Using a slightly different column ratio for better mobile look if possible
            # But consistent sizing is key.
            c1, c2, c3 = st.columns([0.1, 0.7, 0.2], vertical_alignment="center") # Icon/ID,  Info+Progress, Action
            
            # Since we can't easily do a nested grid per row without clutter, let's keep the row simple but styled
            # Actually, let's use the columns closer to the request: Index, Info, Progress, Action
            
            # New Layout:
            # Col 1: Status Icon + URL (Combined)
            # Col 2: Progress Bar (if downloading) or Status Text
            # Col 3: Action Button
            
            row_cols = st.columns([3, 2, 1.5], vertical_alignment="center")
            
            with row_cols[0]:
                # Status Icon
                status = video["status"]
                icon = "⏳"
                if status == "downloading": icon = "⬇️"
                elif status == "success": icon = "✅"
                elif status == "failed": icon = "❌"
                
                st.markdown(f"**{idx+1}.** {icon} `{video_url[:40]}...`")
                
            with row_cols[1]:
                if video["status"] == "waiting":
                    st.caption("Waiting to start...")
                elif video["status"] == "downloading":
                    st.progress(video.get("progress", 0.0), text=f"{int(video.get('progress', 0) * 100)}%")
                elif video["status"] == "success":
                    st.caption("Ready for download")
                elif video["status"] == "failed":
                    st.error("Download failed")

            with row_cols[2]:
                 if video["status"] == "success":
                    file_path = video["file_path"]
                    if file_path and os.path.exists(file_path):
                        mime_type, _ = mimetypes.guess_type(file_path)
                        try:
                            with open(file_path, "rb") as f:
                                video_data = f.read()
                            st.download_button(
                                label="💾 Save File",
                                data=video_data,
                                file_name=os.path.basename(file_path),
                                mime=mime_type or "application/octet-stream",
                                key=f"download_{idx}",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error("File Error")
                 elif video["status"] == "failed":
                    if st.button("🔄 Retry", key=f"retry_{idx}", use_container_width=True):
                        st.session_state["download_queue"][idx]["status"] = "waiting"
                        st.session_state["is_processing"] = True
                        st.rerun()
            
            st.divider() # Separator between items

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
st.markdown(
    f"""
    <div class="footer">
        © {year} All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
