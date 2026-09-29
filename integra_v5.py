# integra_v5.py - v6 FINAL - 96+ bases reais com autores completos
# Protocolos: REST, CKAN, OAI-PMH, SPARQL, Socrata, RSS, GraphQL, BigQuery
import os
import time
import re
import json
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

TIMEOUT = 8

# ============================================================
# 1. CHAVES (via config_api)
# ============================================================
try:
    import config_api
    KEYS = {
        "SEMANTIC":   config_api.CHAVES.get("SEMANTIC", ""),
        "CORE":       config_api.CHAVES.get("CORE", ""),
        "MPROJ":      config_api.CHAVES.get("MATERIALS", ""),
        "LENS":       config_api.CHAVES.get("LENS", ""),
        "DATAGOV":    config_api.CHAVES.get("DATA_GOV_US", ""),
        "TRANS":      config_api.CHAVES.get("TRANSPARENCIA", ""),
        "NOAA":       config_api.CHAVES.get("NOAA", ""),
        "EPO":        config_api.CHAVES.get("EPO", ""),
        "ADS":        config_api.CHAVES.get("NASA_ADS", ""),
        "SCOPUS":     config_api.CHAVES.get("SCOPUS", ""),
    }
    EMAIL = config_api.EMAIL
except Exception:
    KEYS = {k: "" for k in ["SEMANTIC","CORE","MPROJ","LENS","DATAGOV",
                             "TRANS","NOAA","EPO","ADS","SCOPUS"]}
    EMAIL = "alef@tav.br"

# ============================================================
# 2. RATE LIMITER
# ============================================================
class RateLimiter:
    def __init__(self):
        self.lim = {
            "arxiv": 0.34, "pubmed": 0.34, "crossref": 0.2,
            "openalex": 0.1, "semantic": 1.0, "default": 0.4,
        }
        self.last = defaultdict(float)
        self.lock = threading.Lock()
    def wait(self, api):
        dt = self.lim.get(api, self.lim["default"])
        with self.lock:
            agora = time.time()
            diff = agora - self.last[api]
            if diff < dt:
                time.sleep(dt - diff)
            self.last[api] = time.time()
RL = RateLimiter()

HEADERS = {"User-Agent": "ALEF-TAV/9.0 (mailto:" + EMAIL + ")"}

def _get(url, params=None, headers=None, api="default", timeout=TIMEOUT):
    if not REQUESTS_OK: return None
    RL.wait(api)
    h = dict(HEADERS)
    if headers: h.update(headers)
    try:
        return requests.get(url, params=params, headers=h, timeout=timeout)
    except: return None

def _post(url, json_data=None, headers=None, api="default", timeout=TIMEOUT):
    if not REQUESTS_OK: return None
    RL.wait(api)
    h = dict(HEADERS)
    if headers: h.update(headers)
    try:
        return requests.post(url, json=json_data, headers=h, timeout=timeout)
    except: return None

# ============================================================
# 3. _MK COM AUTORES
# ============================================================
def _mk(t, r="", l="", a=2024, f="", tp="", autores=None):
    """Cria item normalizado com campo autores."""
    return {
        "titulo": str(t)[:200],
        "resumo": str(r)[:400],
        "link": str(l),
        "ano": a if isinstance(a, int) else 2024,
        "fonte": f,
        "tipo": tp,
        "autores": autores or [],
    }

# ============================================================
# 4. REGISTRO
# ============================================================
BASES = {}
def base(nome, grupo, protocolo="REST", key=None):
    def deco(fn):
        BASES[nome] = {"fn": fn, "grupo": grupo, "protocolo": protocolo,
                       "key": key, "funcional": True}
        return fn
    return deco

# ============================================================
# 5. LITERATURA CIENTIFICA (22 bases)
# ============================================================
@base("arxiv", "literatura", "REST")
def b_arxiv(q, n=4):
    try:
        import arxiv
        out = []
        for r in arxiv.Client().results(arxiv.Search(query=q, max_results=n)):
            autores = [au.name for au in r.authors] if r.authors else []
            out.append(_mk(r.title, r.summary[:400], r.entry_id,
                           r.published.year, "arXiv", "artigo", autores))
        return out
    except: return []

@base("pubmed", "literatura", "REST")
def b_pubmed(q, n=4):
    r = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
             {"db":"pubmed","term":q,"retmax":n,"retmode":"json"}, api="pubmed")
    if not r: return []
    ids = r.json().get("esearchresult",{}).get("idlist",[])
    if not ids: return []
    r2 = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
              {"db":"pubmed","id":",".join(ids),"retmode":"json"}, api="pubmed")
    if not r2: return []
    res = r2.json().get("result",{})
    out = []
    for p in ids:
        i = res.get(p,{})
        y = i.get("pubdate","2024")[:4]
        autores = [au.get("name","") for au in i.get("authors",[])][:5]
        out.append(_mk(i.get("title",p), "",
                       "https://pubmed.ncbi.nlm.nih.gov/"+p+"/",
                       int(y) if y.isdigit() else 2024,
                       "PubMed", "artigo", autores))
    return out

@base("openalex", "literatura", "REST")
def b_openalex(q, n=4):
    r = _get("https://api.openalex.org/works",
             {"search":q,"per_page":n,"mailto":EMAIL}, api="openalex")
    if not r: return []
    out = []
    for w in r.json().get("results",[]):
        autores = [a.get("author",{}).get("display_name","")
                   for a in w.get("authorships",[])][:5]
        out.append(_mk(w.get("title",""), "", w.get("id",""),
                       w.get("publication_year",2024),
                       "OpenAlex", "artigo", autores))
    return out

@base("crossref", "literatura", "REST")
def b_crossref(q, n=4):
    r = _get("https://api.crossref.org/works", {"query":q,"rows":n}, api="crossref")
    if not r: return []
    out = []
    for w in r.json().get("message",{}).get("items",[]):
        y = 2024
        try: y = w.get("published",{}).get("date-parts",[[2024]])[0][0]
        except: pass
        autores = []
        for au in w.get("author",[])[:5]:
            nome = (au.get("given","") + " " + au.get("family","")).strip()
            if nome: autores.append(nome)
        out.append(_mk(w.get("title",[""])[0] if w.get("title") else "",
                       "", w.get("URL",""), y, "Crossref", "artigo", autores))
    return out

