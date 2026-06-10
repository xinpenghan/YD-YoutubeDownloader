from cx_Freeze import setup, Executable
import sys

# 必须显式包含 Tkinter 相关模块
build_exe_options = {
    "packages": ["tkinter", "tkinter.ttk", "tkinter.filedialog", "tkinter.messagebox", "json", "threading", "urllib", "zipfile", "shutil", "pathlib"],
    "include_files": ["favicon.ico", "LICENSE.txt"],  # 若文件存在则打包，不存在可删此行
    "optimize": 2,
    "silent_level": 2
}

setup(
    name="YD youtube_downloader",
    version="1.3.9.5",
    description="YD youtube_downloader",
    copyright="Copyright © 2026 xinpenghan. All rights reserved.",  # ⭐ 新增版权信息
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "youtube_downloader.py",
        base="Win32GUI",          # ⭐ 隐藏控制台窗口（GUI 必备）
        icon="favicon.ico",       # 替换为你的实际图标文件名
        target_name="YD youtube_downloader.exe"
    )]
)