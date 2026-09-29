# ============================================================
#   ALEF-TAV - PROVEDORES DE IA
# ============================================================
#   Projeto:   ALEF-TAV - Assistente Cientifico
#   Autor:     Jaderson Carvalho
#   Versao:    v1.0
#   Data:      29/09/2026
# ============================================================
#   NVIDIA NIM + Groq (fallback automatico)
# ============================================================

import os

try:
    import requests
    REQUESTS_OK = True
except:
    REQUESTS_OK = False

PROVEDORES = {
    # --------------------------------------------------------
    # NVIDIA NIM (5 modelos com 1 chave)
    # --------------------------------------------------------
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "modelos": [
            "moonshotai/kimi-k3",
            "nvidia/nemotron-3-super-120b-a12b",
            "mistralai/mistral-nemotron",
            "meta/llama-3.3-70b-instruct",
            "deepseek-ai/deepseek-r1",
        ],
        "env_key": "NVIDIA_API_KEY",
        "formato": "openai",
        "prioridade": 1,
        "extra_params": {"reasoning_effort": "max"},
    },
    # --------------------------------------------------------
    # Groq (3 modelos com 1 chave)
    # --------------------------------------------------------
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "modelos": [
            "llama-3.3-70b-versatile",
            "qwen/qwen3-32b",
            "llama-3.1-8b-instant",
        ],
        "env_key": "GROQ_API_KEY",
        "formato": "openai",
        "prioridade": 2,
    },
}

# ============================================================
# LEITURA DE CHAVES
# ============================================================
def _get_key(nome):
    # 1. chaves_config.py
    try:
        import chaves_config
        v = chaves_config.get(nome, "")
        if v: return v
    except: pass
    # 2. .env
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except: pass
    v = os.getenv(nome, "")
    if v: return v
    # 3. Streamlit secrets
    try:
        import streamlit as st
        return st.secrets.get(nome, "")
    except: pass
    return ""

def provedores_disponiveis():
    return [n for n, c in PROVEDORES.items() if _get_key(c["env_key"])]

# ============================================================
# CHAMADA
# ============================================================
def _openai(nome, prompt, modelo, temp, max_t):
    cfg = PROVEDORES[nome]
    payload = {
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": max_t,
    }
    if "extra_params" in cfg:
        payload.update(cfg["extra_params"])
    try:
        r = requests.post(
            cfg["url"],
            headers={
                "Authorization": "Bearer " + _get_key(cfg["env_key"]),
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=90,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except: pass
    return None

# ============================================================
# FUNCAO PRINCIPAL
# ============================================================
def gerar(prompt, temperatura=0.3, max_tokens=2000, provedor_forcado=None):
    if not REQUESTS_OK:
        return None, "requests nao instalado"

    ordem = sorted(PROVEDORES.keys(), key=lambda x: PROVEDORES[x]["prioridade"])
    if provedor_forcado:
        ordem = [provedor_forcado] + [p for p in ordem if p != provedor_forcado]

    for nome in ordem:
        cfg = PROVEDORES[nome]
        if not _get_key(cfg["env_key"]):
            continue
        for modelo in cfg["modelos"]:
            try:
                t = _openai(nome, prompt, modelo, temperatura, max_tokens)
                if t:
                    return t, nome + "/" + modelo
            except:
                continue
    return None, "todos falharam"

def testar_todos():
    res = {}
    for nome in sorted(PROVEDORES.keys(), key=lambda x: PROVEDORES[x]["prioridade"]):
        cfg = PROVEDORES[nome]
        if not _get_key(cfg["env_key"]):
            res[nome] = "sem chave"
            continue
        try:
            texto, _ = gerar("Diga OK", provedor_forcado=nome, max_tokens=10)
            res[nome] = "OK" if texto else "falhou"
        except:
            res[nome] = "erro"
    return res

# ============================================================
# TESTE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  ALEF-TAV - Provedores de IA")
    print("=" * 60)
    disp = provedores_disponiveis()
    print(f"Ativos: {len(disp)}/{len(PROVEDORES)}")
    for p in disp:
        print(f"  OK {p}")
    print()
    if disp:
        print("Testando...")
        for nome, status in testar_todos().items():
            print(f"  {nome}: {status}")
        print()
        print("Teste real:")
        texto, provedor = gerar("Escreva uma frase sobre grafeno.")
        if texto:
            print(f"[{provedor}]")
            print(texto[:400])
        else:
            print(f"Falhou: {provedor}")