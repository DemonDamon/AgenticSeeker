# AgenticSeeker 移动GUI智能体系统 - 环境搭建与运行指南

## 项目概述

AgenticSeeker 是一个基于 AgenticX 框架构建的移动 GUI 智能体系统，支持通过自然语言操作 Android 设备。系统采用四智能体协作架构（Manager、Executor、ActionReflector、Notetaker），融合五阶段学习方法论，实现智能的移动设备自动化操作。

## 功能特性

- 🤖 **四智能体协作**: Manager负责任务规划，Executor执行GUI操作，ActionReflector反思优化，Notetaker记录知识
- 🎯 **自然语言操作**: 支持"帮我发微信给jennifer，说我今晚回家吃饭"等复杂任务
- 📱 **真机连接**: 基于ADB实现Android设备的真机操作
- 🧠 **多模态大模型**: 集成视觉理解和自然语言处理能力
- 📚 **五阶段学习**: 先验知识、引导探索、任务合成、使用优化、边缘情况处理
- 📊 **完整评估**: 性能监控、基准测试、报告生成

## 系统要求

### 硬件要求
- CPU: 4核心以上
- 内存: 8GB以上（推荐16GB）
- 存储: 10GB可用空间
- Android设备: 支持ADB调试的Android 8.0+设备

### 软件要求
- Python 3.8+
- Anaconda/Miniconda
- ADB (Android Debug Bridge) - 已安装
- Git

## 环境搭建步骤

### 1. 创建Conda环境

```bash
# 创建专用的conda环境
conda create -n agenticseeker python=3.9 -y

# 激活环境
conda activate agenticseeker

# 更新conda和pip
conda update conda -y
pip install --upgrade pip
```

### 2. 安装AgenticX框架

```bash
# 进入AgenticX根目录
cd /Users/damon/myWork/AgenticX

# 安装AgenticX框架（开发模式）
pip install -e .

# 验证安装
python -c "import agenticx; print('AgenticX安装成功')"
```

### 3. 安装AgenticSeeker依赖

```bash
# 进入AgenticSeeker目录
cd /Users/damon/myWork/AgenticX/examples/agenticx-for-ecloudcup/agenticx-for-ecloudcup/agenticseeker

# 安装项目依赖
pip install -r requirements.txt

# 安装额外的移动设备控制工具
pip install adbutils pure-python-adb

# 安装多模态模型支持
pip install openai-clip torch torchvision
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
nano .env  # 或使用你喜欢的编辑器
```

**必需配置的环境变量**:

```bash
# LLM配置（选择一个提供商）
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini

# 或者使用其他提供商
# LLM_PROVIDER=deepseek
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
```

### 5. 验证ADB连接

```bash
# 检查ADB版本
adb version

# 启动ADB服务
adb start-server

# 检查连接的设备
adb devices

# 应该看到类似输出：
# List of devices attached
# DEVICE_ID    device
```

### 6. 配置Android设备

1. **启用开发者选项**:
   - 设置 → 关于手机 → 连续点击"版本号"7次

2. **启用USB调试**:
   - 设置 → 开发者选项 → USB调试（开启）
   - 设置 → 开发者选项 → USB安装（开启）

3. **连接设备**:
   - 使用USB线连接设备到电脑
   - 在设备上授权USB调试

4. **验证连接**:
   ```bash
   adb devices
   # 确保设备显示为"device"状态
   ```

## 运行系统

### 1. 基本运行

```bash
# 激活conda环境
conda activate agenticseeker

# 进入项目目录
cd /Users/damon/myWork/AgenticX/examples/agenticx-for-ecloudcup/agenticx-for-ecloudcup/agenticseeker

# 运行系统
python main.py
```

### 2. 交互模式运行

```bash
# 启动交互模式
python main.py --interactive

# 系统启动后，可以输入自然语言指令：
# > 帮我发微信给jennifer，说我今晚回家吃饭
# > 打开抖音，搜索"美食"相关视频
# > 设置明天早上8点的闹钟
```

### 3. 任务执行模式

```bash
# 执行单个任务
python main.py --task "帮我发微信给jennifer，说我今晚回家吃饭"

# 从文件读取任务
python main.py --task-file tasks.txt

# 启用性能评估
python main.py --task "打开设置" --evaluate
```

### 4. 配置自定义参数

```bash
# 使用自定义配置文件
python main.py --config custom_config.yaml

# 设置日志级别
python main.py --log-level DEBUG

# 启用详细输出
python main.py --verbose
```

