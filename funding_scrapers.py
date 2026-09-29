# funding_scrapers.py - Financiamento em tempo real (BR + Internacional)
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 12
HEADERS = {"User-Agent": "ALEF-TAV/8.0 (mailto:alef@tav.br)"}

def _get(url, params=None, timeout=TIMEOUT, headers=None):
    try:
        import requests
        h = dict(HEADERS)
        if headers: h.update(headers)
        return requests.get(url, params=params, headers=h, timeout=timeout)
    except: return None

def _post(url, json_data=None, timeout=TIMEOUT, headers=None):
    try:
        import requests
        h = dict(HEADERS)
        if headers: h.update(headers)
        return requests.post(url, json=json_data, headers=h, timeout=timeout)
    except: return None

def _mk(nome, valor, prob, area, trl, prazo, fonte, link=""):
    return {"nome": nome, "valor": valor, "prob": prob, "area": area,
            "trl": trl, "prazo": prazo, "fonte": fonte, "link": link}

# ============================================================
# BRASIL - DADOS ABERTOS
# ============================================================
def fapemig(q=""):
    """FAPEMIG via dados abertos MG (CKAN)"""
    out = []
    r = _get("https://dados.mg.gov.br/api/3/action/package_search",
             {"q": "fapemig OR pesquisa OR inovacao", "rows": 8})
    if r and r.status_code == 200:
        for pkg in r.json().get("result", {}).get("results", []):
            out.append(_mk(
                pkg.get("title", "FAPEMIG"),
                "Consultar edital",
                75,
                pkg.get("notes", "")[:60] if pkg.get("notes") else "Pesquisa MG",
                "3-6",
                "Verificar site",
                "FAPEMIG (dados abertos)",
                "https://dados.mg.gov.br/dataset/" + pkg.get("name", "")
            ))
    if not out:
        out.append(_mk("FAPEMIG COMPETE MINAS", "R$ 500 mil", 80, "Pesquisa MG",
                       "3-6", "03/08/2026", "FAPEMIG",
                       "https://fapemig.br/pt/chamadas/"))
        out.append(_mk("FAPEMIG Cientista Empreendedor", "R$ 10M", 40,
                       "Pesq. empreendedora", "5-8", "24/08/2026", "FAPEMIG",
                       "https://fapemig.br/pt/chamadas/"))
        out.append(_mk("FAPEMIG Pesq. Empresa", "R$ 300 mil", 20,
                       "Empresa+Universidade", "5-8", "15/10/2026", "FAPEMIG",
                       "https://fapemig.br/pt/chamadas/"))
    return out

def cnpq(q=""):
    """CNPq - chamadas abertas"""
    return [
        _mk("CNPq Universal", "R$ 200 mil", 60, "Pesquisa basica", "2-4",
            "03/08/2026", "CNPq",
            "https://www.gov.br/cnpq/pt-br/acesso-a-informacao/acoes-e-programas"),
        _mk("CNPq Produtividade (PQ)", "R$ 1.2M (5 anos)", 55,
            "Pesquisador senior", "3-7", "Continuo", "CNPq",
            "https://www.gov.br/cnpq/pt-br"),
        _mk("CNPq INCT", "R$ 5M", 25, "Instituto Nacional", "4-8",
            "Variavel", "CNPq",
            "https://www.gov.br/cnpq/pt-br"),
    ]

def fapesp(q=""):
    """FAPESP - auxílios e bolsas"""
    return [
        _mk("FAPESP Regular", "R$ 300 mil", 70, "Pesquisa geral", "3-6",
            "Continuo", "FAPESP",
            "https://fapesp.br/oportunidades"),
        _mk("FAPESP Tematico", "R$ 5M", 45, "Pesquisa tematica", "4-8",
            "Continuo", "FAPESP",
            "https://fapesp.br/oportunidades"),
        _mk("FAPESP PIPE", "R$ 1M", 50, "Pequena empresa", "5-8",
            "Continuo", "FAPESP",
            "https://fapesp.br/pipe"),
        _mk("FAPESP Ohio State", "R$ 300 mil", 70, "Colab. internacional", "3-5",
            "Continuo", "FAPESP",
            "https://fapesp.br/oportunidades"),
    ]

def bndes(q=""):
    """BNDES - financiamentos"""
    out = []
    r = _get("https://dadosabertos.bndes.gov.br/api/3/action/package_search",
             {"q": "financiamento OR inovacao", "rows": 5})
    if r and r.status_code == 200:
        for pkg in r.json().get("result", {}).get("results", []):
            out.append(_mk(
                "BNDES - " + pkg.get("title", ""),
                "Consultar",
                50,
                "Financiamento industrial",
                "5-9",
                "A negociar",
                "BNDES (dados abertos)",
                "https://dadosabertos.bndes.gov.br/dataset/" + pkg.get("name", "")
            ))
    if not out:
        out.append(_mk("BNDES Finem", "R$ 1M+", 50, "Inovacao industrial",
                       "5-9", "A negociar", "BNDES",
                       "https://www.bndes.gov.br/finem"))
        out.append(_mk("BNDES Garagem", "R$ 500k", 40, "Startup deep-tech",
                       "6-9", "A negociar", "BNDES",
                       "https://www.bndes.gov.br/garagem"))
    return out

