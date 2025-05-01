import gradio as gr
import subprocess
import tempfile
import uuid
import os
import re
import logging
from pathlib import Path
from typing import Generator, Tuple, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('secure_downloader')

# Constants
DEFAULT_OUT_DIR = "Downloads"
TEMP_DIR = tempfile.gettempdir()
COOKIE_WARNING = """⚠️ <span style="font-size:1.3em; font-weight:bold">EXTREME SECURITY RISK</span> ⚠️

• <span style="color:yellow; font-weight:bold">NEVER</span> use personal/main account cookies
• Cookies contain <span style="color:yellow; font-weight:bold">SENSITIVE AUTHENTICATION DATA</span>
• Cookies are <span style="color:lime; font-weight:bold">DELETED IMMEDIATELY</span> after use
• We <span style="color:lime; font-weight:bold">DO NOT STORE</span> any cookie data
• Misuse of Cookies Can result in <span style="color:Black; font-weight:bold">PERMANENT ACCOUNT BANS</span>"""

README_CONTENT = """# Secure Media Downloader

## Overview
This tool allows you to download media in highest possible Quality content while respecting your privacy and security.

## Features
- Single video downloads
- Bulk downloads (multiple URLs)
- Restricted content access (with cookies)
- Cloudflare tunnel for remote access

## How to Use

### Single Download
1. Paste video URL
2. Set download location (optional)
3. Select audio/video options
4. Click Download

### Bulk Download
1. Enter one URL per line
2. Configure options
3. Click Start Bulk Download

### Security Warning
When using the Restricted tab:
- NEVER use personal account cookies
- Use temporary accounts only
- All cookie data is deleted after use
- We do not store any sensitive information
- Avoid Youtube PlayLists

### Advanced Options
Use advanced options to customize your downloads:
- `--limit-rate 5M` (limit to 5MB/s)
- `--geo-bypass` (bypass geo-restrictions)
- `--embed-thumbnail` (embed thumbnail in audio)

### This Project Location
- [GitHub](https://github.com/official-imvoiid/YouOwn)

### Cookies Editor (Brave / Chrome)
Following is a Great Cookie-Editor by Moustachauve:
- [Chrome WebStore](https://chromewebstore.google.com/detail/hlkenndednhfkekhgcdicdfddnkalmdm?utm_source=item-share-cb)
- [GitHub](https://github.com/Moustachauve/cookie-editor)
"""

def clean_temp_files(uid: str) -> None:
    """Clean up any temporary files created during the download process."""
    cookie_path = os.path.join(TEMP_DIR, f"cookies_{uid}.txt")
    if os.path.exists(cookie_path):
        try:
            os.remove(cookie_path)
            logger.info(f"Deleted temporary cookie file: {cookie_path}")
        except Exception as e:
            logger.error(f"Failed to delete cookie file: {e}")

def validate_inputs(url: str, out_dir: str) -> Tuple[bool, str]:
    """Validate user inputs before processing."""
    if not url or not url.strip():
        return False, "❌ URL cannot be empty!"
    
    if not out_dir or not out_dir.strip():
        return False, "❌ Output directory cannot be empty!"
    
    # Create output directory if it doesn't exist
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        return False, f"❌ Failed to create output directory: {e}"
    
    return True, ""