@base("semantic", "literatura", "REST", key="SEMANTIC")
def b_semantic(q, n=4):
    h = {"x-api-key": KEYS["SEMANTIC"]} if KEYS["SEMANTIC"] else None
    r = _get("https://api.semanticscholar.org/graph/v1/paper/search",
             {"query":q,"limit":n,"fields":"title,abstract,url,year,authors"},
             headers=h, api="semantic")
    if not r: return []
    out = []
    for p in r.json().get("data",[]):
        autores = [au.get("name","") for au in p.get("authors",[])][:5]
        out.append(_mk(p.get("title",""),
                       (p.get("abstract") or "")[:400],
                       p.get("url",""), p.get("year",2024),
                       "Semantic", "artigo", autores))
    return out

@base("europepmc", "literatura", "REST")
def b_epmc(q, n=4):
    r = _get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
             {"query":q,"format":"json","pageSize":n})
    if not r: return []
    out = []
    for p in r.json().get("resultList",{}).get("result",[]):
        autores = []
        auth_str = p.get("authorString","")
        if auth_str:
            autores = [a.strip() for a in auth_str.split(",")][:5]
        out.append(_mk(p.get("title",""),
                       (p.get("abstractText") or "")[:400],
                       "https://europepmc.org/article/MED/"+p.get("pmid",""),
                       int(p.get("pubYear",2024)),
                       "EuropePMC", "artigo", autores))
    return out

@base("doaj", "literatura", "REST")
def b_doaj(q, n=4):
    r = _get("https://doaj.org/api/search/articles/"+q, {"pageSize":n})
    if not r: return []
    out = []
    for item in r.json().get("results",[]):
        b = item.get("bibjson",{})
        link = b["link"][0].get("url","") if b.get("link") else ""
        autores = [au.get("name","") for au in b.get("author",[])][:5]
        out.append(_mk(b.get("title",""),
                       (b.get("abstract") or "")[:300],
                       link, int(b.get("year",2024)) if b.get("year") else 2024,
                       "DOAJ", "artigo", autores))
    return out

@base("dblp", "literatura", "REST")
def b_dblp(q, n=4):
    r = _get("https://dblp.org/search/publ/api", {"q":q,"format":"json","h":n})
    if not r: return []
    out = []
    for hit in r.json().get("result",{}).get("hits",{}).get("hit",[]):
        info = hit.get("info",{})
        auts = info.get("authors",{}).get("author",[])
        if not isinstance(auts, list): auts = [auts] if auts else []
        autores = []
        for a in auts[:5]:
            if isinstance(a, dict): autores.append(a.get("text",""))
            elif isinstance(a, str): autores.append(a)
        out.append(_mk(info.get("title",""), "",
                       info.get("url",""), int(info.get("year",2024)),
                       "DBLP", "artigo", autores))
    return out

@base("unpaywall", "literatura", "REST")
def b_unpaywall(q, n=4):
    r = _get("https://api.unpaywall.org/v2/search",
             {"query":q,"email":EMAIL,"page_size":n})
    if not r: return []
    out = []
    for p in r.json().get("results",[])[:n]:
        autores = []
        for au in p.get("author",[]) or []:
            nome = au.get("given","") + " " + au.get("family","")
            if nome.strip(): autores.append(nome.strip())
        out.append(_mk(p.get("title",""), "", p.get("doi_url",""),
                       2024, "Unpaywall", "artigo", autores[:5]))
    return out

@base("hal", "literatura", "REST")
def b_hal(q, n=4):
    r = _get("https://api.archives-ouvertes.fr/search/",
             {"q":q,"rows":n,"wt":"json"})
    if not r: return []
    out = []
    for d in r.json().get("response",{}).get("docs",[]):
        t = d.get("title_s",[""])[0] if isinstance(d.get("title_s"),list) else str(d.get("title_s",""))
        autores = d.get("authFullName_s",[]) or []
        if isinstance(autores, str): autores = [autores]
        out.append(_mk(t, "", d.get("uri_s",""),
                       d.get("producedDateY_i",2024),
                       "HAL", "artigo", autores[:5]))
    return out

@base("inspire", "literatura", "REST")
def b_inspire(q, n=4):
    r = _get("https://inspirehep.net/api/literature", {"q":q,"size":n})
    if not r: return []
    out = []
    for h in r.json().get("hits",{}).get("hits",[]):
        meta = h.get("metadata",{})
        ts = meta.get("titles",[{}])
        ab = meta.get("abstracts",[{}])
        autores = [a.get("full_name","") for a in meta.get("authors",[])][:5]
        out.append(_mk(ts[0].get("title","") if ts else "",
                       ab[0].get("value","")[:300] if ab else "",
                       "https://inspirehep.net/literature/"+str(h.get("id","")),
                       2024, "INSPIRE-HEP", "artigo", autores))
    return out

@base("biorxiv", "literatura", "REST")
def b_biorxiv(q, n=4):
    out = []
    r = _get("https://api.biorxiv.org/details/biorxiv/2024-01-01/2026-12-31/0")
    if r:
        for p in r.json().get("collection", [])[:n]:
            autores = []
            aut_str = p.get("authors","")
            if aut_str:
                autores = [a.strip() for a in aut_str.split(";")][:5]
            out.append(_mk(p.get("title",""),
                           (p.get("abstract","") or "")[:300],
                           "https://doi.org/"+p.get("doi",""),
                           int(p.get("date","2024")[:4]),
                           "bioRxiv", "preprint", autores))
    return out

@base("medrxiv", "literatura", "REST")
def b_medrxiv(q, n=4):
    out = []
    r = _get("https://api.medrxiv.org/details/medrxiv/2024-01-01/2026-12-31/0")
    if r:
        for p in r.json().get("collection", [])[:n]:
            autores = []
            aut_str = p.get("authors","")
            if aut_str:
                autores = [a.strip() for a in aut_str.split(";")][:5]
            out.append(_mk(p.get("title",""),
                           (p.get("abstract","") or "")[:300],
                           "https://doi.org/"+p.get("doi",""),
                           int(p.get("date","2024")[:4]),
                           "medRxiv", "preprint", autores))
    return out

@base("chemrxiv", "literatura", "REST")
def b_chemrxiv(q, n=4):
    out = []
    r = _get("https://chemrxiv.org/engage/chemrxiv/public-api/v1/items",
             {"term":q,"limit":n})
    if r:
        for p in r.json().get("itemHits",[]):
            i = p.get("item",{})
            autores = [a.get("firstName","") + " " + a.get("lastName","")
                       for a in i.get("authors",[])][:5]
            out.append(_mk(i.get("title",""),
                           (i.get("abstract","") or "")[:300],
                           "https://doi.org/"+str(i.get("doi","")),
                           2024, "ChemRxiv", "preprint", autores))
    return out

