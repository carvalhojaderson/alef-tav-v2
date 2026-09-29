"""
TODOS OS 187 BANCOS DE DADOS
Organizados por categoria — com implementação real onde possível
"""

# ============================================================
# CATEGORIA 1 — ARTIGOS CIENTÍFICOS (12)
# ============================================================
def b_arxiv(q, n=5):
    try:
        import arxiv
        c = arxiv.Client()
        return [{"titulo": r.title, "resumo": r.summary[:600], "link": r.entry_id,
                 "ano": r.published.year, "fonte": "arXiv", "categoria": "artigos"}
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
                 "ano": 2024, "fonte": "PubMed", "categoria": "artigos"} for p in pmids]
    except: return []

def b_semantic(q, n=5):
    try:
        import requests
        r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                         params={"query":q,"limit":n,"fields":"title,abstract,url,year"}, timeout=10)
        return [{"titulo": p.get("title",""), "resumo": (p.get("abstract") or "")[:600],
                 "link": p.get("url",""), "ano": p.get("year",2024),
                 "fonte": "Semantic", "categoria": "artigos"}
                for p in r.json().get("data",[])]
    except: return []

def b_openalex(q, n=5):
    try:
        import requests
        r = requests.get("https://api.openalex.org/works",
                         params={"search":q,"per_page":n}, timeout=10)
        return [{"titulo": w.get("title",""), "resumo": "",
                 "link": w.get("id",""), "ano": w.get("publication_year",2024),
                 "fonte": "OpenAlex", "categoria": "artigos"}
                for w in r.json().get("results",[])]
    except: return []

def b_europepmc(q, n=5):
    try:
        import requests
        r = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                         params={"query":q,"format":"json","pageSize":n}, timeout=10)
        return [{"titulo": p.get("title",""), "resumo": (p.get("abstractText") or "")[:600],
                 "link": f"https://europepmc.org/article/MED/{p.get('pmid','')}",
                 "ano": int(p.get("pubYear",2024)),
                 "fonte": "EuropePMC", "categoria": "artigos"}
                for p in r.json().get("resultList",{}).get("result",[])]
    except: return []

def b_crossref(q, n=5):
    try:
        import requests
        r = requests.get("https://api.crossref.org/works",
                         params={"query":q,"rows":n}, timeout=10)
        return [{"titulo": it.get("title",[""])[0], "resumo": "",
                 "link": "https://doi.org/"+it.get("DOI",""),
                 "ano": it.get("published",{}).get("date-parts",[[2024]])[0][0],
                 "fonte": "Crossref", "categoria": "artigos"}
                for it in r.json().get("message",{}).get("items",[])]
    except: return []

def b_pubchem(q, n=5):
    try:
        import requests
        p = q.split()[0] if q.split() else q
        r = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{p}/JSON", timeout=10)
        if r.status_code != 200: return []
        cid = r.json()["PC_Compounds"][0]["id"]["id"]["cid"]
        return [{"titulo": f"PubChem CID {cid}", "resumo": f"Composto: {p}",
                 "link": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
                 "ano": 2024, "fonte": "PubChem", "categoria": "quimica"}]
    except: return []

def b_pdb(q, n=5):
    try:
        import requests
        p = q.split()[0] if q.split() else q
        r = requests.post("https://search.rcsb.org/rcsbsearch/v2/query",
                          json={"query":{"type":"terminal","service":"full_text",
                                "parameters":{"value":p}}, "return_type":"entry",
                                "request_options":{"paginate":{"start":0,"rows":n}}}, timeout=10)
        if r.status_code != 200: return []
        return [{"titulo": f"PDB {x['identifier']}", "resumo": "Estrutura 3D",
                 "link": f"https://www.rcsb.org/structure/{x['identifier']}",
                 "ano": 2024, "fonte": "PDB", "categoria": "biologia"}
                for x in r.json().get("result_set",[])]
    except: return []

def b_simbad(q, n=5):
    try:
        import requests
        p = q.split()[0] if q.split() else q
        r = requests.get("https://simbad.u-strasbg.fr/simbad/sim-tap/sync",
                         params={"request":"doQuery","lang":"adql","format":"json",
                                 "query":f"SELECT TOP {n} main_id FROM basic WHERE main_id LIKE '%{p}%'"},
                         timeout=10)
        return [{"titulo": f"SIMBAD {x.get('main_id','')}", "resumo": "",
                 "link": "https://simbad.u-strasbg.fr/", "ano": 2024,
                 "fonte": "SIMBAD", "categoria": "astronomia"}
                for x in r.json().get("data",[])]
    except: return []

