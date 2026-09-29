# configurar_tudo.py - Configura TUDO automaticamente
# Rodar UMA VEZ: python configurar_tudo.py
import os
import sys
import base64
from pathlib import Path

# ============================================================
# ⚠️ COLE A CHAVE AQUI (troque pela NOVA após revogar)
# ============================================================
CHAVE_SCOPUS = "2fb9ddca481b2ef563b5f3fcb070dfde"  # ← TROQUE PELA NOVA!
EMAIL_INSTITUCIONAL = "seu.email@universidade.br"  # ← Troque pelo seu
# ============================================================

BASE_DIR = Path(__file__).parent

# ============================================================
# 1. CRIAR .env
# ============================================================
def criar_env():
    env_path = BASE_DIR / ".env"
    conteudo = f"""# ALEF-TAV - Chaves de API (configurado automaticamente)
# Gerado em: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}

# ============ ACADEMICAS (email institucional) ============
SCOPUS_API_KEY={CHAVE_SCOPUS}
WOS_API_KEY=
SPRINGER_API_KEY=
IEEE_API_KEY=
DIMENSIONS_API_KEY=

# ============ ACADEMICAS (gratuitas) ============
SEMANTIC_SCHOLAR_KEY=
CORE_API_KEY=
MATERIALS_PROJECT_KEY=
LENS_API_KEY=
NASA_ADS_KEY=
EPO_OPS_KEY=

# ============ GOVERNAMENTAIS ============
DATA_GOV_US_KEY=
PORTAL_TRANSPARENCIA_KEY=
NOAA_CDO_KEY=

# ============ EMAIL INSTITUCIONAL ============
INSTITUTIONAL_EMAIL={EMAIL_INSTITUCIONAL}
"""
    env_path.write_text(conteudo, encoding="utf-8")
    print(f"✅ .env criado em {env_path}")
    return True

# ============================================================
# 2. CRIAR .gitignore
# ============================================================
def criar_gitignore():
    gi_path = BASE_DIR / ".gitignore"
    linhas = [".env", "*.env", "**/secrets.txt", "__pycache__/", "*.pyc"]
    conteudo_atual = gi_path.read_text(encoding="utf-8") if gi_path.exists() else ""
    for l in linhas:
        if l not in conteudo_atual:
            conteudo_atual += "\n" + l
    gi_path.write_text(conteudo_atual.strip() + "\n", encoding="utf-8")
    print(f"✅ .gitignore atualizado")
    return True

# ============================================================
# 3. CRIAR config_api.py
# ============================================================
CONFIG_API = '''# config_api.py - Gerenciamento automatico de chaves
import os
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except: pass

CHAVES = {
    "SCOPUS":       os.getenv("SCOPUS_API_KEY", "").strip(),
    "WOS":          os.getenv("WOS_API_KEY", "").strip(),
    "SPRINGER":     os.getenv("SPRINGER_API_KEY", "").strip(),
    "IEEE":         os.getenv("IEEE_API_KEY", "").strip(),
    "DIMENSIONS":   os.getenv("DIMENSIONS_API_KEY", "").strip(),
    "SEMANTIC":     os.getenv("SEMANTIC_SCHOLAR_KEY", "").strip(),
    "CORE":         os.getenv("CORE_API_KEY", "").strip(),
    "MATERIALS":    os.getenv("MATERIALS_PROJECT_KEY", "").strip(),
    "LENS":         os.getenv("LENS_API_KEY", "").strip(),
    "NASA_ADS":     os.getenv("NASA_ADS_KEY", "").strip(),
    "EPO":          os.getenv("EPO_OPS_KEY", "").strip(),
    "DATA_GOV_US":  os.getenv("DATA_GOV_US_KEY", "").strip(),
    "TRANSPARENCIA":os.getenv("PORTAL_TRANSPARENCIA_KEY", "").strip(),
    "NOAA":         os.getenv("NOAA_CDO_KEY", "").strip(),
}

EMAIL = os.getenv("INSTITUTIONAL_EMAIL", "alef@tav.br")

def tem(chave):
    return bool(CHAVES.get(chave, ""))

def status():
    return {k: ("OK" if v else "vazio") for k, v in CHAVES.items()}

def resumo():
    ativas = sum(1 for v in CHAVES.values() if v)
    return len(CHAVES), ativas, len(CHAVES) - ativas

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
        "SCOPUS":       os.getenv("SCOPUS_API_KEY", "").strip(),
        "WOS":          os.getenv("WOS_API_KEY", "").strip(),
        "SPRINGER":     os.getenv("SPRINGER_API_KEY", "").strip(),
        "IEEE":         os.getenv("IEEE_API_KEY", "").strip(),
        "DIMENSIONS":   os.getenv("DIMENSIONS_API_KEY", "").strip(),
        "SEMANTIC":     os.getenv("SEMANTIC_SCHOLAR_KEY", "").strip(),
        "CORE":         os.getenv("CORE_API_KEY", "").strip(),
        "MATERIALS":    os.getenv("MATERIALS_PROJECT_KEY", "").strip(),
        "LENS":         os.getenv("LENS_API_KEY", "").strip(),
        "NASA_ADS":     os.getenv("NASA_ADS_KEY", "").strip(),
        "EPO":          os.getenv("EPO_OPS_KEY", "").strip(),
        "DATA_GOV_US":  os.getenv("DATA_GOV_US_KEY", "").strip(),
        "TRANSPARENCIA":os.getenv("PORTAL_TRANSPARENCIA_KEY", "").strip(),
        "NOAA":         os.getenv("NOAA_CDO_KEY", "").strip(),
    }
    EMAIL = os.getenv("INSTITUTIONAL_EMAIL", "alef@tav.br")
    return CHAVES
'''