## 使用示例

### 示例1: 发送微信消息

```python
# 启动系统后输入：
"帮我发微信给jennifer，说我今晚回家吃饭"

# 系统执行流程：
# 1. Manager分析任务：打开微信 → 找到联系人 → 发送消息
# 2. Executor执行操作：点击微信图标 → 搜索jennifer → 输入消息 → 发送
# 3. ActionReflector验证：确认消息发送成功
# 4. Notetaker记录：保存操作经验和知识
```

### 示例2: 设置闹钟

```python
"设置明天早上8点的闹钟，备注是开会"

# 执行流程：
# 1. 打开时钟应用
# 2. 创建新闹钟
# 3. 设置时间为8:00
# 4. 添加备注"开会"
# 5. 保存闹钟
```

### 示例3: 复杂应用操作

```python
"打开抖音，搜索美食相关视频，点赞前3个视频"

# 执行流程：
# 1. 启动抖音应用
# 2. 点击搜索按钮
# 3. 输入"美食"关键词
# 4. 浏览搜索结果
# 5. 依次点赞前3个视频
```

## 系统架构说明

### 四智能体协作

1. **ManagerAgent (管理者)**:
   - 任务分析和分解
   - 执行计划制定
   - 智能体协调

2. **ExecutorAgent (执行者)**:
   - GUI操作执行
   - 设备控制
   - 实时反馈

3. **ActionReflectorAgent (反思者)**:
   - 操作结果验证
   - 错误检测和修正
   - 性能分析

4. **NotetakerAgent (记录者)**:
   - 知识捕获和存储
   - 经验积累
   - 学习优化

### 技术栈

- **框架**: AgenticX (智能体框架)
- **设备控制**: ADB + uiautomator2
- **视觉理解**: OpenCV + PIL
- **自然语言**: OpenAI GPT-4 / 其他LLM
- **学习引擎**: 自研五阶段学习算法
- **评估系统**: 基准测试 + 性能监控

## 故障排除

### 常见问题

1. **ADB连接失败**:
   ```bash
   # 重启ADB服务
   adb kill-server
   adb start-server
   
   # 检查设备授权
   adb devices
   ```

2. **依赖安装失败**:
   ```bash
   # 更新pip
   pip install --upgrade pip
   
   # 清理缓存
   pip cache purge
   
   # 重新安装
   pip install -r requirements.txt --force-reinstall
   ```

3. **LLM API调用失败**:
   - 检查API密钥是否正确
   - 验证网络连接
   - 确认API配额

4. **设备操作失败**:
   - 确认设备屏幕已解锁
   - 检查应用是否已安装
   - 验证设备权限设置

### 日志调试

```bash
# 启用详细日志
python main.py --log-level DEBUG --verbose

# 查看日志文件
tail -f logs/agenticseeker.log
```

## 性能优化

### 系统优化

1. **内存优化**:
   - 调整批处理大小
   - 启用模型缓存
   - 定期清理历史数据

2. **速度优化**:
   - 使用本地LLM模型
   - 启用操作缓存
   - 优化图像处理

3. **准确性优化**:
   - 调整LLM温度参数
   - 增加验证步骤
   - 完善错误处理

## 扩展开发

### 添加新的操作工具

```python
# 在 tools/ 目录下创建新工具
from agenticx.tools.base import BaseTool

class CustomTool(BaseTool):
    def _run(self, **kwargs):
        # 实现工具逻辑
        pass
```

### 自定义智能体

```python
# 继承基础智能体类
from core.base_agent import BaseAgenticSeekerAgent

class CustomAgent(BaseAgenticSeekerAgent):
    async def process_task(self, task):
        # 实现自定义逻辑
        pass
```

## 部署说明

### Docker部署（后续）

```bash
# 构建Docker镜像
docker build -t agenticseeker .

# 运行容器
docker run -it --privileged -v /dev/bus/usb:/dev/bus/usb agenticseeker
```

### 生产环境配置

1. 使用生产级LLM服务
2. 配置数据库持久化
3. 启用监控和日志
4. 设置安全策略

## 支持与反馈

- 项目地址: `/Users/damon/myWork/AgenticX/examples/agenticx-for-ecloudcup/agenticx-for-ecloudcup/agenticseeker`
- 文档: 查看 `docs/` 目录
- 问题反馈: 创建 GitHub Issue

---

**注意**: 请确保在使用前已正确配置所有环境变量和设备连接。首次运行建议使用简单任务进行测试。