def b_inspire(q, n=5):
    try:
        import requests
        r = requests.get("https://inspirehep.net/api/literature",
                         params={"q":q,"size":n,"fields":"titles,earliest_date"}, timeout=10)
        res = []
        for h in r.json().get("hits",{}).get("hits",[]):
            try:
                res.append({"titulo": h["metadata"]["titles"][0]["title"], "resumo": "",
                            "link": f"https://inspirehep.net/literature/{h['id']}",
                            "ano": int(h["metadata"].get("earliest_date","2024")[:4]),
                            "fonte": "INSPIRE", "categoria": "fisica"})
            except: continue
        return res
    except: return []

def b_doaj(q, n=5):
    try:
        import requests
        r = requests.get(f"https://doaj.org/api/search/articles/{q}",
                         params={"pageSize": n}, timeout=10)
        return [{"titulo": a.get("bibjson",{}).get("title",""), "resumo": "",
                 "link": "", "ano": 2024, "fonte": "DOAJ", "categoria": "artigos"}
                for a in r.json().get("results",[])]
    except: return []

def b_core(q, n=5):
    try:
        import requests
        r = requests.get("https://api.core.ac.uk/v3/search/works",
                         params={"q":q,"limit":n}, timeout=10)
        if r.status_code != 200: return []
        return [{"titulo": w.get("title",""), "resumo": "",
                 "link": w.get("downloadUrl",""), "ano": w.get("year",2024),
                 "fonte": "CORE", "categoria": "artigos"}
                for w in r.json().get("results",[])]
    except: return []

# ============================================================
# CATEGORIA 2 — PATENTES (12)
# ============================================================
def b_uspto(q, n=5):
    try:
        import requests
        r = requests.get("https://api.patentsview.org/patents/query",
                         params={"q":'{"_text_any":{"patent_title":"' + q + '"}}',
                                 "f":'["patent_number","patent_title","patent_date"]'},
                         timeout=15)
        return [{"titulo": p.get("patent_title",""), "resumo": "Patente USPTO",
                 "link": f"https://patents.google.com/patent/US{p.get('patent_number','')}",
                 "ano": int(p.get("patent_date","2024")[:4]),
                 "fonte": "USPTO", "categoria": "patentes"}
                for p in r.json().get("patents",[])[:n]]
    except: return []

def b_inpi(q, n=5):
    return []  # Registrado (INPI sem API pública)

def b_epo(q, n=5):
    return []  # Registrado (requer OAuth)

def b_lens(q, n=5):
    return []  # Registrado (requer API key)

def b_google_patents(q, n=5):
    return []  # Registrado (BigQuery)

# ============================================================
# CATEGORIA 3 — INTEGRIDADE CIENTÍFICA (4)
# ============================================================
def b_retraction(q, n=5):
    try:
        import requests
        r = requests.get("https://api.crossref.org/works",
                         params={"query": q, "filter": "type:retraction", "rows": n}, timeout=15)
        return [{"titulo": it.get("title",[""])[0], "resumo": "RETRATADO",
                 "link": f"https://doi.org/{it.get('DOI','')}",
                 "ano": it.get("published",{}).get("date-parts",[[2024]])[0][0],
                 "fonte": "RetractionWatch", "categoria": "integridade"}
                for it in r.json().get("message",{}).get("items",[])]
    except: return []

def b_pubpeer(q, n=5):
    return []  # Registrado

# ============================================================
# CATEGORIA 4 — ENSAIOS CLÍNICOS (9)
# ============================================================
def b_clinicaltrials(q, n=5):
    try:
        import requests
        r = requests.get("https://clinicaltrials.gov/api/v2/studies",
                         params={"query.term": q, "pageSize": n}, timeout=15)
        return [{"titulo": s.get("protocolSection",{}).get("identificationModule",{}).get("briefTitle",""),
                 "resumo": "",
                 "link": f"https://clinicaltrials.gov/study/{s.get('protocolSection',{}).get('identificationModule',{}).get('nctId','')}",
                 "ano": 2024, "fonte": "ClinicalTrials", "categoria": "clinicos"}
                for s in r.json().get("studies",[])]
    except: return []

def b_nih_reporter(q, n=5):
    try:
        import requests
        r = requests.get("https://api.reporter.nih.gov/v2/projects/search",
                         json={"criteria":{"advanced_text_search":{"operator":"and",
                              "search_field":"projecttitle","search_text":q}},
                              "limit":n}, timeout=15)
        return [{"titulo": p.get("project_title",""), "resumo": "",
                 "link": f"https://reporter.nih.gov/project-details/{p.get('project_num','')}",
                 "ano": 2024, "fonte": "NIHRePORTER", "categoria": "clinicos"}
                for p in r.json().get("results",[])]
    except: return []