def download_stream(
    url: str, 
    out_dir: str, 
    audio_only: bool, 
    video_only: bool, 
    extra_args: str, 
    use_cookies: bool, 
    cookies_txt: str
) -> Generator[Tuple[str, float], None, None]:
    """Stream download progress from yt-dlp."""
    # Input validation
    is_valid, error_msg = validate_inputs(url, out_dir)
    if not is_valid:
        yield error_msg, 0.0
        return

    # Generate unique ID for this download
    uid = uuid.uuid4().hex[:8]
    out_tmpl = os.path.join(out_dir, f"%(title)s_{uid}.%(ext)s")
    
    # Determine format based on user selection
    if audio_only and video_only:
        yield "❌ Cannot select both 'Audio Only' and 'Video Only'", 0.0
        return
    
    fmt = ("bestaudio[ext=m4a]/bestaudio" if audio_only
           else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio" if video_only
           else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best")
    
    # Prepare command
    cmd: List[str] = ["yt-dlp", "-f", fmt, "-o", out_tmpl]
    
    if not audio_only:
        cmd += ["--merge-output-format", "mp4"]
    
    # Handle cookies if provided
    cookie_path = None
    if use_cookies and cookies_txt and cookies_txt.strip():
        try:
            cookie_path = os.path.join(TEMP_DIR, f"cookies_{uid}.txt")
            with open(cookie_path, "w") as f:
                f.write(cookies_txt)
            os.chmod(cookie_path, 0o600)  # Set secure permissions
            cmd += ["--cookies", cookie_path]
            yield "🔒 Using secure cookies (will be deleted after download)\n", 0.0
        except Exception as e:
            yield f"❌ Failed to process cookies: {e}", 0.0
            clean_temp_files(uid)
            return
    
    # Add extra arguments if provided
    if extra_args and extra_args.strip():
        cmd += extra_args.split()
    
    # Add URL
    cmd.append(url)
    
    # Execute command
    try:
        yield f"🚀 Starting download: {url}\n", 0.0
        logger.info(f"Executing command: {' '.join(cmd)}")
        proc = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1
        )
    except Exception as e:
        yield f"❌ Launch failed: {e}", 0.0
        clean_temp_files(uid)
        return

    # Stream progress
    output = ""
    if proc.stdout:
        for line in proc.stdout:
            output += line
            # Extract progress percentage
            m = re.search(r"\[download\]\s+([0-9.]+)%", line)
            prog = float(m.group(1))/100 if m else None
            
            # Format and yield the line with progress
            if prog is not None:
                yield output, prog
            else:
                yield output, 0.0
    
    # Wait for process to complete
    return_code = proc.wait()
    
    # Clean up temporary files
    if cookie_path:
        clean_temp_files(uid)
        yield f"{output}\n✅ Download completed. Cookies securely deleted.\n", 1.0
    else:
        yield f"{output}\n✅ Download completed.\n", 1.0
    
    # Log completion
    logger.info(f"Download completed with return code: {return_code}")

def bulk_wrapper(
    urls: str, 
    out_dir: str, 
    audio_only: bool, 
    video_only: bool, 
    extra_args: str, 
    use_cookies: bool, 
    cookies_txt: str
) -> Generator[Tuple[str, float], None, None]:
    """Process multiple URLs from a list."""
    if not urls or not urls.strip():
        yield "❌ URL list cannot be empty!", 0.0
        return
        
    url_list = [line.strip() for line in urls.splitlines() if line.strip()]
    total_urls = len(url_list)
    
    if total_urls == 0:
        yield "❌ No valid URLs found!", 0.0
        return
    
    yield f"🔄 Processing {total_urls} URLs\n", 0.0
    
    for i, url in enumerate(url_list, 1):
        yield f"\n[{i}/{total_urls}] Processing: {url}\n", (i-1)/total_urls
        
        # Get generator for single download
        download_gen = download_stream(
            url, out_dir, audio_only, video_only, 
            extra_args, use_cookies, cookies_txt
        )
        
        # Process output from the generator
        output = ""
        for line, progress in download_gen:
            # Calculate overall progress
            overall_progress = ((i-1) + progress) / total_urls
            output = line
            yield f"[{i}/{total_urls}] {output}", overall_progress
    
    yield f"\n✅ All {total_urls} downloads completed!\n", 1.0

def generate_tunnel(port: str) -> str:
    """Generate a Cloudflare tunnel for remote access."""
    if not port or not port.strip() or not port.isdigit():
        return "❌ Invalid port number"
    
    cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}", "--no-autoupdate"]
    
    try:
        logger.info(f"Starting cloudflared tunnel on port {port}")
        proc = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True
        )
    except Exception as e:
        logger.error(f"Failed to start cloudflared: {e}")
        return f"❌ cloudflared failed: {e}"
    
    if proc.stdout:
        for line in proc.stdout:
            m = re.search(r"(https://[^\s]+\.trycloudflare\.com)", line)
            if m:
                tunnel_url = m.group(1)
                logger.info(f"Tunnel created: {tunnel_url}")
                return f"🔗 Tunnel URL: {tunnel_url}"
            
            # If cloudflared not found
            if "command not found" in line:
                return "❌ cloudflared not installed. Install with 'brew install cloudflared' (Mac) or download from Cloudflare website."
    
    return "❌ Tunnel creation failed. Check logs for details."

def show_readme() -> gr.Markdown:
    """Toggle README visibility."""
    return gr.update(value=README_CONTENT, visible=True)

def hide_readme() -> gr.Markdown:
    """Hide README content."""
    return gr.update(value="", visible=False)

