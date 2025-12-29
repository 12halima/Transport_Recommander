from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import networkx as nx
import time
import gc
import pandas as pd
import os  # Indispensable pour lire les variables d'environnement

app = FastAPI()

# 1. Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialisation de DuckDB
con = duckdb.connect(database=':memory:')

# 3. Configuration de la source de données (Cloud vs Local)
AZURE_CONN_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if AZURE_CONN_STRING:
    # --- CONFIGURATION CLOUD AZURE ---
    print("Connexion au Cloud Azure détectée...")
    con.execute("INSTALL azure; LOAD azure;")
    con.execute(f"SET azure_storage_connection_string='{AZURE_CONN_STRING}';")
    DATA_PATH = "az://data"  # 'data' est le nom de ton conteneur Azure
else:
    # --- CONFIGURATION LOCALE (Pour tes tests sur PC) ---
    print("Pas de clé Azure trouvée, utilisation du dossier local /data")
    DATA_PATH = "./data"

# 4. Gestion de la session et de la mémoire
session = {"city": None, "graph": None, "nodes_df": None, "start_time_sec": 0}

# 5. Fonctions utilitaires
def fmt(s): 
    return time.strftime('%H:%M:%S', time.gmtime(s))

def get_realistic_arrival(dep_sec, dur_theo_sec, cost):
    dur_real_min = (dur_theo_sec / 60) * cost
    dur_theo_min = dur_theo_sec / 60
    if dur_real_min > 180 and dur_theo_min < 45: 
        dur_real_min /= 2.5
    if dur_real_min > (dur_theo_min * 2.5): 
        dur_real_min = dur_theo_min * 1.8
    return dep_sec + (dur_real_min * 60)

# 6. Endpoints API
@app.get("/get-cities")
def get_cities():
    try:
        query = f"SELECT DISTINCT city FROM read_parquet('{DATA_PATH}/NODES/*.parquet') ORDER BY city"
        return con.execute(query).df()['city'].tolist()
    except Exception as e:
        print(f"Erreur get-cities: {e}")
        return []

@app.get("/init-session")
def init_session(city: str, start_time: str):
    if session["graph"]:
        session["graph"].clear()
    gc.collect()

    h, m = map(int, start_time.split(':'))
    t_sec = h * 3600 + m * 60
    
    # Chargement des Nodes + Gestion des noms NULL
    nodes = con.execute(f"SELECT id, name FROM read_parquet('{DATA_PATH}/NODES/*.parquet') WHERE city = '{city}'").df()
    nodes['name'] = nodes['name'].fillna("Station " + nodes['id'].astype(str))
    nodes.loc[nodes['name'] == '', 'name'] = "Station " + nodes['id'].astype(str)
    
    # Chargement des trajets
    df_travel = con.execute(f"""
        SELECT source, target, weight_final, route_id, trip_id, dep_sec, arr_sec, route_type 
        FROM read_parquet('{DATA_PATH}/EDGES_TRAVEL/*.parquet') 
        WHERE city='{city}' AND dep_sec BETWEEN {t_sec} AND {t_sec+14400}
    """).df()
    
    G = nx.MultiDiGraph()
    for r in df_travel.itertuples():
        G.add_edge(r.source, r.target, weight=r.weight_final, route_id=r.route_id, 
                   trip_id=r.trip_id, dep=r.dep_sec, arr=r.arr_sec, mode=r.route_type)
    
    # Chargement des transferts
    try:
        city_f = city.replace(" ", "_").replace("(", "").replace(")", "")
        df_trans = con.execute(f"""
            SELECT source, target, weight_final, dep_sec, arr_sec FROM read_parquet('{DATA_PATH}/EDGES_TRANSFER/city={city_f}/*.parquet') 
            WHERE dep_sec BETWEEN {t_sec} AND {t_sec+14400}
        """).df()
        for r in df_trans.itertuples():
            G.add_edge(r.source, r.target, weight=r.weight_final + 25, 
                       trip_id='TRANSFER', dep=r.dep_sec, arr=r.arr_sec, mode='TRANSFER')
    except:
        pass
    
    session.update({"city": city, "graph": G, "nodes_df": nodes, "start_time_sec": t_sec})
    return {"status": "ok"}

@app.get("/search-stations")
def search_stations(q: str):
    if session["nodes_df"] is None: return []
    df = session["nodes_df"]
    return df[df['name'].str.contains(q, case=False, na=False)].head(10).to_dict(orient="records")

@app.get("/get-reachable-targets")
def get_reachable(source_id: str):
    G = session["graph"]
    if not G or source_id not in G: return []
    reachable_ids = list(nx.descendants(G, source_id))[:60]
    return session["nodes_df"][session["nodes_df"]['id'].isin(reachable_ids)].to_dict(orient="records")

@app.get("/recommend-multi")
def recommend_multi(source_id: str, target_id: str):
    G = session["graph"]
    t_start = session["start_time_sec"]
    t_limit = t_start + 3600
    names = dict(zip(session["nodes_df"].id, session["nodes_df"].name))
    
    first_trips = [data['trip_id'] for u, v, data in G.edges(source_id, data=True) 
                   if data.get('dep', 0) >= t_start and data.get('dep', 0) <= t_limit]
    
    results = []
    seen_signatures = set()

    for trip in list(set(first_trips))[:12]:
        try:
            path = nx.shortest_path(G, source_id, target_id, weight='weight')
            steps, curr_time, changes, last_trip = [], t_start, 0, None
            actual_start_of_trip = None

            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                edge_data = G.get_edge_data(u, v)
                best_k = min(edge_data, key=lambda k: edge_data[k]['weight'])
                data = edge_data[best_k]

                is_c = False
                if last_trip and data['trip_id'] != last_trip and data['trip_id'] != 'TRANSFER':
                    changes += 1
                    is_c = True
                if data['trip_id'] != 'TRANSFER': last_trip = data['trip_id']

                h_dep = max(curr_time, data['dep'])
                if i == 0: actual_start_of_trip = h_dep
                
                h_arr = get_realistic_arrival(h_dep, (data['arr']-data['dep']), data['weight'])
                curr_time = h_arr
                
                steps.append({
                    "station": names.get(u, u), 
                    "ligne": data.get('route_id', '---'), 
                    "mode": data['mode'], 
                    "dep": fmt(h_dep), 
                    "arr": fmt(h_arr), 
                    "is_change": is_c
                })
            
            total_dur = (curr_time - actual_start_of_trip) // 60
            
            if total_dur < 40 and changes >= 3: continue
            if total_dur < 60 and changes >= 5: continue
            if total_dur < 120 and changes >= 7: continue
            if total_dur >= 120 and changes >= 6: continue

            signature = f"{steps[0]['dep']}_{steps[-1]['arr']}_{steps[0]['ligne']}"
            if signature not in seen_signatures:
                results.append({
                    "ligne": steps[0]['ligne'], 
                    "mode": steps[0]['mode'], 
                    "h_dep": steps[0]['dep'], 
                    "h_arr": steps[-1]['arr'], 
                    "duree": int(total_dur), 
                    "changes": changes, 
                    "stops": len(steps), 
                    "steps": steps
                })
                seen_signatures.add(signature)
        except: continue
    
    return sorted(results, key=lambda x: x['h_dep'])