# config_api.py - Gerenciamento de chaves (todas as APIs)
import os

# Fallbacks embutidos (usados se .env nao existir)
_FALLBACK = {
    "SCOPUS":       "2fb9ddca481b2ef563b5f3fcb070dfde",
    "WOS":          "",
    "SPRINGER":     "",
    "IEEE":         "",
    "DIMENSIONS":   "",
    "SEMANTIC":     "",
    "CORE":         "",
    "MATERIALS":    "",
    "LENS":         "",
    "NASA_ADS":     "",
    "EPO":          "",
    "DATA_GOV_US":  "",
    "TRANSPARENCIA":"",
    "NOAA":         "",
}
_FALLBACK_EMAIL = "jadersoncarvalho@alunos.utfpr.edu.br"

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except: pass

def _ler_env(nome, fallback=""):
    return os.getenv(nome, fallback).strip()

CHAVES = {
    "SCOPUS":       _ler_env("SCOPUS_API_KEY", _FALLBACK["SCOPUS"]),
    "WOS":          _ler_env("WOS_API_KEY", _FALLBACK["WOS"]),
    "SPRINGER":     _ler_env("SPRINGER_API_KEY", _FALLBACK["SPRINGER"]),
    "IEEE":         _ler_env("IEEE_API_KEY", _FALLBACK["IEEE"]),
    "DIMENSIONS":   _ler_env("DIMENSIONS_API_KEY", _FALLBACK["DIMENSIONS"]),
    "SEMANTIC":     _ler_env("SEMANTIC_SCHOLAR_KEY", _FALLBACK["SEMANTIC"]),
    "CORE":         _ler_env("CORE_API_KEY", _FALLBACK["CORE"]),
    "MATERIALS":    _ler_env("MATERIALS_PROJECT_KEY", _FALLBACK["MATERIALS"]),
    "LENS":         _ler_env("LENS_API_KEY", _FALLBACK["LENS"]),
    "NASA_ADS":     _ler_env("NASA_ADS_KEY", _FALLBACK["NASA_ADS"]),
    "EPO":          _ler_env("EPO_OPS_KEY", _FALLBACK["EPO"]),
    "DATA_GOV_US":  _ler_env("DATA_GOV_US_KEY", _FALLBACK["DATA_GOV_US"]),
    "TRANSPARENCIA":_ler_env("PORTAL_TRANSPARENCIA_KEY", _FALLBACK["TRANSPARENCIA"]),
    "NOAA":         _ler_env("NOAA_CDO_KEY", _FALLBACK["NOAA"]),
}
EMAIL = _ler_env("INSTITUTIONAL_EMAIL", _FALLBACK_EMAIL)

def tem(chave):
    return bool(CHAVES.get(chave, ""))

def resumo():
    ativas = sum(1 for v in CHAVES.values() if v)
    return len(CHAVES), ativas, len(CHAVES) - ativas

def status():
    return {k: ("OK" if v else "vazio") for k, v in CHAVES.items()}

def headers(chave):
    h = {"User-Agent": "ALEF-TAV/9.0 (mailto:" + EMAIL + ")"}
    if chave == "SCOPUS" and CHAVES["SCOPUS"]:
        h["X-ELS-APIKey"] = CHAVES["SCOPUS"]
        h["Accept"] = "application/json"
    elif chave == "WOS" and CHAVES["WOS"]:
        h["X-ApiKey"] = CHAVES["WOS"]
    elif chave == "SPRINGER" and CHAVES["SPRINGER"]:
        h["X-APIKey"] = CHAVES["SPRINGER"]
    elif chave == "IEEE" and CHAVES["IEEE"]:
        h["X-API-Key"] = CHAVES["IEEE"]
    elif chave == "SEMANTIC" and CHAVES["SEMANTIC"]:
        h["x-api-key"] = CHAVES["SEMANTIC"]
    elif chave == "CORE" and CHAVES["CORE"]:
        h["Authorization"] = "Bearer " + CHAVES["CORE"]
    elif chave == "MATERIALS" and CHAVES["MATERIALS"]:
        h["X-API-KEY"] = CHAVES["MATERIALS"]
    elif chave == "LENS" and CHAVES["LENS"]:
        h["Authorization"] = "Bearer " + CHAVES["LENS"]
    elif chave == "NASA_ADS" and CHAVES["NASA_ADS"]:
        h["Authorization"] = "Bearer " + CHAVES["NASA_ADS"]
    elif chave == "EPO" and CHAVES["EPO"]:
        h["Authorization"] = "Bearer " + CHAVES["EPO"]
    elif chave == "DATA_GOV_US" and CHAVES["DATA_GOV_US"]:
        h["X-Api-Key"] = CHAVES["DATA_GOV_US"]
    elif chave == "TRANSPARENCIA" and CHAVES["TRANSPARENCIA"]:
        h["chave-api-dados"] = CHAVES["TRANSPARENCIA"]
    elif chave == "NOAA" and CHAVES["NOAA"]:
        h["token"] = CHAVES["NOAA"]
    return h

