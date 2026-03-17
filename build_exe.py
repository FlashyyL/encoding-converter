#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for Encoding Converter
使用 PyInstaller 打包 exe 文件
"""

import os
import sys
import shutil
import subprocess


def clean_build():
    """清理之前的构建文件"""
    print("[INFO] - Cleaning previous build files...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['EncodingConverter.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"[INFO] - Removed {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"[INFO] - Removed {file_name}")


def build_exe():
    """使用 PyInstaller 打包 exe"""
    print("[INFO] - Starting build process...")
    
    # PyInstaller 参数
    cmd = [
        'python', '-m', 'PyInstaller',
        '--onefile',           # 打包成单个exe文件
        '--windowed',          # 不显示控制台窗口（GUI程序）
        '--name', 'EncodingConverter',  # 输出文件名
        '--hidden-import', 'chardet',   # 包含chardet依赖
        '--clean',             # 清理临时文件
        'main.py'
    ]
    
    print(f"[INFO] - Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("[INFO] - Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] - Build failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def verify_build():
    """验证构建结果"""
    exe_path = os.path.join('dist', 'EncodingConverter.exe')
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"[INFO] - Executable created: {exe_path}")
        print(f"[INFO] - File size: {size:.2f} MB")
        return True
    else:
        print("[ERROR] - Executable not found!")
        return False


def main():
    """主函数"""
    print("[INFO] - Encoding Converter Build Script")
    print("=" * 50)
    
    # 清理旧文件
    clean_build()
    
    # 执行打包
    if build_exe():
        # 验证结果
        if verify_build():
            print("\n" + "=" * 50)
            print("[INFO] - Build successful!")
            print(f"[INFO] - Output: dist/EncodingConverter.exe")
            print("[INFO] - You can distribute this file to users without Python installed")
        else:
            print("[ERROR] - Build verification failed!")
            sys.exit(1)
    else:
        print("[ERROR] - Build failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()