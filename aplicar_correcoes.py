# aplicar_correcoes.py - Aplica as 4 correcoes automaticamente
import re
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
REL = BASE / "relatorios_v5.py"
SCOPUS = BASE / "modulo_scopus.py"

print("=" * 60)
print("  ALEF-TAV - Aplicando correcoes")
print("=" * 60)
print()

# ============================================================
# CORRECAO 1 + 2 + 4 - relatorios_v5.py
# ============================================================
if not REL.exists():
    print(f"❌ {REL} nao encontrado")
    exit(1)

conteudo = REL.read_text(encoding="utf-8")
original = conteudo

# ------------------------------------------------------------
# CORRECAO 1: _refs_para com threshold adaptativo
# ------------------------------------------------------------
padrao_refs = re.compile(
    r"def _refs_para\(c, tipo\):.*?return \[a for _, a in scored\[:perfil\[\"refs\"\]\]\]",
    re.DOTALL
)

nova_refs = '''def _refs_para(c, tipo):
    """Filtra refs por relevancia ADAPTATIVA ao tema."""
    perfil = PERFIL_DOC[tipo]
    if perfil["refs"] == 0: return []

    # Coleta das bases do perfil
    arts = []
    for base in perfil["bases"]:
        arts.extend(_coletar_base(c, base))

    # FALLBACK 1: se vazio, tenta TODAS as bases
    if not arts:
        for base, lista in c.get("dados_bases", {}).items():
            if isinstance(lista, list):
                arts.extend(lista)

    # FALLBACK 2: se ainda vazio, usa artigos legados
    if not arts:
        arts = list(c.get("artigos", {}).values())
    if not arts:
        return []

    # Palavras do tema
    palavras = _palavras_tema(_tema(c))
    if not palavras:
        return arts[:perfil["refs"]]

    # THRESHOLD ADAPTATIVO: 1 para tema curto, 2 para tema longo
    threshold = 1 if len(palavras) <= 2 else 2

    scored = []
    for a in arts:
        txt = (a.get("titulo","") + " " + a.get("resumo","")).lower()
        hits = sum(1 for p in palavras if p in txt)
        if hits >= threshold:
            scored.append((hits, a))
    scored.sort(key=lambda x: -x[0])

    # FALLBACK FINAL: se nada passou, relaxa para 1 hit
    if not scored:
        for a in arts:
            txt = (a.get("titulo","") + " " + a.get("resumo","")).lower()
            hits = sum(1 for p in palavras if p in txt)
            if hits >= 1:
                scored.append((hits, a))
        scored.sort(key=lambda x: -x[0])

    return [a for _, a in scored[:perfil["refs"]]]'''

if padrao_refs.search(conteudo):
    conteudo = padrao_refs.sub(nova_refs, conteudo)
    print("✅ Correcao 1: _refs_para() com threshold adaptativo")
else:
    print("⚠️ Correcao 1: _refs_para() nao encontrado - pulando")

# ------------------------------------------------------------
# CORRECAO 2: _autor com multi-formato
# ------------------------------------------------------------
padrao_autor = re.compile(
    r"def _autor\(a\):.*?return a\.get\(\"fonte\", \"Autor\"\)",
    re.DOTALL
)

novo_autor = '''def _autor(a):
    """Extrai autor de multiplos formatos."""
    # 1. Campo autores (lista de strings ou dicts)
    autores = a.get("autores") or a.get("authors") or []
    if autores:
        if isinstance(autores, str):
            return autores.split(",")[0].strip()[:25]
        if isinstance(autores, list) and autores:
            first = autores[0]
            if isinstance(first, str):
                return first[:25]
            if isinstance(first, dict):
                nome = (first.get("name") or first.get("family") or
                        first.get("full_name") or first.get("display_name",""))
                if nome:
                    return str(nome)[:25]
    # 2. Campo creator (Crossref)
    creator = a.get("creator")
    if creator and isinstance(creator, str):
        return creator.split(",")[0].strip()[:25]
    # 3. EuropePMC (authorString)
    aut_str = a.get("authorString")
    if aut_str:
        return aut_str.split(",")[0].strip()[:25]
    # 4. Fallback: fonte
    return a.get("fonte", "Autor")'''

if padrao_autor.search(conteudo):
    conteudo = padrao_autor.sub(novo_autor, conteudo)
    print("✅ Correcao 2: _autor() com multi-formato")
else:
    print("⚠️ Correcao 2: _autor() nao encontrado - pulando")

# ------------------------------------------------------------
# CORRECAO 4: PERFIL_DOC com todas as bases
# ------------------------------------------------------------
padrao_perfil = re.compile(
    r"PERFIL_DOC = \{.*?\n\}",
    re.DOTALL
)

