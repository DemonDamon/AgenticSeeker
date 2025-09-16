#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕尺寸对比实验

对比PIL从截图获取的尺寸和ADB获取的设备分辨率的差异
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional

def get_adb_screen_resolution() -> Optional[Tuple[int, int]]:
    """使用ADB获取设备屏幕分辨率"""
    try:
        # 检查ADB连接
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ ADB设备未连接")
            return None
        
        devices = result.stdout.strip().split('\n')[1:]
        connected_devices = [line for line in devices if line.strip() and 'device' in line]
        if not connected_devices:
            print("❌ 没有检测到连接的设备")
            return None
        
        print(f"✅ 检测到设备: {connected_devices[0].split()[0]}")
        
        # 获取屏幕尺寸
        result = subprocess.run(["adb", "shell", "wm", "size"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            size_line = result.stdout.strip()
            print(f"📱 ADB原始输出: {size_line}")
            
            if "Physical size:" in size_line:
                size_part = size_line.split("Physical size:")[1].strip()
                width, height = map(int, size_part.split('x'))
                return (width, height)
            elif "Override size:" in size_line:
                # 有时候会有Override size
                size_part = size_line.split("Override size:")[1].strip()
                width, height = map(int, size_part.split('x'))
                return (width, height)
            else:
                print(f"⚠️ 无法解析屏幕尺寸输出: {size_line}")
                return None
        else:
            print(f"❌ 获取屏幕尺寸失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ ADB获取屏幕尺寸时出错: {e}")
        return None

def get_pil_screen_dimensions(screenshot_path: str) -> Optional[Tuple[int, int]]:
    """使用PIL从截图获取屏幕尺寸"""
    try:
        from PIL import Image
        with Image.open(screenshot_path) as img:
            return img.size  # (width, height)
    except ImportError:
        print("❌ PIL库未安装，请运行: pip install Pillow")
        return None
    except Exception as e:
        print(f"❌ PIL获取屏幕尺寸失败: {e}")
        return None

def take_adb_screenshot() -> Optional[str]:
    """使用ADB获取截图"""
    try:
        # 设备上截图
        device_path = "/sdcard/test_screenshot.png"
        local_path = "./test_screenshot_compare.png"
        
        print("📸 正在获取ADB截图...")
        
        # 1. 在设备上截图
        result = subprocess.run(["adb", "shell", "screencap", "-p", device_path], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"❌ 设备截图失败: {result.stderr}")
            return None
        
        # 2. 拉取到本地
        result = subprocess.run(["adb", "pull", device_path, local_path], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"❌ 截图拉取失败: {result.stderr}")
            return None
        
        # 3. 清理设备上的文件
        subprocess.run(["adb", "shell", "rm", device_path], 
                     capture_output=True, timeout=5)
        
        print(f"✅ 截图已保存到: {local_path}")
        return local_path
        
    except Exception as e:
        print(f"❌ ADB截图过程出错: {e}")
        return None

def get_adb_display_info() -> dict:
    """获取更详细的ADB显示信息"""
    info = {}
    
    try:
        # 获取显示密度
        result = subprocess.run(["adb", "shell", "wm", "density"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            density_line = result.stdout.strip()
            info['density'] = density_line
        
        # 获取显示信息
        result = subprocess.run(["adb", "shell", "dumpsys", "display"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            display_output = result.stdout
            # 提取关键信息
            lines = display_output.split('\n')
            for line in lines:
                if 'real' in line.lower() and ('x' in line or '×' in line):
                    info['real_size'] = line.strip()
                elif 'app' in line.lower() and ('x' in line or '×' in line):
                    info['app_size'] = line.strip()
                elif 'dpi' in line.lower():
                    info['dpi_info'] = line.strip()
        
        # 获取设备型号
        result = subprocess.run(["adb", "shell", "getprop", "ro.product.model"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            info['device_model'] = result.stdout.strip()
            
    except Exception as e:
        print(f"⚠️ 获取详细显示信息时出错: {e}")
    
    return info

def main():
    """主函数"""
    print("🔍 屏幕尺寸对比实验")
    print("=" * 50)
    
    # 1. 获取ADB屏幕分辨率
    print("\n📱 步骤1: 使用ADB获取屏幕分辨率")
    adb_resolution = get_adb_screen_resolution()
    if adb_resolution:
        print(f"✅ ADB屏幕分辨率: {adb_resolution[0]} x {adb_resolution[1]}")
    else:
        print("❌ ADB获取屏幕分辨率失败")
        return
    
    # 2. 获取详细的ADB显示信息
    print("\n📊 步骤2: 获取详细显示信息")
    display_info = get_adb_display_info()
    for key, value in display_info.items():
        print(f"  {key}: {value}")
    
    # 3. 获取ADB截图
    print("\n📸 步骤3: 获取ADB截图")
    screenshot_path = take_adb_screenshot()
    if not screenshot_path:
        print("❌ 无法获取截图，实验终止")
        return
    
    # 4. 使用PIL获取截图尺寸
    print("\n🖼️ 步骤4: 使用PIL分析截图尺寸")
    pil_dimensions = get_pil_screen_dimensions(screenshot_path)
    if pil_dimensions:
        print(f"✅ PIL截图尺寸: {pil_dimensions[0]} x {pil_dimensions[1]}")
    else:
        print("❌ PIL获取截图尺寸失败")
        return
    
    # 5. 对比分析
    print("\n📊 步骤5: 对比分析")
    print("=" * 30)
    print(f"ADB屏幕分辨率: {adb_resolution[0]} x {adb_resolution[1]}")
    print(f"PIL截图尺寸:   {pil_dimensions[0]} x {pil_dimensions[1]}")
    
    # 计算差异
    width_diff = abs(adb_resolution[0] - pil_dimensions[0])
    height_diff = abs(adb_resolution[1] - pil_dimensions[1])
    
    print(f"\n📏 尺寸差异:")
    print(f"  宽度差异: {width_diff} 像素")
    print(f"  高度差异: {height_diff} 像素")
    
    if width_diff == 0 and height_diff == 0:
        print("\n✅ 结论: ADB分辨率和PIL截图尺寸完全一致")
    else:
        print(f"\n⚠️ 结论: 存在差异")
        
        # 分析可能的原因
        print("\n🔍 可能的差异原因:")
        
        if width_diff > height_diff:
            print("  - 可能存在横竖屏坐标系差异")
        
        if width_diff > 100 or height_diff > 100:
            print("  - 可能存在DPI缩放差异")
            print("  - 可能存在虚拟导航栏影响")
        
        if width_diff < 50 and height_diff < 50:
            print("  - 差异较小，可能是状态栏/导航栏的影响")
        
        # 检查是否是横竖屏问题
        if (adb_resolution[0] == pil_dimensions[1] and 
            adb_resolution[1] == pil_dimensions[0]):
            print("  - 检测到横竖屏坐标系差异！")
    
    # 6. 生成建议
    print("\n💡 建议:")
    if width_diff == 0 and height_diff == 0:
        print("  - 两种方法结果一致，可以互换使用")
        print("  - PIL方法更快，ADB方法更准确反映设备真实分辨率")
    else:
        print("  - 建议优先使用ADB方法获取真实设备分辨率")
        print("  - PIL方法适合快速获取截图文件尺寸")
        print("  - 在坐标计算时需要考虑这些差异")
    
    print("\n🎉 实验完成！")
    
    # 清理临时文件
    try:
        Path(screenshot_path).unlink(missing_ok=True)
        print(f"🧹 已清理临时文件: {screenshot_path}")
    except:
        pass

if __name__ == "__main__":
    main()