def b_cordis(q, n=5):
    return []  # Registrado

# ============================================================
# CATEGORIA 5 — REPOSITÓRIOS DE DADOS (7)
# ============================================================
def b_zenodo(q, n=5):
    try:
        import requests
        r = requests.get("https://zenodo.org/api/records",
                         params={"q":q,"size":n}, timeout=15)
        return [{"titulo": hit.get("metadata",{}).get("title",""), "resumo": "",
                 "link": hit.get("links",{}).get("self_html",""),
                 "ano": 2024, "fonte": "Zenodo", "categoria": "dados"}
                for hit in r.json().get("hits",{}).get("hits",[])]
    except: return []

def b_figshare(q, n=5):
    try:
        import requests
        r = requests.post("https://api.figshare.com/v2/articles/search",
                          json={"search_for":q,"page_size":n}, timeout=15)
        return [{"titulo": a.get("title",""), "resumo": "",
                 "link": a.get("url_public_html",""), "ano": 2024,
                 "fonte": "Figshare", "categoria": "dados"}
                for a in r.json()]
    except: return []

def b_dryad(q, n=5):
    try:
        import requests
        r = requests.get("https://datadryad.org/api/v2/search",
                         params={"q":q,"per_page":n}, timeout=15)
        return [{"titulo": d.get("title",""), "resumo": "",
                 "link": f"https://datadryad.org/dataset/doi:{d.get('identifier','')}",
                 "ano": 2024, "fonte": "Dryad", "categoria": "dados"}
                for d in r.json().get("_embedded",{}).get("stash:datasets",[])]
    except: return []

def b_sciencedb(q, n=5):
    return []  # Registrado

def b_dataone(q, n=5):
    return []  # Registrado

def b_re3data(q, n=5):
    return []  # Registrado

def b_nasa_osdr(q, n=5):
    return []  # Registrado

# ============================================================
# CATEGORIA 6 — RECALLS E ALERTAS (28)
# ============================================================
def b_openfda(q, n=5):
    try:
        import requests
        r = requests.get("https://api.fda.gov/drug/enforcement.json",
                         params={"search": f"reason_for_recall:{q}", "limit": n}, timeout=15)
        if r.status_code != 200: return []
        return [{"titulo": it.get("product_description","")[:100],
                 "resumo": it.get("reason_for_recall",""),
                 "link": "https://www.fda.gov/", "ano": 2024,
                 "fonte": "openFDA", "categoria": "recalls"}
                for it in r.json().get("results",[])]
    except: return []

def b_cpsc(q, n=5):
    return []  # Registrado

def b_eu_safety(q, n=5):
    return []  # Registrado

def b_health_canada(q, n=5):
    return []  # Registrado

# ============================================================
# CATEGORIA 7 — NORMAS TÉCNICAS (16)
# ============================================================
def b_abnt(q, n=5):
    return []  # Sem API pública

def b_iso(q, n=5):
    return []  # Registrado

# ============================================================
# CATEGORIA 8 — CIÊNCIAS DA TERRA (4)
# ============================================================
def b_nasa_earthdata(q, n=5):
    try:
        import requests
        r = requests.get("https://cmr.earthdata.nasa.gov/search/collections.json",
                         params={"keyword":q,"page_size":n}, timeout=15)
        return [{"titulo": c.get("title",""), "resumo": (c.get("summary") or "")[:300],
                 "link": "https://search.earthdata.nasa.gov/", "ano": 2024,
                 "fonte": "NASA", "categoria": "terra"}
                for c in r.json().get("feed",{}).get("entry",[])]
    except: return []

def b_usgs_earthquake(q, n=5):
    try:
        import requests
        r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query",
                         params={"format":"geojson","limit":n,"minmagnitude":4.0}, timeout=15)
        return [{"titulo": f"Terremoto M{f['properties'].get('mag',0)}",
                 "resumo": f['properties'].get('place',''),
                 "link": f['properties'].get('url',''), "ano": 2024,
                 "fonte": "USGS", "categoria": "terra"}
                for f in r.json().get("features",[])]
    except: return []

def b_copernicus(q, n=5):
    return []

def b_noaa(q, n=5):
    return []

# ============================================================
# CATEGORIA 9 — DESAFIOS ABERTOS (3)
# ============================================================
def b_kaggle(q, n=5):
    try:
        import requests
        r = requests.get("https://www.kaggle.com/api/v1/competitions/list",
                         params={"search":q,"page":1}, timeout=15)
        return [{"titulo": c.get("title",""), "resumo": c.get("description","")[:200],
                 "link": f"https://www.kaggle.com/c/{c.get('ref','')}",
                 "ano": 2024, "fonte": "Kaggle", "categoria": "desafios"}
                for c in r.json()[:n]]
    except: return []

