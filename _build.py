import json, os, shutil

d = r"D:\桌面\测评\天赋测评X职业方向"

# Load data
with open(os.path.join(d, "quiz_dims.json"), encoding="utf-8") as f:
    dims = json.load(f)["dims"]
with open(os.path.join(d, "quiz_questions.json"), encoding="utf-8") as f:
    questions = json.load(f)
with open(os.path.join(d, "quiz_results.json"), encoding="utf-8") as f:
    results = json.load(f)

# Placeholders
PH = {
    "__DIMS__": json.dumps(dims, ensure_ascii=False),
    "__QUESTIONS__": json.dumps(questions, ensure_ascii=False),
    "__RESULTS__": json.dumps(results, ensure_ascii=False),
    "__TITLE__": json.dumps("前任残留度测试", ensure_ascii=False),
    "__SCORE__": json.dumps("分", ensure_ascii=False),
    "__SITE_TAG__": json.dumps("💔 前任残留度测试 · pjh2237.github.io/ex-remain-test", ensure_ascii=False),
    "__SUBMIT_BTN__": json.dumps("✅ 提交查看结果", ensure_ascii=False),
    "__NEXT_BTN__": json.dumps("下一题 →", ensure_ascii=False),
}

with open(os.path.join(d, "_css.txt"), encoding="utf-8") as f:
    css = f.read()
with open(os.path.join(d, "_js.txt"), encoding="utf-8") as f:
    js_template = f.read()

for k, v in PH.items():
    js_template = js_template.replace(k, v)

# Build homepage preview cards using OSS images
def card_html(r):
    """Generate the exact same card HTML used everywhere - homepage, result, share, healing."""
    img = r.get("image", "")
    return (
        '<div class="type-preview">'
        + (f'<img src="{img}" alt="{r["type"]}" class="tp-img" loading="lazy">' if img else "")
        + f'<div class="tp-name" style="color:{r["color"]}">{r["type"]}</div>'
        + f'<div class="tp-range">{r["min"]}-{r["max"]} 分</div>'
        + f'<div class="tp-tagline">{r["tagline"]}</div>'
        + "</div>"
    )

def compact_card_html(r):
    """Same card but without the outer .type-preview wrapper, for embedding."""
    img = r.get("image", "")
    return (
        (f'<img src="{img}" alt="{r["type"]}" class="tp-img" loading="lazy">' if img else "")
        + f'<div class="tp-name" style="color:{r["color"]}">{r["type"]}</div>'
        + f'<div class="tp-range">{r["min"]}-{r["max"]} 分</div>'
        + f'<div class="tp-tagline">{r["tagline"]}</div>'
    )

# Pre-build card HTML for JS template
prebuilt_cards = {}
for r in results:
    prebuilt_cards[f"__CARD_{r['min']}_{r['max']}__"] = json.dumps(compact_card_html(r))

for k, v in prebuilt_cards.items():
    js_template = js_template.replace(k, v)

# Build HTML
html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>前任残留度测试</title>\n'
html += '<style>\n' + css + '\n</style>\n</head>\n<body>\n'

# Header
html += '<div class="header"><div class="icon">💔</div><h1>前任残留度测试</h1><p class="subtitle">20道情景行为题 · 5维深度评估</p><div class="badge">🔬 基于情感心理学设计</div></div>\n'

html += '<div class="container">\n'

# Landing page
html += '<div id="landing">\n'
html += '<div class="start-section"><button class="start-btn" onclick="showCodeModal()">🚀 开始前任残留度测试</button></div>\n'
html += '<div class="result-types-grid">\n'
for r in results:
    html += card_html(r) + '\n'
html += '</div></div>\n'

# Code modal
html += '<div class="modal-overlay" id="codeModal"><div class="modal-box"><div class="modal-icon">🔒</div><h3>请输入测试码</h3><input type="password" id="codeInput" placeholder="输入测试码"><br><button class="code-submit" onclick="verifyCode()">确认</button><p class="code-error" id="codeError">测试码错误，请重试</p></div></div>\n'

# Progress bar
html += '<div class="progress-wrap" id="pw"><div class="progress-bar"><div class="progress-fill" id="pf"></div></div><span class="progress-text" id="pt">1 / 20</span></div>\n'

# Quiz area
html += '<div class="quiz-area" id="quizArea"><div id="quizContainer"></div>\n'
html += '<div class="q-nav"><button class="nav-prev" id="navPrev" onclick="prevQuestion()" disabled>← 上一题</button><button class="nav-next" id="navNext" onclick="nextQuestion()">下一题 →</button></div>\n'
html += '<p class="must-answer-msg" id="mustAnswerMsg">⚠️ 请先选择你的答案</p></div>\n'

# Result area
html += '<div class="result-area" id="resultArea">\n'

# Result area: single integrated module card (card image + radar + desc + advice + share/retest)
html += '<div class="result-card" id="resultCard">\n'
html += '  <div class="rc-header" id="rcHeader"></div>\n'
html += '  <div class="radar-section">\n'
html += '    <h3 class="radar-title">📊 五维雷达图</h3>\n'
html += '    <p class="radar-tip-text">👆 点击或滑动雷达图上的圆点，查看各维度得分</p>\n'
html += '    <div class="radar-canvas-wrap"><canvas id="radarCanvas"></canvas><div class="radar-tip" id="radarTip"></div></div>\n'
html += '    <div class="dim-breakdown" id="dimBreakdown"></div>\n'
html += '  </div>\n'
html += '  <p class="result-desc" id="rd"></p>\n'
html += '  <div class="hc-advice" id="hcAdvice"></div>\n'
html += '  <div class="share-inline" id="shareInline">\n'
html += '    <div class="share-label">📤 分享你的测试结果</div>\n'
html += '    <div class="share-card-visual" id="shareCardVisual"></div>\n'
html += '    <div class="btn-row"><button class="action-btn" onclick="copyCard()">📋 复制卡片文字</button><button class="action-btn primary" onclick="shareResult()">📤 分享结果</button></div>\n'
html += '    <div class="retest-row"><button class="action-btn ghost" onclick="resetQuiz()">🔄 重新测试</button></div>\n'
html += '  </div>\n'
html += '</div>\n'
html += '</div>\n'

html += '</div>\n'  # close container

html += '<script>\n' + js_template + '\n</script>\n</body>\n</html>'

with open(os.path.join(d, "index.html"), "wb") as f:
    f.write(html.encode("utf-8"))

print("Generated:", len(html), "chars")
shutil.copy2(os.path.join(d, "index.html"), os.path.join(d, "outputs", "ex-remain-test.html"))
print("Done")
