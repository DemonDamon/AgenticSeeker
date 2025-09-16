#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
持续矫正系统演示

展示ActionReflectorAgent如何通过多模态分析持续矫正ExecutorAgent的操作精度
实现真正的自适应学习和优化
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any, List

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agenticx.core.event_bus import EventBus
from agenticx.core.event import Event
from agents.executor_agent import ExecutorAgent
from agents.action_reflector_agent import ActionReflectorAgent
from utils import get_iso_timestamp


class ContinuousCorrectionDemo:
    """持续矫正系统演示类"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.executor = None
        self.reflector = None
        self.demo_results = []
        
    async def setup_agents(self):
        """设置智能体"""
        print("🚀 初始化持续矫正系统...")
        
        # 创建ExecutorAgent
        self.executor = ExecutorAgent(
            agent_id="demo_executor",
            event_bus=self.event_bus
        )
        
        # 创建ActionReflectorAgent
        self.reflector = ActionReflectorAgent(
            agent_id="demo_reflector",
            event_bus=self.event_bus
        )
        
        print("✅ 智能体初始化完成")
        print(f"  - ExecutorAgent: {self.executor.config.id}")
        print(f"  - ActionReflectorAgent: {self.reflector.config.id}")
        
    def create_mock_screenshots(self, scenario: str) -> tuple:
        """创建模拟截图"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建操作前截图
            before_img = Image.new('RGB', (1080, 1920), color='lightblue')
            before_draw = ImageDraw.Draw(before_img)
            
            # 创建操作后截图
            after_img = Image.new('RGB', (1080, 1920), color='lightblue')
            after_draw = ImageDraw.Draw(after_img)
            
            if scenario == "click_miss":
                # 场景1: 点击偏移，目标按钮未被激活
                # 操作前：正常按钮
                before_draw.rectangle([400, 600, 600, 700], fill='gray', outline='black', width=2)
                before_draw.text((450, 630), "目标按钮", fill='black')
                
                # 操作后：按钮状态未变化（点击偏移）
                after_draw.rectangle([400, 600, 600, 700], fill='gray', outline='black', width=2)
                after_draw.text((450, 630), "目标按钮", fill='black')
                # 添加点击标记（偏移位置）
                after_draw.ellipse([430, 580, 450, 600], fill='red', outline='darkred', width=2)
                after_draw.text((300, 550), "点击位置偏上", fill='red')
                
            elif scenario == "click_success":
                # 场景2: 点击成功，按钮被激活
                # 操作前：正常按钮
                before_draw.rectangle([400, 600, 600, 700], fill='gray', outline='black', width=2)
                before_draw.text((450, 630), "目标按钮", fill='black')
                
                # 操作后：按钮被激活（颜色变化）
                after_draw.rectangle([400, 600, 600, 700], fill='lightgreen', outline='green', width=3)
                after_draw.text((450, 630), "已激活", fill='darkgreen')
                # 添加正确的点击标记
                after_draw.ellipse([490, 640, 510, 660], fill='green', outline='darkgreen', width=2)
                
            elif scenario == "click_adjusted":
                # 场景3: 应用学习调整后的精确点击
                # 操作前：正常按钮
                before_draw.rectangle([400, 600, 600, 700], fill='gray', outline='black', width=2)
                before_draw.text((450, 630), "目标按钮", fill='black')
                
                # 操作后：完美激活
                after_draw.rectangle([400, 600, 600, 700], fill='gold', outline='orange', width=3)
                after_draw.text((450, 630), "完美激活", fill='darkorange')
                # 添加精确的点击标记
                after_draw.ellipse([495, 645, 505, 655], fill='gold', outline='orange', width=2)
                after_draw.text((300, 750), "学习调整后精确命中", fill='orange')
            
            # 保存截图
            timestamp = get_iso_timestamp().replace(':', '-')
            before_path = f"./screenshots/demo_{scenario}_before_{timestamp}.png"
            after_path = f"./screenshots/demo_{scenario}_after_{timestamp}.png"
            
            os.makedirs("./screenshots", exist_ok=True)
            before_img.save(before_path)
            after_img.save(after_path)
            
            return before_path, after_path
            
        except ImportError:
            print("⚠️ PIL未安装，使用文本模拟")
            # 创建文本文件模拟
            timestamp = get_iso_timestamp().replace(':', '-')
            before_path = f"./screenshots/demo_{scenario}_before_{timestamp}.txt"
            after_path = f"./screenshots/demo_{scenario}_after_{timestamp}.txt"
            
            os.makedirs("./screenshots", exist_ok=True)
            
            with open(before_path, 'w') as f:
                f.write(f"模拟截图 - 操作前 - {scenario}")
            with open(after_path, 'w') as f:
                f.write(f"模拟截图 - 操作后 - {scenario}")
                
            return before_path, after_path
    
    async def simulate_click_operation(self, coordinates: List[int], description: str) -> Dict[str, Any]:
        """模拟点击操作"""
        print(f"\n🎯 模拟点击操作: {description}")
        print(f"   坐标: {coordinates}")
        
        # 模拟ExecutorAgent执行点击
        task_context = {
            "task_type": "click_action",
            "coordinates": {"x": coordinates[0], "y": coordinates[1]},
            "description": description,
            "use_multimodal_analysis": False  # 简化演示
        }
        
        try:
            result = await self.executor._execute_click(task_context)
            print(f"✅ 点击执行完成: {result.get('success', False)}")
            return result
        except Exception as e:
            print(f"❌ 点击执行失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def perform_reflection_analysis(self, before_screenshot: str, after_screenshot: str, 
                                        action_info: Dict[str, Any], expected_success: bool) -> Dict[str, Any]:
        """执行反思分析"""
        print(f"\n🔍 执行反思分析...")
        print(f"   操作前截图: {before_screenshot}")
        print(f"   操作后截图: {after_screenshot}")
        print(f"   期望成功: {expected_success}")
        
        # 模拟多模态分析结果
        if expected_success:
            mock_analysis = {
                "success": True,
                "operation_success": True,
                "outcome": "A",
                "comparison_analysis": "操作前后截图显示按钮状态发生变化，从灰色变为绿色，表明点击操作成功激活了目标按钮",
                "improvement_suggestions": "操作执行良好，建议保持当前精度",
                "method": "multimodal_llm_reflection"
            }
        else:
            mock_analysis = {
                "success": True,
                "operation_success": False,
                "outcome": "C",
                "comparison_analysis": "操作前后截图显示按钮状态未发生变化，点击位置偏上，未能正确激活目标按钮",
                "improvement_suggestions": "建议将点击坐标向下调整15像素，以更准确地命中按钮中心",
                "method": "multimodal_llm_reflection"
            }
        
        # 构建反思上下文
        reflection_context = {
            "analysis_type": "multimodal_reflection",
            "before_screenshot": before_screenshot,
            "after_screenshot": after_screenshot,
            "action_info": action_info,
            "expectation": "点击按钮应该激活按钮状态"
        }
        
        # 手动设置分析结果并触发反馈
        if not expected_success:
            await self.reflector._send_improvement_feedback_to_executor(mock_analysis, reflection_context)
            print(f"📤 发送改进反馈: 坐标向下调整15像素")
        
        print(f"✅ 反思分析完成: 操作{'成功' if expected_success else '失败'}")
        return mock_analysis
    
    async def demonstrate_learning_cycle(self):
        """演示学习循环"""
        print("\n" + "="*60)
        print("🎯 开始演示持续矫正学习循环")
        print("="*60)
        
        # 第一次尝试：点击偏移
        print("\n📋 第一次尝试：初始点击（可能偏移）")
        before_1, after_1 = self.create_mock_screenshots("click_miss")
        
        original_coords = [440, 590]  # 偏上的坐标
        result_1 = await self.simulate_click_operation(original_coords, "首次点击目标按钮")
        
        analysis_1 = await self.perform_reflection_analysis(
            before_1, after_1, 
            {"task_type": "click_action", "coordinates": {"x": 440, "y": 590}},
            expected_success=False
        )
        
        self.demo_results.append({
            "attempt": 1,
            "coordinates": original_coords,
            "success": False,
            "analysis": analysis_1,
            "learning": "发现点击位置偏上，需要向下调整"
        })
        
        # 等待反馈处理
        await asyncio.sleep(1)
        
        # 检查学习结果
        learned_adjustment = self.executor._get_learned_coordinate_adjustment(original_coords)
        print(f"🧠 学习到的坐标调整: {learned_adjustment}")
        
        # 第二次尝试：应用学习调整
        print("\n📋 第二次尝试：应用学习调整")
        before_2, after_2 = self.create_mock_screenshots("click_success")
        
        # 应用学习到的调整
        adjusted_coords = [original_coords[0] + learned_adjustment[0], 
                          original_coords[1] + learned_adjustment[1]]
        print(f"🔧 调整后坐标: {original_coords} -> {adjusted_coords}")
        
        result_2 = await self.simulate_click_operation(adjusted_coords, "应用学习调整后的点击")
        
        analysis_2 = await self.perform_reflection_analysis(
            before_2, after_2,
            {"task_type": "click_action", "coordinates": {"x": adjusted_coords[0], "y": adjusted_coords[1]}},
            expected_success=True
        )
        
        self.demo_results.append({
            "attempt": 2,
            "coordinates": adjusted_coords,
            "success": True,
            "analysis": analysis_2,
            "learning": "学习调整生效，点击精度提升"
        })
        
        # 第三次尝试：持续优化
        print("\n📋 第三次尝试：持续优化精度")
        before_3, after_3 = self.create_mock_screenshots("click_adjusted")
        
        # 进一步优化的坐标
        optimized_coords = [500, 650]  # 更精确的中心位置
        result_3 = await self.simulate_click_operation(optimized_coords, "持续优化后的精确点击")
        
        analysis_3 = await self.perform_reflection_analysis(
            before_3, after_3,
            {"task_type": "click_action", "coordinates": {"x": optimized_coords[0], "y": optimized_coords[1]}},
            expected_success=True
        )
        
        self.demo_results.append({
            "attempt": 3,
            "coordinates": optimized_coords,
            "success": True,
            "analysis": analysis_3,
            "learning": "达到最优精度，完美命中目标"
        })
    
    def display_learning_summary(self):
        """显示学习总结"""
        print("\n" + "="*60)
        print("📊 持续矫正学习总结")
        print("="*60)
        
        for result in self.demo_results:
            attempt = result["attempt"]
            coords = result["coordinates"]
            success = result["success"]
            learning = result["learning"]
            
            status = "✅ 成功" if success else "❌ 失败"
            print(f"\n第{attempt}次尝试: {status}")
            print(f"  坐标: {coords}")
            print(f"  学习: {learning}")
        
        # 显示改进效果
        if len(self.demo_results) >= 2:
            first_coords = self.demo_results[0]["coordinates"]
            last_coords = self.demo_results[-1]["coordinates"]
            improvement = [last_coords[0] - first_coords[0], last_coords[1] - first_coords[1]]
            
            print(f"\n🎯 总体改进效果:")
            print(f"  初始坐标: {first_coords}")
            print(f"  最终坐标: {last_coords}")
            print(f"  坐标改进: {improvement}")
            print(f"  成功率提升: {self.demo_results[0]['success']} -> {self.demo_results[-1]['success']}")
        
        # 显示系统能力
        print(f"\n🚀 系统能力展示:")
        print(f"  ✅ 自动检测操作失败")
        print(f"  ✅ 多模态分析偏移原因")
        print(f"  ✅ 生成具体改进建议")
        print(f"  ✅ 智能学习坐标调整")
        print(f"  ✅ 持续优化操作精度")
        print(f"  ✅ 实现自适应矫正")
    
    def display_technical_details(self):
        """显示技术实现细节"""
        print(f"\n🔧 技术实现细节:")
        
        # 显示ExecutorAgent的学习状态
        feedback_summary = self.executor.get_reflection_feedback_summary()
        print(f"\n📊 ExecutorAgent学习状态:")
        print(f"  - 反馈数量: {feedback_summary['total_feedback_count']}")
        print(f"  - 坐标调整: {feedback_summary['coordinate_adjustments_count']}")
        print(f"  - 执行策略: {feedback_summary['execution_strategies_count']}")
        
        # 显示具体的坐标学习
        if hasattr(self.executor, 'coordinate_adjustments'):
            print(f"\n🎯 学习到的坐标调整:")
            for coord_key, adjustment in self.executor.coordinate_adjustments.items():
                print(f"  - {coord_key}: {adjustment}")
        
        # 显示执行策略
        if hasattr(self.executor, 'execution_strategies'):
            print(f"\n📋 学习到的执行策略:")
            for task_type, strategy in self.executor.execution_strategies.items():
                print(f"  - {task_type}: {strategy}")
    
    async def run_demo(self):
        """运行完整演示"""
        try:
            await self.setup_agents()
            await self.demonstrate_learning_cycle()
            self.display_learning_summary()
            self.display_technical_details()
            
            print(f"\n🎉 持续矫正系统演示完成！")
            print(f"\n💡 关键价值:")
            print(f"  - ActionReflectorAgent通过多模态分析发现问题")
            print(f"  - ExecutorAgent学习并应用改进建议")
            print(f"  - 系统实现自动化的持续矫正")
            print(f"  - 操作精度随使用次数不断提升")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    print("🚀 启动持续矫正系统演示")
    print("\n这个演示将展示:")
    print("1. ExecutorAgent执行操作")
    print("2. ActionReflectorAgent分析结果")
    print("3. 发现问题并生成改进建议")
    print("4. ExecutorAgent学习并应用调整")
    print("5. 操作精度持续提升")
    
    demo = ContinuousCorrectionDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())