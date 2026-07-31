import os
import json
from groq import Groq
from opticargo_agents.orchestrator.state import OrchestratorState

def intent_extraction_node(state: OrchestratorState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Intent Parser: GROQ_API_KEY tidak ditemukan.")
        return {"trace": state.trace + ["intent_extraction"]}
        
    prompt = f"""
    Analisis pertanyaan pengguna berikut dan ekstrak informasinya.
    Teks: "{state.query}"
    
    Keluarkan format JSON dengan struktur persis seperti ini:
    {{
        "intent_type": "ROUTE_OPTIMIZATION atau REGULATION_QUERY atau GENERAL_CHAT",
        "origin_port": "nama kota asal (jika ada, jika tidak kosongkan)",
        "destination_port": "nama kota tujuan (jika ada, jika tidak kosongkan)",
        "commodity": "jenis barang/komoditas yang ditanyakan (jika ada, jika tidak kosongkan)",
        "min_capacity": angka_kapasitas_minimum_dalam_ton_atau_null
    }}
    Catatan: Jika user bertanya tentang hukum, aturan, atau syarat pengiriman, pilih REGULATION_QUERY. Jika mencari muatan atau rute kapal, pilih ROUTE_OPTIMIZATION.
    Contoh: "kapasitas minimal 1000 ton" -> "min_capacity": 1000. Jika tidak disebut -> "min_capacity": null.
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
        origin = parsed.get("origin_port", "")
        destination = parsed.get("destination_port", "")
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