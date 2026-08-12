import html
import inspect
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

print("API key loaded:", bool(os.getenv("OPENAI_API_KEY")))

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"

APP_TITLE = "Revival Lab"
APP_TAGLINE = "Old ideas. New evidence. Future solutions."

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --archive-black: #10100f;
  --charcoal: #181716;
  --charcoal-soft: #22201e;
  --paper: #f2ead8;
  --paper-deep: #e4d5b5;
  --ink: #22201d;
  --muted-ink: #6f6659;
  --folder-blue: #8fa3af;
  --folder-blue-dark: #637781;
  --tab-red: #9f3530;
  --receipt-yellow: #d6bb73;
  --excerpt-pink: #d6a8a8;
  --border-dark: #2b2925;
  --shadow: rgba(0, 0, 0, 0.45);
}

body, .gradio-container {
  background: var(--archive-black) !important;
  color: #eee7d7 !important;
  font-family: 'Inter', system-ui, sans-serif !important;
}

.gradio-container {
  max-width: 1280px !important;
  margin: 0 auto !important;
}

/* Hide Gradio Footer */
footer {
  display: none !important;
}

#revival-shell {
  background: var(--archive-black);
  min-height: auto;
}

.archive-hero {
  border: 1px solid #38332d;
  background: #151412;
  padding: 18px 24px;
  margin: 0 auto 12px auto;
  box-shadow: 0 18px 60px var(--shadow);
  text-align: center;
  max-width: 900px;
}

.eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: #b8aa8d !important;
  font-size: 12px;
}

.archive-title {
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: clamp(36px, 5vw, 68px);
  line-height: .96;
  margin: 8px 0 10px;
  color: #eee2c7 !important;
  font-weight: 700;
  text-align: center;
}

.archive-subtitle {
  max-width: 760px;
  color: #bdb3a1 !important;
  font-size: 15px;
  line-height: 1.6;
  margin: 0 auto;
  text-align: center;
}

.gr-button {
  background: #22201e !important;
  border: 1px solid #b8aa8d !important;
  color: #f1e6cb !important;
  border-radius: 2px !important;
  font-family: 'IBM Plex Mono', monospace !important;
  text-transform: uppercase;
  letter-spacing: .08em;
  box-shadow: none !important;
}

.gr-button:hover {
  background: #2c2925 !important;
  border-color: #ead8aa !important;
}

textarea, input, select, .wrap, .block, .form, .panel {
  border-radius: 2px !important;
}

textarea, input, select {
  background: #ebe0c8 !important;
  color: #211f1b !important;
  border: 1px solid #8a7d65 !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-weight: 700 !important;
}

textarea::placeholder, input::placeholder {
  color: #534c3e !important;
  font-weight: 600 !important;
}

label, .label-wrap span {
  color: #d8c8a7 !important;
  font-family: 'IBM Plex Mono', monospace !important;
  letter-spacing: .04em;
  font-weight: 700 !important;
}

.input-folder {
  position: relative;
  background: var(--folder-blue);
  border: 1px solid #53656e;
  color: #1f2528 !important;
  padding: 28px 24px 24px;
  margin-bottom: 16px;
  box-shadow: 0 18px 40px var(--shadow);
}

.input-folder:before {
  content: '';
  position: absolute;
  top: -22px;
  left: 22px;
  width: 190px;
  height: 28px;
  background: var(--folder-blue-dark);
  border: 1px solid #53656e;
  border-bottom: none;
}

.input-folder h2 {
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 34px;
  margin: 0 0 10px;
  color: #172023 !important;
}

.input-folder p {
  font-family: 'IBM Plex Mono', monospace;
  margin: 0;
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #29363b !important;
}

.closed-case {
  position: relative;
  min-height: 520px;
  background: #141311;
  border: 1px solid #38332d;
  padding: 34px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px #0c0b0a, 0 18px 70px var(--shadow);
}

