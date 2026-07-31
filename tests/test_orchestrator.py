import asyncio
import json
import sys
import os

# Konfigurasi PATH Otomatis (Mencegah user mengatur PYTHONPATH manual)
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_src = os.path.abspath(os.path.join(current_dir, "..", "src"))
shared_src = os.path.abspath(os.path.join(current_dir, "..", "..", "opticargo-shared", "src"))
rag_src = os.path.abspath(os.path.join(current_dir, "..", "..", "opticargo-rag-pipeline", "src"))
kg_src = os.path.abspath(os.path.join(current_dir, "..", "..", "opticargo-knowledge-graph", "src"))

for p in [agents_src, shared_src, rag_src, kg_src]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dotenv import load_dotenv
load_dotenv()

from opticargo_agents.orchestrator.graph import build_graph
from opticargo_agents.orchestrator.state import OrchestratorState

def test_run_agents():
    # 1. Inisialisasi graph
    agent_graph = build_graph()
    
    import uuid
    print("\n" + "="*50)
    print("🤖 OPTICARGO AI - INTERACTIVE TEST")
    print("="*50)
    print("Ketik 'exit' atau 'keluar' untuk berhenti.\n")

    while True:
        # Meminta input langsung dari user di terminal
        user_input = input("👤 Anda: ")
        
        if user_input.strip().lower() in ['exit', 'quit', 'keluar']:
            print("Sampai jumpa!")
            break
            
        if not user_input.strip():
            continue

        print("\n[Menjalankan Alur LangGraph OptiCargo AI...]")
        initial_state = OrchestratorState(
            request_id=uuid.uuid4(),
            query=user_input,
            request_type="backhaul_discovery",
            trace=[]
        )
        
        # Eksekusi graph
        final_state = agent_graph.invoke(initial_state)
        
        print("\n=== HASIL EKSEKUSI ===")
        print(f"Alur Agen (Trace): {' -> '.join(final_state['trace'])}")
        
        rec = final_state.get('final_recommendation')
        if rec:
            if hasattr(rec.final_recommendation.content, "summary"):
                print(f"\n🤖 Rekomendasi AI:\n{rec.final_recommendation.content.summary}")
            else:
                print(f"\n🤖 Rekomendasi AI:\n{rec.final_recommendation.content}")
        else:
            print("Gagal mendapatkan rekomendasi.")
        
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    test_run_agents()