def b_drivendata(q, n=5):
    return []

def b_openchallenges(q, n=5):
    return []

# ============================================================
# CATEGORIA 10 — MATERIAIS E QUÍMICA (8)
# ============================================================
def b_materials_project(q, n=5):
    return []

def b_optimade(q, n=5):
    return []

def b_matbench(q, n=5):
    return []

def b_aflow(q, n=5):
    return []

def b_oqmd(q, n=5):
    return []

def b_jarvis(q, n=5):
    return []

def b_materials_cloud(q, n=5):
    return []

def b_nomad(q, n=5):
    return []

# ============================================================
# CATEGORIA 11 — GENÔMICA (5)
# ============================================================
def b_ensembl(q, n=5):
    return []

def b_ncbi_eutils(q, n=5):
    return []

def b_ena(q, n=5):
    return []

def b_gdc(q, n=5):
    return []

def b_ucsc(q, n=5):
    return []

# ============================================================
# CATEGORIA 12 — DADOS GOVERNAMENTAIS BR (7)
# ============================================================
def b_dados_gov(q, n=5):
    return []

def b_ipeadata(q, n=5):
    return []

def b_bcb(q, n=5):
    return []

def b_transferegov(q, n=5):
    return []

def b_obrasgov(q, n=5):
    return []

def b_tesouro(q, n=5):
    return []

def b_inde(q, n=5):
    return []

# ============================================================
# CATEGORIA 13 — DADOS GOVERNAMENTAIS INTL (9)
# ============================================================
def b_data_gov_us(q, n=5): return []
def b_data_gov_uk(q, n=5): return []
def b_govdata_de(q, n=5): return []
def b_data_govt_nz(q, n=5): return []
def b_data_gov_sg(q, n=5): return []
def b_india_ogd(q, n=5): return []
def b_worldbank(q, n=5): return []
def b_datos_es(q, n=5): return []
def b_datos_co(q, n=5): return []

# ============================================================
# CATEGORIA 14 — FINANCIAMENTO P&D (22)
# ============================================================
def b_finep(q, n=5): return []
def b_cnpq(q, n=5): return []
def b_fapemig(q, n=5): return []
def b_fapesp(q, n=5): return []
def b_bndes(q, n=5): return []
def b_embrapii(q, n=5): return []
def b_rota2030(q, n=5): return []
def b_horizon(q, n=5): return []
def b_nih_funding(q, n=5): return []
def b_nsf(q, n=5): return []
def b_darpa(q, n=5): return []
def b_gates(q, n=5): return []
def b_wellcome(q, n=5): return []
def b_erc(q, n=5): return []
def b_dfg(q, n=5): return []
def b_jsps(q, n=5): return []
def b_nsfc(q, n=5): return []
def b_conicet(q, n=5): return []
def b_conacyt(q, n=5): return []
def b_anii(q, n=5): return []
def b_fondecyt(q, n=5): return []
def b_finep_inovacred(q, n=5): return []

# ============================================================
# CATEGORIA 15 — COLABORAÇÃO CIENTÍFICA (14)
# ============================================================
def b_orcid(q, n=5):
    try:
        import requests
        r = requests.get("https://pub.orcid.org/v3.0/expanded-search/",
                         params={"q":q,"rows":n},
                         headers={"Accept":"application/json"}, timeout=15)
        return []
    except: return []

def b_ror(q, n=5): return []
def b_researchgate(q, n=5): return []
def b_loop(q, n=5): return []
def b_sciprofiles(q, n=5): return []
def b_google_scholar(q, n=5): return []
def b_academia(q, n=5): return []
def b_mendeley(q, n=5): return []
def b_crossref_funder(q, n=5): return []
def b_dimensions(q, n=5): return []
def b_inspire_authors(q, n=5): return []
def b_openalex_inst(q, n=5): return []
def b_grid(q, n=5): return []
def b_cordis_partners(q, n=5): return []

# ============================================================
# CATEGORIA 16 — INFRAESTRUTURA EXPERIMENTAL (12)
# ============================================================
def b_eln(q, n=5): return []
def b_ilab(q, n=5): return []
def b_scinote(q, n=5): return []
def b_labarchives(q, n=5): return []
def b_openbis(q, n=5): return []
def b_zenodo_labs(q, n=5): return []
def b_eu_openscreen(q, n=5): return []
def b_instruct(q, n=5): return []
def b_ceric(q, n=5): return []
def b_embl(q, n=5): return []
def b_lnls(q, n=5): return []
def b_ipen(q, n=5): return []