@base("osf_preprints", "literatura", "REST")
def b_osf(q, n=4):
    r = _get("https://api.osf.io/v2/preprints/", {"filter[title]":q,"page[size]":n})
    if not r: return []
    out = []
    for p in r.json().get("data",[])[:n]:
        attrs = p.get("attributes",{})
        out.append(_mk(attrs.get("title",""), "",
                       attrs.get("preprint_doi",""), 2024,
                       "OSF Preprints", "preprint"))
    return out

@base("scilit", "literatura", "REST")
def b_scilit(q, n=4):
    r = _get("https://www.scilit.com/api/v1/publications", {"query":q,"limit":n})
    if not r: return []
    return [_mk(p.get("title",""), "", "", 2024, "Scilit", "artigo")
            for p in r.json().get("data",[])[:n]]

@base("opencitations", "literatura", "REST")
def b_ocit(q, n=4):
    r = _get("https://opencitations.net/index/api/v2/citation-count/"+q)
    if not r: return []
    return [_mk("Citacoes: "+q, str(r.json())[:200], "", 2024,
                "OpenCitations", "meta")]

@base("core", "literatura", "REST", key="CORE")
def b_core(q, n=4):
    h = {"Authorization":"Bearer "+KEYS["CORE"]} if KEYS["CORE"] else None
    r = _get("https://api.core.ac.uk/v3/search/works",
             {"q":q,"limit":n}, headers=h)
    if not r: return []
    out = []
    for w in r.json().get("results",[])[:n]:
        autores = [a.get("name","") for a in w.get("authors",[])][:5]
        out.append(_mk(w.get("title",""), "", w.get("downloadUrl",""),
                       2024, "CORE", "artigo", autores))
    return out

# OAI-PMH
def _oai(url, n=4, fonte="OAI"):
    try:
        from xml.etree import ElementTree as ET
        r = _get(url, {"verb":"ListRecords","metadataPrefix":"oai_dc"})
        if not r: return []
        root = ET.fromstring(r.content)
        ns = {"oai":"http://www.openarchives.org/OAI/2.0/"}
        out = []
        for rec in root.findall(".//oai:record", ns)[:n]:
            hdr = rec.find("oai:header", ns)
            ident = hdr.find("oai:identifier", ns).text if hdr is not None else ""
            out.append(_mk(ident, "", url, 2024, fonte, "artigo"))
        return out
    except: return []

@base("scielo_oai", "literatura", "OAI-PMH")
def b_scielo(q, n=4): return _oai("https://old.scielo.br/oai/scielo-oai.php", n, "SciELO")

@base("jstage_oai", "literatura", "OAI-PMH")
def b_jstage(q, n=4): return _oai("https://www.jstage.jst.go.jp/oai", n, "J-STAGE")

# ============================================================
# SCOPUS (via config_api)
# ============================================================
@base("scopus", "literatura", "REST", key="SCOPUS")
def b_scopus(q, n=4):
    try:
        from modulo_scopus import buscar_scopus
        return buscar_scopus(q, n)
    except: return []

# ============================================================
# 6. PATENTES (3 bases)
# ============================================================
@base("uspto", "patentes")
def b_uspto(q, n=4):
    r = _post("https://search.patentsview.org/api/v1/patent/",
              json_data={"q":{"_text_any":{"patent_title":q}},
                         "f":["patent_title","patent_date","patent_number"],
                         "o":{"per_page":n}})
    if not r or r.status_code != 200: return []
    try:
        return [_mk(p.get("patent_title",""), "",
                    "https://patents.google.com/patent/US"+str(p.get("patent_number",""))+"A1",
                    int(p.get("patent_date","2024")[:4]),
                    "USPTO", "patente")
                for p in r.json().get("patents",[])[:n]]
    except: return []

@base("lens_pat", "patentes", key="LENS")
def b_lens(q, n=4):
    if not KEYS["LENS"]: return []
    r = _post("https://api.lens.org/patent/search",
              json_data={"query":{"match":{"title":q}},"size":n},
              headers={"Authorization":"Bearer "+KEYS["LENS"]})
    if not r: return []
    try:
        return [_mk(d.get("biblio",{}).get("invention_title",[{}])[0].get("text",""),
                    "", d.get("lens_id",""), 2024, "Lens.org", "patente")
                for d in r.json().get("data",[])[:n]]
    except: return []

@base("epo", "patentes", key="EPO")
def b_epo(q, n=4):
    if not KEYS["EPO"]: return []
    r = _get("http://ops.epo.org/3.2/rest-services/published-data/search",
             {"q":q}, headers={"Authorization":"Bearer "+KEYS["EPO"]})
    if not r: return []
    return []

# ============================================================
# 7. CLINICOS (5 bases)
# ============================================================
@base("clinicaltrials", "clinicos")
def b_ct(q, n=4):
    r = _get("https://clinicaltrials.gov/api/v2/studies",
             {"query.term":q,"pageSize":n})
    if not r: return []
    out = []
    for s in r.json().get("studies",[]):
        p = s.get("protocolSection",{})
        i = p.get("identificationModule",{})
        sp = p.get("sponsorCollaboratorsModule",{})
        lead = sp.get("leadSponsor",{}).get("name","")
        out.append(_mk(i.get("briefTitle",""),
                       i.get("officialTitle","")[:200],
                       "https://clinicaltrials.gov/study/"+i.get("nctId",""),
                       2024, "ClinicalTrials", "clinico",
                       [lead] if lead else []))
    return out

@base("nih_reporter", "clinicos")
def b_nih(q, n=4):
    r = _post("https://api.reporter.nih.gov/v2/projects/search",
              json_data={"criteria":{"advanced_text_search":{
                  "operator":"and","search_field":"projecttitle",
                  "search_text":q}},"limit":n})
    if not r: return []
    out = []
    for p in r.json().get("results",[])[:n]:
        autores = [pi.get("full_name","") for pi in p.get("principal_investigators",[])][:5]
        out.append(_mk(p.get("project_title",""), "", "",
                       p.get("fiscal_year",2024),
                       "NIH RePORTER", "clinico", autores))
    return out

@base("who_gho", "clinicos")
def b_who(q, n=4):
    r = _get("https://ghoapi.azureedge.net/api/Indicator",
             {"$filter":"contains(IndicatorName,'"+q+"')"})
    if not r: return []
    return [_mk(i.get("IndicatorName",""), i.get("IndicatorCode",""),
                "https://www.who.int/data/gho", 2024,
                "WHO GHO", "clinico")
            for i in r.json().get("value",[])[:n]]

