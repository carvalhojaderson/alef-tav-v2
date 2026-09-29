"""
PONTE FERMILINK - Acelera simuladores pesados do SHIRYON
"""
import numpy as np

FERMILINK_DISPONIVEL = False
try:
    import fermilink
    FERMILINK_DISPONIVEL = True
    print("[BRIDGE] FermiLink carregado.")
except ImportError:
    print("[BRIDGE] FermiLink nao instalado. Usando analitico.")

def fl_dft(material="Si", n_kpoints=20):
    if not FERMILINK_DISPONIVEL: return None
    try:
        sim = fermilink.DFT(material=material)
        sim.set_kpoints(n_kpoints)
        r = sim.run()
        return {"simulador":"FermiLink DFT","bandgap_eV":r.bandgap,
                "k_points":r.k_path.tolist(),"fonte":"fermilink"}
    except Exception as e:
        print(f"[BRIDGE] Erro DFT: {e}"); return None

def fl_fdtd(geometria="opal", resolucao=50):
    if not FERMILINK_DISPONIVEL: return None
    try:
        sim = fermilink.FDTD(geometry=geometria, resolution=resolucao)
        r = sim.run()
        return {"simulador":"FermiLink FDTD","campo_E":r.E_field.tolist(),
                "freqs":r.freqs.tolist(),"fonte":"fermilink"}
    except Exception as e:
        print(f"[BRIDGE] Erro FDTD: {e}"); return None

def fl_md(material="diamond", n_atomos=216, T=300):
    if not FERMILINK_DISPONIVEL: return None
    try:
        sim = fermilink.MD(material=material, n_atoms=n_atomos, temperature=T)
        r = sim.run(steps=1000)
        return {"simulador":"FermiLink MD","energia_total":r.total_energy,
                "temperatura_final":r.temperature,"fonte":"fermilink"}
    except Exception as e:
        print(f"[BRIDGE] Erro MD: {e}"); return None

def fl_fem(geometria="traje", material="diamond", forca=1000):
    if not FERMILINK_DISPONIVEL: return None
    try:
        sim = fermilink.FEM(geometry=geometria, material=material)
        sim.apply_force(forca)
        r = sim.run()
        return {"simulador":"FermiLink FEM","tensao_max":r.max_stress,
                "deformacao":r.strain.tolist(),"fonte":"fermilink"}
    except Exception as e:
        print(f"[BRIDGE] Erro FEM: {e}"); return None

UPGRADE_MAP = {
    "dft": fl_dft,
    "md": fl_md,
    "estrutural": fl_fem,
}

if __name__ == "__main__":
    print("Bridge carregado.")
    print("FermiLink disponivel:", FERMILINK_DISPONIVEL)
    print("Simuladores aceleraveis:", list(UPGRADE_MAP.keys()))
