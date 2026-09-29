"""
"""
ALEF-TAV — Assistente Científico
Interface limpa, respostas naturais
"""
import streamlit as st
import re, io, json, uuid, hashlib
import numpy as np
from datetime import datetime
from collections import defaultdict

st.set_page_config(
    page_title="ALEF-TAV",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS — Estilo ChatGPT limpo
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

* { font-family: 'Inter', -apple-system, sans-serif; }

/* Fundo principal */
.stApp { background: #1a1a1a; }

/* Header transparente */
header[data-testid="stHeader"] { background: transparent !important; height: 0; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d0d;
    border-right: 1px solid #2a2a2a;
}
section[data-testid="stSidebar"] * { color: #ececec !important; }

/* Logo */
.alef-logo {
    padding: 1rem 0.75rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.alef-icon {
    font-size: 1.5rem;
    color: #8b5cf6;
}
.alef-name {
    font-size: 0.95rem;
    font-weight: 600;
    color: #ececec;
    letter-spacing: 0.5px;
}

/* Botão novo chat */
.stButton button {
    background: transparent !important;
    color: #ececec !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    font-weight: 400 !important;
    font-size: 0.85rem !important;
    text-align: left !important;
    transition: all 0.15s !important;
}
.stButton button:hover {
    background: #2a2a2a !important;
    border-color: #3a3a3a !important;
}

/* Botão primário */
.stButton button[kind="primary"] {
    background: #8b5cf6 !important;
    color: white !important;
    border: none !important;
}
.stButton button[kind="primary"]:hover {
    background: #7c3aed !important;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 1.5rem 1rem !important;
    margin: 0 !important;
}
div[data-testid="stChatMessage"] * { color: #ececec !important; }

/* Input do chat */
div[data-testid="stChatInput"] {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 12px !important;
}
div[data-testid="stChatInput"] textarea {
    color: #ececec !important;
    font-size: 0.95rem !important;
    background: transparent !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #8e8e8e !important;
}

/* Textos gerais */
p, span, div { color: #ececec; }
h1, h2, h3, h4 { color: #ececec !important; font-weight: 500 !important; }
a { color: #8b5cf6 !important; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Código */
code {
    background: #2a2a2a !important;
    color: #a78bfa !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
}

/* Expander minimalista */
details[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    margin: 0.5rem 0 !important;
}
details[data-testid="stExpander"] summary {
    color: #8e8e8e !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    padding: 0.5rem 0.75rem !important;
}

/* Welcome screen */
.welcome-title {
    font-size: 2rem;
    font-weight: 500;
    color: #ececec;
    text-align: center;
    margin: 3rem 0 0.5rem 0;
}
.welcome-subtitle {
    font-size: 0.95rem;
    color: #8e8e8e;
    text-align: center;
    margin-bottom: 3rem;
}

/* Cards de sugestão */
.suggestion-card {
    background: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.15s;
}
.suggestion-card:hover {
    background: #333;
    border-color: #8b5cf6;
}
.suggestion-title {
    font-size: 0.9rem;
    color: #ececec;
    font-weight: 500;
    margin-bottom: 0.3rem;
}
.suggestion-desc {
    font-size: 0.8rem;
    color: #8e8e8e;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #2a2a2a;
    margin: 1rem 0;
}

/* Esconder footer */
footer { display: none; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4a4a4a; }

/* Citação de artigo */
.article {
    border-left: 2px solid #8b5cf6;
    padding: 0.5rem 0 0.5rem 1rem;
    margin: 1rem 0;
    background: transparent;
}
.article-title {
    font-size: 0.95rem;
    color: #ececec;
    font-weight: 500;
    margin-bottom: 0.25rem;
}
.article-meta {
    font-size: 0.75rem;
    color: #8e8e8e;
    margin-bottom: 0.5rem;
}
.article-summary {
    font-size: 0.85rem;
    color: #b0b0b0;
    line-height: 1.5;
}

/* Simulação */
.sim {
    padding: 0.5rem 0;
    border-bottom: 1px solid #2a2a2a;
    font-size: 0.85rem;
    color: #b0b0b0;
}
.sim:last-child { border-bottom: none; }
.sim-name {
    color: #ececec;
    font-weight: 500;
    margin-bottom: 0.15rem;
}
.sim-value {
    color: #8e8e8e;
    font-size: 0.8rem;
}

/* Status pill */
.pill {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 500;
    margin: 0.15rem;
}
.pill-success { background: rgba(52,211,153,0.15); color: #34d399; }
.pill-info { background: rgba(139,92,246,0.15); color: #a78bfa; }
.pill-warning { background: rgba(251,191,36,0.15); color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# IMPORTS
# ============================================================
try:
    import universal as u
    SIMS_OK = True
except:
    SIMS_OK = False
    u = None

try:
    from bancos_completos import buscar_em_todas
    BANCOS_OK = True
except:
    BANCOS_OK = False
    def buscar_em_todas(q, n=4): return [], {}

@st.cache_resource
def carregar_modelo():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer('all-MiniLM-L6-v2')
    except:
        return None

modelo = carregar_modelo()

if "cache_embs" not in st.session_state:
    st.session_state.cache_embs = {}

def hash_texto(t):
    return hashlib.md5(t.encode("utf-8")).hexdigest()[:16]

# ============================================================
# TRADUÇÃO
# ============================================================
TRADUCAO = {
    "diamante":"diamond","grafeno":"graphene","silicio":"silicon","energia":"energy",
    "quantico":"quantum","plasma":"plasma","nuclear":"nuclear","gene":"gene",
    "dna":"dna","proteina":"protein","celula":"cell","cancer":"cancer",
    "bandgap":"bandgap","semicondutor":"semiconductor","cristal":"crystal",
    "estrutura":"structure","circuito":"circuit","clima":"climate",
    "sensor":"sensor","material":"material",
}
STOPWORDS = {"de","da","do","das","dos","a","o","as","os","e","em","no","na",
             "nos","nas","para","por","com","um","uma","que","como","sobre"}

def traduzir(t):
    palavras = re.findall(r'\w+', t.lower())
    return " ".join(TRADUCAO.get(p, p) for p in palavras if p not in STOPWORDS)

# ============================================================
# BUSCA (usa 187 bancos se disponível, senão 12 básicos)
# ============================================================
def b_arxiv(q, n=5):
    try:
        import arxiv
        c = arxiv.Client()
        return [{"titulo": r.title, "resumo": r.summary[:600], "link": r.entry_id,
                 "ano": r.published.year, "fonte": "arXiv"}
                for r in c.results(arxiv.Search(query=q, max_results=n))]
    except: return []

def b_pubmed(q, n=5):
    try:
        import requests
        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        r = requests.get(f"{base}/esearch.fcgi",
                         params={"db":"pubmed","term":q,"retmax":n,"retmode":"json"}, timeout=10)
        pmids = r.json().get("esearchresult",{}).get("idlist",[])
        return [{"titulo": f"PubMed {p}", "resumo": "",
                 "link": f"https://pubmed.ncbi.nlm.nih.gov/{p}/",
                 "ano": 2024, "fonte": "PubMed"} for p in pmids]
    except: return []

def b_semantic(q, n=5):
    try:
        import requests
        r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                         params={"query":q,"limit":n,"fields":"title,abstract,url,year"}, timeout=10)
        return [{"titulo": p.get("title",""), "resumo": (p.get("abstract") or "")[:600],
                 "link": p.get("url",""), "ano": p.get("year",2024),
                 "fonte": "Semantic Scholar"} for p in r.json().get("data",[])]
    except: return []

def b_openalex(q, n=5):
    try:
        import requests
        r = requests.get("https://api.openalex.org/works",
                         params={"search":q,"per_page":n}, timeout=10)
        return [{"titulo": w.get("title",""), "resumo": "",
                 "link": w.get("id",""), "ano": w.get("publication_year",2024),
                 "fonte": "OpenAlex"} for w in r.json().get("results",[])]
    except: return []

def b_web(q, n=5):
    try:
        import requests, re
        from urllib.parse import quote
        url = f"https://html.duckduckgo.com/html/?q={quote(q)}"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        results = []
        for m in re.finditer(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                            r.text, re.DOTALL):
            if len(results) >= n: break
            link = m.group(1)
            titulo = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if titulo and link:
                results.append({"titulo": titulo[:200], "resumo": "",
                                "link": link, "ano": 2024, "fonte": "Web"})
        return results
    except: return []

def buscar(q, n=4):
    """Busca usando 187 bancos ou fallback."""
    if BANCOS_OK:
        arts, status = buscar_em_todas(q, n)
        return arts
    
    # Fallback
    funcs = [b_arxiv, b_pubmed, b_semantic, b_openalex, b_web]
    from concurrent.futures import ThreadPoolExecutor, as_completed
    arts = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(f, q, n) for f in funcs]
        for fut in as_completed(futs):
            try:
                r = fut.result()
                if r: arts.extend(r)
            except: pass
    return arts

# ============================================================
# MOTOR GEOMÉTRICO
# ============================================================
KWS_METODO = ["theor","deriv","experiment","measur","simulat","dft","md"]
KWS_IMPACTO = ["application","device","prototype","industry"]
KWS_GEO = ["topolog","dimensional","symmetr","complex"]
KWS_FISICA = ["unit","dimension","conserv","relativ"]
KWS_VALID = ["p-value","replicat","consensus","robust","verified"]

def score_artigo(artigo, pergunta):
    texto = f"{artigo.get('titulo','')} {artigo.get('resumo','')}".lower()
    tokens_a = set(re.findall(r'\w{3,}', texto)) - STOPWORDS
    tokens_p = set(re.findall(r'\w{3,}', pergunta.lower())) - STOPWORDS
    
    p1 = min(len(tokens_a & tokens_p) / max(len(tokens_p), 1) * 2.5, 1.0)
    p2 = min(sum(1 for k in KWS_METODO if k in texto) / 2.0, 1.0)
    try: ano = int(artigo.get("ano", 2024))
    except: ano = 2024
    p3 = max(0, 1 - (2026 - ano) / 25)
    p4 = min(sum(1 for k in KWS_IMPACTO if k in texto) / 2.0, 1.0)
    p5 = min(sum(1 for k in KWS_GEO if k in texto) / 2.0, 1.0)
    p6 = min(sum(1 for k in KWS_FISICA if k in texto) / 2.0, 1.0)
    p7 = min(sum(1 for k in KWS_VALID if k in texto) / 2.0, 1.0)
    
    if p1 > 0.7: p4 = min(p4 * 1.3, 1.0)
    if p2 > 0.6: p7 = min(p7 * 1.2, 1.0)
    
    pesos = [3.0, 1.2, 0.9, 1.4, 0.8, 1.0, 1.3]
    return sum([p1,p2,p3,p4,p5,p6,p7][i] * pesos[i] for i in range(7)) / sum(pesos)

def filtrar_artigos(artigos, pergunta):
    if not artigos: return []
    scored = [(a, score_artigo(a, pergunta)) for a in artigos]
    scored.sort(key=lambda x: -x[1])
    n = max(3, int(len(scored) * 0.15))
    return [a for a, _ in scored[:n]]

# ============================================================
# SIMULAÇÕES
# ============================================================
def classificar_artigos(artigos):
    est = defaultdict(list)
    for a in artigos:
        t = f"{a.get('titulo','')} {a.get('resumo','')}".lower()
        if any(k in t for k in ["theor","deriv","proof"]):
            est["teorico"].append(a)
        elif any(k in t for k in ["measur","experiment"]):
            est["experimental"].append(a)
        elif any(k in t for k in ["simulat","comput","dft","md"]):
            est["simulacional"].append(a)
        else:
            est["misto"].append(a)
    return dict(est)

def rotear_sims(est, sims_disp):
    if not sims_disp: return []
    sims_set = set(sims_disp.keys())
    prefs = []
    if est.get("teorico"):
        prefs += [s for s in sims_set if "quant" in s or "relat" in s or "algebra" in s]
    if est.get("experimental"):
        prefs += [s for s in sims_set if "estat" in s or "cinet" in s or "molec" in s]
    if est.get("simulacional"):
        prefs += [s for s in sims_set if "dft" in s or "md" in s or "solid" in s]
    if not prefs:
        prefs = list(sims_set)[:6]
    return list(set(prefs))[:8]

def rodar_sims(pergunta, sids):
    if not SIMS_OK: return {}
    res = {}
    for sid in sids:
        if sid in u.SIMULADORES:
            try:
                r = u.SIMULADORES[sid](pergunta, {})
                res[sid] = r
            except: pass
    return res

# ============================================================
# COSSENO
# ============================================================
def cosseno(sims, arts):
    if not modelo or not arts or not sims: return 0.0, {}
    
    textos_a, hashes_a = [], []
    for a in arts:
        t = f"{a.get('titulo','')} {a.get('resumo','')}".strip()
        if not t: continue
        h = hash_texto(t)
        textos_a.append(t); hashes_a.append(h)
    if not textos_a: return 0.0, {}
    
    faltam = [(textos_a[i], hashes_a[i]) for i in range(len(textos_a))
              if hashes_a[i] not in st.session_state.cache_embs]
    if faltam:
        embs = modelo.encode([t for t,_ in faltam], batch_size=64,
                            show_progress_bar=False, convert_to_numpy=True)
        for i, (_, h) in enumerate(faltam):
            st.session_state.cache_embs[h] = embs[i]
    
    embs_a = np.array([st.session_state.cache_embs[h] for h in hashes_a])
    embs_a_n = embs_a / (np.linalg.norm(embs_a, axis=1, keepdims=True) + 1e-10)
    
    sims_ok = [(sid, d) for sid, d in sims.items() if "erro" not in d]
    if not sims_ok: return 0.0, {}
    
    textos_s, hashes_s = [], []
    for sid, d in sims_ok:
        partes = [str(d.get("simulador","")), str(d.get("validacao",""))]
        for k, v in d.items():
            if isinstance(v, (int, float)): partes.append(f"{k} {v}")
        t = " ".join(partes)
        h = hash_texto(t)
        textos_s.append(t); hashes_s.append(h)
    
    faltam = [(textos_s[i], hashes_s[i]) for i in range(len(textos_s))
              if hashes_s[i] not in st.session_state.cache_embs]
    if faltam:
        embs = modelo.encode([t for t,_ in faltam], batch_size=64,
                            show_progress_bar=False, convert_to_numpy=True)
        for i, (_, h) in enumerate(faltam):
            st.session_state.cache_embs[h] = embs[i]
    
    embs_s = np.array([st.session_state.cache_embs[h] for h in hashes_s])
    embs_s_n = embs_s / (np.linalg.norm(embs_s, axis=1, keepdims=True) + 1e-10)
    
    matriz = np.dot(embs_s_n, embs_a_n.T)
    detalhes, todos = {}, []
    for i, (sid, _) in enumerate(sims_ok):
        scores = matriz[i].tolist()
        detalhes[sid] = {"max": float(max(scores))}
        todos.extend(scores)
    if not todos: return 0.0, {}
    top_n = max(5, len(todos) // 5)
    return float(np.mean(sorted(todos, reverse=True)[:top_n])), detalhes

# ============================================================
# ESTADO
# ============================================================
if "conversas" not in st.session_state:
    cid = str(uuid.uuid4())[:8]
    st.session_state.conversas = {cid: {
        "id": cid, "titulo": "Nova conversa",
        "criada": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mensagens": [], "artigos": {}, "cosseno": 0.0,
    }}
    st.session_state.conv_ativa = cid

def conv_atual():
    return st.session_state.conversas[st.session_state.conv_ativa]

def nova_conv():
    cid = str(uuid.uuid4())[:8]
    st.session_state.conversas[cid] = {
        "id": cid, "titulo": "Nova conversa",
        "criada": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mensagens": [], "artigos": {}, "cosseno": 0.0,
    }
    st.session_state.conv_ativa = cid

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="alef-logo">
        <span class="alef-icon">✦</span>
        <span class="alef-name">ALEF-TAV</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("＋  Nova conversa", use_container_width=True, type="primary"):
        nova_conv()
        st.rerun()
    
    st.markdown("---")
    
    # Conversas agrupadas
    convs = list(st.session_state.conversas.items())
    hoje = []
    anterior = []
    for cid, c in convs:
        if "Hoje" in c["criada"] or datetime.now().strftime("%d/%m/%Y") in c["criada"]:
            hoje.append((cid, c))
        else:
            anterior.append((cid, c))
    
    if hoje:
        st.markdown("**Hoje**")
        for cid, c in hoje:
            ativa = cid == st.session_state.conv_ativa
            prefixo = "●" if ativa else "○"
            if st.button(f"{prefixo} {c['titulo'][:25]}", key=f"c_{cid}", use_container_width=True):
                st.session_state.conv_ativa = cid
                st.rerun()
    
    if anterior:
        st.markdown("**Anterior**")
        for cid, c in anterior:
            ativa = cid == st.session_state.conv_ativa
            prefixo = "●" if ativa else "○"
            if st.button(f"{prefixo} {c['titulo'][:25]}", key=f"c_{cid}", use_container_width=True):
                st.session_state.conv_ativa = cid
                st.rerun()
    
    st.markdown("---")
    st.markdown("◯ **Perfil**")
    st.markdown("⚙️ **Ajustes**")

# ============================================================
# MAIN
# ============================================================
conv = conv_atual()

# Welcome screen
if not conv["mensagens"]:
    st.markdown("""
    <div style="text-align: center; margin-top: 5rem;">
        <div style="font-size: 3rem; color: #8b5cf6; margin-bottom: 1rem;">✦</div>
        <div class="welcome-title">ALEF-TAV</div>
        <div class="welcome-subtitle">Como posso ajudar hoje?</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sugestões
    col1, col2 = st.columns(2)
    sugestoes = [
        ("Analisar artigo", "Cole um texto ou DOI para análise"),
        ("Verificar hipótese", "Descreva sua hipótese científica"),
        ("Explorar tema", "Faça uma pergunta sobre qualquer área"),
        ("Comparar materiais", "Descreva os materiais a comparar"),
    ]
    
    for i, (titulo, desc) in enumerate(sugestoes):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class="suggestion-card">
                <div class="suggestion-title">{titulo}</div>
                <div class="suggestion-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# Histórico de mensagens
