# 句子排序评估系统

这是一个基于Streamlit和streamlit-sortables实现的拖拽式句子排序界面，用于评估句子匹配的相关性。

## 功能特点

- 📝 **直观的拖拽排序**: 使用streamlit-sortables实现流畅的拖拽体验
- 🎯 **批量处理**: 支持对多个句子及其匹配项进行批量排序
- 💾 **结果保存**: 自动保存排序结果，支持JSON格式下载
- 📊 **进度跟踪**: 实时显示排序进度和统计信息
- 🎨 **美观界面**: 现代化的UI设计，清晰的视觉层次

## 安装依赖

```bash
pip install -r requirements.txt
```

所需的依赖包括：
- `streamlit>=1.28.0` - Web应用框架
- `Pillow>=10.0.0` - 图像处理（可选）
- `streamlit-sortables>=0.2.0` - 拖拽排序组件

## 快速开始

### 方式1: 使用启动脚本

```bash
./run_sorting.sh
```

该脚本会自动：
1. 检查并安装依赖
2. 启动Streamlit应用（端口8502）
3. 在浏览器中打开界面

### 方式2: 直接运行

```bash
streamlit run interface_sorting.py --server.port 8502
```

## 使用说明

### 1. 输入用户名

在侧边栏的"用户信息"区域输入您的用户名，用于标识排序结果。

### 2. 加载数据

有两种方式加载数据：

**方式A: 使用示例数据**
- 选择"使用示例数据"
- 点击"加载示例数据"按钮
- 系统会自动加载`example_data.json`

**方式B: 上传JSON文件**
- 选择"上传JSON文件"
- 点击文件上传器上传您的JSON文件

### 3. 拖拽排序

对于每个句子：
1. 查看原始句子（蓝色背景框）
2. 查看匹配的候选句子列表
3. 拖拽候选句子，按相关性从高到低排序
4. 最相关的句子放在最上面

每个候选句子都带有标签，表示匹配使用的指标（BERT、BLEU、ROUGE等）。

### 4. 保存结果

完成所有句子的排序后：
- 点击"保存排序结果"按钮，将结果保存到本地文件夹
- 或点击"下载JSON结果"按钮，直接下载JSON文件

## 数据格式

### 输入格式

JSON文件应该包含以下结构：

```json
{
    "sentences": [
        {
            "his_sentence": "原始句子文本",
            "matched_sentence": [
                {
                    "metric": "bert",
                    "sentence": "匹配的句子1"
                },
                {
                    "metric": "bleu",
                    "sentence": "匹配的句子2"
                },
                {
                    "metric": "rouge",
                    "sentence": "匹配的句子3"
                }
            ]
        },
        {
            "his_sentence": "另一个原始句子",
            "matched_sentence": [...]
        }
    ]
}
```

### 输出格式

排序结果会以以下格式保存：

```json
{
    "username": "用户名",
    "timestamp": "20250103_143000",
    "results": {
        "0": {
            "his_sentence": "原始句子",
            "sorted_sentences": [
                "[BERT] 最相关的句子",
                "[BLEU] 次相关的句子",
                "[ROUGE] 最不相关的句子"
            ],
            "original_matched": [...]
        },
        "1": {...}
    }
}
```

## 示例数据

项目包含了一个示例数据文件 `example_data.json`，包含3个句子及其匹配项，可以直接用于测试。

示例数据展示了：
- 心脏大小相关的句子
- 肺部清晰度相关的句子
- 胸腔积液相关的句子

每个句子都有3个使用不同指标（BERT、BLEU、ROUGE）匹配的候选句子。

## 文件说明

- `interface_sorting.py` - 主应用程序文件
- `run_sorting.sh` - Linux/Mac启动脚本
- `requirements.txt` - Python依赖列表
- `example_data.json` - 示例数据文件
- `ranking_results/` - 排序结果保存目录（自动创建）

## 与其他模块的关系

本排序系统是`interface_sentence_rank`模块的一部分，与其他文件的关系：

- `interface_report.py` - 报告评分系统（原始界面）
- `interface_sorting.py` - 句子排序系统（本文件）
- `sentence_ranking.py` - 句子排序算法实现
- `examples.py` - 示例代码

这些模块共同构成了一个完整的句子评估和排序系统。

## 技术细节

### 核心组件

1. **streamlit-sortables**: 提供拖拽排序功能
2. **Streamlit**: Web应用框架
3. **Session State**: 保持排序状态

### 主要函数

- `load_example_data()` - 加载JSON数据
- `get_metric_class()` - 获取指标对应的CSS样式类
- `save_ranking_results()` - 保存排序结果到文件
- `main()` - 主应用逻辑

### 自定义样式

使用了自定义CSS来美化界面：
- 句子卡片样式
- 指标标签颜色
- 响应式布局

## 常见问题

### Q: 如何更改端口号？

A: 修改`run_sorting.sh`中的端口号，或运行时指定：
```bash
streamlit run interface_sorting.py --server.port YOUR_PORT
```

### Q: 排序结果保存在哪里？

A: 默认保存在`ranking_results/`目录下，文件名格式为`ranking_{用户名}_{时间戳}.json`

### Q: 可以使用自己的数据吗？

A: 可以，只需按照"数据格式"部分的要求准备JSON文件，然后通过界面上传即可。

### Q: 如何重置排序？

A: 点击界面底部的"重置所有排序"按钮，会清除所有排序记录并重新开始。

## 后续开发

可能的增强功能：
- [ ] 添加快捷键支持
- [ ] 支持批量导入/导出
- [ ] 添加排序质量评估指标
- [ ] 支持多用户协作
- [ ] 添加数据可视化分析

## 联系方式

如有问题或建议，请通过项目issue反馈。

