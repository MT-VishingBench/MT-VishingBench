#!/usr/bin/env python3
"""
MT-PhishingBench 종합 보고서 HTML 생성 (개요·방법론·통계·참고문헌 + 전체 합성 대화).
이후 Chrome headless로 PDF 변환.
"""
import json, html
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
KB = ROOT.parent.parent / "knowledge_base"
FSS = ROOT.parent / "fss_voice" / "data"
OUT = ROOT / "report.html"

synth = json.load(open(ROOT / "synth_dialogues.json", encoding="utf-8"))
convos = synth["conversations"]
stats = json.load(open(FSS / "fss_stats.json", encoding="utf-8"))
fss = json.load(open(FSS / "fss_dialogues.json", encoding="utf-8"))
try:
    ver = json.load(open(ROOT / "verify" / "label_verification_report.json", encoding="utf-8"))["metrics"]
except Exception:
    ver = {}
e = html.escape

def tag(t):  # 단계 약어
    return {"contact": "접촉", "deception": "기망", "compliance": "행동유도", "extraction": "편취"}.get(t, t or "")

def dist(key):
    return Counter(key(c) for c in convos)

prim = dist(lambda c: c["fraud_type"]["primary_code"][:2])
outc = dist(lambda c: c["outcome"])
chan = dist(lambda c: c.get("channel"))
TYPE_NAME = {"T1": "기관사칭", "T2": "금융기관사칭", "T3": "대출사기", "T4": "가족·지인사칭",
             "T5": "투자사기", "T6": "전자금융", "T7": "일반사기", "T8": "불법금융", "T9": "자금세탁"}

def row(d):
    return "".join(f"<tr><td>{e(k)}</td><td style='text-align:right'>{v}</td></tr>" for k, v in d)

parts = []
parts.append(f"""<!doctype html><html lang=ko><head><meta charset=utf-8>
<style>
@page {{ size:A4; margin:14mm 12mm; }}
body {{ font-family:'Apple SD Gothic Neo','Noto Sans KR',sans-serif; font-size:10pt; line-height:1.5; color:#1a1a1a; }}
h1 {{ font-size:22pt; }} h2 {{ font-size:15pt; border-bottom:2px solid #2b5; padding-bottom:3px; margin-top:22px; page-break-after:avoid;}}
h3 {{ font-size:12pt; color:#225; margin-top:14px; }}
table {{ border-collapse:collapse; font-size:9pt; margin:6px 0; }} td,th {{ border:1px solid #ccc; padding:2px 7px; }}
.cover {{ text-align:center; margin-top:120px; page-break-after:always; }}
.cover h1 {{ font-size:30pt; margin-bottom:4px;}} .muted {{ color:#666; }}
.dlg {{ page-break-inside:avoid; border:1px solid #ddd; border-radius:6px; padding:7px 10px; margin:9px 0; }}
.dh {{ font-size:8.5pt; color:#444; background:#f3f5f7; padding:3px 6px; border-radius:4px; margin:-7px -10px 6px; }}
.atk {{ color:#b30000; font-weight:600; }} .vic {{ color:#0050b3; font-weight:600; }}
.turn {{ margin:1px 0; }} .tg {{ color:#999; font-size:7.5pt; }}
.ip {{ background:#fff3cd; }}
.toc li {{ margin:2px 0; }}
small {{ color:#666; }}
</style></head><body>""")

# 표지
parts.append(f"""<div class=cover>
<h1>MT-PhishingBench</h1>
<p style='font-size:13pt'>한국어 보이스피싱 멀티턴 대화 벤치마크 데이터셋</p>
<p class=muted>합성 대화 {len(convos):,}건 · FSS 실데이터 {fss['n_conversations']}건<br>
금융보안원(FSI) · 종합 보고서</p>
<p class=muted style='margin-top:40px;font-size:9pt'>github.com/FSI-AI/MT-PhishingBench</p>
</div>""")