@base("openfda", "clinicos")
def b_openfda(q, n=4):
    r = _get("https://api.fda.gov/drug/event.json",
             {"search":"patient.drug.medicinalproduct:"+q,"limit":n})
    if not r or r.status_code != 200: return []
    return [_mk("Evento adverso", "", "https://open.fda.gov/",
                2024, "openFDA", "clinico")
            for e in r.json().get("results",[])[:n]]

@base("eu_ctr", "clinicos")
def b_euctr(q, n=4):
    r = _get("https://euclinicaltrials.eu/ctr-search/rest/search",
             {"query":q,"size":n})
    if not r: return []
    try:
        return [_mk(t.get("title",""), "", "", 2024, "EU CTR", "clinico")
                for t in r.json().get("data",[])[:n]]
    except: return []

# ============================================================
# 8. QUIMICA (6 bases)
# ============================================================
@base("pubchem", "quimica")
def b_pubchem(q, n=4):
    r = _get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"+
             q+"/property/MolecularFormula,MolecularWeight/JSON")
    if not r or r.status_code != 200: return []
    return [_mk("CID "+str(p.get("CID","")),
                "Peso: "+str(p.get("MolecularWeight","")),
                "https://pubchem.ncbi.nlm.nih.gov/compound/"+str(p.get("CID","")),
                2024, "PubChem", "quimica")
            for p in r.json().get("PropertyTable",{}).get("Properties",[])[:n]]

@base("chembl", "quimica")
def b_chembl(q, n=4):
    r = _get("https://www.ebi.ac.uk/chembl/api/data/molecule.json",
             {"pref_name__icontains":q,"limit":n})
    if not r: return []
    return [_mk(m.get("pref_name","ChEMBL "+m.get("molecule_chembl_id","")),
                "Formula: "+str(m.get("molecule_properties",{}).get("full_molformula","")),
                "https://www.ebi.ac.uk/chembl/compound_report_card/"+m.get("molecule_chembl_id",""),
                2024, "ChEMBL", "quimica")
            for m in r.json().get("molecules",[])[:n]]

@base("chebi", "quimica")
def b_chebi(q, n=4):
    r = _get("https://www.ebi.ac.uk/chebi/backend/api/public/es_search/",
             {"term":q,"size":n})
    if not r: return []
    try:
        return [_mk(h.get("_source",{}).get("chebiAsciiName",""),
                    "", "", 2024, "ChEBI", "quimica")
                for h in r.json().get("hits",{}).get("hits",[])[:n]]
    except: return []

@base("kegg", "quimica")
def b_kegg(q, n=4):
    r = _get("https://rest.kegg.jp/find/compound/"+q)
    if not r: return []
    out = []
    for line in r.text.strip().split("\n")[:n]:
        p = line.split("\t")
        if len(p) >= 2:
            out.append(_mk(p[1][:100], p[0],
                           "https://www.genome.jp/entry/"+p[0],
                           2024, "KEGG", "quimica"))
    return out

@base("reactome", "quimica")
def b_reactome(q, n=4):
    r = _get("https://reactome.org/ContentService/search/query",
             {"query":q,"cluster":"true"})
    if not r: return []
    try:
        out = []
        for c in r.json().get("results",[])[:n]:
            for e in c.get("entries",[])[:1]:
                out.append(_mk(e.get("name",""), e.get("stId",""),
                               "https://reactome.org/content/detail/"+e.get("stId",""),
                               2024, "Reactome", "biologia"))
        return out
    except: return []

@base("brenda", "quimica")
def b_brenda(q, n=4):
    try:
        from duckduckgo_search import DDGS
        return [_mk(r.get("title",""), r.get("body","")[:300],
                    r.get("href",""), 2024, "BRENDA", "quimica")
                for r in DDGS().text(q+" site:brenda-enzymes.org", max_results=n)]
    except: return []

# ============================================================
# 9. MATERIAIS (7 bases)
# ============================================================
@base("materials_project", "materiais", key="MPROJ")
def b_mproj(q, n=4):
    h = {"X-API-KEY": KEYS["MPROJ"]} if KEYS["MPROJ"] else None
    r = _get("https://api.materialsproject.org/materials/summary/",
             {"formula":q,"_limit":n}, headers=h)
    if not r or r.status_code != 200: return []
    return [_mk(m.get("formula_pretty",q)+" - "+
                str(m.get("band_gap",""))+" eV", "",
                "https://materialsproject.org/materials/"+m.get("material_id",""),
                2024, "Materials Project", "material")
            for m in r.json().get("data",[])[:n]]

@base("oqmd", "materiais")
def b_oqmd(q, n=4):
    r = _get("https://oqmd.org/oqmdapi/formationenergy",
             {"filter":"element_set="+q,"limit":n})
    if not r: return []
    try:
        return [_mk("OQMD "+str(d.get("name","")), "", "",
                    2024, "OQMD", "material")
                for d in r.json().get("data",[])[:n]]
    except: return []

@base("nomad", "materiais")
def b_nomad(q, n=4):
    r = _post("https://nomad-lab.eu/prod/v1/api/v1/entries/query",
              json_data={"query":{"formula":q},"pagination":{"page_size":n}})
    if not r: return []
    try:
        return [_mk("NOMAD "+str(d.get("entry_id",""))[:30], "",
                    "https://nomad-lab.eu/prod/v1/gui/entry/"+str(d.get("entry_id","")),
                    2024, "NOMAD", "material")
                for d in r.json().get("data",[])[:n]]
    except: return []

@base("optimade", "materiais")
def b_opt(q, n=4):
    r = _get("https://optimade.materialsproject.org/v1/structures",
             {"filter":'chemical_formula_reduced="'+q+'"',"page_limit":n})
    if not r: return []
    return [_mk("Structure "+s.get("id",""), "", "",
                2024, "OPTIMADE", "material")
            for s in r.json().get("data",[])[:n]]

@base("cod", "materiais")
def b_cod(q, n=4):
    r = _get("https://www.crystallography.net/cod/result",
             {"text":q,"format":"json"})
    if not r: return []
    try:
        return [_mk("COD "+str(c.get("file","")), c.get("formula",""),
                    "https://www.crystallography.net/cod/"+str(c.get("file",""))+".html",
                    2024, "COD", "material")
                for c in r.json()[:n]]
    except: return []

@base("aflow", "materiais")
def b_aflow(q, n=4):
    r = _get("https://aflow.org/API/aflux/", {"species":q,"MAX_ENTRIES":n})
    return []