# CSS for styling the UI
css = """
<style>
body {
    background-color: #121212;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
}
.warning-header {
    background: linear-gradient(135deg, #ff0057, #f9003f);
    color: white;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    font-size: 18px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(255,0,0,0.3);
    border: 2px solid #ff0000;
    font-weight: bold;
    animation: pulse 2s infinite;
    position: relative;
    overflow: hidden;
}
@keyframes pulse {
    0% { box-shadow: 0 0 8px rgba(255,0,0,0.5); }
    50% { box-shadow: 0 0 15px rgba(255,0,0,0.8); }
    100% { box-shadow: 0 0 8px rgba(255,0,0,0.5); }
}
.warning-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shine 3s infinite;
}
@keyframes shine {
    0% { left: -100%; }
    20% { left: 100%; }
    100% { left: 100%; }
}
.security-alert {
    background: linear-gradient(135deg, #ff0057, #d10000);
    color: white;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
    border: 2px solid #ff0000;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.danger-button {
    background: linear-gradient(135deg, #dc3545, #c01d2e) !important;
    color: white !important;
    border: 1px solid #ff0000 !important;
    font-weight: bold !important;
}
.danger-button:hover {
    background: linear-gradient(135deg, #c01d2e, #a01525) !important;
    box-shadow: 0 0 8px rgba(255,0,0,0.5) !important;
}
.cookie-note {
    font-size: 0.9em;
    color: #ff6666;
    margin-top: 10px;
    padding: 8px;
    background-color: rgba(255,0,0,0.1);
    border-radius: 4px;
}
.console-output {
    font-family: 'Courier New', monospace;
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #333;
}
.readme-button {
    background: linear-gradient(135deg, #4a90e2, #3677c5) !important;
    color: white !important;
    transition: all 0.3s ease;
}
.readme-button:hover {
    background: linear-gradient(135deg, #3677c5, #2d6ab4) !important;
    box-shadow: 0 0 8px rgba(74,144,226,0.5) !important;
}
.readme-close-button {
    background: linear-gradient(135deg, #6c757d, #5a6268) !important;
    color: white !important;
    margin-top: 10px;
    width: 100%;
}
.tab-active {
    border-bottom: 2px solid #4a90e2 !important;
}
</style>
"""

# Modify the download_stream function to handle progress tracking through output text
def download_stream_with_progress(
    url: str, 
    out_dir: str, 
    audio_only: bool, 
    video_only: bool, 
    extra_args: str, 
    use_cookies: bool, 
    cookies_txt: str
) -> str:
    """Modified version that uses text-based progress instead of gr.Progress"""
    output_text = ""
    
    # Process download and collect output
    for text, _ in download_stream(
        url, out_dir, audio_only, video_only, 
        extra_args, use_cookies, cookies_txt
    ):
        output_text = text
    
    return output_text

def bulk_wrapper_with_progress(
    urls: str, 
    out_dir: str, 
    audio_only: bool, 
    video_only: bool, 
    extra_args: str, 
    use_cookies: bool, 
    cookies_txt: str
) -> str:
    """Modified version that uses text-based progress instead of gr.Progress"""
    output_text = ""
    
    # Process download and collect output
    for text, _ in bulk_wrapper(
        urls, out_dir, audio_only, video_only, 
        extra_args, use_cookies, cookies_txt
    ):
        output_text = text
    
    return output_text