# 1. 개요
parts.append(f"""<h2>1. 개요와 기여</h2>
<p>MT-PhishingBench는 집요한 공격자와 단계적으로 반응하는 피해자의 사실적 한국어 보이스피싱 대화를,
금융당국 공식 사기유형 분류(T1–T9)와 실데이터(FSS)에 grounding 하여 합성한 멀티턴 벤치마크다.</p>
<ul>
<li><b>멀티턴</b>: 평균 {round(sum(len(c['turns']) for c in convos)/len(convos),1)}턴의 집요한 전개(저항→반박→순응/차단)</li>
<li><b>3축 라벨</b>: 유형(T1–T9) × 진행단계 × 설득기법을 발화 단위로 부착</li>
<li><b>페르소나 통제</b>: Nemotron-Personas-Korea 취약군 층화</li>
<li><b>다태스크</b>: 탐지 · 유형분류 · 단계/기법 시퀀스 · 방어 개입시점</li>
<li><b>이중 grounding</b>: 실 피싱(FSS)·실 정상통화(AIHub) 기반</li>
</ul>""")

# 2. 방법론
parts.append("""<h2>2. 방법론 요약</h2>
<h3>2.1 3축 토대</h3>
<table><tr><th>축</th><th>내용</th><th>근거</th></tr>
<tr><td>유형</td><td>무슨 사기인가 (T1–T9)</td><td>금융당국 공식분류(FSI)</td></tr>
<tr><td>진행단계</td><td>접촉→기망→행동유도→편취</td><td>Crime Script Analysis (Cornish 1994)</td></tr>
<tr><td>설득기법</td><td>권위·긴급성·공포·고립·신뢰형성·순응유도·사회적증거</td><td>Cialdini / Stajano-Wilson(2011) / Ferreira(2015)</td></tr></table>
<h3>2.2 생성 파이프라인</h3>
<p>지식베이스[A] → 설계행렬[B](유형×페르소나×outcome×난이도×채널) → 시나리오 스캐폴드[C]
→ 멀티에이전트 합성[D](도메인지식 프롬프트·메타인식 차단·outcome 통제) → 라벨 검증[E] → 품질게이트[F].
턴길이·기법분포는 FSS 실통계에 맞춰 보정.</p>""")

# 3. 통계
ver_rows = "".join(f"<tr><td>{e(k)}</td><td>{e(str(v))}</td></tr>" for k, v in ver.items())
parts.append(f"""<h2>3. 데이터셋 통계</h2>
<h3>3.1 합성 대화 분포 ({len(convos):,}건)</h3>
<table><tr><th>유형</th><th>건수</th></tr>
{''.join(f"<tr><td>{k} {TYPE_NAME.get(k,'')}</td><td style='text-align:right'>{v}</td></tr>" for k,v in sorted(prim.items()))}</table>
<table><tr><th>결과(outcome)</th><th>건수</th></tr>{row(sorted(outc.items()))}</table>
<table><tr><th>채널</th><th>건수</th></tr>{row(sorted(chan.items()))}</table>
<h3>3.2 FSS 실데이터 통계 (grounding)</h3>
<table><tr><td>턴/대화 (median)</td><td>{stats['turns_per_conversation']['median']}</td></tr>
<tr><td>사기범:피해자 발화량비</td><td>{stats['attacker_vs_victim_char_ratio']} : 1</td></tr>
<tr><td>설득기법 신호빈도(상위)</td><td>{e(', '.join(list(stats['persuasion_technique_signal_freq'])[:4]))}</td></tr></table>
<h3>3.3 라벨 검증 (독립 표본 {ver.get('표본 대화수','')})</h3>
<table>{ver_rows}</table>""")

