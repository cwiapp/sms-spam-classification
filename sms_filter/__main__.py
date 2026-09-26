"""Command-line entry point: python -m sms_filter --text '...'"""

import argparse
import json

from .rules import classify_sms


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase-1 English SMS screening prototype")
    parser.add_argument("--text", required=True, help="One English SMS to screen")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()
    try:
        result = classify_sms(args.text)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps({"label": result.label, "score": result.score,
                          "signals": result.signals}, ensure_ascii=False))
    else:
        label_zh = "疑似垃圾短信" if result.label == "spam" else "暂未识别为垃圾短信"
        print(f"结果：{label_zh}（规则分数 {result.score}；非概率）")
        print("触发规则：" + ("、".join(result.signals) if result.signals else "无"))
        print("用途：仅供人工复核，不自动拦截或删除。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
