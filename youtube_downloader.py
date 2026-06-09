#!/usr/bin/env python3
""" YD YouTube 视频下载器 v13.9.5 (重试逻辑优化版) - 双语版
更新:
1. 修复"重试失败链接"的逻辑顺序问题
2. 只有用户点击"是"确认重试，才会更新输入框内容
3. 点击"取消"时保留原输入框内容不变
4. 增加中英文切换功能
5. 语言切换按钮调整至右上角，点击直接切换
6. 修复初始加载时"就绪"等状态文字未随配置语言刷新的问题
7. 修复增加语言后导致下载及更新核心失效的严重问题
8. 修复不同URL同标题文件互相覆盖的问题 (文件名增加视频ID)
9. 统一软件顶部标题固定为中文
10. 修复 cx_Freeze 打包时 sys._MEIPASS 不兼容导致的启动卡死问题
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
import platform
from datetime import datetime
import webbrowser

# ============================================================
# 国际化 (i18n) 语言包
# ============================================================
class Languages:
    ZH_CN = "简体中文"
    EN_US = "English"
    TRANSLATIONS = {
        ZH_CN: {
            "app_title": "YD YouTube 视频下载器 v13.9.5",
            "lang_btn_text": "English",
            "url_frame_title": "视频链接 (每行一个)",
            "btn_clear": "清空",
            "btn_paste": "粘贴",
            "options_frame_title": "下载选项",
            "save_location": "保存位置:",
            "btn_browse": "浏览",
            "quality_label": "画质:",
            "audio_only": "仅下载音频(MP3)",
            "proxy_frame_title": "代理设置",
            "proxy_none": "不用代理",
            "proxy_system": "系统代理",
            "proxy_manual": "手动代理",
            "proxy_host": "主机:",
            "proxy_port": "端口:",
            "btn_test_proxy": "检测代理",
            "btn_start": "开始下载",
            "btn_stop": "停止",
            "btn_update": "更新/下载 yt-dlp",
            "status_loading": "正在加载组件...",
            "status_missing": "缺少组件",
            "status_ready": "就绪 (v{ver})",
            "status_corrupted": "文件损坏",
            "status_new_version": "有新版本 {ver}",
            "log_frame_title": "日志",
            "msg_init_error": "程序正在初始化，请稍后再试",
            "msg_missing_core": "缺少 yt-dlp，请先点击更新按钮下载核心组件",
            "msg_empty_url": "请输入视频链接",
            "msg_stop_success": "✓ 下载已强制停止",
            "msg_stop_error_prefix": "停止时出错: ",
            "msg_update_check": "开始检查更新...",
            "msg_update_success": "yt-dlp 更新成功！",
            "msg_update_fail_prefix": "更新失败：",
            "msg_update_fail_suffix": "\n请检查网络。",
            "msg_download_end": "下载结束",
            "msg_success_count": "成功: {count}",
            "msg_fail_count": "失败: {count}",
            "msg_retry_prompt": "\n检测到失败的链接，是否立即重试?",
            "log_checking_ver": "正在检测 yt-dlp 版本...",
            "log_ver_ready": "✓ yt-dlp 已就绪 (版本: {ver})",
            "log_ver_corrupted": "❌ yt-dlp 文件损坏，请删除后重新下载",
            "log_new_ver": "⚠ 发现新版本: {ver}",
            "log_ffmpeg_ready": "✓ FFmpeg 已就绪",
            "log_ffmpeg_missing": "⚠ 未找到 FFmpeg，高分辨率合并可能失败",
            "log_ytdlp_missing": "❌ 未找到 yt-dlp，请点击更新按钮下载",
            "log_start_process": "▶ 开始处理: {url}",
            "log_success": "✅ 成功: {url}",
            "log_fail": "❌ 失败: {url}",
            "log_interrupted": "⚠ 已中断: {url}",
            "log_error": "❌ 错误: {url} ({err})",
            "log_stopping": "正在强制停止下载...",
            "log_testing_proxy": "正在检测代理: {proxy}",
            "log_proxy_result": "代理检测结果: {msg}",
            "log_using_proxy": "使用代理: {proxy}",
            "log_downloading_ytdlp": "正在下载 yt-dlp...",
            "log_ytdlp_downloaded": "✓ yt-dlp 下载完成 ({size}MB)",
            "log_ytdlp_exe_perm": "✓ 已赋予执行权限",
            "log_updating_ytdlp": "正在启动 yt-dlp 自更新...",
            "log_ver_check_failed": "获取版本失败: {err}",
            "proxy_test_testing": "检测中...",
            "proxy_test_none": "未配置代理",
        },
        EN_US: {
            "app_title": "YD YouTube Video Downloader v13.9.5",
            "lang_btn_text": "简体中文",
            "url_frame_title": "Video URLs (one per line)",
            "btn_clear": "Clear",
            "btn_paste": "Paste",
            "options_frame_title": "Download Options",
            "save_location": "Save Location:",
            "btn_browse": "Browse",
            "quality_label": "Quality:",
            "audio_only": "Audio Only (MP3)",
            "proxy_frame_title": "Proxy Settings",
            "proxy_none": "No Proxy",
            "proxy_system": "System Proxy",
            "proxy_manual": "Manual Proxy",
            "proxy_host": "Host:",
            "proxy_port": "Port:",
            "btn_test_proxy": "Test Proxy",
            "btn_start": "Start Download",
            "btn_stop": "Stop",
            "btn_update": "Update/Download yt-dlp",
            "status_loading": "Loading components...",
            "status_missing": "Missing components",
            "status_ready": "Ready (v{ver})",
            "status_corrupted": "Corrupted file",
            "status_new_version": "New version {ver}",
            "log_frame_title": "Log",
            "msg_init_error": "Program is initializing, please try again later",
            "msg_missing_core": "Missing yt-dlp, please click the update button to download the core component",
            "msg_empty_url": "Please enter video URLs",
            "msg_stop_success": "✓ Download forcefully stopped",
            "msg_stop_error_prefix": "Error while stopping: ",
            "msg_update_check": "Checking for updates...",
            "msg_update_success": "yt-dlp updated successfully!",
            "msg_update_fail_prefix": "Update failed: ",
            "msg_update_fail_suffix": "\nPlease check your network.",
            "msg_download_end": "Download Finished",
            "msg_success_count": "Success: {count}",
            "msg_fail_count": "Failed: {count}",
            "msg_retry_prompt": "\nFailed URLs detected. Retry now?",
            "log_checking_ver": "Checking yt-dlp version...",
            "log_ver_ready": "✓ yt-dlp ready (Version: {ver})",
            "log_ver_corrupted": "❌ yt-dlp file is corrupted, please delete and redownload",
            "log_new_ver": "⚠ New version found: {ver}",
            "log_ffmpeg_ready": "✓ FFmpeg ready",
            "log_ffmpeg_missing": "⚠ FFmpeg not found, high-resolution merging may fail",
            "log_ytdlp_missing": "❌ yt-dlp not found, please click update button to download",
            "log_start_process": "▶ Start processing: {url}",
            "log_success": "✅ Success: {url}",
            "log_fail": "❌ Failed: {url}",
            "log_interrupted": "⚠ Interrupted: {url}",
            "log_error": "❌ Error: {url} ({err})",
            "log_stopping": "Forcefully stopping download...",
            "log_testing_proxy": "Testing proxy: {proxy}",
            "log_proxy_result": "Proxy test result: {msg}",
            "log_using_proxy": "Using proxy: {proxy}",
            "log_downloading_ytdlp": "Downloading yt-dlp...",
            "log_ytdlp_downloaded": "✓ yt-dlp downloaded ({size}MB)",
            "log_ytdlp_exe_perm": "✓ Execute permission granted",
            "log_updating_ytdlp": "Starting yt-dlp self-update...",
            "log_ver_check_failed": "Failed to get version: {err}",
            "proxy_test_testing": "Testing...",
            "proxy_test_none": "No proxy configured",
        }
    }

    @staticmethod
    def get(lang, key, **kwargs):
        text = Languages.TRANSLATIONS.get(lang, Languages.TRANSLATIONS[Languages.ZH_CN]).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text


# ============================================================
# 核心功能类 (完全保留原版内部逻辑)
# ============================================================
class ConfigManager:
    """配置管理器"""
    def __init__(self, config_file="config.json"):
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.base_dir, config_file)
        self.default_config = {
            "output_dir": os.path.join(self.base_dir, "downloads"),
            "proxy_mode": "system",
            "proxy_host": "127.0.0.1",
            "proxy_port": "7890",
            "video_quality": "best",
            "download_audio_only": False,
            "language": Languages.EN_US
        }
        self.config = self.load()

    def load(self):
        import json
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                for key in self.default_config:
                    if key not in loaded:
                        loaded[key] = self.default_config[key]
                return loaded
            except:
                return self.default_config.copy()
        return self.default_config.copy()

    def save(self):
        import json
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")


class ProxyDetector:
    """系统代理检测器"""
    @staticmethod
    def get_system_proxy():
        if platform.system() == 'Windows':
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
                proxy_enable = winreg.QueryValueEx(key, "ProxyEnable")[0]
                if proxy_enable:
                    proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
                    winreg.CloseKey(key)
                    if "=" in proxy_server:
                        for part in proxy_server.split(";"):
                            if "=" in part:
                                proto, addr = part.split("=")
                                if proto in ["http", "https"]:
                                    return f"http://{addr}"
                    else:
                        return f"http://{proxy_server}"
            except:
                pass
        for env_var in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"]:
            if os.environ.get(env_var):
                return os.environ[env_var]
        return None

    @staticmethod
    def test_proxy(proxy_url, timeout=5):
        import socket
        import urllib.request
        if not proxy_url:
            return False, "代理地址为空"
        try:
            proxy_addr = proxy_url.replace("http://", "").replace("socks5://", "")
            host, port = proxy_addr.split(":")
            port = int(port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            if result != 0:
                return False, f"端口 {port} 无法连接"
            start_time = datetime.now()
            proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            response = opener.open("https://www.google.com/favicon.ico", timeout=timeout)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            if response.status == 200:
                return True, f"正常 (延迟: {latency:.0f}ms)"
            return False, f"状态码: {response.status}"
        except Exception as e:
            return False, f"错误: {str(e)[:40]}"


class ToolFinder:
    """工具查找器 (跨平台/跨打包工具版)"""
    @staticmethod
    def find_ffmpeg():
        is_windows = platform.system() == 'Windows'
        exe_name = "ffmpeg.exe" if is_windows else "ffmpeg"

        # 1. 优先查找打包目录 (兼容 PyInstaller 和 cx_Freeze)
        if getattr(sys, 'frozen', False):
            # cx_Freeze 使用 sys.executable 所在目录, PyInstaller 使用 _MEIPASS
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            internal_exe = os.path.join(base_path, exe_name)
            if os.path.exists(internal_exe):
                return internal_exe

        # 2. 查找程序运行所在目录
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        local_exe = os.path.join(base_dir, exe_name)
        if os.path.exists(local_exe):
            return local_exe

        # 3. 查找系统环境变量
        import shutil
        return shutil.which("ffmpeg")


class YTDLPManager:
    """YT-DLP 核心管理器 (跨平台版) - 严格保留原版内部逻辑"""
    def __init__(self, base_dir, log_callback):
        self.base_dir = base_dir
        self.log = log_callback
        self.current_version = "未知"
        is_windows = platform.system() == 'Windows'
        exe_name = "yt-dlp.exe" if is_windows else "yt-dlp"
        self.exe_path = os.path.join(base_dir, exe_name)

    def check_exists(self):
        return os.path.exists(self.exe_path)

    def get_local_version(self):
        import subprocess
        if not self.check_exists():
            return None
        try:
            kwargs = {}
            if platform.system() == 'Windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(
                [self.exe_path, "--version"],
                capture_output=True,
                text=True,
                **kwargs
            )
            if result.returncode == 0:
                self.current_version = result.stdout.strip()
                return self.current_version
        except Exception as e:
            self.log(f"获取版本失败: {e}")
            return None

    def get_latest_version(self):
        import urllib.request
        import json
        try:
            url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get('tag_name', 'unknown')
        except:
            return None

    def update(self):
        import subprocess
        if not self.check_exists():
            return False, "yt-dlp 不存在"
        try:
            self.log("正在启动 yt-dlp 自更新...")
            kwargs = {}
            if platform.system() == 'Windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(
                [self.exe_path, "-U"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                **kwargs
            )
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.log(line.strip())
            if process.returncode == 0:
                self.get_local_version()
                return True, "更新完成"
            else:
                return False, "更新失败"
        except Exception as e:
            return False, f"更新异常: {str(e)}"

    def download_ytdlp(self, proxy_url=None):
        import urllib.request
        try:
            self.log("正在下载 yt-dlp...")
            is_windows = platform.system() == 'Windows'
            if is_windows:
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
            else:
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            if proxy_url:
                self.log(f"使用代理: {proxy_url}")
                proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
            with opener.open(req, timeout=120) as response:
                data = response.read()
            with open(self.exe_path, 'wb') as f:
                f.write(data)
            if not is_windows:
                import stat
                os.chmod(self.exe_path, os.stat(self.exe_path).st_mode | stat.S_IEXEC)
                self.log("✓ 已赋予执行权限")
            file_size = os.path.getsize(self.exe_path)
            if file_size < 5 * 1024 * 1024:
                os.remove(self.exe_path)
                return False, f"下载的文件不完整 ({file_size/1024:.0f}KB)，请重试"
            self.log(f"✓ yt-dlp 下载完成 ({file_size/1024/1024:.1f}MB)")
            return True, "下载完成"
        except Exception as e:
            return False, f"下载失败: {str(e)}"

    def build_command(self, url, output_dir, quality, audio_only, proxy, ffmpeg_path):
        cmd = [self.exe_path]
        cmd.extend([
            "--no-playlist",
            "--newline",
            "--no-mtime",
            # 修复：增加 %(id)s 防止不同URL同标题视频覆盖
            "-o", os.path.join(output_dir, "%(title)s.%(id)s.%(ext)s")
        ])
        if ffmpeg_path:
            cmd.extend(["--ffmpeg-location", os.path.dirname(ffmpeg_path)])
        if proxy:
            cmd.extend(["--proxy", proxy])
        if audio_only:
            cmd.extend([
                "-x", "--audio-format", "mp3", "--audio-quality", "192K"
            ])
        else:
            fmt = "bestvideo+bestaudio/best"
            if "8K" in quality:
                fmt = "bestvideo[vheight>2160]+bestaudio/best[vheight>2160]/best"
            elif "2160p" in quality:
                fmt = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
            elif "1440p" in quality:
                fmt = "bestvideo[height<=1440]+bestaudio/best[height<=1440]"
            elif "1080p" in quality:
                fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            elif "720p" in quality:
                fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
            elif "480p" in quality:
                fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"
            elif "360p" in quality:
                fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
            cmd.extend(["-f", fmt])
            if quality != "best":
                cmd.extend(["--merge-output-format", "mp4"])
        cmd.append(url)
        return cmd


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.config_manager = ConfigManager()
        self.lang = self.config_manager.config.get("language", Languages.ZH_CN)
        self.root.title(self.t("app_title"))
        self.root.geometry("920x750")
        
        # 设置窗口图标
        icon_path = os.path.join(self.config_manager.base_dir, "favicon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.ffmpeg_path = None
        self.ytdlp = None
        self.is_downloading = False
        self.process = None
        self.current_status_text = ""
        config = self.config_manager.config
        self.output_dir = tk.StringVar(value=config["output_dir"])
        self.proxy_mode = tk.StringVar(value=config["proxy_mode"])
        self.proxy_host = tk.StringVar(value=config["proxy_host"])
        self.proxy_port = tk.StringVar(value=config["proxy_port"])
        self.video_quality = tk.StringVar(value=config["video_quality"])
        self.download_audio_only = tk.BooleanVar(value=config["download_audio_only"])
        self.detected_system_proxy = None
        self.success_count = 0
        self.fail_count = 0
        self.failed_urls = []
        
        self.create_widgets()
        self.root.after(50, self.async_init_tasks)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def t(self, key, **kwargs):
        return Languages.get(self.lang, key, **kwargs)

    def async_init_tasks(self):
        try:
            self.ffmpeg_path = ToolFinder.find_ffmpeg()
            self.ytdlp = YTDLPManager(self.config_manager.base_dir, self.log_message)
            threading.Thread(target=self.auto_detect_system_proxy, daemon=True).start()
            threading.Thread(target=self.check_environment, daemon=True).start()
        except Exception as e:
            import traceback
            print(f"初始化异常: {traceback.format_exc()}")
            self.update_status_text("status_corrupted", "red")

    def on_closing(self):
        self.save_current_config()
        self.root.destroy()

    def save_current_config(self):
        self.config_manager.config["output_dir"] = self.output_dir.get()
        self.config_manager.config["proxy_mode"] = self.proxy_mode.get()
        self.config_manager.config["proxy_host"] = self.proxy_host.get()
        self.config_manager.config["proxy_port"] = self.proxy_port.get()
        self.config_manager.config["video_quality"] = self.video_quality.get()
        self.config_manager.config["download_audio_only"] = self.download_audio_only.get()
        self.config_manager.config["language"] = self.lang
        self.config_manager.save()

    def show_settings_menu(self):
        self.settings_menu.post(self.settings_btn.winfo_rootx(),
                                self.settings_btn.winfo_rooty() + self.settings_btn.winfo_height())

    def switch_language(self):
        if self.lang == Languages.ZH_CN:
            self.lang = Languages.EN_US
        else:
            self.lang = Languages.ZH_CN
        self.settings_menu.entryconfig(0, label=self.t("lang_btn_text"))
        self.settings_menu.entryconfig(1, label=("About" if self.lang == Languages.EN_US else "关于"))
        self.settings_menu.entryconfig(2, label=("LICENSE" if self.lang == Languages.EN_US else "许可证"))
        self.settings_menu.entryconfig(3, label=("Check for Updates" if self.lang == Languages.EN_US else "查看更新"))
        self.settings_menu.entryconfig(4, label=("Support Me!" if self.lang == Languages.EN_US else "支持我！"))
        self.settings_btn.config(text=("Settings" if self.lang == Languages.EN_US else "设置"))
        self.root.title(self.t("app_title"))
        self.update_ui_language()
        self.save_current_config()

    def show_about(self):
        webbrowser.open("https://github.com/xinpenghan/YD-YoutubeDownloader")

    def show_license(self):
        license_file = os.path.join(self.config_manager.base_dir, "LICENSE.txt")
        if os.path.exists(license_file):
            try:
                with open(license_file, 'r', encoding='utf-8') as f:
                    license_content = f.read()
                license_window = tk.Toplevel(self.root)
                license_window.title(("LICENSE" if self.lang == Languages.EN_US else "许可证"))
                license_window.geometry("600x400")
                text_widget = scrolledtext.ScrolledText(license_window, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True)
                text_widget.insert(tk.END, license_content)
                text_widget.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror(("Error" if self.lang == Languages.EN_US else "错误"),
                                     f"Failed to read LICENSE.txt: {str(e)}" if self.lang == Languages.EN_US else f"无法读取 LICENSE.txt: {str(e)}")
        else:
            messagebox.showwarning(("Warning" if self.lang == Languages.EN_US else "提示"),
                                   "LICENSE.txt not found in the application directory." if self.lang == Languages.EN_US else "在应用程序目录中未找到 LICENSE.txt 文件。")

    def open_github(self):
        webbrowser.open("https://github.com/xinpenghan/YD-YoutubeDownloader/releases")

    def support_me(self):
        webbrowser.open("https://www.paypal.com/ncp/payment/E3KMAPWSR2X3S")

    def update_ui_language(self):
        self.root.title(self.t("app_title"))
        self.url_frame.config(text=self.t("url_frame_title"))
        self.btn_clear.config(text=self.t("btn_clear"))
        self.btn_paste.config(text=self.t("btn_paste"))
        self.options_frame.config(text=self.t("options_frame_title"))
        self.save_location_label.config(text=self.t("save_location"))
        self.btn_browse.config(text=self.t("btn_browse"))
        self.quality_label.config(text=self.t("quality_label"))
        self.audio_only_check.config(text=self.t("audio_only"))
        self.proxy_frame.config(text=self.t("proxy_frame_title"))
        self.proxy_none_radio.config(text=self.t("proxy_none"))
        self.proxy_system_radio.config(text=self.t("proxy_system"))
        self.proxy_manual_radio.config(text=self.t("proxy_manual"))
        self.proxy_host_label.config(text=self.t("proxy_host"))
        self.proxy_port_label.config(text=self.t("proxy_port"))
        self.btn_test_proxy.config(text=self.t("btn_test_proxy"))
        self.btn_start.config(text=self.t("btn_start"))
        self.btn_stop.config(text=self.t("btn_stop"))
        self.btn_update.config(text=self.t("btn_update"))
        self.log_frame.config(text=self.t("log_frame_title"))
        self.settings_btn.config(text=("Settings" if self.lang == Languages.EN_US else "设置"))
        if self.current_status_text:
            self.update_status_text(
                self.current_status_text["key"],
                self.current_status_text["fg"],
                **self.current_status_text.get("kwargs", {})
            )

    def update_status_text(self, key, fg_color, **kwargs):
        text = self.t(key, **kwargs)
        self.status_label.config(text=text, foreground=fg_color)
        self.current_status_text = {"key": key, "fg": fg_color, "kwargs": kwargs}

    def check_environment(self):
        if self.ffmpeg_path:
            self.log_message(self.t("log_ffmpeg_ready"))
        else:
            self.log_message(self.t("log_ffmpeg_missing"))
        if not self.ytdlp.check_exists():
            self.log_message(self.t("log_ytdlp_missing"))
            self.root.after(0, lambda: self.update_status_text("status_missing", "red"))
        else:
            self.log_message(self.t("log_checking_ver"))
            ver = self.ytdlp.get_local_version()
            if ver:
                self.log_message(self.t("log_ver_ready", ver=ver))
                self.root.after(0, lambda: self.update_status_text("status_ready", "green", ver=ver))
                threading.Thread(target=self._check_latest_version, daemon=True).start()
            else:
                self.log_message(self.t("log_ver_corrupted"))
                self.root.after(0, lambda: self.update_status_text("status_corrupted", "red"))

    def _check_latest_version(self):
        latest = self.ytdlp.get_latest_version()
        if latest and latest != self.ytdlp.current_version:
            self.log_message(self.t("log_new_ver", ver=latest))
            self.root.after(0, lambda: self.update_status_text("status_new_version", "orange", ver=latest))

    def log_message(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        def update():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        if threading.current_thread() is threading.main_thread():
            update()
        else:
            self.root.after(0, update)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # --- 顶部栏 ---
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        top_frame.columnconfigure(0, weight=1)
        self.settings_menu = tk.Menu(top_frame, tearoff=0)
        self.settings_menu.add_command(label=self.t("lang_btn_text"), command=self.switch_language)
        self.settings_menu.add_command(label=("About" if self.lang == Languages.EN_US else "关于"), command=self.show_about)
        self.settings_menu.add_command(label=("LICENSE" if self.lang == Languages.EN_US else "许可证"), command=self.show_license)
        self.settings_menu.add_command(label=("Check for Updates" if self.lang == Languages.EN_US else "查看更新"), command=self.open_github)
        self.settings_menu.add_command(label=("Support Me!" if self.lang == Languages.EN_US else "支持我！"), command=self.support_me)
        self.settings_btn = ttk.Button(top_frame, text=("Settings" if self.lang == Languages.EN_US else "设置"),
                                       command=self.show_settings_menu)
        self.settings_btn.grid(row=0, column=1, sticky=tk.E)

        # --- 链接输入 ---
        url_frame = ttk.LabelFrame(main_frame, text=self.t("url_frame_title"), padding="10")
        url_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.url_frame = url_frame
        url_frame.columnconfigure(0, weight=1)
        url_frame.rowconfigure(0, weight=1)
        self.url_text = scrolledtext.ScrolledText(url_frame, height=3, font=('Arial', 10))
        self.url_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        btn_frame = ttk.Frame(url_frame)
        btn_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.btn_clear = ttk.Button(btn_frame, text=self.t("btn_clear"), command=lambda: self.url_text.delete(1.0, tk.END))
        self.btn_clear.grid(row=0, column=0, padx=5)
        self.btn_paste = ttk.Button(btn_frame, text=self.t("btn_paste"), command=self.paste_clipboard)
        self.btn_paste.grid(row=0, column=1, padx=5)

        # --- 选项 ---
        options_frame = ttk.LabelFrame(main_frame, text=self.t("options_frame_title"), padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        self.options_frame = options_frame
        self.save_location_label = ttk.Label(options_frame, text=self.t("save_location"))
        self.save_location_label.grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.btn_browse = ttk.Button(options_frame, text=self.t("btn_browse"), command=self.browse_dir)
        self.btn_browse.grid(row=0, column=2)
        self.quality_label = ttk.Label(options_frame, text=self.t("quality_label"))
        self.quality_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        quality_combo = ttk.Combobox(options_frame, textvariable=self.video_quality, width=15, state="readonly")
        quality_combo['values'] = ('best', '8K', '2160p (4K)', '1440p (2K)', '1080p', '720p', '480p', '360p')
        quality_combo.grid(row=1, column=1, sticky=tk.W)
        self.audio_only_check = ttk.Checkbutton(options_frame, text=self.t("audio_only"), variable=self.download_audio_only)
        self.audio_only_check.grid(row=2, column=0, columnspan=3, sticky=tk.W)
        options_frame.columnconfigure(1, weight=1)

        # --- 代理 ---
        proxy_frame = ttk.LabelFrame(main_frame, text=self.t("proxy_frame_title"), padding="10")
        proxy_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        self.proxy_frame = proxy_frame
        self.proxy_none_radio = ttk.Radiobutton(proxy_frame, text=self.t("proxy_none"), variable=self.proxy_mode, value="none")
        self.proxy_none_radio.grid(row=0, column=0, padx=5)
        self.proxy_system_radio = ttk.Radiobutton(proxy_frame, text=self.t("proxy_system"), variable=self.proxy_mode, value="system")
        self.proxy_system_radio.grid(row=0, column=1, padx=5)
        self.proxy_manual_radio = ttk.Radiobutton(proxy_frame, text=self.t("proxy_manual"), variable=self.proxy_mode, value="manual")
        self.proxy_manual_radio.grid(row=0, column=2, padx=5)
        manual_frame = ttk.Frame(proxy_frame)
        manual_frame.grid(row=1, column=0, columnspan=4, pady=5, sticky=tk.W)
        self.proxy_host_label = ttk.Label(manual_frame, text=self.t("proxy_host"))
        self.proxy_host_label.pack(side=tk.LEFT)
        self.proxy_host_entry = ttk.Entry(manual_frame, textvariable=self.proxy_host, width=12)
        self.proxy_host_entry.pack(side=tk.LEFT, padx=2)
        self.proxy_port_label = ttk.Label(manual_frame, text=self.t("proxy_port"))
        self.proxy_port_label.pack(side=tk.LEFT)
        self.proxy_port_entry = ttk.Entry(manual_frame, textvariable=self.proxy_port, width=6)
        self.proxy_port_entry.pack(side=tk.LEFT, padx=2)
        self.btn_test_proxy = ttk.Button(manual_frame, text=self.t("btn_test_proxy"), command=self.test_proxy_connection)
        self.btn_test_proxy.pack(side=tk.LEFT, padx=10)
        self.proxy_test_label = ttk.Label(manual_frame, text="", foreground="gray")
        self.proxy_test_label.pack(side=tk.LEFT, padx=5)

        # --- 控制按钮 ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, pady=10)
        self.btn_start = ttk.Button(control_frame, text=self.t("btn_start"), command=self.start_download, width=15)
        self.btn_start.grid(row=0, column=0, padx=10)
        self.btn_stop = ttk.Button(control_frame, text=self.t("btn_stop"), command=self.stop_download, state=tk.DISABLED, width=10)
        self.btn_stop.grid(row=0, column=1, padx=10)
        self.btn_update = ttk.Button(control_frame, text=self.t("btn_update"), command=self.update_ytdlp, width=15)
        self.btn_update.grid(row=0, column=2, padx=10)
        self.status_label = ttk.Label(control_frame, text=self.t("status_loading"), foreground="orange", font=('Arial', 9, 'bold'))
        self.status_label.grid(row=0, column=3, padx=10)

        # --- 日志 ---
        log_frame = ttk.LabelFrame(main_frame, text=self.t("log_frame_title"), padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        self.log_frame = log_frame
        log_frame.columnconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def browse_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def paste_clipboard(self):
        try:
            text = self.root.clipboard_get()
            self.url_text.insert(tk.END, text + "\n")
        except:
            pass

    def get_proxy(self):
        mode = self.proxy_mode.get()
        if mode == "none":
            return None
        if mode == "system":
            return self.detected_system_proxy
        return f"http://{self.proxy_host.get()}:{self.proxy_port.get()}"

    def auto_detect_system_proxy(self):
        self.detected_system_proxy = ProxyDetector.get_system_proxy()

    def test_proxy_connection(self):
        proxy_url = self.get_proxy()
        mode = self.proxy_mode.get()
        self.proxy_test_label.config(text=self.t("proxy_test_testing"), foreground="blue")
        self.log_message(self.t("log_testing_proxy", proxy=proxy_url if proxy_url else '无'))
        def do_test():
            if mode == "none":
                success, msg = False, self.t("proxy_test_none")
            else:
                success, msg = ProxyDetector.test_proxy(proxy_url)
            self.root.after(0, lambda: self.proxy_test_label.config(text=msg, foreground="green" if success else "red"))
            self.root.after(0, lambda: self.log_message(self.t("log_proxy_result", msg=msg)))
        threading.Thread(target=do_test, daemon=True).start()

    def update_ytdlp(self):
        if not self.ytdlp:
            messagebox.showerror(("Error" if self.lang == Languages.EN_US else "错误"), self.t("msg_init_error"))
            return
        self.log_message(self.t("msg_update_check"))
        self.btn_update.config(state=tk.DISABLED)
        self.save_current_config()
        current_proxy = self.get_proxy()
        threading.Thread(target=self._update_thread, args=(current_proxy,), daemon=True).start()

    def _update_thread(self, proxy_url):
        if not self.ytdlp.check_exists():
            success, msg = self.ytdlp.download_ytdlp(proxy_url)
        else:
            success, msg = self.ytdlp.update()
        self.root.after(0, lambda: self.btn_update.config(state=tk.NORMAL))
        if success:
            self.root.after(0, lambda: messagebox.showinfo(("Success" if self.lang == Languages.EN_US else "成功"), self.t("msg_update_success")))
            self.check_environment()
        else:
            self.log_message(f"❌ {msg}")
            self.root.after(0, lambda: messagebox.showwarning(("Failed" if self.lang == Languages.EN_US else "失败"), f"{self.t('msg_update_fail_prefix')}{msg}{self.t('msg_update_fail_suffix')}"))

    def start_download(self):
        if not self.ytdlp:
            messagebox.showerror(("Error" if self.lang == Languages.EN_US else "错误"), self.t("msg_init_error"))
            return
        if not self.ytdlp.check_exists():
            messagebox.showerror(("Error" if self.lang == Languages.EN_US else "错误"), self.t("msg_missing_core"))
            return
        urls = self.url_text.get(1.0, tk.END).strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        if not urls:
            messagebox.showwarning(("Warning" if self.lang == Languages.EN_US else "提示"), self.t("msg_empty_url"))
            return
        self.is_downloading = True
        self.success_count = 0
        self.fail_count = 0
        self.failed_urls = []
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.save_current_config()
        threading.Thread(target=self._download_thread, args=(urls,), daemon=True).start()

    def stop_download(self):
        self.is_downloading = False
        if self.process:
            try:
                self.log_message(self.t("log_stopping"))
                if platform.system() == 'Windows':
                    import ctypes
                    PROCESS_TERMINATE = 1
                    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, self.process.pid)
                    if handle:
                        ctypes.windll.kernel32.TerminateProcess(handle, -1)
                        ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    import signal
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.log_message(self.t("msg_stop_success"))
            except Exception as e:
                self.log_message(f"{self.t('msg_stop_error_prefix')}{str(e)}")
            try:
                self.process.kill()
            except:
                pass
            self.process = None

    def _download_thread(self, urls):
        import subprocess
        proxy = self.get_proxy()
        for url in urls:
            if not self.is_downloading:
                break
            self.log_message("=" * 60)
            self.log_message(self.t("log_start_process", url=url))
            self.log_message("-" * 60)
            cmd = self.ytdlp.build_command(
                url, self.output_dir.get(), self.video_quality.get(),
                self.download_audio_only.get(), proxy, self.ffmpeg_path
            )
            try:
                kwargs = {}
                if platform.system() == 'Windows':
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                self.process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kwargs
                )
                while True:
                    if not self.is_downloading:
                        break
                    line = self.process.stdout.readline()
                    if not line and self.process.poll() is not None:
                        break
                    if line:
                        self.log_message(line.strip())
                if self.is_downloading:
                    if self.process.returncode == 0:
                        self.success_count += 1
                        self.log_message(self.t("log_success", url=url))
                    else:
                        self.fail_count += 1
                        self.failed_urls.append(url)
                        self.log_message(self.t("log_fail", url=url))
                else:
                    self.fail_count += 1
                    self.failed_urls.append(url)
                    self.log_message(self.t("log_interrupted", url=url))
            except Exception as e:
                if self.is_downloading:
                    self.fail_count += 1
                    self.failed_urls.append(url)
                    self.log_message(self.t("log_error", url=url, err=str(e)))
            self.process = None
            self.log_message("=" * 60 + "\n")
        self.root.after(0, self._on_download_complete)

    def _on_download_complete(self):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        msg = f"{self.t('msg_download_end')}\n{self.t('msg_success_count', count=self.success_count)}\n{self.t('msg_fail_count', count=self.fail_count)}"
        if self.failed_urls:
            if messagebox.askyesno(self.t("msg_download_end"), msg + self.t("msg_retry_prompt")):
                self.url_text.delete(1.0, tk.END)
                self.url_text.insert(tk.END, "\n".join(self.failed_urls))
                self.start_download()
        else:
            messagebox.showinfo(("Finished" if self.lang == Languages.EN_US else "结束"), msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()