# 4. 참고문헌
parts.append("""<h2>4. 참고문헌</h2>
<h3>A. 이론 토대</h3><ul>
<li>Cornish, D. (1994). The Procedural Analysis of Offending (Crime Script Analysis).</li>
<li>Whitty, M. (2013). The Anatomy of the Online Dating Romance Scam. Security Journal.</li>
<li>Cialdini, R. Influence: The Psychology of Persuasion.</li>
<li>Stajano, F. & Wilson, P. (2011). Understanding Scam Victims: Seven Principles. CACM.</li>
<li>Ferreira, A. et al. (2015). Principles of Persuasion in Social Engineering and Their Use in Phishing. Springer.</li></ul>
<h3>B. 합성 대화 방법론</h3><ul>
<li>Wang, Y. et al. (2023). Self-Instruct. ACL.</li>
<li>Kim, H. et al. (2023). SODA: Million-scale Dialogue Distillation. EMNLP.</li>
<li>Li, G. et al. (2023). CAMEL: Communicative Agents. NeurIPS.</li>
<li>Park, J. et al. (2023). Generative Agents. UIST.</li>
<li>Jandaghi, P. et al. (2024). Faithful Persona-based Conversational Dataset Generation (Generator-Critic). NLP4ConvAI.</li>
<li>Liu, Y. et al. (2023). G-Eval. EMNLP.</li></ul>
<h3>C. 한국어 보이스피싱 탐지 선례</h3><ul>
<li>Kim, J.-W. et al. (2021). Real-time Korean voice phishing detection. J. Ambient Intelligence & Humanized Computing (Springer).</li>
<li>Boussougou & Park (2022/2023/2024). KoBERT / CNN-BiLSTM+FastText / KorCCVi v2(back-translation+SMOTE).</li>
<li>Yu, S. et al. (2024). NER + Sentence-Level N-Gram. IEEE Access.</li>
<li>Park, H. et al. (2025). LLM-Based Augmentation & CCDV metric. IEEE Access.</li>
<li>Sim & Kim (2025). Fine-Tuning Small LMs (arXiv 2506.06180); Talking Like a Phisher (arXiv 2507.16291).</li></ul>
<h3>D. AI 기반 공격 연구 (윤리 비교)</h3><ul>
<li>Figueiredo et al. (2024/2025). ViKing / Sounds Vishy (AsiaCCS).</li>
<li>Heiding & Lermen (2025). Jailbreaking LLMs to Phish Elderly (AAAI workshop).</li></ul>
<h3>E. 자원·문서화</h3><ul>
<li>NVIDIA (2026). Nemotron-Personas-Korea (CC BY 4.0).</li>
<li>금융감독원 보이스피싱 체험관 "바로 이 목소리" (실 피싱 음성).</li>
<li>Gebru, T. et al. (2021). Datasheets for Datasets. CACM.</li></ul>
<h3>윤리</h3><p><small>모든 대화는 합성이며 탐지·방어 연구 전용. 실 피싱은 공개자료 전사 텍스트만 grounding 에 사용. 텍스트 전용·비식별.</small></p>""")

# 5. FSS 실데이터 예시 (앞 3건)
def render_turns(turns, show_tags=True):
    out = []
    for t in turns:
        cls = "atk" if t["speaker"] == "사기범" else "vic"
        ipcls = " ip" if t.get("intervention_point") else ""
        tg = ""
        if show_tags and (t.get("stage") or t.get("psych_technique")):
            tg = f" <span class=tg>[{tag(t.get('stage',''))}{('·'+'/'.join(t['psych_technique'])) if t.get('psych_technique') else ''}]</span>"
        out.append(f"<div class='turn{ipcls}'><span class={cls}>{e(t['speaker'])}</span>: {e(t['text'])}{tg}</div>")
    return "".join(out)

parts.append("<h2>5. FSS 실데이터 예시</h2>")
for c in [x for x in fss["conversations"] if x["source"] == "fss_body_text"][:3]:
    parts.append(f"<div class=dlg><div class=dh>{e(c['conversation_id'])} · {e(c.get('title','')[:40])} · 출처:{e(c['source'])}</div>{render_turns(c['turns'], False)}</div>")

# 6. 합성 대화 전체
parts.append(f"<h2>6. 합성 대화 전체 ({len(convos):,}건)</h2>")
parts.append("<p><small>형식: 발화 끝 <span class=tg>[단계·기법]</span>, 노란 음영 = 방어 개입시점(intervention_point)</small></p>")
order = sorted(convos, key=lambda c: c["conversation_id"])
for c in order:
    p = c["victim_persona"]
    mo = ("·MO:" + ",".join(c["modus_operandi"])) if c.get("modus_operandi") else ""
    ld = ("·세탁:" + ",".join(c["laundering_overlay"])) if c.get("laundering_overlay") else ""
    head = (f"{e(c['conversation_id'])} · {e(c['fraud_type']['primary_code'])} {e(c['fraud_type']['leaf'])} · "
            f"{e(c['outcome'])} · {e(str(p.get('age')))}세 {e(p.get('vulnerability_group',''))} · "
            f"{e(c.get('channel',''))} · {len(c['turns'])}턴{e(mo)}{e(ld)}")
    parts.append(f"<div class=dlg><div class=dh>{head}</div>{render_turns(c['turns'])}</div>")

parts.append("</body></html>")
OUT.write_text("".join(parts), encoding="utf-8")
print(f"HTML 생성: {OUT} ({OUT.stat().st_size//1024} KB, 대화 {len(convos)+3}건 수록)")