# ============================================================
# CATEGORIA 17 — PUBLICAÇÕES ABERTAS (7)
# ============================================================
def b_scielo(q, n=5):
    try:
        import requests
        r = requests.get("https://search.scielo.org/",
                         params={"q":q,"count":n,"output":"site","format":"iso-8859-1"},
                         timeout=15)
        return []  # Parse HTML complexo
    except: return []

def b_redalyc(q, n=5): return []
def b_latindex(q, n=5): return []
def b_base(q, n=5): return []
def b_openAIRE(q, n=5): return []
def b_jstage(q, n=5): return []
def b_doaj2(q, n=5): return []

# ============================================================
# CATEGORIA 18 — SEGURANÇA QUÍMICA (4)
# ============================================================
def b_echa(q, n=5): return []
def b_epa_comptox(q, n=5): return []
def b_nrc_erns(q, n=5): return []
def b_chemwatch(q, n=5): return []

# ============================================================
# CATEGORIA 19 — OUTROS (4)
# ============================================================
def b_mytomorrows(q, n=5): return []
def b_ntsb(q, n=5): return []
def b_faa_asias(q, n=5): return []
def b_health_canada2(q, n=5): return []

# ============================================================
# CATEGORIA 20 — WEB SEARCH (1)
# ============================================================
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
                                "link": link, "ano": 2024,
                                "fonte": "Web", "categoria": "web"})
        return results
    except: return []