# Create the Gradio interface
with gr.Blocks(css=css, title="Secure Media Downloader") as app:
    gr.HTML('<div class="warning-header">⚠️ <b>FOR PERSONAL USE ONLY - DO NOT USE WITH MAIN ACCOUNTS</b> ⚠️ <br><span style="font-size: 16px;">Developed By VOIID</span></div>')
    
    with gr.Row():
        with gr.Column(scale=4):
            with gr.Tabs() as tabs:
                # Single Video Tab
                with gr.Tab("🎯 Single Download", id="single"):
                    url = gr.Textbox(
                        label="Video URL",
                        placeholder="https://www.youtube.com/watch?v=..."
                    )
                    
                    with gr.Row():
                        with gr.Column():
                            out_dir = gr.Textbox(
                                label="Save Location", 
                                value=DEFAULT_OUT_DIR,
                                placeholder="Path to save downloads"
                            )
                        with gr.Column():
                            with gr.Row():
                                audio_only = gr.Checkbox(label="Audio Only")
                                video_only = gr.Checkbox(label="Video Only")
                    
                    extra_args = gr.Textbox(
                        label="Advanced Options",
                        placeholder="--limit-rate 5M --geo-bypass"
                    )
                    
                    console = gr.Textbox(
                        label="Progress Log", 
                        lines=12,
                        elem_classes="console-output"
                    )
                    
                    gr.Button("⏬ Download").click(
                        fn=download_stream_with_progress,
                        inputs=[url, out_dir, audio_only, video_only,
                              extra_args, gr.Checkbox(False, visible=False), gr.Textbox("", visible=False)],
                        outputs=console
                    )

                # Bulk Download Tab
                with gr.Tab("📦 Bulk Download", id="bulk"):
                    bulk_urls = gr.Textbox(
                        label="URL List (One per line)", 
                        lines=8,
                        placeholder="https://www.youtube.com/watch?v=...\nhttps://Instagram.com/..."
                    )
                    
                    with gr.Row():
                        with gr.Column():
                            out_dir2 = gr.Textbox(
                                label="Save Location", 
                                value=DEFAULT_OUT_DIR
                            )
                        with gr.Column():
                            with gr.Row():
                                audio2 = gr.Checkbox(label="Audio Only")
                                video2 = gr.Checkbox(label="Video Only")
                    
                    extra2 = gr.Textbox(
                        label="Advanced Options",
                        placeholder="--limit-rate 5M --geo-bypass"
                    )
                    
                    console2 = gr.Textbox(
                        label="Progress Log", 
                        lines=12,
                        elem_classes="console-output"
                    )
                    
                    gr.Button("⏬ Start Bulk Download").click(
                        fn=bulk_wrapper_with_progress,
                        inputs=[bulk_urls, out_dir2, audio2, video2,
                              extra2, gr.Checkbox(False, visible=False), gr.Textbox("", visible=False)],
                        outputs=console2
                    )

                # Restricted Access Tab
                with gr.Tab("🔒 Restricted Content", id="restricted"):
                    gr.HTML(f'<div class="security-alert">{COOKIE_WARNING}</div>')
                    
                    with gr.Row():
                        with gr.Column():
                            cookies3 = gr.Textbox(
                                label="Cookies.txt Content",
                                lines=10,
                                placeholder="Paste Netscape-format cookies here\n\n# WARNING: Use temporary accounts only!",
                                info="Data will be destroyed after use!"
                            )
                            gr.HTML('<div class="cookie-note">💡 Browser extensions like "CookieEditor" or "EditThisCookie" can export cookies in NetScape Format</div>')
                        
                        with gr.Column():
                            url3 = gr.Textbox(
                                label="Protected URL (Youtube / Other Social Platform Age-Restricted Videos Etc...)",
                                placeholder="https://www.youtube.com/watch?v=..."
                            )
                            
                            with gr.Row():
                                with gr.Column():
                                    out_dir3 = gr.Textbox(
                                        label="Save Location", 
                                        value=DEFAULT_OUT_DIR
                                    )
                                with gr.Column():
                                    with gr.Row():
                                        audio3 = gr.Checkbox(label="Audio Only")
                                        video3 = gr.Checkbox(label="Video Only")
                            
                            extra3 = gr.Textbox(
                                label="Advanced Options",
                                placeholder="--limit-rate 5M --geo-bypass"
                            )
                    
                    console3 = gr.Textbox(
                        label="Security Log", 
                        lines=12,
                        elem_classes="console-output"
                    )
                    
                    gr.Button("⏬ Download Content (I Accept All Risks)", 
                             variant="stop", 
                             elem_classes="danger-button").click(
                        fn=download_stream_with_progress,
                        inputs=[url3, out_dir3, audio3, video3,
                              extra3, gr.Checkbox(True, visible=False), cookies3],
                        outputs=console3
                    )

                # Cloudflare Tunnel Tab
                with gr.Tab("☁️ Tunnel", id="tunnel"):
                    gr.Markdown("Generate public URL via Cloudflare for remote access")
                    
                    port_in = gr.Textbox(
                        label="Local Port", 
                        value="7860",
                        placeholder="Port number (e.g. 7860)"
                    )
                    
                    tunnel_out = gr.Textbox(
                        label="Public URL",
                        placeholder="Your tunnel URL will appear here"
                    )
                    
                    gr.Button("🔗 Create Tunnel").click(
                        fn=generate_tunnel,
                        inputs=port_in,
                        outputs=tunnel_out
                    )
        
        # Right side - README button and content with close button
        with gr.Column(scale=1):
            readme_button = gr.Button("📚 HELP / README", elem_classes="readme-button")
            with gr.Column(visible=False) as readme_container:
                readme_output = gr.Markdown(value="", elem_id="readme_content")
                close_button = gr.Button("Close Help", elem_classes="readme-close-button")
            
            readme_button.click(
                fn=lambda: [gr.update(visible=True), README_CONTENT],
                outputs=[readme_container, readme_output]
            )
            
            close_button.click(
                fn=lambda: gr.update(visible=False),
                outputs=readme_container
            )

    app.launch(share=False)