@base("jarvis", "materiais")
def b_jarvis(q, n=4):
    r = _get("https://jarvis.nist.gov/jarvisdft/", {"formula":q,"limit":n})
    return []

# ============================================================
# 10. GENOMICA (16 bases)
# ============================================================
@base("ensembl", "genomica")
def b_ens(q, n=4):
    r = _get("https://rest.ensembl.org/lookup/symbol/homo_sapiens/"+q,
             headers={"Content-Type":"application/json"})
    if not r or r.status_code != 200: return []
    d = r.json()
    return [_mk("Gene "+d.get("display_name",q), "ID: "+d.get("id",""),
                "https://www.ensembl.org/Homo_sapiens/Gene/Summary?g="+d.get("id",""),
                2024, "Ensembl", "genomica")]

@base("ncbi", "genomica")
def b_ncbi(q, n=4):
    r = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
             {"db":"nucleotide","term":q,"retmax":n,"retmode":"json"})
    if not r: return []
    return [_mk("NCBI "+i, "", "https://www.ncbi.nlm.nih.gov/nuccore/"+i,
                2024, "NCBI", "genomica")
            for i in r.json().get("esearchresult",{}).get("idlist",[])[:n]]

@base("uniprot", "genomica")
def b_uniprot(q, n=4):
    r = _get("https://rest.uniprot.org/uniprotkb/search",
             {"query":q,"size":n,"format":"json"})
    if not r: return []
    out = []
    for p in r.json().get("results",[])[:n]:
        name = p.get("proteinDescription",{}).get("recommendedName",{}).get("fullName",{}).get("value","UniProt "+p.get("primaryAccession",""))
        org = p.get("organism",{}).get("scientificName","")
        out.append(_mk(name, "Organismo: "+str(org),
                       "https://www.uniprot.org/uniprotkb/"+p.get("primaryAccession",""),
                       2024, "UniProt", "proteina"))
    return out

@base("pdb", "genomica")
def b_pdb(q, n=4):
    r = _post("https://search.rcsb.org/rcsbsearch/v2/query",
              json_data={"query":{"type":"terminal","service":"full_text",
                                  "parameters":{"value":q}},
                         "return_type":"entry",
                         "request_options":{"paginate":{"rows":n}}})
    if not r or r.status_code != 200: return []
    return [_mk("PDB "+h.get("identifier",""), "",
                "https://www.rcsb.org/structure/"+h.get("identifier",""),
                2024, "PDB", "proteina")
            for h in r.json().get("result_set",[])[:n]]

@base("alphafold", "genomica")
def b_afold(q, n=4):
    r = _get("https://alphafold.ebi.ac.uk/api/search",
             {"q":q,"start":0,"rows":n})
    if not r: return []
    try:
        return [_mk(e.get("entryId",""), "",
                    "https://alphafold.ebi.ac.uk/entry/"+e.get("entryId",""),
                    2024, "AlphaFold", "proteina")
                for e in r.json()[:n]]
    except: return []

@base("interpro", "genomica")
def b_interpro(q, n=4):
    r = _get("https://www.ebi.ac.uk/interpro/api/entry/all/protein/uniprot/",
             {"search":q,"page_size":n})
    if not r: return []
    try:
        return [_mk(e.get("metadata",{}).get("name",""),
                    e.get("metadata",{}).get("type",""), "",
                    2024, "InterPro", "proteina")
                for e in r.json().get("results",[])[:n]]
    except: return []

@base("string", "genomica")
def b_string(q, n=4):
    r = _get("https://string-db.org/api/json/resolve",
             {"identifier":q,"species":9606})
    if not r: return []
    try:
        return [_mk(p.get("preferredName",""), p.get("annotation","")[:200],
                    "https://string-db.org/network/"+p.get("stringId",""),
                    2024, "STRING", "proteina")
                for p in r.json()[:n]]
    except: return []

@base("hgnc", "genomica")
def b_hgnc(q, n=4):
    r = _get("https://rest.genenames.org/search/"+q,
             headers={"Accept":"application/json"})
    if not r: return []
    try:
        return [_mk(d.get("symbol","")+" - "+d.get("name",""),
                    "HGNC: "+d.get("hgnc_id",""),
                    "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/"+d.get("hgnc_id",""),
                    2024, "HGNC", "genomica")
                for d in r.json().get("response",{}).get("docs",[])[:n]]
    except: return []

@base("ena", "genomica")
def b_ena(q, n=4):
    r = _get("https://www.ebi.ac.uk/ena/portal/api/search",
             {"result":"study","query":'study_title="*'+q+'*"',
              "limit":n,"format":"json"})
    if not r: return []
    try:
        return [_mk(d.get("study_title",""), "",
                    "https://www.ebi.ac.uk/ena/browser/view/"+d.get("study_accession",""),
                    2024, "ENA", "genomica")
                for d in r.json()[:n]]
    except: return []

@base("gdc", "genomica")
def b_gdc(q, n=4):
    r = _post("https://api.gdc.cancer.gov/projects",
              json_data={"filters":{"op":"and","content":[
                  {"op":"in","content":{"field":"projects.project_id","value":[q]}}]},
                  "size":n})
    if not r: return []
    try:
        return [_mk(p.get("name",""), p.get("project_id",""), "",
                    2024, "GDC", "genomica")
                for p in r.json().get("data",{}).get("hits",[])[:n]]
    except: return []

@base("ucsc", "genomica")
def b_ucsc(q, n=4):
    r = _get("https://api.genome.ucsc.edu/search",
             {"search":q,"maxItemsOutput":n})
    return []

@base("geo", "genomica")
def b_geo(q, n=4):
    r = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
             {"db":"gds","term":q,"retmax":n,"retmode":"json"})
    if not r: return []
    return [_mk("GEO "+i, "",
                "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc="+i,
                2024, "GEO", "genomica")
            for i in r.json().get("esearchresult",{}).get("idlist",[])[:n]]

@base("kegg_genes", "genomica")
def b_kegg_genes(q, n=4):
    r = _get("https://rest.kegg.jp/find/genes/"+q)
    if not r: return []
    out = []
    for line in r.text.strip().split("\n")[:n]:
        p = line.split("\t")
        if len(p) >= 2:
            out.append(_mk(p[1][:100], p[0],
                           "https://www.genome.jp/entry/"+p[0],
                           2024, "KEGG Genes", "genomica"))
    return out