.closed-folder {
  position: relative;
  width: min(660px, 92%);
  margin: 40px auto 0;
  padding: 54px 46px 70px;
  background: var(--folder-blue);
  border: 1px solid #52646d;
  box-shadow: 0 30px 80px rgba(0,0,0,.54);
  transform-origin: center bottom;
  animation: folderLift 900ms ease both;
  text-align: center;
}

.closed-folder:before {
  content: '';
  position: absolute;
  left: 28px;
  top: -34px;
  width: 220px;
  height: 44px;
  background: var(--folder-blue-dark);
  border: 1px solid #52646d;
  border-bottom: none;
}

.closed-folder h1 {
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: clamp(42px, 7vw, 76px);
  line-height: 1;
  color: #172023 !important;
  margin: 0 auto 14px auto;
  text-align: center;
}

.closed-folder .seal {
  display: inline-block;
  margin-top: 28px;
  padding: 9px 14px;
  border: 2px solid var(--tab-red);
  color: var(--tab-red) !important;
  font-family: 'IBM Plex Mono', monospace;
  text-transform: uppercase;
  letter-spacing: .11em;
  transform: rotate(-4deg);
}

.closed-folder p {
  color: #2f3c41 !important;
  max-width: 480px;
  line-height: 1.7;
  margin: 0 auto;
  text-align: center;
}

.dossier {
  position: relative;
  background: #12110f;
  border: 1px solid #3b362f;
  padding: 38px 34px 52px;
  min-height: 620px;
  box-shadow: inset 0 0 0 1px #0a0908, 0 18px 70px var(--shadow);
}

.dossier:before {
  content: '';
  position: absolute;
  left: 42px;
  top: 30px;
  right: 42px;
  height: 72px;
  background: var(--folder-blue);
  border: 1px solid #52646d;
}

.dossier:after {
  content: 'ARCHIVE';
  position: absolute;
  top: 44px;
  right: 64px;
  background: var(--tab-red);
  color: #f3dfc2 !important;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  letter-spacing: .16em;
  padding: 8px 14px;
}

.paper-stack {
  position: relative;
  margin: 62px auto 0;
  max-width: 980px;
}

.paper-stack:before,
.paper-stack:after {
  content: '';
  position: absolute;
  inset: 18px -14px -18px 18px;
  background: #d8cab0;
  border: 1px solid #9a8c75;
  transform: rotate(1.1deg);
  z-index: 0;
}

.paper-stack:after {
  inset: 34px 10px -34px -12px;
  background: #cfc0a5;
  transform: rotate(-1.2deg);
}

.case-paper {
  position: relative;
  z-index: 1;
  background: var(--paper);
  color: var(--ink) !important;
  border: 1px solid #9b8d73;
  padding: 34px;
  box-shadow: 0 24px 50px rgba(0,0,0,.32);
  animation: fadePaper 650ms ease both;
}

.case-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  border-bottom: 1px solid #b7a98d;
  padding-bottom: 18px;
  margin-bottom: 22px;
}

.case-header h2 {
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: clamp(34px, 5vw, 64px);
  margin: 0;
  line-height: 1;
  color: var(--ink) !important;
}

.case-meta {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: var(--muted-ink) !important;
  text-transform: uppercase;
  line-height: 1.7;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0 22px;
}