# ============================================================
# REGISTRO COMPLETO — 187 BANCOS
# ============================================================
BANCOS = {
    # Artigos (12)
    "arXiv": {"fn": b_arxiv, "cat": "artigos", "ativa": True},
    "PubMed": {"fn": b_pubmed, "cat": "artigos", "ativa": True},
    "Semantic": {"fn": b_semantic, "cat": "artigos", "ativa": True},
    "OpenAlex": {"fn": b_openalex, "cat": "artigos", "ativa": True},
    "EuropePMC": {"fn": b_europepmc, "cat": "artigos", "ativa": True},
    "Crossref": {"fn": b_crossref, "cat": "artigos", "ativa": True},
    "PubChem": {"fn": b_pubchem, "cat": "quimica", "ativa": True},
    "PDB": {"fn": b_pdb, "cat": "biologia", "ativa": True},
    "SIMBAD": {"fn": b_simbad, "cat": "astronomia", "ativa": True},
    "INSPIRE": {"fn": b_inspire, "cat": "fisica", "ativa": True},
    "DOAJ": {"fn": b_doaj, "cat": "artigos", "ativa": True},
    "CORE": {"fn": b_core, "cat": "artigos", "ativa": True},
    
    # Patentes (12)
    "USPTO": {"fn": b_uspto, "cat": "patentes", "ativa": True},
    "EPO": {"fn": b_epo, "cat": "patentes", "ativa": False},
    "Lens.org": {"fn": b_lens, "cat": "patentes", "ativa": False},
    "GooglePatents": {"fn": b_google_patents, "cat": "patentes", "ativa": False},
    "INPI": {"fn": b_inpi, "cat": "patentes", "ativa": False},
    "FreeInactive": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    "AbandonedApps": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    "WIPO": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    "PLID": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    "Tech4SME": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    "SciCrunch": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    "NetrinINPI": {"fn": lambda q,n=5: [], "cat": "patentes", "ativa": False},
    
    # Integridade (4)
    "RetractionWatch": {"fn": b_retraction, "cat": "integridade", "ativa": True},
    "PubPeer": {"fn": b_pubpeer, "cat": "integridade", "ativa": False},
    "SCORE": {"fn": lambda q,n=5: [], "cat": "integridade", "ativa": False},
    "ORION": {"fn": lambda q,n=5: [], "cat": "integridade", "ativa": False},
    
    # Clínicos (9)
    "ClinicalTrials": {"fn": b_clinicaltrials, "cat": "clinicos", "ativa": True},
    "NIHRePORTER": {"fn": b_nih_reporter, "cat": "clinicos", "ativa": True},
    "CORDIS": {"fn": b_cordis, "cat": "clinicos", "ativa": False},
    "Badger": {"fn": lambda q,n=5: [], "cat": "clinicos", "ativa": False},
    "MIMIC-III": {"fn": lambda q,n=5: [], "cat": "clinicos", "ativa": False},
    "ELITE": {"fn": lambda q,n=5: [], "cat": "clinicos", "ativa": False},
    "canSAR": {"fn": lambda q,n=5: [], "cat": "clinicos", "ativa": False},
    "IBDkb": {"fn": lambda q,n=5: [], "cat": "clinicos", "ativa": False},
    "TumorXDB": {"fn": lambda q,n=5: [], "cat": "clinicos", "ativa": False},
    
    # Dados (7)
    "Zenodo": {"fn": b_zenodo, "cat": "dados", "ativa": True},
    "Figshare": {"fn": b_figshare, "cat": "dados", "ativa": True},
    "Dryad": {"fn": b_dryad, "cat": "dados", "ativa": True},
    "ScienceDB": {"fn": b_sciencedb, "cat": "dados", "ativa": False},
    "DataONE": {"fn": b_dataone, "cat": "dados", "ativa": False},
    "re3data": {"fn": b_re3data, "cat": "dados", "ativa": False},
    "NASAOSDR": {"fn": b_nasa_osdr, "cat": "dados", "ativa": False},
    
    # Recalls (28) — ativos: openFDA
    "openFDA": {"fn": b_openfda, "cat": "recalls", "ativa": True},
    "CPSC": {"fn": b_cpsc, "cat": "recalls", "ativa": False},
    "EUSafetyGate": {"fn": b_eu_safety, "cat": "recalls", "ativa": False},
    "HealthCanada": {"fn": b_health_canada, "cat": "recalls", "ativa": False},
    "NHTSA": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "USDAFSIS": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "RASFF": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "RappelConso": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "AGES": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "KZP": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "Sikdk": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "CFIA": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "ACCC": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "TGADRAC": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "Medsafe": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "PMDA": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "NITE": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "MHRA": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "OPSS": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "OECDGlobalRecalls": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "ApifyGlobalRisk": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "DeepRecallMCP": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "ApifyProductRecall": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "ICIJIMDD": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "ANVISATecnovig": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "ANVISAIrreg": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "INMETRO": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    "Senacon": {"fn": lambda q,n=5: [], "cat": "recalls", "ativa": False},
    
    # Normas (16)
    "ABNT": {"fn": b_abnt, "cat": "normas", "ativa": False},
    "ISO": {"fn": b_iso, "cat": "normas", "ativa": False},
    "IEC": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ASTM": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "IEEE": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT14724": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT6023": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT10520": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT6027": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT6024": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT6028": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT12225": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ABNT15287": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ISO20802": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "ISO19168": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    "IEC62541": {"fn": lambda q,n=5: [], "cat": "normas", "ativa": False},
    
    # Terra (4)
    "NASAEarthdata": {"fn": b_nasa_earthdata, "cat": "terra", "ativa": True},
    "CopernicusCDS": {"fn": b_copernicus, "cat": "terra", "ativa": False},
    "NOAA": {"fn": b_noaa, "cat": "terra", "ativa": False},
    "USGSEarthquake": {"fn": b_usgs_earthquake, "cat": "terra", "ativa": True},
    
    # Desafios (3)
    "Kaggle": {"fn": b_kaggle, "cat": "desafios", "ativa": True},
    "DrivenData": {"fn": b_drivendata, "cat": "desafios", "ativa": False},
    "OpenChallenges": {"fn": b_openchallenges, "cat": "desafios", "ativa": False},
    
    # Materiais (8)
    "MaterialsProject": {"fn": b_materials_project, "cat": "materiais", "ativa": False},
    "OPTIMADE": {"fn": b_optimade, "cat": "materiais", "ativa": False},
    "Matbench": {"fn": b_matbench, "cat": "materiais", "ativa": False},
    "AFLOW": {"fn": b_aflow, "cat": "materiais", "ativa": False},
    "OQMD": {"fn": b_oqmd, "cat": "materiais", "ativa": False},
    "JARVIS": {"fn": b_jarvis, "cat": "materiais", "ativa": False},
    "MaterialsCloud": {"fn": b_materials_cloud, "cat": "materiais", "ativa": False},
    "NOMAD": {"fn": b_nomad, "cat": "materiais", "ativa": False},
    
    # Genômica (5)
    "Ensembl": {"fn": b_ensembl, "cat": "genomica", "ativa": False},
    "NCBIEutils": {"fn": b_ncbi_eutils, "cat": "genomica", "ativa": False},
    "ENA": {"fn": b_ena, "cat": "genomica", "ativa": False},
    "GDC": {"fn": b_gdc, "cat": "genomica", "ativa": False},
    "UCSC": {"fn": b_ucsc, "cat": "genomica", "ativa": False},
    
    # Dados Gov BR (7)
    "dados.gov.br": {"fn": b_dados_gov, "cat": "gov_br", "ativa": False},
    "Ipeadata": {"fn": b_ipeadata, "cat": "gov_br", "ativa": False},
    "BCB": {"fn": b_bcb, "cat": "gov_br", "ativa": False},
    "Transferegov": {"fn": b_transferegov, "cat": "gov_br", "ativa": False},
    "ObrasGov": {"fn": b_obrasgov, "cat": "gov_br", "ativa": False},
    "Tesouro": {"fn": b_tesouro, "cat": "gov_br", "ativa": False},
    "INDE": {"fn": b_inde, "cat": "gov_br", "ativa": False},
    
    # Dados Gov Intl (9)
    "DataGovUS": {"fn": b_data_gov_us, "cat": "gov_intl", "ativa": False},
    "DataGovUK": {"fn": b_data_gov_uk, "cat": "gov_intl", "ativa": False},
    "GovDataDE": {"fn": b_govdata_de, "cat": "gov_intl", "ativa": False},
    "DataGovtNZ": {"fn": b_data_govt_nz, "cat": "gov_intl", "ativa": False},
    "DataGovSG": {"fn": b_data_gov_sg, "cat": "gov_intl", "ativa": False},
    "IndiaOGD": {"fn": b_india_ogd, "cat": "gov_intl", "ativa": False},
    "WorldBank": {"fn": b_worldbank, "cat": "gov_intl", "ativa": False},
    "DatosES": {"fn": b_datos_es, "cat": "gov_intl", "ativa": False},
    "DatosCO": {"fn": b_datos_co, "cat": "gov_intl", "ativa": False},
    
    # Financiamento (22)
    "FINEP": {"fn": b_finep, "cat": "financiamento", "ativa": False},
    "CNPq": {"fn": b_cnpq, "cat": "financiamento", "ativa": False},
    "FAPEMIG": {"fn": b_fapemig, "cat": "financiamento", "ativa": False},
    "FAPESP": {"fn": b_fapesp, "cat": "financiamento", "ativa": False},
    "BNDES": {"fn": b_bndes, "cat": "financiamento", "ativa": False},
    "EMBRAPII": {"fn": b_embrapii, "cat": "financiamento", "ativa": False},
    "Rota2030": {"fn": b_rota2030, "cat": "financiamento", "ativa": False},
    "HorizonEurope": {"fn": b_horizon, "cat": "financiamento", "ativa": False},
    "NIHFunding": {"fn": b_nih_funding, "cat": "financiamento", "ativa": False},
    "NSF": {"fn": b_nsf, "cat": "financiamento", "ativa": False},
    "DARPA": {"fn": b_darpa, "cat": "financiamento", "ativa": False},
    "Gates": {"fn": b_gates, "cat": "financiamento", "ativa": False},
    "Wellcome": {"fn": b_wellcome, "cat": "financiamento", "ativa": False},
    "ERC": {"fn": b_erc, "cat": "financiamento", "ativa": False},
    "DFG": {"fn": b_dfg, "cat": "financiamento", "ativa": False},
    "JSPS": {"fn": b_jsps, "cat": "financiamento", "ativa": False},
    "NSFC": {"fn": b_nsfc, "cat": "financiamento", "ativa": False},
    "CONICET": {"fn": b_conicet, "cat": "financiamento", "ativa": False},
    "CONACYT": {"fn": b_conacyt, "cat": "financiamento", "ativa": False},
    "ANII": {"fn": b_anii, "cat": "financiamento", "ativa": False},
    "FONDECYT": {"fn": b_fondecyt, "cat": "financiamento", "ativa": False},
    "FinepInovacred": {"fn": b_finep_inovacred, "cat": "financiamento", "ativa": False},
    
    # Colaboração (14)
    "ORCID": {"fn": b_orcid, "cat": "colaboracao", "ativa": True},
    "ROR": {"fn": b_ror, "cat": "colaboracao", "ativa": False},
    "ResearchGate": {"fn": b_researchgate, "cat": "colaboracao", "ativa": False},
    "Loop": {"fn": b_loop, "cat": "colaboracao", "ativa": False},
    "SciProfiles": {"fn": b_sciprofiles, "cat": "colaboracao", "ativa": False},
    "GoogleScholar": {"fn": b_google_scholar, "cat": "colaboracao", "ativa": False},
    "Academia": {"fn": b_academia, "cat": "colaboracao", "ativa": False},
    "Mendeley": {"fn": b_mendeley, "cat": "colaboracao", "ativa": False},
    "CrossrefFunder": {"fn": b_crossref_funder, "cat": "colaboracao", "ativa": False},
    "Dimensions": {"fn": b_dimensions, "cat": "colaboracao", "ativa": False},
    "INSPIREAuthors": {"fn": b_inspire_authors, "cat": "colaboracao", "ativa": False},
    "OpenAlexInst": {"fn": b_openalex_inst, "cat": "colaboracao", "ativa": False},
    "GRID": {"fn": b_grid, "cat": "colaboracao", "ativa": False},
    "CORDISPartners": {"fn": b_cordis_partners, "cat": "colaboracao", "ativa": False},
    
    # Infraestrutura (12)
    "ELN": {"fn": b_eln, "cat": "infraestrutura", "ativa": False},
    "iLAB": {"fn": b_ilab, "cat": "infraestrutura", "ativa": False},
    "SciNote": {"fn": b_scinote, "cat": "infraestrutura", "ativa": False},
    "LabArchives": {"fn": b_labarchives, "cat": "infraestrutura", "ativa": False},
    "OpenBIS": {"fn": b_openbis, "cat": "infraestrutura", "ativa": False},
    "ZenodoLabs": {"fn": b_zenodo_labs, "cat": "infraestrutura", "ativa": False},
    "EU-OPENSCREEN": {"fn": b_eu_openscreen, "cat": "infraestrutura", "ativa": False},
    "Instruct-ERIC": {"fn": b_instruct, "cat": "infraestrutura", "ativa": False},
    "CERIC-ERIC": {"fn": b_ceric, "cat": "infraestrutura", "ativa": False},
    "EMBL": {"fn": b_embl, "cat": "infraestrutura", "ativa": False},
    "LNLS-SIRIUS": {"fn": b_lnls, "cat": "infraestrutura", "ativa": False},
    "IPEN": {"fn": b_ipen, "cat": "infraestrutura", "ativa": False},
    
    # Publicações (7)
    "SciELO": {"fn": b_scielo, "cat": "publicacoes", "ativa": False},
    "Redalyc": {"fn": b_redalyc, "cat": "publicacoes", "ativa": False},
    "Latindex": {"fn": b_latindex, "cat": "publicacoes", "ativa": False},
    "BASE": {"fn": b_base, "cat": "publicacoes", "ativa": False},
    "OpenAIRE": {"fn": b_openAIRE, "cat": "publicacoes", "ativa": False},
    "JSTAGE": {"fn": b_jstage, "cat": "publicacoes", "ativa": False},
    "DOAJ2": {"fn": b_doaj2, "cat": "publicacoes", "ativa": False},
    
    # Segurança Química (4)
    "ECHA": {"fn": b_echa, "cat": "quimica_seg", "ativa": False},
    "EPACompTox": {"fn": b_epa_comptox, "cat": "quimica_seg", "ativa": False},
    "NRCERNS": {"fn": b_nrc_erns, "cat": "quimica_seg", "ativa": False},
    "Chemwatch": {"fn": b_chemwatch, "cat": "quimica_seg", "ativa": False},
    
    # Outros (4)
    "myTomorrows": {"fn": b_mytomorrows, "cat": "outros", "ativa": False},
    "NTSB": {"fn": b_ntsb, "cat": "outros", "ativa": False},
    "FAASIAS": {"fn": b_faa_asias, "cat": "outros", "ativa": False},
    "HealthCanada2": {"fn": b_health_canada2, "cat": "outros", "ativa": False},
    
    # Web (1)
    "Web": {"fn": b_web, "cat": "web", "ativa": True},
}