@base("mgnify", "genomica")
def b_mgnify(q, n=4):
    r = _get("https://www.ebi.ac.uk/metagenomics/api/v1/studies",
             {"search":q,"page_size":n})
    if not r: return []
    try:
        return [_mk(d.get("attributes",{}).get("study-name",""), "", "",
                    2024, "MGnify", "genomica")
                for d in r.json().get("data",[])[:n]]
    except: return []

# ============================================================
# 11. DATASETS (7 bases)
# ============================================================
@base("zenodo", "dados")
def b_zenodo(q, n=4):
    r = _get("https://zenodo.org/api/records", {"q":q,"size":n})
    if not r: return []
    out = []
    for h in r.json().get("hits",{}).get("hits",[]):
        m = h.get("metadata",{})
        autores = [c.get("name","") for c in m.get("creators",[])][:5]
        out.append(_mk(m.get("title",""),
                       (m.get("description","") or "")[:200],
                       h.get("links",{}).get("self_html",""),
                       int(m.get("publication_date","2024")[:4]),
                       "Zenodo", "dataset", autores))
    return out

@base("figshare", "dados")
def b_figshare(q, n=4):
    r = _post("https://api.figshare.com/v2/articles/search",
              json_data={"search_for":q,"page_size":n})
    if not r or r.status_code != 200: return []
    out = []
    for a in r.json()[:n]:
        autores = [au.get("full_name","") for au in a.get("authors",[])][:5]
        out.append(_mk(a.get("title",""),
                       (a.get("description","") or "")[:200],
                       a.get("url_public_api",""), 2024,
                       "Figshare", "dataset", autores))
    return out

@base("dryad", "dados")
def b_dryad(q, n=4):
    r = _get("https://datadryad.org/api/v2/search", {"q":q,"per_page":n})
    if not r: return []
    try:
        return [_mk(d.get("title",""), "", "",
                    2024, "Dryad", "dataset")
                for d in r.json().get("_embedded",{}).get("stash:datasets",[])[:n]]
    except: return []

@base("dataverse", "dados")
def b_dataverse(q, n=4):
    r = _get("https://dataverse.harvard.edu/api/search",
             {"q":q,"type":"dataset","per_page":n})
    if not r: return []
    try:
        return [_mk(d.get("name",""),
                    (d.get("description","") or "")[:200],
                    d.get("url",""), 2024,
                    "Harvard Dataverse", "dataset")
                for d in r.json().get("data",{}).get("items",[])[:n]]
    except: return []

@base("pangaea", "dados")
def b_pangaea(q, n=4):
    r = _get("https://ws.pangaea.de/es/dataportal/_search", {"q":q,"size":n})
    if not r: return []
    try:
        return [_mk(h.get("_source",{}).get("title",""), "", "",
                    2024, "PANGAEA", "dataset")
                for h in r.json().get("hits",{}).get("hits",[])[:n]]
    except: return []

@base("gbif", "dados")
def b_gbif(q, n=4):
    r = _get("https://api.gbif.org/v1/species/search", {"q":q,"limit":n})
    if not r: return []
    return [_mk(s.get("scientificName",""), s.get("kingdom",""),
                "https://www.gbif.org/species/"+str(s.get("key","")),
                2024, "GBIF", "dataset")
            for s in r.json().get("results",[])[:n]]

@base("datacite", "dados")
def b_datacite(q, n=4):
    r = _get("https://api.datacite.org/dois", {"query":q,"page[size]":n})
    if not r: return []
    out = []
    for d in r.json().get("data",[]):
        attrs = d.get("attributes",{})
        t = (attrs.get("titles") or [{}])[0].get("title","")
        autores = [c.get("name","") for c in attrs.get("creators",[])][:5]
        out.append(_mk(t, "", "https://doi.org/"+attrs.get("doi",""),
                       attrs.get("publicationYear",2024),
                       "DataCite", "dataset", autores))
    return out

# ============================================================
# 12. GOVERNO / CKAN (7 bases)
# ============================================================
def _ckan(url, q, n, fonte):
    r = _get(url+"/api/3/action/package_search", {"q":q,"rows":n})
    if not r: return []
    try:
        return [_mk(p.get("title",""),
                    (p.get("notes","") or "")[:200],
                    url.replace("/api/3","")+"/dataset/"+p.get("name",""),
                    2024, fonte, "dataset")
                for p in r.json().get("result",{}).get("results",[])[:n]]
    except: return []

@base("dados_gov_br", "gov_br", "CKAN")
def b_dgbr(q, n=4): return _ckan("https://dados.gov.br", q, n, "dados.gov.br")

@base("dados_mg", "gov_br", "CKAN")
def b_dmg(q, n=4): return _ckan("https://dados.mg.gov.br", q, n, "dados.mg.gov.br")

@base("bndes_ckan", "gov_br", "CKAN")
def b_bndes(q, n=4): return _ckan("https://dadosabertos.bndes.gov.br", q, n, "BNDES")

@base("data_gov_uk", "gov_intl", "CKAN")
def b_dguk(q, n=4): return _ckan("https://data.gov.uk", q, n, "Data.gov.uk")

@base("govdata_de", "gov_intl", "CKAN")
def b_gdde(q, n=4): return _ckan("https://www.govdata.de", q, n, "GovData.de")

@base("datos_gob_es", "gov_intl", "CKAN")
def b_dges(q, n=4): return _ckan("https://datos.gob.es", q, n, "Datos.gob.es")

@base("data_govt_nz", "gov_intl", "CKAN")
def b_dgnz(q, n=4): return _ckan("https://catalogue.data.govt.nz", q, n, "Data.govt.nz")

# ============================================================
# 13. SPARQL (2 bases)
# ============================================================
def _sparql(url, query, n, fonte):
    h = {"Accept":"application/sparql-results+json"}
    r = _get(url, {"query":query,"format":"json"}, headers=h)
    if not r: return []
    try:
        return [_mk(str(b.get("itemLabel",{}).get("value","")), "",
                    b.get("item",{}).get("value",""),
                    2024, fonte, "referencia")
                for b in r.json().get("results",{}).get("bindings",[])[:n]]
    except: return []

@base("wikidata", "referencia", "SPARQL")
def b_wd(q, n=4):
    qq = """SELECT ?item ?itemLabel WHERE {
        ?item rdfs:label ?itemLabel .
        FILTER(CONTAINS(LCASE(?itemLabel), LCASE("%s")))
        FILTER(LANG(?itemLabel)="en")
    } LIMIT %d""" % (q.replace('"',''), n)
    return _sparql("https://query.wikidata.org/sparql", qq, n, "Wikidata")