novo_perfil = '''PERFIL_DOC = {
    "tcc": {
        "refs": 20, "nivel": "basico",
        "bases": ["cientifica", "literatura", "materiais", "quimica"],
    },
    "mestrado": {
        "refs": 50, "nivel": "intermediario",
        "bases": ["cientifica", "literatura", "materiais", "quimica",
                  "genomica", "dados", "colaboracao"],
    },
    "doutorado": {
        "refs": 150, "nivel": "avancado",
        "bases": ["cientifica", "literatura", "materiais", "quimica",
                  "genomica", "dados", "patentes", "clinicos",
                  "colaboracao", "referencia"],
    },
    "artigo": {
        "refs": 30, "nivel": "avancado",
        "bases": ["cientifica", "literatura"],
    },
    "tecnico": {
        "refs": 40, "nivel": "intermediario",
        "bases": ["cientifica", "literatura", "patentes", "materiais",
                  "quimica", "genomica", "clinicos", "dados",
                  "gov_br", "gov_intl", "financiamento"],
    },
    "poc": {
        "refs": 25, "nivel": "intermediario",
        "bases": ["cientifica", "literatura", "materiais", "patentes",
                  "quimica", "financiamento"],
    },
    "financeiro": {
        "refs": 0, "nivel": "basico",
        "bases": ["financiamento"],
    },
    "captacao": {
        "refs": 0, "nivel": "basico",
        "bases": ["financiamento"],
    },
}'''

if padrao_perfil.search(conteudo):
    conteudo = padrao_perfil.sub(novo_perfil, conteudo)
    print("✅ Correcao 4: PERFIL_DOC com todas as bases")
else:
    print("⚠️ Correcao 4: PERFIL_DOC nao encontrado - pulando")

# Salva o arquivo corrigido
if conteudo != original:
    REL.write_text(conteudo, encoding="utf-8")
    print()
    print(f"✅ relatorios_v5.py atualizado")
else:
    print(f"⚠️ relatorios_v5.py nao mudou")

# ============================================================
# CORRECAO 3 - modulo_scopus.py (substituir inteiro)
# ============================================================
novo_scopus = '''# modulo_scopus.py - CORRIGIDO com TITLE-ABS-KEY
try:
    import config_api
except:
    config_api = None

def buscar_scopus(q, n=4, debug=False):
    """Busca na Scopus via API institucional."""
    if not config_api or not config_api.tem("SCOPUS"):
        if debug: print("[SCOPUS] Chave nao configurada")
        return []
    try:
        import requests
    except:
        return []

    # CORRECAO: query Scopus precisa de TITLE-ABS-KEY
    query = 'TITLE-ABS-KEY("' + q + '")'

    try:
        r = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            params={
                "query": query,
                "count": n,
                "httpAccept": "application/json",
            },
            headers=config_api.headers("SCOPUS"),
            timeout=15,
        )
        if debug:
            print(f"[SCOPUS] Status: {r.status_code}")
            print(f"[SCOPUS] Query: {query}")
        if r.status_code != 200:
            if debug: print(f"[SCOPUS] Erro: {r.text[:300]}")
            return []

        dados = r.json()
        entradas = dados.get("search-results", {}).get("entry", [])
        if debug: print(f"[SCOPUS] Retornou {len(entradas)} resultados")

        out = []
        for e in entradas:
            titulo = e.get("dc:title", "")
            doi = e.get("prism:doi", "")
            link = "https://doi.org/" + doi if doi else e.get("prism:url", "")
            ano = 2024
            try:
                ano = int(e.get("prism:coverDate", "2024")[:4])
            except:
                pass
            autor = e.get("dc:creator", "")
            autores = [{"name": autor}] if autor else []
            out.append({
                "titulo": titulo,
                "resumo": "",
                "link": link,
                "ano": ano,
                "fonte": "Scopus",
                "tipo": "artigo",
                "autores": autores,
            })
        return out
    except Exception as e:
        if debug: print(f"[SCOPUS] Exception: {e}")
        return []

def testar():
    r = buscar_scopus("diamond", 3, debug=True)
    if r:
        return f"OK - {len(r)} resultados"
    return "Sem resultados"

if __name__ == "__main__":
    print(testar())
'''

SCOPUS.write_text(novo_scopus, encoding="utf-8")
print("✅ Correcao 3: modulo_scopus.py com TITLE-ABS-KEY")

# ============================================================
# RESUMO
# ============================================================
print()
print("=" * 60)
print("  CORRECOES APLICADAS")
print("=" * 60)
print()
print("1. _refs_para()      -> threshold adaptativo")
print("2. _autor()          -> multi-formato")
print("3. modulo_scopus.py  -> TITLE-ABS-KEY")
print("4. PERFIL_DOC        -> todas as bases")
print()
print("Backups em: backup_correcoes/")
print()