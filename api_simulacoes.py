# ============================================================
#   ALEF-TAV - API DE SIMULACOES (FastAPI)
# ============================================================
#   Expoe os 113 simuladores do universal.py como API HTTP
#   Endpoints:
#     GET  /                     -> health
#     GET  /simuladores          -> lista todos
#     POST /simular/{sim_id}     -> executa 1
#     POST /simular_lote         -> executa varios
#     POST /executar_relevantes  -> IA escolhe + executa
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import base64
import io
import json

# Importa o motor de simulacoes
try:
    import universal as u
    SIMS_OK = True
except Exception as e:
    SIMS_OK = False
    SIMS_ERRO = str(e)

app = FastAPI(title="ALEF-TAV Simulacoes API", version="1.0")

# CORS (permite ser chamado de qualquer frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MODELOS
# ============================================================
class SimRequest(BaseModel):
    pergunta: str
    parametros: Optional[Dict[str, Any]] = {}

class LoteRequest(BaseModel):
    pergunta: str
    sim_ids: List[str]
    parametros: Optional[Dict[str, Any]] = {}

class RelevantesRequest(BaseModel):
    pergunta: str
    max_sims: Optional[int] = 5

# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/")
def raiz():
    return {
        "status": "online",
        "servico": "ALEF-TAV Simulacoes API",
        "sims_disponiveis": len(u.SIMULADORES) if SIMS_OK else 0,
    }

@app.get("/simuladores")
def listar_simuladores():
    """Lista todos os 113 simuladores disponiveis."""
    if not SIMS_OK:
        raise HTTPException(500, f"universal.py nao carregou: {SIMS_ERRO}")
    return {
        "total": len(u.SIMULADORES),
        "simuladores": list(u.SIMULADORES.keys()),
    }

@app.post("/simular/{sim_id}")
def simular(sim_id: str, req: SimRequest):
    """Executa um simulador especifico."""
    if not SIMS_OK:
        raise HTTPException(500, "motor nao disponivel")
    if sim_id not in u.SIMULADORES:
        raise HTTPException(404, f"Simulador '{sim_id}' nao encontrado")

    try:
        resultado = u.SIMULADORES[sim_id](req.pergunta, req.parametros)
        return {
            "sucesso": True,
            "sim_id": sim_id,
            "resultado": resultado,
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao executar {sim_id}: {e}")

@app.post("/simular_lote")
def simular_lote(req: LoteRequest):
    """Executa varios simuladores de uma vez."""
    if not SIMS_OK:
        raise HTTPException(500, "motor nao disponivel")

    resultados = {}
    for sim_id in req.sim_ids:
        if sim_id not in u.SIMULADORES:
            resultados[sim_id] = {"erro": "nao encontrado"}
            continue
        try:
            r = u.SIMULADORES[sim_id](req.pergunta, req.parametros)
            resultados[sim_id] = {
                "simulador": r.get("simulador", sim_id),
                "resultado": r,
            }
        except Exception as e:
            resultados[sim_id] = {"erro": str(e)}

    return {
        "sucesso": True,
        "total": len(resultados),
        "resultados": resultados,
    }

@app.post("/executar_relevantes")
def executar_relevantes(req: RelevantesRequest):
    """Escolhe automaticamente os simuladores relevantes e executa."""
    if not SIMS_OK:
        raise HTTPException(500, "motor nao disponivel")

    # Logica de relevancia (mesma do app.py)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    ss = set(u.SIMULADORES.keys())
    txt = req.pergunta.lower()

    prefs = []
    if any(k in txt for k in ["theor", "quant", "relat", "quantic"]):
        prefs += [s for s in ss if "quant" in s or "relat" in s
                  or "algebra" in s or "schrodinger" in s]
    if any(k in txt for k in ["experiment", "measur", "estat"]):
        prefs += [s for s in ss if "estat" in s or "cinet" in s
                  or "monte" in s]
    if any(k in txt for k in ["simulat", "dft", "md", "molec"]):
        prefs += [s for s in ss if "dft" in s or "md" in s
                  or "solid" in s or "molec" in s]
    if any(k in txt for k in ["termo", "energia", "thermo"]):
        prefs += [s for s in ss if "termo" in s or "energ" in s]
    if any(k in txt for k in ["eletro", "circuito", "sensor"]):
        prefs += [s for s in ss if "eletro" in s or "circuito" in s]

    if not prefs:
        prefs = list(ss)[:req.max_sims]

    sims_ids = list(set(prefs))[:req.max_sims]

    resultados = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(u.SIMULADORES[sid], req.pergunta, {}): sid
                for sid in sims_ids if sid in u.SIMULADORES}
        for fut in as_completed(futs):
            sid = futs[fut]
            try:
                resultados[sid] = fut.result()
            except Exception as e:
                resultados[sid] = {"erro": str(e)}

    return {
        "sucesso": True,
        "pergunta": req.pergunta,
        "total": len(resultados),
        "executados": sims_ids,
        "resultados": resultados,
    }

@app.post("/grafico/{sim_id}")
def gerar_grafico(sim_id: str, req: SimRequest):
    """Gera grafico da simulacao em PNG base64."""
    if not SIMS_OK:
        raise HTTPException(500, "motor nao disponivel")

    try:
        r = u.SIMULADORES[sim_id](req.pergunta, req.parametros)
    except Exception as e:
        raise HTTPException(500, f"Erro: {e}")

    # Tenta gerar grafico com matplotlib
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 4))

        # Escolhe grafico conforme tipo de simulacao
        if "bandgap_eV" in r:
            bg = r["bandgap_eV"]
            x = list(range(10))
            y = [bg * (1 + 0.1 * (i - 5)) for i in x]
            ax.plot(x, y, "o-", label=f"Bandgap {bg} eV")
            ax.set_title("Estrutura de Bandas")
            ax.set_xlabel("k-point")
            ax.set_ylabel("Energia (eV)")

        elif "media" in r:
            import numpy as np
            dados = np.random.normal(r["media"], r.get("desvio", 1), 1000)
            ax.hist(dados, bins=30, alpha=0.7)
            ax.set_title("Distribuicao Monte Carlo")
            ax.set_xlabel("Valor")

        elif "gamma" in r:
            g = r["gamma"]
            ax.bar(["γ"], [g], color="purple")
            ax.set_title(f"Fator γ = {g}")
            ax.axhline(y=1, color="red", linestyle="--", label="Clássico")

        elif "taxa" in str(r).lower() or "k_T" in r:
            k = r.get("k_T", r.get("taxa", 1))
            ax.bar(["k(T)"], [k], color="orange")
            ax.set_title(f"Constante de Taxa = {k:.3e}")

        else:
            # Grafico generico de valores numericos
            vals = [(k, v) for k, v in r.items()
                    if isinstance(v, (int, float))][:6]
            if vals:
                k_nomes = [v[0] for v in vals]
                v_vals = [v[1] for v in vals]
                ax.barh(k_nomes, v_vals)
            else:
                ax.text(0.5, 0.5, "Sem dados numericos",
                        ha="center", va="center")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=80)
        plt.close(fig)
        buf.seek(0)

        img_base64 = base64.b64encode(buf.read()).decode("utf-8")

        return {
            "sucesso": True,
            "sim_id": sim_id,
            "imagem_base64": img_base64,
            "formato": "png",
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao gerar grafico: {e}")

# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "sims": len(u.SIMULADORES) if SIMS_OK else 0,
        "motor": "OK" if SIMS_OK else "FALHOU",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)