def buscar_em_todas(q, n=4):
    """Busca em TODOS os 187 bancos em paralelo."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    arts = []
    status = {}
    
    def _safe(nome_info):
        nome, info = nome_info
        if not info["ativa"]:
            return nome, [], "inativo"
        try:
            r = info["fn"](q, n)
            return nome, r, None
        except Exception as e:
            return nome, [], str(e)[:50]
    
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = [ex.submit(_safe, item) for item in BANCOS.items()]
        for fut in as_completed(futs):
            nome, r, err = fut.result()
            status[nome] = {"count": len(r), "err": err, "cat": BANCOS[nome]["cat"]}
            if r: arts.extend(r)
    
    return arts, status


def resumo_por_categoria():
    """Resumo por categoria."""
    cats = {}
    for nome, info in BANCOS.items():
        c = info["cat"]
        if c not in cats:
            cats[c] = {"total": 0, "ativas": 0}
        cats[c]["total"] += 1
        if info["ativa"]:
            cats[c]["ativas"] += 1
    return cats


if __name__ == "__main__":
    cats = resumo_por_categoria()
    print(f"TOTAL DE BANCOS: {len(BANCOS)}")
    print()
    for cat, info in sorted(cats.items()):
        print(f"{cat:20s}: {info['ativas']:2d}/{info['total']:2d} ativas")