def recarregar():
    global CHAVES, EMAIL
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except: pass
    CHAVES = {
        "SCOPUS":       _ler_env("SCOPUS_API_KEY", _FALLBACK["SCOPUS"]),
        "WOS":          _ler_env("WOS_API_KEY", _FALLBACK["WOS"]),
        "SPRINGER":     _ler_env("SPRINGER_API_KEY", _FALLBACK["SPRINGER"]),
        "IEEE":         _ler_env("IEEE_API_KEY", _FALLBACK["IEEE"]),
        "DIMENSIONS":   _ler_env("DIMENSIONS_API_KEY", _FALLBACK["DIMENSIONS"]),
        "SEMANTIC":     _ler_env("SEMANTIC_SCHOLAR_KEY", _FALLBACK["SEMANTIC"]),
        "CORE":         _ler_env("CORE_API_KEY", _FALLBACK["CORE"]),
        "MATERIALS":    _ler_env("MATERIALS_PROJECT_KEY", _FALLBACK["MATERIALS"]),
        "LENS":         _ler_env("LENS_API_KEY", _FALLBACK["LENS"]),
        "NASA_ADS":     _ler_env("NASA_ADS_KEY", _FALLBACK["NASA_ADS"]),
        "EPO":          _ler_env("EPO_OPS_KEY", _FALLBACK["EPO"]),
        "DATA_GOV_US":  _ler_env("DATA_GOV_US_KEY", _FALLBACK["DATA_GOV_US"]),
        "TRANSPARENCIA":_ler_env("PORTAL_TRANSPARENCIA_KEY", _FALLBACK["TRANSPARENCIA"]),
        "NOAA":         _ler_env("NOAA_CDO_KEY", _FALLBACK["NOAA"]),
    }
    EMAIL = _ler_env("INSTITUTIONAL_EMAIL", _FALLBACK_EMAIL)
    return CHAVES

def testar_scopus():
    if not CHAVES["SCOPUS"]:
        return "Chave nao configurada"
    try:
        import requests
        r = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            params={"query": "diamond", "count": 1, "httpAccept": "application/json"},
            headers=headers("SCOPUS"),
            timeout=15
        )
        if r.status_code == 200:
            return "OK"
        elif r.status_code == 401:
            return "ERRO 401"
        elif r.status_code == 403:
            return "ERRO 403"
        elif r.status_code == 429:
            return "AVISO 429"
        return f"ERRO {r.status_code}"
    except Exception as e:
        return f"ERRO: {str(e)[:80]}"

if __name__ == "__main__":
    print("=" * 60)
    print("  ALEF-TAV - Teste de chaves")
    print("=" * 60)
    total, ativas, inativas = resumo()
    print(f"Total de chaves: {total}")
    print(f"Ativas:          {ativas}")
    print(f"Inativas:        {inativas}")
    print(f"Email:           {EMAIL}")
    print()
    print("Status por chave:")
    for k, v in status().items():
        icon = "✅" if v == "OK" else "❌"
        print(f"  {icon} {k:15s} — {v}")
    print()
    print("Testando Scopus...")
    print(testar_scopus())