def criar_config_api():
    p = BASE_DIR / "config_api.py"
    p.write_text(CONFIG_API, encoding="utf-8")
    print(f"✅ config_api.py criado em {p}")
    return True

# ============================================================
# 4. CRIAR modulo_scopus.py
# ============================================================
SCOPUS_MODULE = '''# modulo_scopus.py - Busca na Scopus
try:
    import config_api
except:
    config_api = None

def buscar_scopus(q, n=4):
    """Busca na Scopus via API institucional."""
    if not config_api or not config_api.tem("SCOPUS"):
        return []
    
    try:
        import requests
    except:
        return []
    
    h = config_api.headers("SCOPUS")
    try:
        r = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            params={"query": q, "count": n, "httpAccept": "application/json"},
            headers=h,
            timeout=10
        )
        if r.status_code != 200:
            return []
        dados = r.json()
        entradas = dados.get("search-results", {}).get("entry", [])
        out = []
        for e in entradas:
            titulo = e.get("dc:title", "")
            doi = e.get("prism:doi", "")
            link = "https://doi.org/" + doi if doi else e.get("prism:url", "")
            ano = 2024
            try: ano = int(e.get("prism:coverDate", "2024")[:4])
            except: pass
            autor = e.get("dc:creator", "")
            out.append({
                "titulo": titulo,
                "resumo": ("Autor: " + str(autor)) if autor else "",
                "link": link,
                "ano": ano,
                "fonte": "Scopus",
                "tipo": "artigo"
            })
        return out
    except Exception as e:
        return []

def testar():
    """Testa a chave Scopus."""
    r = buscar_scopus("diamond", 1)
    if r:
        return "OK - " + r[0].get("titulo", "")[:80]
    return "Falhou ou chave invalida"
'''

def criar_modulo_scopus():
    p = BASE_DIR / "modulo_scopus.py"
    p.write_text(SCOPUS_MODULE, encoding="utf-8")
    print(f"✅ modulo_scopus.py criado em {p}")
    return True

# ============================================================
# 5. TESTAR CHAVE
# ============================================================
def testar_chave():
    print("\n🔍 Testando chave Scopus...")
    try:
        import requests
    except ImportError:
        print("⚠️ requests nao instalado. Rode: pip install requests")
        return False
    
    h = {
        "X-ELS-APIKey": CHAVE_SCOPUS,
        "Accept": "application/json",
        "User-Agent": "ALEF-TAV/9.0 (mailto:" + EMAIL_INSTITUCIONAL + ")"
    }
    
    try:
        r = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            params={"query": "diamond", "count": 2, "httpAccept": "application/json"},
            headers=h,
            timeout=15
        )
        
        if r.status_code == 200:
            dados = r.json()
            entradas = dados.get("search-results", {}).get("entry", [])
            print(f"✅ CHAVE VALIDA! Retornou {len(entradas)} resultados")
            for e in entradas[:2]:
                print(f"   → {e.get('dc:title', '')[:80]}")
            return True
        elif r.status_code == 401:
            print(f"❌ CHAVE INVALIDA (401) - Revogue e gere nova")
            return False
        elif r.status_code == 403:
            print(f"❌ CHAVE SEM PERMISSAO (403) - Verifique se esta ativa")
            return False
        elif r.status_code == 429:
            print(f"⚠️ LIMITE ATINGIDO (429) - Chave funciona mas cota esgotada")
            return True
        else:
            print(f"❌ Erro {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisicao: {e}")
        return False

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  ALEF-TAV - Configuracao Automatica")
    print("=" * 60)
    print()
    print(f"Chave Scopus: {CHAVE_SCOPUS[:10]}...{CHAVE_SCOPUS[-4:]}")
    print(f"Email: {EMAIL_INSTITUCIONAL}")
    print()
    
    # 1. Testa a chave PRIMEIRO
    if not testar_chave():
        print("\n⚠️ A chave nao funcionou. Configure manualmente o .env")
        resp = input("\nDeseja continuar mesmo assim? (s/n): ").lower()
        if resp != "s":
            print("Cancelado.")
            return
    
    print("\n" + "=" * 60)
    print("  Criando arquivos...")
    print("=" * 60)
    
    # 2. Cria arquivos
    criar_env()
    criar_gitignore()
    criar_config_api()
    criar_modulo_scopus()
    
    print("\n" + "=" * 60)
    print("  ✅ CONFIGURACAO COMPLETA!")
    print("=" * 60)
    print()
    print("Proximos passos:")
    print("  1. Rode: streamlit run app.py")
    print("  2. Abra: http://localhost:8501")
    print("  3. Sidebar deve mostrar: APIs com chave: 1 / 14")
    print()
    print("⚠️  SEGURANCA:")
    print("  - Revogue a chave atual em: https://dev.elsevier.com/apikey/manage")
    print("  - Gere uma nova e edite o .env")
    print("  - NUNCA compartilhe a chave em chat publico")
    print()

if __name__ == "__main__":
    main()