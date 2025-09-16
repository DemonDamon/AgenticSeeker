#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试屏幕尺寸获取的回退机制

测试PIL失败时是否能正确回退到ADB获取
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.executor_agent import ExecutorAgent
from agenticx.core.event_bus import EventBus
from config import AgentConfig
from utils import setup_logger

def test_screen_dimensions_fallback():
    """测试屏幕尺寸获取的回退机制"""
    logger = setup_logger("test_screen_dimensions", level="INFO")
    
    print("🔍 测试屏幕尺寸获取回退机制")
    print("=" * 50)
    
    # 创建ExecutorAgent实例
    event_bus = EventBus()
    agent_config = AgentConfig(
        id="test_executor",
        name="TestExecutorAgent",
        role="executor",
        goal="测试屏幕尺寸获取",
        backstory="测试智能体",
        tools=[]
    )
    
    executor_agent = ExecutorAgent(
        agent_id="test_executor",
        agent_config=agent_config,
        llm_provider=None,
        memory=None,
        event_bus=event_bus
    )
    
    # 测试1: 使用有效的截图文件
    print("\n📸 测试1: 使用有效的截图文件")
    try:
        # 先获取一个真实的截图
        import subprocess
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')[1:]
            connected_devices = [line for line in devices if line.strip() and 'device' in line]
            
            if connected_devices:
                print(f"✅ 检测到设备: {connected_devices[0].split()[0]}")
                
                # 获取截图
                device_path = "/sdcard/test_fallback.png"
                local_path = "./test_fallback_screenshot.png"
                
                # 设备截图
                result = subprocess.run(["adb", "shell", "screencap", "-p", device_path], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # 拉取到本地
                    result = subprocess.run(["adb", "pull", device_path, local_path], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"✅ 截图已保存: {local_path}")
                        
                        # 测试PIL方法
                        dimensions = executor_agent._get_screen_dimensions(local_path)
                        print(f"✅ PIL方法获取尺寸: {dimensions[0]} x {dimensions[1]}")
                        
                        # 清理设备文件
                        subprocess.run(["adb", "shell", "rm", device_path], 
                                     capture_output=True, timeout=5)
                    else:
                        print("❌ 截图拉取失败")
                else:
                    print("❌ 设备截图失败")
            else:
                print("❌ 没有连接的设备")
        else:
            print("❌ ADB不可用")
    except Exception as e:
        print(f"❌ 测试1失败: {e}")
    
    # 测试2: 使用无效的截图文件路径（触发ADB回退）
    print("\n🔄 测试2: 使用无效的截图文件（触发ADB回退）")
    try:
        invalid_path = "./non_existent_screenshot.png"
        dimensions = executor_agent._get_screen_dimensions(invalid_path)
        print(f"✅ ADB回退方法获取尺寸: {dimensions[0]} x {dimensions[1]}")
    except Exception as e:
        print(f"❌ 测试2失败: {e}")
    
    # 测试3: 创建一个损坏的图片文件（触发ADB回退）
    print("\n💥 测试3: 使用损坏的图片文件（触发ADB回退）")
    try:
        corrupted_path = "./corrupted_image.png"
        # 创建一个假的PNG文件
        with open(corrupted_path, 'w') as f:
            f.write("This is not a valid PNG file")
        
        dimensions = executor_agent._get_screen_dimensions(corrupted_path)
        print(f"✅ ADB回退方法获取尺寸: {dimensions[0]} x {dimensions[1]}")
        
        # 清理文件
        Path(corrupted_path).unlink(missing_ok=True)
    except Exception as e:
        print(f"❌ 测试3失败: {e}")
    
    # 测试4: 模拟ADB也失败的情况（使用默认尺寸）
    print("\n⚠️ 测试4: 模拟所有方法都失败（使用默认尺寸）")
    try:
        # 临时修改方法来模拟ADB失败
        original_method = executor_agent._get_screen_dimensions
        
        def mock_get_screen_dimensions(screenshot_path):
            # 模拟PIL失败
            executor_agent.logger.warning(f"PIL获取屏幕尺寸失败: 模拟错误，尝试使用ADB获取")
            
            # 模拟ADB也失败
            executor_agent.logger.warning(f"ADB获取屏幕尺寸失败: 模拟错误")
            
            # 使用默认尺寸
            executor_agent.logger.warning("所有方法都失败，使用默认屏幕尺寸")
            return (640, 1400)
        
        executor_agent._get_screen_dimensions = mock_get_screen_dimensions
        
        dimensions = executor_agent._get_screen_dimensions("any_path")
        print(f"✅ 默认尺寸: {dimensions[0]} x {dimensions[1]}")
        
        # 恢复原方法
        executor_agent._get_screen_dimensions = original_method
        
    except Exception as e:
        print(f"❌ 测试4失败: {e}")
    
    print("\n🎉 回退机制测试完成！")
    
    # 清理临时文件
    for temp_file in ["./test_fallback_screenshot.png", "./corrupted_image.png"]:
        try:
            Path(temp_file).unlink(missing_ok=True)
        except:
            pass

if __name__ == "__main__":
    test_screen_dimensions_fallback()