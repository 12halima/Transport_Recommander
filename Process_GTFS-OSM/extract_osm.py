import os
import subprocess
import pandas as pd
from pyrosm import OSM

# ====== CHEMINS ======
OSM_PBF = r"C:\Users\hp\Desktop\MyDrive\OSM\spain.osm.pbf"
CSV_BBOX = r"C:\Users\hp\Desktop\MyDrive\GTFS_CLEAN\gtfs_bounding_boxes.csv"
OUTPUT_DIR = r"C:\Users\hp\Desktop\MyDrive\OSM_BY_CITY"
TMP_DIR = r"C:\Users\hp\Desktop\MyDrive\OSM_BY_CITY_TMP"
OSMCONVERT_PATH = r"C:\Users\hp\Desktop\MyDrive\OSM\tools\osmconvert.exe"  # chemin vers osmconvert.exe

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# ====== CHARGEMENT DES BBOX ======
df = pd.read_csv(CSV_BBOX)
print(f"📄 {len(df)} villes détectées")

def clean_name(name):
    return name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")

success, fail = 0, 0

for _, row in df.iterrows():
    city = clean_name(row["source_folder"])
    min_lon, min_lat, max_lon, max_lat = row["min_lon"], row["min_lat"], row["max_lon"], row["max_lat"]
    
    print(f"\n🚦 Traitement de {city}")

    # ====== Créer un PBF par ville avec osmconvert ======
    city_pbf = os.path.join(TMP_DIR, f"{city}.osm.pbf")
    cmd = [
        OSMCONVERT_PATH,
        OSM_PBF,
        f"-b={min_lon},{min_lat},{max_lon},{max_lat}",
        "--complete-ways",
        f"-o={city_pbf}"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"🗂️ PBF créé pour {city}")
    except Exception as e:
        print(f"❌ Erreur osmconvert pour {city} : {e}")
        fail += 1
        continue

    # ====== Charger le PBF réduit avec Pyrosm ======
    try:
        osm = OSM(city_pbf)
        roads = osm.get_network(network_type="driving")
        if roads is None or roads.empty:
            print(f"⚠️ Aucune route trouvée pour {city}")
            fail += 1
            continue

        city_dir = os.path.join(OUTPUT_DIR, city)
        os.makedirs(city_dir, exist_ok=True)
        roads.to_parquet(os.path.join(city_dir, "roads.parquet"))
        print(f"✅ Routes sauvegardées pour {city} ({len(roads)} segments)")
        success += 1

    except Exception as e:
        print(f"❌ Erreur Pyrosm pour {city} : {e}")
        fail += 1

print(f"\n🎉 Extraction terminée : {success} villes traitées | {fail} ignorées")
