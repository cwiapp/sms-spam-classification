"""Build the data-driven five-page phase-2 PDF report."""

from pathlib import Path
import json

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((ROOT / "artifacts" / "phase2_summary.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / "reports" / "phase2_report.pdf"
OUTPUT.parent.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))

NAVY = colors.HexColor("#15324A")
BLUE = colors.HexColor("#23688B")
PALE = colors.HexColor("#EAF2F6")
GRAY = colors.HexColor("#4B5563")
TEAL = colors.HexColor("#178F87")
ORANGE = colors.HexColor("#D97B31")

styles = {
    "title": ParagraphStyle("title", fontName="SimHei", fontSize=21, leading=31,
                            textColor=NAVY, alignment=TA_CENTER, spaceAfter=12),
    "subtitle": ParagraphStyle("subtitle", fontName="SimHei", fontSize=12, leading=18,
                               textColor=GRAY, alignment=TA_CENTER, spaceAfter=18),
    "h1": ParagraphStyle("h1", fontName="SimHei", fontSize=14, leading=21,
                         textColor=NAVY, spaceBefore=7, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="SimHei", fontSize=11.3, leading=17,
                         textColor=BLUE, spaceBefore=6, spaceAfter=5),
    "body": ParagraphStyle("body", fontName="SimHei", fontSize=10.5, leading=16.2,
                           textColor=colors.black, wordWrap="CJK", spaceAfter=6),
    "small": ParagraphStyle("small", fontName="SimHei", fontSize=9.3, leading=14.3,
                            textColor=colors.black, wordWrap="CJK", spaceAfter=4),
    "table": ParagraphStyle("table", fontName="SimHei", fontSize=9.4, leading=14,
                            textColor=colors.black, wordWrap="CJK"),
    "thead": ParagraphStyle("thead", fontName="SimHei", fontSize=9.4, leading=14,
                            textColor=colors.white, wordWrap="CJK"),
}


def p(text, style="body"):
    return Paragraph(text, styles[style])


def section(title):
    return p(title, "h1")


def sub(title):
    return p(title, "h2")


