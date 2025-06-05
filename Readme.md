# 🔐 YouOwn - Secure Media Downloader

## ⚠️ IMPORTANT DISCLAIMER

**FOR PERSONAL/PRIVATE USE ONLY!**

The developers are **NOT** responsible for:
- How you use this tool
- Any account bans or restrictions
- Any violations of terms of service

## 📋 Prerequisites

- **Python Version**: 3.10.6 - 3.11.9
- **Operating System**: Windows

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/official-imvoiid/YouOwn

# Navigate to the project directory
cd YouOwn

# Install dependencies
Install_requirements.bat

# Launch the WebUI
webui.bat
```

## 🛡️ Security Warnings

- ⚠️ **NEVER USE YOUR MAIN ACCOUNTS** ⚠️
- Always use alternate/temporary accounts when downloading restricted content
- Cookies contain sensitive authentication data that could compromise your account
- This tool **DOES NOT STORE** any cookie data
- All cookie data is **DELETED IMMEDIATELY** after use
- Misuse of cookies can result in **PERMANENT ACCOUNT BANS**

## 🔧 Features

- 🎯 **Single Video Downloads**: Download individual videos in highest quality
- 📦 **Bulk Downloads**: Process multiple URLs in one operation
- 🔒 **Restricted Content Access**: Download age-restricted or region-locked content
- ☁️ **Cloudflare Tunnel**: Generate public URLs for remote access
- 🔄 **Format Options**: Download video only, audio only, or both
- ⚙️ **Advanced Options**: Customize your downloads with extra parameters

## 💻 Interface Guide

### Single Download Tab
- Paste video URL
- Set download location
- Choose audio/video options
- Click Download

### Bulk Download Tab
- Enter one URL per line
- Configure options
- Start bulk download process

### Restricted Content Tab
- Paste Netscape-format cookies
- Enter protected URL
- Set download options
- Accept risks and download

### Cloudflare Tunnel Tab
- Enter local port (default: 7860)
- Create tunnel for remote access

## 🍪 Cookie Management

To download restricted content:

1. Install a cookie editor extension:
   - [Cookie Editor (Chrome/Brave)](https://chromewebstore.google.com/detail/hlkenndednhfkekhgcdicdfddnkalmdm)
   - [Cookie Editor (GitHub)](https://github.com/Moustachauve/cookie-editor)

2. Export cookies in Netscape format
3. Paste into the Restricted Content tab
4. **REMEMBER**: Use temporary accounts only!

## ⚡ Performance Notes

- Download times depend on:
  - Your network connection speed
  - Hardware capabilities
  - Server limitations
  - Video quality/size

## 🛠️ Advanced Usage

Use the Advanced Options field to customize downloads:

- `--limit-rate 5M` (limit download speed to 5MB/s)
- `--geo-bypass` (bypass geographic restrictions)
- `--embed-thumbnail` (embed thumbnail in audio files)
- `--no-check-certificate` (skip HTTPS verification)

## 📝 Contributing

Feel free to fork and contribute to this project! All contributions are welcome.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the core download functionality
- [Gradio](https://www.gradio.app/) for the web interface framework
- [FFmpeg](https://ffmpeg.org/) for media processing capabilities
- [Cloudflared](https://github.com/cloudflare/cloudflared) for tunneling capabilities

## ✅ Compatibility

Tested and working on:
- Windows 10/11
- 
## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**⭐ Developed by [VOIID](https://github.com/official-imvoiid) ⭐**
