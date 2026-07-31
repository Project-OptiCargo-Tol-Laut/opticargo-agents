"""
utils/canonicalizer.py

Fuzzy Entity Canonicalization untuk nama pelabuhan OptiCargo.

Fungsi utama:
- canonicalize_port(user_input) → nama baku yang ada di Neo4j

Strategi (berlapis):
  1. Exact match          : langsung cocok (case-insensitive)
  2. Alias dictionary     : kamus alias yang diketahui pasti (typo umum, singkatan, nama kota)
  3. Fuzzy string match   : difflib SequenceMatcher untuk menangkap typo lainnya
     - Skor >= 0.80 → otomatis dikoreksi
     - Skor <  0.80 → kembalikan input asli (lebih aman daripada menebak salah)

Semua nama baku diambil langsung dari:
  opticargo-data/dataset/ports/ports.json
  (Sumber: SK Jaringan Tol Laut 2022 / Permenhub PM 29 Tahun 2018)
"""

from difflib import SequenceMatcher


# ─── Daftar nama baku lengkap dari ports.json ─────────────────────────────────
# Total: 69 pelabuhan resmi Tol Laut Indonesia
CANONICAL_PORTS: list[str] = [
    # Jawa
    "Tanjung Perak",
    "Tanjung Priok",
    # Sulawesi
    "Makassar",
    "Belang Belang",
    "Amurang",
    "Biaro",
    "Buhias",
    "Kahakitang",
    "Kakorotan",
    "Lirung",
    "Marore",
    "Melangoane",
    "Miangas",
    "Tagulandang",
    "Tahuna",
    "Bau Bau",
    "Wanci",
    # Sulawesi Barat
    # Sumatera
    "Teluk Bayur",
    "Bengkulu",
    "Pangkal Balam",
    "Mentawai",
    "Enggano",
    "Nias",
    # Kepulauan Riau & Bangka
    "Natuna",
    "Tarempa",
    "Tanjung Batu",
    "Serasan",
    "Midai",
    "Blinyu",
    "Tanjung Pandan",
    # Kalimantan
    "Nunukan",
    "P. Sebatik",
    "Sangatta",
    # Maluku Utara
    "Maba",
    "Morotai",
    "Obi",
    "Pulau Gebe",
    "Sanana",
    "Tidore",
    "Tobelo",
    # Maluku
    "Dobo",
    "Kisar (Wonreli)",
    "Moa",
    "Namlea",
    "Namrole",
    "Saumlaki",
    # NTT
    "Adonara (Terong)",
    "Kalabahi",
    "Larantuka",
    "Lewoleba",
    "Maumere",
    "Rote",
    "Sabu",
    "Waingapu",
    # NTB
    "Calabai (Dompu)",
    # Papua Barat
    "Fakfak",
    "Kaimana",
    "Manokwari",
    "Oransbari",
    "Wasior",
    # Papua
    "Agats",
    "Biak",
    "Merauke",
    "Nabire",
    "Sarmi",
    "Serui",
    "Teba",
    "Timika",
    "Waren",
    # Ternate — pelabuhan penting di data agen kita
    "Ternate",
]