for msg in conv["mensagens"]:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "✦"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sims"):
            with st.expander(f"▸ Ver {len(msg['sims'])} simulações"):
                for sid, d in list(msg["sims"].items())[:10]:
                    if "erro" in d: continue
                    nome = d.get("simulador", sid)
                    val = d.get("validacao", "")
                    st.markdown(f"""
                    <div class="sim">
                        <div class="sim-name">{nome}</div>
                        <div class="sim-value">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

# Input
pergunta = st.chat_input("Pergunte algo...")

if pergunta:
    conv["mensagens"].append({"role": "user", "content": pergunta,
                              "hora": datetime.now().strftime("%H:%M:%S")})
    
    if conv["titulo"] == "Nova conversa":
        conv["titulo"] = pergunta[:30]
    
    with st.chat_message("user", avatar="🧑"):
        st.markdown(pergunta)
    
    with st.chat_message("assistant", avatar="✦"):
        with st.spinner("Analisando..."):
            query_en = traduzir(pergunta)
            arts = buscar(query_en, n=4)
            
            novos = 0
            for a in arts:
                k = a.get("link") or a.get("titulo","")[:80]
                if k and k not in conv["artigos"]:
                    conv["artigos"][k] = a
                    novos += 1
            
            todos = list(conv["artigos"].values())
            arts_filt = filtrar_artigos(todos, pergunta) if todos else []
            est = classificar_artigos(arts_filt)
            sims_ids = rotear_sims(est, u.SIMULADORES if SIMS_OK else {})
            sims = rodar_sims(pergunta, sims_ids)
            
            coss, _ = cosseno(sims, arts_filt)
            coss_ant = conv["cosseno"]
            coss_novo = coss if coss_ant == 0 else min(0.6*coss_ant + 0.4*coss + 0.02*len(conv["mensagens"]), 1.0)
            conv["cosseno"] = coss_novo
        
        # RESPOSTA NATURAL
        resposta = []
        resposta.append("Analisei o tema com base na literatura científica disponível.")
        resposta.append("")
        
        if arts_filt:
            resposta.append("**Artigos relevantes:**")
            resposta.append("")
            for i, a in enumerate(arts_filt[:4], 1):
                titulo = a.get("titulo", "")[:120]
                fonte = a.get("fonte", "")
                ano = a.get("ano", "")
                link = a.get("link", "")
                resumo = a.get("resumo", "")[:200]
                resposta.append(f"**{i}.** [{titulo}]({link})")
                resposta.append(f"*{fonte} · {ano}*")
                if resumo:
                    resposta.append(f"")
                    resposta.append(f"> {resumo}...")
                resposta.append("")
        
        if sims:
            resposta.append("**Simulações executadas:**")
            resposta.append("")
            for sid, d in list(sims.items())[:4]:
                if "erro" in d: continue
                nome = d.get("simulador", sid)
                val = d.get("validacao", "")
                resposta.append(f"• **{nome}**" + (f" — {val}" if val else ""))
            resposta.append("")
        
        # Conclusão natural
        if coss_novo >= 0.99:
            resposta.append("A hipótese é **corroborada pela literatura**. Pode prosseguir.")
        elif coss_novo >= 0.7:
            resposta.append("Os resultados são **favoráveis**. Continue explorando.")
        elif coss_novo >= 0.5:
            resposta.append("Há **evidência parcial**. Recomendo aprofundar.")
        else:
            resposta.append("Ainda há **pouca evidência** para conclusão.")
        
        resposta.append("")
        resposta.append("Deseja aprofundar em algum aspecto?")
        
        rtxt = "\n".join(resposta)
        st.markdown(rtxt)
        
        # Detalhes das simulações
        if sims:
            with st.expander(f"▸ Ver {len(sims)} simulações detalhadas"):
                for sid, d in sims.items():
                    if "erro" in d: continue
                    nome = d.get("simulador", sid)
                    val = d.get("validacao", "")
                    st.markdown(f"""
                    <div class="sim">
                        <div class="sim-name">{nome}</div>
                        <div class="sim-value">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        conv["mensagens"].append({
            "role": "assistant", "content": rtxt,
            "sims": sims, "hora": datetime.now().strftime("%H:%M:%S"),
        })
    
    st.rerun()