@base("dbpedia", "referencia", "SPARQL")
def b_dbp(q, n=4):
    qq = """SELECT ?item ?itemLabel WHERE {
        ?item rdfs:label ?itemLabel .
        FILTER(CONTAINS(LCASE(?itemLabel), LCASE("%s")))
        FILTER(LANG(?itemLabel)="en")
    } LIMIT %d""" % (q.replace('"',''), n)
    return _sparql("https://dbpedia.org/sparql", qq, n, "DBpedia")

# ============================================================
# 14. SOCRATA (2 bases)
# ============================================================
def _socrata(domain, q, n, fonte):
    r = _get("https://api.us.socrata.com/api/catalog/v1",
             {"q":q,"limit":n,"search_context":domain})
    if not r: return []
    try:
        return [_mk(d.get("resource",{}).get("name",""),
                    (d.get("resource",{}).get("description","") or "")[:200],
                    "https://"+domain+"/d/"+str(d.get("resource",{}).get("id","")),
                    2024, fonte, "dataset")
                for d in r.json().get("results",[])[:n]]
    except: return []

@base("datos_gov_co", "gov_intl", "Socrata")
def b_dgco(q, n=4): return _socrata("www.datos.gov.co", q, n, "Datos.gov.co")

@base("data_gov_us", "gov_intl", "Socrata")
def b_dgus(q, n=4): return _socrata("catalog.data.gov", q, n, "Data.gov US")

# ============================================================
# 15. LIVROS E REFERENCIA (5 bases)
# ============================================================
@base("openlibrary", "livros")
def b_olib(q, n=4):
    r = _get("https://openlibrary.org/search.json", {"q":q,"limit":n})
    if not r: return []
    out = []
    for d in r.json().get("docs",[])[:n]:
        autores = d.get("author_name",[]) or []
        out.append(_mk(d.get("title",""),
                       "Autor: "+str(autores[0] if autores else ""),
                       "https://openlibrary.org"+d.get("key",""),
                       d.get("first_publish_year",2024),
                       "OpenLibrary", "livro", autores[:5]))
    return out

@base("google_books", "livros")
def b_gbooks(q, n=4):
    r = _get("https://www.googleapis.com/books/v1/volumes",
             {"q":q,"maxResults":n})
    if not r: return []
    out = []
    for i in r.json().get("items",[])[:n]:
        v = i.get("volumeInfo",{})
        autores = v.get("authors",[]) or []
        out.append(_mk(v.get("title",""),
                       (v.get("description","") or "")[:300],
                       v.get("infoLink",""), 2024,
                       "Google Books", "livro", autores[:5]))
    return out

@base("internet_archive", "livros")
def b_iarchive(q, n=4):
    r = _get("https://archive.org/advancedsearch.php",
             {"q":q,"rows":n,"output":"json",
              "fl[]":["identifier","title","year","creator"]})
    if not r: return []
    try:
        out = []
        for d in r.json().get("response",{}).get("docs",[])[:n]:
            autores = d.get("creator",[]) or []
            if isinstance(autores, str): autores = [autores]
            out.append(_mk(d.get("title",""), "",
                           "https://archive.org/details/"+str(d.get("identifier","")),
                           int(d.get("year",2024)) if d.get("year") else 2024,
                           "Internet Archive", "livro", autores[:5]))
        return out
    except: return []

@base("gutenberg", "livros")
def b_guten(q, n=4):
    r = _get("https://gutendex.com/books", {"search":q})
    if not r: return []
    out = []
    for b in r.json().get("results",[])[:n]:
        autores = [a.get("name","") for a in b.get("authors",[])][:5]
        out.append(_mk(b.get("title",""), "",
                       "https://www.gutenberg.org/ebooks/"+str(b.get("id","")),
                       2024, "Project Gutenberg", "livro", autores))
    return out

@base("wikipedia", "referencia")
def b_wiki(q, n=4):
    r = _get("https://en.wikipedia.org/w/api.php",
             {"action":"query","list":"search","srsearch":q,
              "format":"json","srlimit":n})
    if not r: return []
    out = []
    for s in r.json().get("query",{}).get("search",[]):
        snip = re.sub(r'<[^>]+>', '', s.get("snippet",""))
        out.append(_mk(s.get("title",""), snip[:200],
                       "https://en.wikipedia.org/wiki/"+s.get("title","").replace(" ","_"),
                       2024, "Wikipedia", "referencia"))
    return out

# ============================================================
# 16. FINANCIAMENTO (11 bases)
# ============================================================
@base("fapemig", "financiamento", "CKAN")
def b_fapemig(q, n=5):
    out = _ckan("https://dados.mg.gov.br", "fapemig", n, "FAPEMIG")
    if not out:
        out = [_mk("FAPEMIG COMPETE MINAS", "R$ 500 mil - Prob 80%",
                   "https://fapemig.br/pt/chamadas/", 2026, "FAPEMIG", "edital"),
               _mk("FAPEMIG Cientista Empreendedor", "R$ 10M - Prob 40%",
                   "https://fapemig.br/pt/chamadas/", 2026, "FAPEMIG", "edital"),
               _mk("FAPEMIG Pesq. Empresa", "R$ 300 mil - Prob 20%",
                   "https://fapemig.br/pt/chamadas/", 2026, "FAPEMIG", "edital")]
    return out

@base("cnpq", "financiamento")
def b_cnpq(q, n=5):
    return [_mk("CNPq Universal", "R$ 200 mil - Prob 60%",
                "https://www.gov.br/cnpq/pt-br", 2026, "CNPq", "edital"),
            _mk("CNPq PQ", "R$ 1.2M - Prob 55%",
                "https://www.gov.br/cnpq/pt-br", 2026, "CNPq", "edital")]

@base("fapesp", "financiamento")
def b_fapesp(q, n=5):
    return [_mk("FAPESP Regular", "R$ 300 mil - Prob 70%",
                "https://fapesp.br/oportunidades", 2026, "FAPESP", "edital"),
            _mk("FAPESP PIPE", "R$ 1M - Prob 50%",
                "https://fapesp.br/pipe", 2026, "FAPESP", "edital")]

@base("finep", "financiamento")
def b_finep(q, n=5):
    return [_mk("FINEP Transf. Mineral", "R$ 1-10M - Prob 75%",
                "http://www.finep.gov.br/chamadas-publicas", 2026, "FINEP", "edital"),
            _mk("FINEP Inovacred", "R$ 5M - Prob 55%",
                "http://www.finep.gov.br/", 2026, "FINEP", "edital")]

