"""Build the five-page phase-1 PDF report with a bundled Chinese font."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "phase1_report.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))

NAVY = colors.HexColor("#15324A")
BLUE = colors.HexColor("#23688B")
PALE = colors.HexColor("#EAF2F6")
GRAY = colors.HexColor("#4B5563")

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


def bullet(text):
    return p("• " + text)


def grid(rows, widths, header=True):
    built = []
    for i, row in enumerate(rows):
        built.append([p(str(cell), "thead" if header and i == 0 else "table") for cell in row])
    table = Table(built, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                     ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE])]
    else:
        commands += [("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, PALE])]
    table.setStyle(TableStyle(commands))
    return table


def decorate(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D5E2EA"))
    canvas.line(2 * cm, height - 1.55 * cm, width - 2 * cm, height - 1.55 * cm)
    canvas.setFont("SimHei", 8.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, height - 1.27 * cm, "Python 与人工智能课程项目 · 阶段 1")
    canvas.drawRightString(width - 2 * cm, 1.2 * cm, f"{doc.page} / 5")
    canvas.restoreState()


story = []

# Page 1: project definition and executive summary.
story += [Spacer(1, 0.55 * cm), p("英文短信垃圾信息识别", "title"),
          p("阶段 1 报告：问题界定与计算原型", "subtitle"),
          HRFlowable(width="100%", thickness=1.2, color=BLUE), Spacer(1, 0.25 * cm),
          grid([
              ["项目 / 阶段", "英文短信垃圾信息识别 / 阶段 1"],
              ["队名 / 成员", "队名待填写；成员：杨俊炜、赵煜凡"],
              ["日期 / 版本", "2026-09-26 / phase-1-submission-v3（本地标签）"],
              ["仓库地址", "暂留空；创建远程仓库后补充 URL"],
          ], [3.5 * cm, 13.4 * cm], header=False), Spacer(1, 0.2 * cm),
          section("执行摘要"),
          p("本项目拟开发一个供个人用户复核英文短信的垃圾信息识别工具。阶段 1 将问题限定为单条纯文本短信的二分类，明确输入验证、输出解释与人工复核边界，并完成无需外部依赖的 Python 命令行原型。原型依据中奖、领取、催促和链接等线索给出规则分数，附带触发原因；14 个自动化测试已通过。自行编写的演示短信仅用于检查程序行为，不能证明真实分类性能。下一阶段将引入 UCI SMS Spam Collection，检查来源、重复与类别分布，建立固定划分和基线评估，再比较学习方法。当前主要风险是英文语料与实际短信之间的分布差异，以及规则误判和规避。"),
          section("1. 问题定义与范围"),
          p("现实问题：用户收到陌生短信时，需要快速识别值得重点检查的可疑内容。目标用户是对英文短信进行初步筛查的个人；最终处置仍由用户决定。系统任务是单条文本分类，而不是判断发信人身份或验证链接安全性。"),
          grid([
              ["项目要素", "阶段 1 定义"],
              ["输入", "一条 1–1000 字符的英文纯文本短信；不接受空白或明显中文输入。"],
              ["输出", "spam / ham 标签、非概率的整数规则分数、触发的规则名。"],
              ["范围边界", "只给出复核建议；不读取私人收件箱，不自动拦截/删除，不处理附件、图片或多语言。"],
          ], [3.2 * cm, 13.7 * cm]),
          p("可衡量的最终目标（预先设定，尚未达成）：在冻结的独立测试集上，垃圾短信召回率不低于 0.90，正常短信误拦率不高于 0.05；报告精确率与混淆矩阵。阶段 1 的完成标准是可重复运行、至少 8 个有意义测试通过。")]
story.append(PageBreak())

# Page 2: motivation and computational model.
story += [section("2. 动机与相关工作"),
          p("垃圾短信筛查同时面对漏检与误拦：漏检会让用户继续接触可疑内容；误拦可能妨碍正常沟通。因此后续评估必须同时观察垃圾短信召回率与正常短信误拦率，而不能只看总体准确率。"),
          grid([
              ["资料", "本项目的借鉴与边界"],
              ["[1] UCI SMS Spam Collection", "公开英文短信标签语料，页面列出 5,574 条记录与 CC BY 4.0 许可。适合作为后续数据来源；数据来源混合，不能代表所有语言或当前短信流量。"],
              ["[2] Almeida 等，2011", "介绍短信垃圾过滤语料与研究结果，为问题与数据背景提供依据。本项目不直接沿用其结果数值。"],
              ["[3] scikit-learn 文本分类教程", "示范文本向量化、朴素贝叶斯与流水线。后续阶段将据此实现学习方法，并与本阶段规则基线在同一划分上比较。"],
          ], [4.4 * cm, 12.5 * cm]),
          sub("2.1 项目差距与学习目标"),
          p("现成教程可以演示分类器，却不能代替本课程要求的任务定义、数据泄漏检查、受控比较、端到端系统和失败分析。本项目的学习目标是把这些环节连成可复现的证据链，并明确何时只能建议人工复核。"),
          section("3. 计算建模"),
          grid([
              ["组件", "输入与输出 / 职责"],
              ["输入验证", "str → 合法短信或明确异常；限制原始长度、空白、明显不支持的文字。"],
              ["文本归一化", "短信 → NFKC、大小写折叠、空白折叠后的文本；保持确定性。"],
              ["规则评分", "归一化文本 → 触发规则集合与整数分数；每条规则最多计一次。"],
              ["决策与输出", "分数达到 3 → spam，否则 ham；返回标签、分数和规则名称。"],
          ], [4.1 * cm, 12.8 * cm]),
          sub("3.1 数据结构与流程"),
          p("数据结构：输入为 Python 字符串；输出为不可变的 Classification(label: str, score: int, signals: tuple[str, ...])。处理流程：输入 → 校验 → 归一化 → 规则匹配/加权 → 阈值判断 → 命令行呈现。每个模块只处理一项职责，便于后续把规则模块替换为学习模型。"),
          p("假设：当前演示输入主要是英文纯文本。规则数量固定为 6，每条规则至多扫描一次短信，因此对长度为 n 的短信，粗略运行成本为 O(6n)，即随文本长度近似线性增长；这只是代码结构分析，不是实测延迟。", "small")]
story.append(PageBreak())

# Page 3: prototype evidence and tests.
story += [section("4. Python 原型与可检查输出"),
          p("原型位于 sms_filter/rules.py，命令行入口位于 sms_filter/__main__.py。它不训练模型；所有规则和阈值公开且可修改。分数是规则加权和，不代表“垃圾概率”。"),
          grid([
              ["匹配线索", "权重", "设计理由"],
              ["中奖/奖品词", "2", "较强可疑线索，但单独出现不足以判定。"],
              ["领取要求、免费/现金/奖励、立即拨打、网址", "各 1", "弱线索组合后触发，避免一个普通链接直接导致误拦。"],
              ["紧急/限时措辞", "2", "与其他线索结合后触发。"],
          ], [7.3 * cm, 1.5 * cm, 8.1 * cm]),
          sub("4.1 可复现的示例运行"),
          grid([
              ["输入（自行编写）", "实际输出", "说明"],
              ["You won a prize. Claim it now!", "spam，分数 3", "中奖词 2 + 领取要求 1。"],
              ["Are you free for lunch tomorrow?", "ham，分数 1", "仅含 free，不足阈值。"],
              ["恭喜中奖", "明确报错", "明显中文文本超出原型支持范围。"],
          ], [7.3 * cm, 3.5 * cm, 6.1 * cm]),
          p("运行命令：python -m sms_filter --text \"You won a prize. Claim it now!\"。演示数据保存在 data/demo_messages.jsonl；它由项目编写，不参与真实性能评估。"),
          sub("4.2 自动化测试"),
          p("使用 Python 标准库 unittest 执行 python -m unittest discover -s tests -v，结果为 14/14 通过。测试覆盖明显垃圾信息、普通对话、大小写、全角字符归一化、词边界、正常句中的 free、单独链接、规则解释、空白输入、非字符串、超长输入、中文、纯数字和重复运行的确定性。"),
          grid([
              ["观察", "证据能支持什么", "证据不能支持什么"],
              ["14 个测试通过", "约定的规则行为与边界处理在当前环境正确。", "无法推出真实短信的召回率、误拦率或跨领域效果。"],
              ["4 条合成演示短信", "命令行能接受代表性输入并产生可检查输出。", "不能当作独立测试集，也不能据此调阈值后报告性能。"],
          ], [3.0 * cm, 7.0 * cm, 6.9 * cm]),
          sub("4.3 已知失败与异常"),
          p("“Urgent cash needed for taxi”会触发紧急词与 cash，可能将正常求助误判为 spam；“Claim your package at https://...”可能因分数不足而漏检。两者是人为构造的风险示例，不是来自真实数据的错误率估计。")]
story.append(PageBreak())

# Page 4: feasibility, risks, milestone map.
story += [section("5. 可行性、资源与风险"),
          grid([
              ["资源", "当前状态 / 后续动作"],
              ["软件与运行环境", "阶段 1 仅 Python 3.10+ 标准库；README 给出运行和测试命令。阶段 2–3 计划固定 scikit-learn 等依赖版本。"],
              ["数据", "阶段 1 使用自行编写的合成演示文本；阶段 2 再下载 UCI 英文短信语料，记录来源、许可、类别、重复和字段。"],
              ["时间与人员", "成员：杨俊炜、赵煜凡；各阶段具体分工与截止日期待填写。"],
          ], [4.1 * cm, 12.8 * cm]),
          sub("5.1 主要风险与应对"),
          grid([
              ["风险", "影响", "计划中的处理"],
              ["误拦正常短信", "用户可能错过消息。", "优先报告正常短信误拦率；输出仅供人工复核，不自动删除。"],
              ["漏检与词形规避", "可疑短信仍被当作普通短信。", "阶段 3 比较学习模型；阶段 5 做拼写扰动压力测试。"],
              ["数据偏差/年代差", "公开英文语料与当前、本地短信不同。", "限制外推结论，记录数据收集背景；另做分布偏移测试。"],
              ["重复文本泄漏", "训练与测试共享近似短信导致虚高。", "阶段 2 先检查重复与近重复，再冻结划分；仅在训练集拟合向量器。"],
              ["隐私与许可证", "真实短信可能包含个人信息。", "不收集私人短信；使用公开许可数据，标注来源和 AI 协助。"],
          ], [3.7 * cm, 4.5 * cm, 8.7 * cm]),
          section("6. 阶段 2–5 里程碑"),
          grid([
              ["阶段", "具体任务", "完成标准"],
              ["2 数据与实验", "核对语料、数据字典、去重、固定划分、EDA、规则基线。", "能复现主要图表与召回率/误拦率；划分和泄漏检查有记录。"],
              ["3 比较建模", "同一数据划分下比较规则、词袋+朴素贝叶斯、TF-IDF+逻辑回归。", "统一指标、重复试验、至少一项消融和错误分类。"],
              ["4 系统集成", "封装所选模型，提供 CLI 或简单 Web 界面、输入验证与日志。", "正常、困难、拒绝/错误三类端到端演示及集成测试。"],
              ["5 扩展与综合", "针对阶段 3–4 暴露的问题做字符级特征或弃权机制等扩展。", "固定数据上做前后受控比较、鲁棒性审计、成本与部署计划。"],
          ], [2.4 * cm, 7.1 * cm, 7.4 * cm])]
story.append(PageBreak())

# Page 5: next stage plan, contribution, references.
story += [section("7. 下一阶段执行计划"),
          grid([
              ["任务", "责任人", "依赖与完成标准"],
              ["下载和核验语料", "待填写", "记录来源、许可、文件校验值；核对记录数和标签。"],
              ["探索与数据字典", "待填写", "统计类别、长度、缺失与重复；至少一项发现改变后续设计。"],
              ["划分与防泄漏", "待填写", "先处理重复，再固定训练/验证/测试划分和随机种子。"],
              ["规则基线评估", "待填写", "报告垃圾召回率、正常误拦率、精确率、混淆矩阵和错误案例。"],
              ["复现与报告", "待填写", "一条命令重建主要结果；提交阶段 2 PDF 与对应标签。"],
          ], [5.0 * cm, 2.0 * cm, 9.9 * cm]),
          p("依赖关系：先完成许可和数据核验，再冻结划分，然后才计算基线结果；不得根据测试集表现回调规则或阈值。团队确认后填写实际责任人和日期。"),
          section("8. 局限性与个人贡献"),
          p("本阶段没有使用 UCI 真实数据，也没有训练机器学习模型，因此不报告准确率、召回率或任何“AI 优于基线”的结论。规则只处理英文纯文本，并以有限词汇捕捉可疑线索。后续阶段需要验证这些规则是否值得保留。"),
          p("成员：杨俊炜、赵煜凡。队名与每人的实际贡献待填写；最终提交前，应写明各自完成的代码、实验和报告部分，并能解释所提交的内容。"),
          p("生成式 AI 披露：阶段 1 的选题整理、代码与报告初稿由生成式 AI 协助形成；提交者应逐项运行、复核和修改，并对结论负责。本阶段未调用外部模型或付费 API，未使用外部代码复制。"),
          section("9. 参考资料"),
          p("[1] Almeida, T. 与 Hidalgo, J. UCI Machine Learning Repository: SMS Spam Collection. https://archive.ics.uci.edu/dataset/228/sms+spam+collection ，访问日期：2026-09-26。", "small"),
          p("[2] Almeida, T. A., Hidalgo, J. M. G., &amp; Yamakami, A. (2011). Contributions to the study of SMS spam filtering: New collection and results. ACM DocEng. DOI: 10.1145/2034691.2034742。", "small"),
          p("[3] scikit-learn developers. Working with text data. https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html ，访问日期：2026-09-26。", "small"),
          p("[4] scikit-learn developers. Classification metrics API. https://scikit-learn.org/stable/api/sklearn.metrics.html ，访问日期：2026-09-26。", "small"),
          section("附：可复现性与反馈记录"),
          p("仓库应含 README、源码、数据样例、依赖说明及 14 个测试。修订版使用本地标签 phase-1-submission-v3 固定提交版本；远程仓库 URL 待建立。教师的第一轮反馈尚未收到，反馈回复表将在阶段 2 增补。", "small")]

doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=1.85 * cm, bottomMargin=1.9 * cm,
    title="英文短信垃圾信息识别：阶段 1 报告",
    author="杨俊炜、赵煜凡（队名待填写）",
)
doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
print(OUTPUT)
