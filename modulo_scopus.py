# modulo_scopus.py - CORRIGIDO com TITLE-ABS-KEY
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