.tab {
  background: var(--tab-red);
  color: #f3dfc2 !important;
  padding: 7px 12px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.paper-card {
  background: #fff6df;
  border: 1px solid #bdad8e;
  padding: 18px 19px;
  color: var(--ink) !important;
  box-shadow: 7px 8px 0 rgba(81, 67, 44, .12);
  animation: fadePaper 700ms ease both;
}

.paper-card h3 {
  font-family: 'Libre Baskerville', Georgia, serif;
  margin: 0 0 10px;
  color: #1e1b18 !important;
  font-size: 22px;
  font-weight: 700 !important;
}

.paper-card p, .paper-card li, .case-paper p, .case-paper li, .closed-folder p {
  line-height: 1.65;
  color: #1e1b18 !important;
  font-weight: 700 !important;
}


.paper-card strong,
.case-paper strong,
.verdict-card strong {
  color: #6f1d1b !important;
  font-weight: 800 !important;
}



.paper-card ul {
  padding-left: 20px;
}

.paper-card:nth-child(2n) {
  background: var(--excerpt-pink);
}

.paper-card:nth-child(3n) {
  background: var(--receipt-yellow);
}

.paper-card.full {
  grid-column: 1 / -1;
}

.verdict-card {
  position: relative;
  background: #fff6df;
  border: 1px solid #9f3530;
  padding: 20px;
  min-height: 150px;
}

.verdict-stamp {
  display: inline-block;
  border: 3px solid var(--tab-red);
  color: var(--tab-red) !important;
  padding: 10px 16px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 18px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  transform: rotate(-5deg);
  animation: stampIn 620ms cubic-bezier(.2,1.2,.3,1) both;
  margin-bottom: 12px;
}

.source-list {
  margin-top: 18px;
  border-top: 1px solid #b7a98d;
  padding-top: 16px;
}

.source-chip {
  display: inline-block;
  background: #e8dcc4;
  border: 1px solid #a99a80;
  color: #383025 !important;
  margin: 4px 5px 4px 0;
  padding: 7px 9px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
}

.evidence-drawer {
  margin-top: 18px;
  background: #191715;
  border: 1px solid #3b362f;
  padding: 16px;
  color: #dfd2b8 !important;
}

.evidence-drawer h3 {
  font-family: 'Libre Baskerville', Georgia, serif;
  margin: 0 0 10px;
  color: #f1e6cb !important;
}

.evidence-item {
  border-left: 3px solid var(--folder-blue);
  padding: 10px 12px;
  background: #211f1b;
  margin: 10px 0;
  color: #d7c9ab !important;
}

.evidence-item b {
  color: #f1e6cb !important;
}

@keyframes folderLift {
  from { opacity: 0; transform: translateY(24px) rotate(.5deg); }
  to { opacity: 1; transform: translateY(0) rotate(-.4deg); }
}

@keyframes fadePaper {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes stampIn {
  0% { opacity: 0; transform: scale(1.45) rotate(-12deg); }
  62% { opacity: 1; transform: scale(.96) rotate(-5deg); }
  100% { opacity: 1; transform: scale(1) rotate(-5deg); }
}

@media (max-width: 900px) {
  .card-grid { grid-template-columns: 1fr; }
  .case-header { display: block; }
  .dossier { padding: 24px 16px 36px; }
  .case-paper { padding: 24px 18px; }
}
"""


def parse_doc(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    data = {"filename": path.name, "content": text, "title": path.stem.replace("_", " ").title()}
    current = None
    buf: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"^([A-Za-z /&-]+):\s*(.*)$", line)
        if m and len(m.group(1)) < 40:
            if current:
                data[current] = "\n".join(buf).strip()
            current = m.group(1).strip().lower().replace(" ", "_").replace("/", "_").replace("&", "and")
            buf = [m.group(2).strip()] if m.group(2).strip() else []
        else:
            if current:
                buf.append(raw)
    if current:
        data[current] = "\n".join(buf).strip()
    if data.get("title"):
        data["title"] = data["title"].splitlines()[0].strip()
    return data


def load_docs() -> List[Dict[str, str]]:
    if not DATA_DIR.exists():
        return []
    return [parse_doc(p) for p in sorted(DATA_DIR.glob("*.txt"))]


def score_doc(query: str, doc: Dict[str, str]) -> int:
    q_words = set(re.findall(r"[a-zA-Z]{4,}", query.lower()))
    content = (doc.get("title", "") + " " + doc.get("content", "")).lower()
    score = sum(3 if w in doc.get("title", "").lower() else 1 for w in q_words if w in content)
    synonyms = {
        "cool": ["windcatcher", "courtyard", "jaali", "roof", "thermal", "ventilation", "mudbrick"],
        "heat": ["windcatcher", "courtyard", "jaali", "roof", "shade", "thermal", "solar"],
        "flood": ["rain", "bioswale", "wetland", "permeable", "drainage", "mangrove"],
        "water": ["qanat", "stepwell", "rainwater", "cistern", "irrigation", "fog", "tank"],
        "crop": ["zai", "terracing", "agroforestry", "mulch", "irrigation", "seed"],
        "drought": ["zai", "qanat", "rainwater", "clay", "terracing", "seed", "tank"],
        "food": ["zeer", "storage", "cellar", "cool", "seed"],
        "coastal": ["mangrove", "buffer", "storm", "surge", "erosion"],
    }
    for key, vals in synonyms.items():
        if key in query.lower():
            score += sum(4 for v in vals if v in content)
    return score


def keyword_retrieve(query: str, docs: List[Dict[str, str]], k: int = 6) -> List[Dict[str, str]]:
    ranked = sorted(docs, key=lambda d: score_doc(query, d), reverse=True)
    return [d for d in ranked[:k] if score_doc(query, d) > 0] or ranked[:k]


def chroma_retrieve(query: str, k: int = 6) -> Tuple[List[Dict[str, str]], str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        api_key = api_key.strip()
    if not api_key or not DB_DIR.exists():
        return [], "Keyword fallback"
    try:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
        db = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
        results = db.max_marginal_relevance_search(query, k=k, fetch_k=max(20, k * 4), lambda_mult=0.55)
        docs = []
        for r in results:
            metadata = dict(r.metadata or {})
            docs.append({
                "title": metadata.get("title", metadata.get("source_file", "Retrieved Evidence")),
                "filename": metadata.get("source_file", "chroma_db"),
                "content": r.page_content,
                "source": "Chroma MMR vector search",
                **metadata,
            })
        return docs, "Chroma vector search (MMR)"
    except Exception as exc:
        return [], f"Keyword fallback because Chroma/OpenAI retrieval failed: {exc}"


def build_context(retrieved: List[Dict[str, str]]) -> str:
    parts = []
    for i, d in enumerate(retrieved, 1):
        metadata_bits = []
        for key in ["category", "problem_type", "climate_fit", "regions", "modern_verdict", "risk_level", "confidence_level", "tags"]:
            if d.get(key):
                metadata_bits.append(f"{key}: {d.get(key)}")
        metadata = "\n".join(metadata_bits)
        parts.append(
            f"SOURCE {i}: {d.get('title')} ({d.get('filename')})\n"
            f"{metadata}\n\n{d.get('content','')[:1800]}"
        )
    return "\n\n".join(parts)


def llm_answer(problem: str, location: str, conditions: str, resources: str, retrieved: List[Dict[str, str]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        api_key = api_key.strip()
    context = build_context(retrieved)
    if api_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.22, api_key=api_key)
            prompt = f"""
You are Revival Lab, an AI investigation team. Use ONLY the retrieved evidence below. If evidence is missing, say so.

User problem: {problem}
Location: {location}
Conditions: {conditions or 'Not specified'}
Available resources: {resources or 'Not specified'}

Retrieved evidence:
{context}

Write a sophisticated archival case-file report with exactly these sections and headings:
1. Case Summary
2. Retrieved Forgotten Solutions
3. Origin Investigation
4. Evidence Review
5. Revival Engineering Plan
6. Final Review Board Verdict

Rules:
- Be specific, skeptical, and practical.
- Include a final verdict of Worth Reviving, Needs More Research, or Not Practical Today.
- Explain climate/location fit.
- Do not sound like a chatbot. Sound like a careful investigation brief.
"""
            return llm.invoke(prompt).content
        except Exception as exc:
            return fallback_answer(problem, location, conditions, resources, retrieved, f"LLM call failed: {exc}")
    return fallback_answer(problem, location, conditions, resources, retrieved, "No OPENAI_API_KEY found, so this is a local fallback report.")


def fallback_answer(problem: str, location: str, conditions: str, resources: str, retrieved: List[Dict[str, str]], note: str) -> str:
    titles = [d.get("title", "Untitled") for d in retrieved]
    primary = titles[0] if titles else "No candidate found"
    evidence = "\n".join([f"- {d.get('title')}: {d.get('content','')[:260].replace(chr(10),' ')}..." for d in retrieved[:4]])
    verdict = "Needs More Research"
    combined = f"{problem} {location} {conditions} {resources}".lower()
    if any(w in combined for w in ["cool", "heat", "air conditioning"]) and any("wind" in t.lower() or "courtyard" in t.lower() or "roof" in t.lower() for t in titles):
        verdict = "Worth Reviving — with climate-specific modifications"
    if any(w in combined for w in ["karachi", "humid", "coastal"]):
        verdict = "Needs More Research — humidity and pollution require hybrid design"
    return f"""
1. Case Summary
Problem: {problem}
Location: {location}
Conditions: {conditions or 'Not specified'}
Available resources: {resources or 'Not specified'}
Primary candidate: {primary}
System note: {note}

2. Retrieved Forgotten Solutions
{chr(10).join([f'- {t}' for t in titles])}

3. Origin Investigation
The retrieved documents suggest these are not random modern hacks. They come from older building, water, farming, storage, or landscape traditions. Exact origin should be treated carefully because several practices evolved independently across different regions.

4. Evidence Review
{evidence}

5. Revival Engineering Plan
Modern revival should not copy the old form blindly. Begin with a small pilot, adapt it to the local climate, use present-day materials and monitoring, and compare performance against a normal control site. Where relevant, add filters, low-power fans, sensors, maintenance planning, or local construction methods.

6. Final Review Board Verdict
Verdict: {verdict}
Reason: The evidence suggests promise, but feasibility depends on local climate, maintenance capacity, materials, cost, and social adoption.
"""


def escape(text: str) -> str:
    return html.escape(text or "")


def inline_markdown(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    return text


def block_markdown(text: str) -> str:
    lines = [line.rstrip() for line in (text or "").strip().splitlines()]
    html_parts: List[str] = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue
        if re.match(r"^[-•]\s+", stripped):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            item = re.sub(r"^[-•]\s+", "", stripped)
            html_parts.append(f"<li>{inline_markdown(item)}</li>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            cleaned = re.sub(r"^#{1,4}\s*", "", stripped)
            cleaned = re.sub(r"^\d+\.\s*", "", cleaned)
            html_parts.append(f"<p>{inline_markdown(cleaned)}</p>")
    if in_list:
        html_parts.append("</ul>")
    return "\n".join(html_parts) or "<p>Evidence not available.</p>"


def sectionize(report: str) -> Dict[str, str]:
    wanted = [
        "Case Summary",
        "Retrieved Forgotten Solutions",
        "Origin Investigation",
        "Evidence Review",
        "Revival Engineering Plan",
        "Final Review Board Verdict",
    ]
    normalized = report.replace("\r\n", "\n")
    pattern = r"(?im)^\s*(?:\*+)?(?:#{1,4}\s*)?(?:\d+\.\s*)?(?:\*+)?(Case Summary|Retrieved Forgotten Solutions|Origin Investigation|Evidence Review|Revival Engineering Plan|Final Review Board Verdict)(?:\*+)?\s*:?.*$"
    matches = list(re.finditer(pattern, normalized))
    sections = {name: "" for name in wanted}
    if not matches:
        sections["Case Summary"] = normalized
        return sections
    for idx, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
        sections[name] = normalized[start:end].strip()
    return sections


def verdict_text(report: str) -> str:
    m = re.search(r"(?i)verdict\s*:\s*([^\n.]+)", report)
    if m:
        return m.group(1).strip()[:72]
    lowered = report.lower()
    if "worth reviving" in lowered:
        return "Worth Reviving"
    if "not practical" in lowered:
        return "Not Practical Today"
    return "Needs More Research"


def source_chips(retrieved: List[Dict[str, str]]) -> str:
    chips = []
    for d in retrieved:
        title = escape(d.get("title", "Source"))
        climate = escape(d.get("climate_fit", ""))
        label = title if not climate else f"{title} · {climate}"
        chips.append(f"<span class='source-chip'>{label}</span>")
    return "".join(chips)


def evidence_drawer(retrieved: List[Dict[str, str]], mode: str) -> str:
    items = []
    for i, d in enumerate(retrieved, 1):
        meta = []
        for key, label in [("filename", "File"), ("category", "Category"), ("problem_type", "Problem"), ("climate_fit", "Climate"), ("modern_verdict", "Stored Verdict")]:
            if d.get(key):
                meta.append(f"<b>{label}:</b> {escape(str(d.get(key)))}")
        snippet = escape(d.get("content", "")[:640]).replace("\n", "<br>")
        items.append(
            f"<div class='evidence-item'><b>{i}. {escape(d.get('title', 'Source'))}</b><br>"
            f"{'<br>'.join(meta)}<br><br>{snippet}</div>"
        )
    return f"""
    <div class='evidence-drawer'>
      <h3>Retrieved Evidence Drawer</h3>
      <div class='case-meta'>Retrieval mode: {escape(mode)}</div>
      {''.join(items)}
    </div>
    """


def closed_state_html() -> str:
    return f"""
    <div class='closed-case'>
      <div class='closed-folder'>
        <div class='eyebrow'>Sealed archive dossier</div>
        <h1>Revival Case File</h1>
        <p>Enter a modern problem, location, conditions, and available resources. The archive will open after the investigation returns its report.</p>
        <div class='seal'>Awaiting Investigation</div>
      </div>
    </div>
    """


def open_case_html(problem: str, location: str, conditions: str, resources: str, report: str, retrieved: List[Dict[str, str]], mode: str) -> str:
    sections = sectionize(report)
    stamp = escape(verdict_text(report))
    case_id = abs(hash(problem + location)) % 10000
    return f"""
    <div class='dossier'>
      <div class='paper-stack'>
        <div class='case-paper'>
          <div class='case-header'>
            <div>
              <div class='eyebrow'>Revival Lab archive</div>
              <h2>Case File</h2>
            </div>
            <div class='case-meta'>
              Case No. RL-{case_id:04d}<br>
              Evidence Retrieved: {len(retrieved)}<br>
              Mode: {escape(mode)}
            </div>
          </div>

          <div class='tabs'>
            <span class='tab'>Origin</span>
            <span class='tab'>Evidence</span>
            <span class='tab'>Engineering</span>
            <span class='tab'>Verdict</span>
          </div>

          <div class='card-grid'>
            <div class='paper-card full'>
              <h3>1. Case Summary</h3>
              <p><strong>Problem:</strong> {escape(problem)}</p>
              <p><strong>Location:</strong> {escape(location)}</p>
              <p><strong>Conditions:</strong> {escape(conditions or 'Not specified')}</p>
              <p><strong>Resources:</strong> {escape(resources or 'Not specified')}</p>
            </div>

            <div class='paper-card'>
              <h3>2. Retrieved Forgotten Solutions</h3>
              {block_markdown(sections.get('Retrieved Forgotten Solutions', ''))}
            </div>

            <div class='paper-card'>
              <h3>3. Origin Investigation</h3>
              {block_markdown(sections.get('Origin Investigation', ''))}
            </div>

            <div class='paper-card'>
              <h3>4. Evidence Review</h3>
              {block_markdown(sections.get('Evidence Review', ''))}
            </div>

            <div class='paper-card'>
              <h3>5. Revival Engineering Plan</h3>
              {block_markdown(sections.get('Revival Engineering Plan', ''))}
            </div>

            <div class='paper-card full verdict-card'>
              <div class='verdict-stamp'>{stamp}</div>
              <h3>6. Final Review Board Verdict</h3>
              {block_markdown(sections.get('Final Review Board Verdict', ''))}
            </div>
          </div>

          <div class='source-list'>
            <div class='case-meta'>Source tags recovered from archive</div>
            {source_chips(retrieved)}
          </div>
        </div>
      </div>
      {evidence_drawer(retrieved, mode)}
    </div>
    """


def run_investigation(problem: str, location: str, conditions: str, resources: str) -> str:
    docs = load_docs()
    if not docs:
        return "<div class='closed-case'><div class='closed-folder'><h1>No archive found</h1><p>No documents were found in data/.</p></div></div>"
    if not problem or not problem.strip():
        return closed_state_html()

    query = " ".join([problem.strip(), location or "", conditions or "", resources or ""])
    retrieved, mode = chroma_retrieve(query, k=6)
    if not retrieved:
        retrieved = keyword_retrieve(query, docs, k=6)
        if mode and "Keyword fallback" in mode:
            mode = "Local keyword retrieval"
    report = llm_answer(problem.strip(), location or "General / unknown", conditions or "", resources or "", retrieved)
    return open_case_html(problem.strip(), location or "General / unknown", conditions or "", resources or "", report, retrieved, mode)


def demo_values():
    return (
        "How can we cool buildings without expensive air conditioning?",
        "Karachi — hot humid coastal",
        "Dense urban blocks, unreliable electricity, dust, humidity, limited roof space",
        "Low-cost materials, local labor, school or community-center pilot",
    )


blocks_kwargs = {"title": "Revival Lab — Case File"}
if "css" in inspect.signature(gr.Blocks).parameters:
    blocks_kwargs["css"] = CSS

with gr.Blocks(**blocks_kwargs) as demo:
    gr.HTML(
        """
        <div id='revival-shell'>
          <div class='archive-hero'>
            <div class='eyebrow'>Forensic AI research lab</div>
            <div class='archive-title'>Revival Lab</div>
            <p class='archive-subtitle'>A RAG-powered archive that investigates forgotten solutions, checks their evidence, and decides whether they deserve a second life.</p>
          </div>
        </div>
        """
    )

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, min_width=360):
            gr.HTML(
                """
                <div class='input-folder'>
                  <p>Closed state</p>
                  <h2>Revival Case File</h2>
                  <p>Complete the dossier fields, then start the investigation.</p>
                </div>
                """
            )
            problem_input = gr.Textbox(
                label="Problem",
                placeholder="Example: How can we cool buildings without expensive air conditioning?",
                lines=4,
            )
            location_input = gr.Dropdown(
                label="Location",
                choices=[
                    "Karachi — hot humid coastal",
                    "Lahore — hot summers / mixed humidity",
                    "Hot-dry city",
                    "Flood-prone city",
                    "Drought-prone farming region",
                    "General / unknown",
                ],
                value="Karachi — hot humid coastal",
            )
            conditions_input = gr.Textbox(
                label="Conditions",
                placeholder="Example: high humidity, dust, dense buildings, unreliable electricity",
                lines=3,
            )
            resources_input = gr.Textbox(
                label="Resources",
                placeholder="Example: low-cost materials, local labor, school pilot, rooftop access",
                lines=3,
            )
            with gr.Row():
                demo_button = gr.Button("Load Judge Demo")
                start_button = gr.Button("Start Investigation", variant="primary")

        with gr.Column(scale=2):
            output_html = gr.HTML(value=closed_state_html())

    demo_button.click(
        fn=demo_values,
        inputs=None,
        outputs=[problem_input, location_input, conditions_input, resources_input],
    )
    start_button.click(
        fn=run_investigation,
        inputs=[problem_input, location_input, conditions_input, resources_input],
        outputs=output_html,
    )

if __name__ == "__main__":
    launch_kwargs = {}
    if "css" in inspect.signature(demo.launch).parameters:
        launch_kwargs["css"] = CSS
    demo.launch(**launch_kwargs)
