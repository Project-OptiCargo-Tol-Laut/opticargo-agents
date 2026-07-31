import os
import json
from groq import Groq
from opticargo_agents.orchestrator.state import OrchestratorState
from opticargo_agents.utils.canonicalizer import canonicalize_port

def intent_extraction_node(state: OrchestratorState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Intent Parser: GROQ_API_KEY tidak ditemukan.")
        return {"trace": state.trace + ["intent_extraction"]}
        
    prompt = f"""
    Anda adalah router AI untuk sistem logistik maritim OptiCargo.
    Analisis pertanyaan pengguna dan tentukan intent-nya.
    Teks: "{state.query}"
    
    Keluarkan format JSON dengan struktur persis seperti ini:
    {{
        "intent_type": "ROUTE_OPTIMIZATION atau REGULATION_QUERY atau GENERAL_CHAT atau OUT_OF_SCOPE",
        "origin_port": "nama kota asal (jika ada, jika tidak kosongkan)",
        "destination_port": "nama kota tujuan (jika ada, jika tidak kosongkan)",
        "commodity": "jenis barang/komoditas yang ditanyakan (jika ada, jika tidak kosongkan)",
        "min_capacity": angka_kapasitas_minimum_dalam_ton_atau_null
    }}
    
    Aturan penentuan intent_type:
    - ROUTE_OPTIMIZATION : Mencari muatan, rute kapal, backhaul, atau jadwal pelayaran.
    - REGULATION_QUERY   : Bertanya tentang hukum, aturan, regulasi, syarat pengiriman, atau dokumen maritim.
    - GENERAL_CHAT       : Sapaan atau pertanyaan ringan yang MASIH BERKAITAN dengan logistik/maritim/kapal/pelabuhan (contoh: "halo", "apa itu backhaul?", "cara kerja agen ini?").
    - OUT_OF_SCOPE       : Pertanyaan yang SAMA SEKALI TIDAK BERHUBUNGAN dengan logistik, maritim, kapal, muatan, atau pelabuhan (contoh: "cara tidak malas", "resep masakan", "berita bola", "cuaca hari ini").
    
    Catatan: Kapasitas contoh: "kapasitas minimal 1000 ton" -> "min_capacity": 1000. Jika tidak disebut -> "min_capacity": null.
    """
    
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI router. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        parsed = json.loads(response.choices[0].message.content)
        intent_type = parsed.get("intent_type", "GENERAL_CHAT")
        # Canonicalize nama pelabuhan ke nama baku yang ada di Neo4j
        origin      = canonicalize_port(parsed.get("origin_port", "")) or ""
        destination = canonicalize_port(parsed.get("destination_port", "")) or ""
        commodity = parsed.get("commodity", "")
        min_capacity = parsed.get("min_capacity")
        if min_capacity is not None:
            min_capacity = float(min_capacity)
        else:
            min_capacity = 0.0
        
        print(f"[Intent Parser] Type: {intent_type} | Cmdty: {commodity} | Org: {origin} | Dst: {destination} | MinCap: {min_capacity}")
        
        return {
            "intent_type": intent_type,
            "commodity": commodity,
            "origin_port": origin,
            "destination_port": destination,
            "min_capacity": min_capacity,
            "trace": state.trace + ["intent_extraction"]
        }
        
    except Exception as e:
        print(f"Intent Parser Error: {e}")
        return {"trace": state.trace + ["intent_extraction"]}