# ─── Kamus alias statis (yang tidak bisa ditangkap fuzzy saja) ─────────────────
# Format: alias_lowercase → nama_baku_di_neo4j
ALIAS_DICT: dict[str, str] = {
    # ── Tanjung Perak / Surabaya ──────────────────────────────────────────────
    "tanjung perak":         "Tanjung Perak",
    "tj perak":              "Tanjung Perak",
    "tj. perak":             "Tanjung Perak",
    "perak":                 "Tanjung Perak",
    "surabaya":              "Tanjung Perak",
    "sby":                   "Tanjung Perak",
    "pelabuhan surabaya":    "Tanjung Perak",
    "pelabuhan sby":         "Tanjung Perak",
    "port surabaya":         "Tanjung Perak",

    # ── Tanjung Priok / Jakarta ───────────────────────────────────────────────
    "tanjung priok":         "Tanjung Priok",
    "tj priok":              "Tanjung Priok",
    "tj. priok":             "Tanjung Priok",
    "priok":                 "Tanjung Priok",
    "jakarta":               "Tanjung Priok",
    "jkt":                   "Tanjung Priok",
    "jakarta utara":         "Tanjung Priok",
    "pelabuhan jakarta":     "Tanjung Priok",
    "north jakarta port":    "Tanjung Priok",

    # ── Makassar ──────────────────────────────────────────────────────────────
    "makassar":              "Makassar",
    "makasar":               "Makassar",   # typo umum
    "ujung pandang":         "Makassar",   # nama lama
    "upg":                   "Makassar",   # kode IATA/ICAO
    "sulawesi selatan":      "Makassar",
    "sulsel":                "Makassar",
    "pelabuhan makassar":    "Makassar",

    # ── Ternate ───────────────────────────────────────────────────────────────
    "ternate":               "Ternate",
    "maluku utara":          "Ternate",
    "malut":                 "Ternate",
    "tnt":                   "Ternate",

    # ── Teluk Bayur / Padang ──────────────────────────────────────────────────
    "teluk bayur":           "Teluk Bayur",
    "padang":                "Teluk Bayur",
    "sumatera barat":        "Teluk Bayur",
    "sumbar":                "Teluk Bayur",
    "pdg":                   "Teluk Bayur",

    # ── Belang Belang / Mamuju ────────────────────────────────────────────────
    "belang belang":         "Belang Belang",
    "mamuju":                "Belang Belang",
    "sulawesi barat":        "Belang Belang",
    "sulbar":                "Belang Belang",

    # ── Pangkal Balam / Pangkalpinang ─────────────────────────────────────────
    "pangkal balam":         "Pangkal Balam",
    "pangkalpinang":         "Pangkal Balam",
    "bangka belitung":       "Pangkal Balam",
    "babel":                 "Pangkal Balam",

    # ── Bau Bau ───────────────────────────────────────────────────────────────
    "bau bau":               "Bau Bau",
    "baubau":                "Bau Bau",
    "sulawesi tenggara":     "Bau Bau",
    "sultra":                "Bau Bau",

    # ── Manokwari ─────────────────────────────────────────────────────────────
    "manokwari":             "Manokwari",
    "papua barat":           "Manokwari",

    # ── Merauke ───────────────────────────────────────────────────────────────
    "merauke":               "Merauke",
    "papua selatan":         "Merauke",

    # ── Ambon — tidak ada di dataset, arahkan ke Namlea/Saumlaki ──────────────
    "ambon":                 "Namlea",     # Ambon → Namlea (Maluku terdekat di data)
    "maluku":                "Namlea",

    # ── Singkatan Umum ────────────────────────────────────────────────────────
    "p. sebatik":            "P. Sebatik",
    "sebatik":               "P. Sebatik",
    "pulau sebatik":         "P. Sebatik",

    # ── Timika ────────────────────────────────────────────────────────────────
    "timika":                "Timika",
    "mimika":                "Timika",
    "papua tengah":          "Timika",

    # ── Biak ──────────────────────────────────────────────────────────────────
    "biak":                  "Biak",
    "biak numfor":           "Biak",
}


# ─── Fungsi Utama ──────────────────────────────────────────────────────────────

def canonicalize_port(user_input: str | None, threshold: float = 0.80) -> str | None:
    """
    Mengonversi input nama pelabuhan dari user ke nama baku yang ada di Neo4j.

    Args:
        user_input  : String nama pelabuhan dari user (bisa typo, singkatan, dll)
        threshold   : Skor minimum fuzzy match (0.0–1.0). Default 0.80.

    Returns:
        Nama baku jika ditemukan, atau user_input asli jika tidak ada padanan cukup dekat.
        Mengembalikan None jika user_input adalah None atau string kosong.
    """
    if not user_input or not user_input.strip():
        return None

    normalized = user_input.strip().lower()

    # ── Step 1: Exact match (case-insensitive) ────────────────────────────────
    for canonical in CANONICAL_PORTS:
        if canonical.lower() == normalized:
            return canonical

    # ── Step 2: Alias dictionary lookup ──────────────────────────────────────
    if normalized in ALIAS_DICT:
        result = ALIAS_DICT[normalized]
        print(f"[Canonicalizer] Alias: '{user_input}' → '{result}'")
        return result

    # ── Step 3: Fuzzy string matching ─────────────────────────────────────────
    best_match: str | None = None
    best_score: float = 0.0

    for canonical in CANONICAL_PORTS:
        score = SequenceMatcher(None, normalized, canonical.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = canonical

    if best_score >= threshold and best_match:
        print(f"[Canonicalizer] Fuzzy: '{user_input}' → '{best_match}' (skor={best_score:.2f})")
        return best_match

    # ── Step 4: Tidak ada padanan → kembalikan input asli ─────────────────────
    print(f"[Canonicalizer] Tidak dikenali: '{user_input}' (skor terbaik={best_score:.2f}). Tetap gunakan input asli.")
    return user_input