def grid(rows, widths, header=True):
    data = [[p(str(cell), "thead" if header and i == 0 else "table") for cell in row]
            for i, row in enumerate(rows)]
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ])
    else:
        commands.append(("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, PALE]))
    table.setStyle(TableStyle(commands))
    return table


def percent(value):
    return f"{value * 100:.1f}%"


def interval(values):
    return f"{percent(values[0])}–{percent(values[1])}"


def bar_chart(title, entries, maximum, suffix=""):
    """Vector chart; values come only from the generated summary JSON."""
    drawing = Drawing(480, 138)
    drawing.add(String(0, 119, title, fontName="SimHei", fontSize=10.5, fillColor=NAVY))
    for index, (label, value, color) in enumerate(entries):
        y = 75 - index * 42
        drawing.add(String(0, y + 8, label, fontName="SimHei", fontSize=10, fillColor=NAVY))
        drawing.add(Rect(75, y, 335, 20, fillColor=PALE, strokeColor=None))
        drawing.add(Rect(75, y, 335 * value / maximum, 20, fillColor=color, strokeColor=None))
        drawing.add(String(418, y + 6, f"{value:g}{suffix}", fontName="SimHei", fontSize=9.5,
                           fillColor=NAVY))
    return drawing


def decorate(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D5E2EA"))
    canvas.line(2 * cm, height - 1.55 * cm, width - 2 * cm, height - 1.55 * cm)
    canvas.setFont("SimHei", 8.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, height - 1.27 * cm, "Python 与人工智能课程项目 · 阶段 2")
    canvas.drawRightString(width - 2 * cm, 1.2 * cm, f"{doc.page} / 5")
    canvas.restoreState()


counts = SUMMARY["label_counts"]
split = SUMMARY["splits"]
row_metrics = SUMMARY["baseline_validation"]
unique_metrics = SUMMARY["baseline_validation_unique_text"]
row_cm = row_metrics["confusion"]
group_cm = unique_metrics["confusion"]
length = SUMMARY["length_characters"]
url = SUMMARY["url_count"]
story = []

# Page 1: scope, abstract, data provenance.
story += [Spacer(1, .55 * cm), p("英文短信垃圾信息识别", "title"),
          p("阶段 2 报告：数据与实验设计", "subtitle"),
          HRFlowable(width="100%", thickness=1.2, color=BLUE), Spacer(1, .25 * cm),
          grid([
              ["项目 / 阶段", "英文短信垃圾信息识别 / 阶段 2"],
              ["队名 / 成员", "队名待填写；成员：杨俊炜、赵煜凡"],
              ["日期 / 版本", "2026-09-26 / phase-2-submission-v2（本地标签）"],
              ["仓库地址", "暂留空；远程仓库建立后填写 URL"],
          ], [3.5 * cm, 13.4 * cm], header=False), Spacer(1, .2 * cm),
          section("执行摘要"),
          p(f"阶段 2 使用 UCI SMS Spam Collection 的 {SUMMARY['source_rows']:,} 条已标注英文短信，核验许可、压缩包校验值、标签和文本完整性，并完成数据字典与探索分析。语料中垃圾短信占 {percent(SUMMARY['label_fraction_spam'])}，按归一化文本发现 {SUMMARY['duplicate_rows']} 条重复行；因此采用按文本分组的固定划分，并以召回率和正常短信误拦率作为关键指标。第一阶段规则及阈值保持不变，只在验证集评估：按独特文本计，识别出 {group_cm['tp']}/{group_cm['tp']+group_cm['fn']} 条垃圾短信，正常短信误拦 {group_cm['fp']}/{group_cm['fp']+group_cm['tn']}，另有 1 条不支持的输入。结果显示规则漏检明显，测试集保留给后续模型研究。主要局限是语料来源混合、年代较早，且没有可验证的用户级与时间信息。"),
          section("1. 问题表述与本阶段变化"),
          p("目标用户仍是需要人工复核英文短信的个人。输入是一条英文纯文本短信；输出是 spam/ham 标签、非概率规则分数和触发原因。系统只给出复核建议，不自动删除。阶段 1 预设的最终目标为独立测试集垃圾短信召回率至少 0.90、正常短信误拦率至多 0.05；这两个值是目标，不是本阶段结果。"),
          p("本阶段依据真实数据修订实验设计：因为类别不平衡，总体准确率不足以概括效果；因为存在重复文本，先分组再划分；因为原型拒绝明显中文文本，评估同时报告覆盖率。第一阶段的规则和阈值 3 未改动。"),
          section("2. 数据来源与许可"),
          p("数据来自 UCI Machine Learning Repository 的 SMS Spam Collection [1]，原始压缩包按 SHA-256 固定：1587ea43e58e82b14ff1f5425c88e17f8496bfcdb67a583dbff9eefaf9963ce3。数据页标注 CC BY 4.0 许可。公开页面说明正常与垃圾短信由多个来源合并，文本未按时间排序；因此结果不自动代表当前短信流量。原始文本可能含电话号码，仓库只保存下载程序与行号划分清单，不再分发短信全文。")]
story.append(PageBreak())

# Page 2: dataset card and EDA.
story += [section("3. 数据集描述与质量核验"),
          grid([
              ["字段", "类型与含义", "处理方式"],
              ["row_id", "原文件行号，从 1 开始；观察单位为一条短信。", "仅用于追踪和冻结划分，不作模型特征。"],
              ["label", "ham（正常）或 spam（垃圾）；分类目标。", "验证限定取值；后续保持二分类定义。"],
              ["text", "UTF-8 原始短信文本，可能含网址或号码。", "不展示未脱敏内容；训练变换仅拟合训练集。"],
              ["派生字段", "长度、显式网址标记、归一化文本分组键。", "仅用于探索与防泄漏；不修改原文本。"],
          ], [2.7 * cm, 7.1 * cm, 7.1 * cm]),
          sub("3.1 类别与完整性"),
          bar_chart("图 1  原始短信标签数量（单位：条）", [
              ("正常", counts["ham"], TEAL), ("垃圾", counts["spam"], ORANGE)
          ], maximum=max(counts.values())),
          p(f"图 1 显示正常短信 {counts['ham']:,} 条、垃圾短信 {counts['spam']:,} 条。标签或文本缺失 0；归一化后独特文本 {SUMMARY['unique_normalized_texts']:,}，重复行 {SUMMARY['duplicate_rows']}，重复组的标签冲突 0。压缩包共 {SUMMARY['source_rows']:,} 行且 UTF-8 可完整解码。以上只是结构核验，无法证明每条标签语义均正确。", "small"),
          sub("3.2 与任务相关的分布"),
          bar_chart("图 2  按标签的短信长度中位数（单位：字符）", [
              ("正常", length["ham"]["median"], TEAL),
              ("垃圾", length["spam"]["median"], ORANGE)
          ], maximum=max(length["ham"]["median"], length["spam"]["median"]), suffix=" 字"),
          p(f"垃圾短信长度中位数为 {length['spam']['median']} 字符，正常短信为 {length['ham']['median']}；90 分位数分别为 {length['spam']['p90']} 与 {length['ham']['p90']} 字符。显式网址分别出现在垃圾短信 {url['spam']}/{counts['spam']} 条、正常短信 {url['ham']}/{counts['ham']} 条。该网址检测只认 http(s):// 或 www.，不能覆盖所有链接。", "small"),
          p("改变设计的观察：类别比例不均，使“总准确率”容易掩盖漏检；重复文本要求分组划分；网址分布差异可能部分反映语料来源，而非可直接泛化的垃圾信息规律。", "small")]
story.append(PageBreak())

# Page 3: cleaning and split design.
story += [section("4. 数据处理流水线与防泄漏"),
          grid([
              ["步骤", "实现与验证"],
              ["获取与固定", "tools/fetch_uci_data.py 从 UCI 官方地址下载压缩包；与固定 SHA-256 比对，变化时拒绝静默替换。"],
              ["解析与验证", "sms_filter/dataset.py 逐行 UTF-8 解码，按首个制表符拆出标签和文本；未知标签或空文本立即报错。"],
              ["保留与派生", "保留原始文本；NFKC、大小写和空白归一化仅用于精确重复分组，不删除数字、标点或网址。"],
              ["固定划分", "每个标签内部按归一化文本组排序后用种子 42 洗牌，约 70/15/15 分到训练、验证、测试。"],
              ["泄漏检查", "原始行号只出现一次；三个集合的归一化文本组两两不交。后续词表、TF-IDF 等只在训练集拟合。"],
          ], [3.2 * cm, 13.7 * cm]),
          sub("4.1 冻结的划分结果"),
          grid([
              ["集合", "短信行数", "正常", "垃圾", "独特文本组", "用途"],
              ["训练", split["train"]["rows"], split["train"]["ham"],
               split["train"]["spam"], split["train"]["unique_groups"], "拟合未来学习模型"],
              ["验证", split["validation"]["rows"], split["validation"]["ham"],
               split["validation"]["spam"], split["validation"]["unique_groups"], "本阶段基线与后续选择"],
              ["测试", split["test"]["rows"], split["test"]["ham"],
               split["test"]["spam"], split["test"]["unique_groups"], "阶段 3 后的一次性评估"],
          ], [2.0 * cm, 2.1 * cm, 1.8 * cm, 1.8 * cm, 3.1 * cm, 6.1 * cm]),
          p("注：比例按独特文本组分配，同组的重复行必须进入同一集合，因此实际行数并非严格 70/15/15。短信没有可靠时间戳或用户标识，无法进行时序或用户级独立划分；这限制了外部有效性。"),
          sub("4.2 可复现性与数据访问"),
          p("执行 python -m tools.fetch_uci_data、python -m tools.run_phase2 可重建汇总表、划分清单及验证结果。artifacts/split_manifest.json 只含源行号、种子与源文件校验值；data/dataset_card.md 记录字段、来源、许可和风险。原始压缩包位于 Git 忽略的 data/raw/。"),
          p("阶段 2 检查了完全相同或仅有全角、大小写、空白差异的文本；拼写替换、号码改写等近重复仍可能跨集合。后续应做近重复敏感性分析，不能把“无精确重复跨集合”解释为完全没有相似文本泄漏。", "small")]
story.append(PageBreak())

# Page 4: baseline and uncertainty.
story += [section("5. 规则基线与评估方案"),
          p("基线是阶段 1 已固定的六类人工规则，分数达到 3 判为 spam，其余判为 ham。它不使用训练数据，也未根据验证或测试结果调阈值。主要指标是垃圾短信召回率 TP/(TP+FN)，反映漏检；次要指标为正常短信误拦率 FP/(FP+TN)、垃圾短信精确率与覆盖率，反映误拦和弃权。"),
          sub("5.1 验证集结果：以独特文本组为单位"),
          grid([
              ["实际标签 / 预测", "spam", "ham", "弃权"],
              ["垃圾 spam", group_cm["tp"], group_cm["fn"], unique_metrics["abstentions"].get("spam", 0)],
              ["正常 ham", group_cm["fp"], group_cm["tn"], unique_metrics["abstentions"].get("ham", 0)],
          ], [6.2 * cm, 3.2 * cm, 3.2 * cm, 4.3 * cm]),
          p(f"基于 {unique_metrics['total']} 个独特文本组，覆盖 {unique_metrics['covered']} 个（{percent(unique_metrics['coverage'])}）。垃圾召回率 {group_cm['tp']}/{group_cm['tp']+group_cm['fn']} = {percent(unique_metrics['spam_recall'])}，95% Wilson 区间 {interval(unique_metrics['spam_recall_95pct_wilson'])}；正常误拦率 {group_cm['fp']}/{group_cm['fp']+group_cm['tn']} = {percent(unique_metrics['ham_false_positive_rate'])}，区间 {interval(unique_metrics['ham_fpr_95pct_wilson'])}。精确率为 100%，但仅基于 {group_cm['tp']} 个被识别的垃圾文本，不能解释为稳定的完美表现。[3]"),
          sub("5.2 按原始行加权的敏感性结果"),
          p(f"验证集有 {row_metrics['total']} 行，规则覆盖 {row_metrics['covered']} 行。按行计 TP={row_cm['tp']}、FN={row_cm['fn']}、FP={row_cm['fp']}、TN={row_cm['tn']}，垃圾召回率 {percent(row_metrics['spam_recall'])}，正常误拦率 {percent(row_metrics['ham_false_positive_rate'])}。独特文本组召回率更低，提示重复短信会改变汇总指标；因此以独特文本组结果作为本阶段的主要比较依据。"),
          sub("5.3 错误与不确定性"),
          p(f"验证集按行有 {row_cm['fn']} 条垃圾短信漏检，其中 {SUMMARY['validation_diagnostics']['score_histogram_by_true_label']['spam'].get('0',0)} 条连一条规则都未触发；{SUMMARY['validation_diagnostics']['false_negatives_with_digit']} 条包含数字，但数字本身不能证明其为垃圾信息。另有 1 条含汉字的正常短信被明确弃权。结果支持在阶段 3 比较词袋及字符级表示，但不证明任何一种表示必然改善效果。"),
          p("Wilson 区间以独特文本组近似作为观察单位，仍未消除共同语料来源和相似表达造成的相关性。零误拦只表示本验证样本的观察值；独立测试集尚未用于性能报告。", "small")]
story.append(PageBreak())

# Page 5: ethics, next stage, references.
story += [section("6. 数据风险、伦理与适用边界"),
          grid([
              ["问题", "本阶段判断与处理"],
              ["来源与选择偏差", "正常/垃圾信息由不同早期语料组合，语言、年代和采集方式不一致；不声称当前用户表现。"],
              ["标签与敏感信息", "标签质量尚未逐条人工复核；原始短信可能含电话和私人内容，仓库不重新分发原文。"],
              ["假正例/假反例", "误拦可能影响正常沟通，漏检会留下风险；界面应提供复核而非自动删除。"],
              ["公平性与滥用", "没有可靠的人口属性，不能做群体公平性结论；只研究防护性筛查，不生成攻击短信。"],
          ], [4.1 * cm, 12.8 * cm]),
          section("7. 下一阶段计划"),
          grid([
              ["任务", "责任人", "完成标准"],
              ["模型对比", "待填写", "同一冻结划分比较规则、词袋+朴素贝叶斯、TF-IDF+逻辑回归。"],
              ["受控实验", "待填写", "仅训练集拟合特征；验证集选择；记录种子、配置、耗时和至少一项消融。"],
              ["错误分析", "待填写", "按短信长度、网址、拼写变体检查失败与模型分歧，不展示未脱敏文本。"],
              ["最终测试", "待填写", "方法冻结后才在测试集运行一次，报告模型及系统约束下的选择理由。"],
          ], [3.7 * cm, 2.0 * cm, 11.2 * cm]),
          section("8. 复现、贡献与反馈"),
          p("本阶段可运行命令和环境见 README；核心处理只需 Python 3.10+ 标准库，报告生成脚本使用 ReportLab 与 Windows SimHei 字体。自动化测试共 22 个且全部通过。成员为杨俊炜、赵煜凡；队名、真实个人贡献和远程仓库 URL 暂留空；本地修订版使用 phase-2-submission-v2 标签。"),
          p("生成式 AI 披露：阶段 2 代码、分析和报告草稿由生成式 AI 协助完成，提交者需复核并能解释。教师对阶段 1 的反馈尚未提供，故反馈回复表暂记“未收到”，取得反馈后应增补修改及证据位置。"),
          section("参考资料"),
          p("[1] Almeida, T. &amp; Hidalgo, J. (2011). SMS Spam Collection. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/228/sms+spam+collection ，访问日期：2026-09-26。", "small"),
          p("[2] Almeida, T. A., Hidalgo, J. M. G., &amp; Yamakami, A. (2011). Contributions to the study of SMS spam filtering: New collection and results. ACM DocEng. DOI: 10.1145/2034691.2034742。", "small"),
          p("[3] NIST/SEMATECH. Confidence intervals for a binomial proportion (Wilson method). https://itl.nist.gov/div898/handbook/prc/section2/prc241.htm ，访问日期：2026-09-26。", "small")]

doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=2 * cm,
                        rightMargin=2 * cm, topMargin=1.85 * cm,
                        bottomMargin=1.9 * cm,
                        title="英文短信垃圾信息识别：阶段 2 报告",
                        author="杨俊炜、赵煜凡（队名待填写）")
doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
print(OUTPUT)