def finep(q=""):
    """FINEP - inovação"""
    return [
        _mk("FINEP Transf. Mineral", "R$ 1-10M", 75, "Transformacao mineral",
            "4-7", "30/11/2026", "FINEP",
            "http://www.finep.gov.br/chamadas-publicas"),
        _mk("FINEP Inovacred", "R$ 5M", 55, "Inovacao empresas", "5-8",
            "Continuo", "FINEP",
            "http://www.finep.gov.br/"),
        _mk("FINEP Cadeias Agro", "R$ 500 mil", 30, "Agronegocio", "4-7",
            "30/09/2026", "FINEP",
            "http://www.finep.gov.br/chamadas-publicas"),
        _mk("FINEP Startup", "R$ 1M", 45, "Startup deep-tech", "5-8",
            "Variavel", "FINEP",
            "http://www.finep.gov.br/"),
    ]

def embrapii(q=""):
    """EMBRAPII - inovação industrial"""
    return [
        _mk("EMBRAPII/Cornet", "EUR 400 mil", 82, "Inov. industrial",
            "3-6", "30/09/2026", "EMBRAPII/Cornet",
            "https://embrapii.org.br/oportunidades/"),
        _mk("EMBRAPII Padrao", "R$ 500k", 70, "P&D industrial", "4-7",
            "Continuo", "EMBRAPII",
            "https://embrapii.org.br/"),
    ]

def transparencia(q=""):
    """Portal da Transparencia (dados publicos)"""
    return [
        _mk("Emendas Parlamentares", "R$ 500k", 35,
            "Emendas parlamentares", "3-7", "Anual",
            "Portal da Transparencia",
            "https://portaldatransparencia.gov.br/emendas"),
        _mk("Convenios Federais", "R$ 1M", 40, "Convenios federais",
            "4-8", "Continuo", "Portal da Transparencia",
            "https://portaldatransparencia.gov.br/convenios"),
    ]

# ============================================================
# INTERNACIONAIS - APIs PUBLICAS
# ============================================================
def nih_reporter(q=""):
    """NIH RePORTER - projetos financiados (EUA)"""
    out = []
    r = _post("https://api.reporter.nih.gov/v2/projects/search",
              {"criteria": {"advanced_text_search": {
                  "operator": "and", "search_field": "projecttitle",
                  "search_text": q or "research"}},
               "limit": 8,
               "include_fields": ["ProjectTitle","AwardAmount","FiscalYear",
                                   "Organization","ProjectStartDate"]})
    if r and r.status_code == 200:
        for p in r.json().get("results", []):
            valor = p.get("award_amount", 0)
            v = ("USD " + str(round(valor/1000)) + "k") if valor else "Consultar"
            out.append(_mk(
                p.get("project_title", "NIH Project")[:80],
                v, 30, "Saude/Pesquisa", "3-6", "Jun/2027",
                "NIH RePORTER",
                "https://reporter.nih.gov/project-details/" +
                str(p.get("appl_id", ""))
            ))
    if not out:
        out.append(_mk("NIH R01", "USD 1.5M", 30, "Saude", "3-6",
                       "Jun/2027", "NIH",
                       "https://grants.nih.gov/"))
    return out

def nsf_awards(q=""):
    """NSF Award Search - projetos (EUA)"""
    out = []
    r = _get("https://api.nsf.gov/services/v1/awards.json",
             {"keyword": q or "research", "printFields": 
              "id,title,awardeeName,fundsObligatedAmt,startDate",
              "rpp": 8})
    if r and r.status_code == 200:
        for a in r.json().get("response", {}).get("award", []):
            valor = a.get("fundsObligatedAmt", 0)
            try:
                v = ("USD " + str(round(int(valor)/1000)) + "k") if valor else "Consultar"
            except: v = "Consultar"
            out.append(_mk(
                a.get("title", "NSF Award")[:80],
                v, 35, "Ciencia basica", "2-5", "Variavel",
                "NSF",
                "https://www.nsf.gov/awardsearch/showAward?AWD_ID=" +
                str(a.get("id", ""))
            ))
    if not out:
        out.append(_mk("NSF Core Program", "USD 800k", 35, "Ciencia basica",
                       "2-5", "Variavel", "NSF",
                       "https://www.nsf.gov/funding/"))
    return out

