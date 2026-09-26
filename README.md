# 短信垃圾信息识别：阶段 1–2

本仓库是“Python 与人工智能”课程项目。阶段 1 是英文短信规则筛查原型；阶段 2 在 UCI 公开数据上完成数据检查、分组划分和规则基线评估。原型接收**一条英文短信**，返回 `spam`（疑似垃圾信息）或 `ham`（暂未识别为垃圾信息）、规则分数及触发原因。分数不是概率。结果仅供人工复核，不会自动拦截、删除或发送短信。

## 运行环境

- Python 3.10 或更新版本。
- 阶段 1–2 的核心程序只使用 Python 标准库，不需要安装第三方依赖。
- 在本目录打开终端运行下列命令。

```powershell
python -m sms_filter --text "You won a prize. Claim it now!"
python -m sms_filter --text "Are you free for lunch tomorrow?" --json
python -m unittest discover -s tests -v
```

## 阶段 2：复现数据分析与基线

在项目根目录运行：

```powershell
python -m tools.fetch_uci_data
python -m tools.run_phase2
python -m unittest discover -s tests -v
```

若要重新生成第二阶段 PDF 和其中两张图，在 Windows 环境安装可选依赖后运行：

```powershell
python -m pip install -e ".[report]"
python -m tools.build_phase2_report
```

报告脚本使用 Windows 自带的 `C:\Windows\Fonts\simhei.ttf`。分析、划分和基线结果的重建不需要 ReportLab。

下载脚本从 UCI 官方地址取得压缩包并核验 SHA-256；原始短信存放在被 Git 忽略的 `data/raw/`，避免在仓库中再分发文本。分析脚本生成 `artifacts/phase2_summary.json` 与 `artifacts/split_manifest.json`。后者只保存原始行号，不保存短信内容。数据集说明见 [data/dataset_card.md](data/dataset_card.md)。

本阶段按归一化文本分组，再在每个标签内用固定种子 42 做约 70/15/15 的训练、验证、测试划分。**规则基线只在验证集上评估；测试集仍保留给后续受控比较。**第一阶段固定的规则和阈值没有利用数据集修改。

若系统中命令是 `py`，可用 `py -m sms_filter ...`。命令行对空白、超长、中文或不含英文字母的输入报错并给出原因。

## 目录

| 路径 | 用途 |
| --- | --- |
| `sms_filter/rules.py` | 规则、输入验证和分类函数 |
| `sms_filter/__main__.py` | 可运行命令行入口 |
| `sms_filter/dataset.py` | 数据验证、分组划分、统计和基线指标 |
| `tests/` | 22 个行为、边界和数据处理测试 |
| `data/demo_messages.jsonl` | 4 条自行编写的演示短信，**不是**真实评测数据 |
| `reports/phase1_report.pdf` | 第一阶段报告 |
| `reports/phase2_report.pdf` | 第二阶段报告 |
| `artifacts/` | 可由脚本重建的汇总结果和划分清单 |

## 任务范围与限制

- 目标用户：希望先筛查短信、再自行决定如何处理的个人用户。
- 输入：单条英文短信文本，最多 1000 个原始字符。
- 输出：标签、整数规则分数、触发的规则名。
- 不处理中文、多语言、图片、附件、群发来源判断，也不自动删除消息。
- 当前规则容易被拼写变体绕过，且可能误判包含促销词的正常短信；不能把本原型当作可靠的安全防护工具。

## 后续数据与实验

阶段 2 使用 [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)。公开页面说明其许可为 CC BY 4.0；使用时须注明来源。数据来自不同语料来源，不能代表所有当前或中文短信。演示数据是自行编写的合成样例，不用于真实性能评估。后续将沿用已冻结划分，用垃圾短信召回率、正常短信误拦率和精确率比较规则基线与学习模型，并记录失败样例、运行环境和重复实验结果。

## 归属与贡献

课程资料提供者：授课教师。阶段 1–2 项目代码、分析和报告由生成式 AI 辅助起草，必须由提交者检查、运行、修改并能够解释每个模块与实验结论。成员为杨俊炜、赵煜凡；队名和实际个人贡献待填写，不得将占位信息当作真实贡献声明。远程仓库地址为 <https://github.com/cwiapp/sms-spam-classification>。项目代码采用根目录的 MIT LICENSE；UCI 数据集依据其 CC BY 4.0 许可使用，来源和归属见数据卡。
