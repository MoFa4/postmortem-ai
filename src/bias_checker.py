# bias_checker.py (or src/bias_checker.py)
import re

print("✅ Script loaded successfully!")  # ← This proves Python is running it

# 🔍 Blame patterns
BLAME_PATTERNS = [r'\b(forgot|missed|neglected)\b', r'\b(human error|who broke)\b']
REWRITE_MAP = {"forgot": "the process lacked validation for", "missed": "test coverage did not include", "human error": "system design did not prevent", "who broke": "what condition allowed"}

def check_bias(text: str) -> dict:
    flags = []
    suggestions = {}
    for pattern in BLAME_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            phrase = match.group(0).strip()
            if phrase not in flags: flags.append(phrase)
            for kw, rw in REWRITE_MAP.items():
                if kw in phrase.lower(): suggestions[phrase] = rw; break
    return {"has_bias": len(flags) > 0, "flags": flags, "suggestions": suggestions}

def fix_bias(text: str) -> str:
    res = check_bias(text)
    if not res["has_bias"]: return text
    for phrase in sorted(res["suggestions"].keys(), key=len, reverse=True):
        text = re.sub(re.escape(phrase), res["suggestions"][phrase], text, flags=re.IGNORECASE)
    return text

if __name__ == "__main__":
    print("🔍 Running bias checker...\n")
    for txt in ["John forgot the config", "Human error caused outage", "Pipeline lacked validation"]:
        res = check_bias(txt)
        print(f"{'🚩' if res['has_bias'] else '✅'} {txt}")
        if res['suggestions']: print(f"   💡 → {fix_bias(txt)}")
    print("\n🎉 Done!")