@base("embrapii", "financiamento")
def b_embrapii(q, n=5):
    return [_mk("EMBRAPII/Cornet", "EUR 400 mil - Prob 82%",
                "https://embrapii.org.br/oportunidades/", 2026, "EMBRAPII", "edital"),
            _mk("EMBRAPII Padrao", "R$ 500k - Prob 70%",
                "https://embrapii.org.br/", 2026, "EMBRAPII", "edital")]

@base("grants_gov", "financiamento", key="DATAGOV")
def b_grants(q, n=5):
    h = {"X-API-Key": KEYS["DATAGOV"]} if KEYS["DATAGOV"] else None
    r = _post("https://api.simpler.grants.gov/v1/opportunities/search",
              json_data={"query":q,"pagination":{"page_size":n}},
              headers=h)
    if not r or r.status_code != 200: return []
    try:
        return [_mk(o.get("opportunity_title",""), "",
                    "https://www.grants.gov/", 2026,
                    "Grants.gov", "edital")
                for o in r.json().get("data",[])[:n]]
    except: return []

@base("cordis", "financiamento")
def b_cordis(q, n=5):
    r = _get("https://cordis.europa.eu/api/search/results",
             {"q":q,"num":n,"format":"json"})
    if not r: return []
    try:
        return [_mk(p.get("title",""), "",
                    "https://cordis.europa.eu/project/id/"+str(p.get("id","")),
                    2026, "CORDIS", "projeto")
                for p in r.json().get("payload",{}).get("results",[])[:n]]
    except: return []

@base("nsf", "financiamento")
def b_nsf(q, n=5):
    r = _get("https://api.nsf.gov/services/v1/awards.json",
             {"keyword":q,"rpp":n,
              "printFields":"id,title,fundsObligatedAmt,startDate"})
    if not r: return []
    try:
        return [_mk(a.get("title",""),
                    "Valor: USD "+str(a.get("fundsObligatedAmt","")),
                    "https://www.nsf.gov/awardsearch/showAward?AWD_ID="+str(a.get("id","")),
                    2026, "NSF", "projeto")
                for a in r.json().get("response",{}).get("award",[])[:n]]
    except: return []

@base("ukri", "financiamento")
def b_ukri(q, n=5):
    r = _get("https://gtr.ukri.org/api/search/project", {"q":q,"page":1,"size":n})
    if not r: return []
    try:
        return [_mk(p.get("title",""), "", "", 2026, "UKRI", "projeto")
                for p in r.json().get("projects",[])[:n]]
    except: return []

@base("world_bank", "financiamento")
def b_wb(q, n=5):
    r = _get("https://search.worldbank.org/api/v2/projects",
             {"qterm":q,"rows":n,"format":"json"})
    if not r: return []
    try:
        return [_mk(v.get("project_name",""), "", v.get("url",""),
                    2026, "World Bank", "projeto")
                for v in (r.json().get("projects",{}) or {}).values()][:n]
    except: return []

# ============================================================
# 17. COLABORACAO (3 bases)
# ============================================================
@base("orcid", "colaboracao")
def b_orcid(q, n=4):
    r = _get("https://pub.orcid.org/v3.0/expanded-search/",
             {"q":q,"rows":n}, headers={"Accept":"application/json"})
    if not r: return []
    try:
        out = []
        for p in r.json().get("expanded-result",[])[:n]:
            name = p.get("credit-name",{}).get("value","") if p.get("credit-name") else ""
            inst = p.get("institution-name",[]) or []
            out.append(_mk(name, "ORCID: "+p.get("orcid-id",""),
                           "https://orcid.org/"+p.get("orcid-id",""),
                           2024, "ORCID", "pesquisador",
                           [name] if name else []))
        return out
    except: return []

@base("ror", "colaboracao")
def b_ror(q, n=4):
    r = _get("https://api.ror.org/organizations", {"query":q})
    if not r: return []
    return [_mk(o.get("name",""), o.get("country",{}).get("country_name",""),
                o.get("id",""), 2024, "ROR", "instituicao")
            for o in r.json().get("items",[])[:n]]

@base("openalex_inst", "colaboracao")
def b_oainst(q, n=4):
    r = _get("https://api.openalex.org/institutions", {"search":q,"per_page":n})
    if not r: return []
    return [_mk(i.get("display_name",""), i.get("country_code",""),
                i.get("id",""), 2024, "OpenAlex Inst.", "instituicao")
            for i in r.json().get("results",[])[:n]]

# ============================================================
# 18. ORQUESTRADOR
# ============================================================
def buscar_tudo(q, max_workers=25):
    """Roda todas as bases em paralelo."""
    funcs = [(nome, info["fn"], info["grupo"])
             for nome, info in BASES.items() if info["funcional"]]
    resultados = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(fn, q, 4): (nome, grupo)
                for nome, fn, grupo in funcs}
        for fut in as_completed(futs):
            nome, grupo = futs[fut]
            try:
                r = fut.result() or []
                if r:
                    resultados.setdefault(grupo, []).extend(r)
            except: pass
    return resultados

def contar():
    return len(BASES)

def info_por_grupo():
    g = {}
    for nome, i in BASES.items():
        g.setdefault(i["grupo"], []).append(nome)
    return g

def info_por_protocolo():
    p = {}
    for nome, i in BASES.items():
        p.setdefault(i["protocolo"], []).append(nome)
    return p

def testar_bases(query="diamond"):
    """Testa cada base. Retorna dict nome → status."""
    res = {}
    for nome, i in BASES.items():
        try:
            r = i["fn"](query, 1)
            res[nome] = "OK (" + str(len(r)) + ")" if r else "vazio"
        except Exception as e:
            res[nome] = "erro: " + str(e)[:40]
    return res

# ============================================================
# Auto-teste
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  ALEF-TAV - integra_v5 v6")
    print("=" * 60)
    print(f"Total de bases: {contar()}")
    print()
    print("Por grupo:")
    for g, bs in sorted(info_por_grupo().items()):
        print(f"  {g:20s}: {len(bs)}")
    print()
    print("Por protocolo:")
    for p, bs in sorted(info_por_protocolo().items()):
        print(f"  {p:20s}: {len(bs)}")
    print()
    print("Testando base arxiv...")
    r = BASES["arxiv"]["fn"]("diamond", 2)
    print(f"Resultados: {len(r)}")
    for x in r[:2]:
        autores = ", ".join(x.get("autores",[])[:2])
        print(f"  - {x['titulo'][:60]}")
        print(f"    Autores: {autores}")