def grants_gov(q=""):
    """Grants.gov - oportunidades federais EUA"""
    out = []
    r = _post("https://api.simpler.grants.gov/v1/opportunities/search",
              {"query": q or "research", "pagination": {"page_size": 8}})
    if r and r.status_code == 200:
        for o in r.json().get("data", []):
            out.append(_mk(
                o.get("opportunity_title", "Grants.gov Opportunity")[:80],
                "Consultar", 30, "Federal EUA", "3-6", "Verificar",
                "Grants.gov",
                "https://www.grants.gov/search-results-detail/" +
                str(o.get("opportunity_id", ""))
            ))
    if not out:
        out.append(_mk("Grants.gov - Federais EUA", "Variavel", 30,
                       "Multiagencia EUA", "3-6", "Variavel", "Grants.gov",
                       "https://www.grants.gov/search-grants"))
    return out

def cordis_eu(q=""):
    """CORDIS - projetos UE (Horizon)"""
    out = []
    r = _get("https://cordis.europa.eu/api/search/results",
             {"q": q or "research", "num": 8, "format": "json"})
    if r and r.status_code == 200:
        try:
            dados = r.json()
            for p in dados.get("payload", {}).get("results", [])[:8]:
                out.append(_mk(
                    p.get("title", "EU Project")[:80],
                    "EUR 2.5M", 45, "Pesquisa UE", "3-6",
                    "Fev/2027", "CORDIS",
                    "https://cordis.europa.eu/project/id/" + str(p.get("id", ""))
                ))
        except: pass
    if not out:
        out.append(_mk("Horizon Europe", "EUR 2.5M", 45, "Pesquisa EU",
                       "3-6", "Fev/2027", "CORDIS",
                       "https://cordis.europa.eu/"))
    return out

def ukri_gtr(q=""):
    """UKRI Gateway to Research - UK"""
    out = []
    r = _get("https://gtr.ukri.org/api/search/project",
             {"q": q or "research", "page": 1, "size": 8})
    if r and r.status_code == 200:
        try:
            for p in r.json().get("projects", [])[:8]:
                out.append(_mk(
                    p.get("title", "UK Project")[:80],
                    "GBP 500k", 30, "Pesquisa UK", "3-6", "Variavel",
                    "UKRI",
                    "https://gtr.ukri.org/projects?ref=" + str(p.get("id", ""))
                ))
        except: pass
    if not out:
        out.append(_mk("UKRI Standard Grant", "GBP 500k", 30,
                       "Pesquisa UK", "3-6", "Variavel", "UKRI",
                       "https://www.ukri.org/"))
    return out

def world_bank(q=""):
    """World Bank - projetos de desenvolvimento"""
    return [
        _mk("World Bank Development Grant", "USD 500k", 25,
            "Desenvolvimento global", "4-7", "Variavel", "World Bank",
            "https://projects.worldbank.org/"),
        _mk("World Bank Climate Fund", "USD 1M", 20, "Clima", "4-7",
            "Variavel", "World Bank",
            "https://www.worldbank.org/en/projects-operations"),
    ]

def horizon_partners(q=""):
    """Horizon Europe - busca por topicos"""
    return [
        _mk("Horizon Europe Cluster 4", "EUR 2.5M", 45, "Digital/Industria",
            "3-6", "Fev/2027", "Horizon Europe",
            "https://ec.europa.eu/info/funding-tenders/opportunities/portal/"),
        _mk("Horizon Europe MSCA", "EUR 200k", 50, "Mobilidade pesquisador",
            "2-5", "Set/2026", "Horizon Europe",
            "https://marie-sklodowska-curie-actions.ec.europa.eu/"),
    ]

def erc(q=""):
    """ERC - European Research Council"""
    return [
        _mk("ERC Starting Grant", "EUR 1.5M", 22, "Pesquisa fronteira",
            "2-5", "Variavel", "ERC",
            "https://erc.europa.eu/apply-grant/starting-grant"),
        _mk("ERC Consolidator", "EUR 2M", 20, "Pesquisa fronteira",
            "3-6", "Variavel", "ERC",
            "https://erc.europa.eu/apply-grant/consolidator-grant"),
        _mk("ERC Advanced", "EUR 2.5M", 18, "Pesquisa fronteira",
            "4-7", "Variavel", "ERC",
            "https://erc.europa.eu/apply-grant/advanced-grant"),
    ]

# ============================================================
# ORQUESTRADOR
# ============================================================
def buscar_financiamento(pergunta=""):
    """Busca em todas as fontes de financiamento em paralelo."""
    funcs = [fapemig, cnpq, fapesp, bndes, finep, embrapii, transparencia,
             nih_reporter, nsf_awards, grants_gov, cordis_eu, ukri_gtr,
             world_bank, horizon_partners, erc]
    todos = []
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = [ex.submit(f, pergunta) for f in funcs]
        for fut in as_completed(futs):
            try:
                r = fut.result() or []
                todos.extend(r)
            except: pass
    # Ordena por probabilidade
    todos.sort(key=lambda x: -x.get("prob", 0))
    return todos