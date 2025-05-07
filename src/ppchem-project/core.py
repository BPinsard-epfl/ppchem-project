import requests
import pandas as pd
import json
import regex as re
from time import sleep

def get_smiles_from_name(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/CanonicalSMILES/TXT"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text.strip()
    except:
        return None

def get_pka_from_smiles(smiles):
    try:
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/cids/TXT"
        cid = int(requests.get(cid_url).text.strip())
        data_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/?heading=Dissociation+Constants"
        req = requests.get(data_url)
        x = json.loads(req.text)
        pka = x['Record']['Section'][0]['Section'][0]['Section'][0]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        return float(re.search(r'\d+\.\d+', pka).group())
    except:
        return None

import os

def build_data_table(molecule_names, output_file=None, delay=0.5):
    if output_file is None:
        # Crée le chemin absolu vers le vrai dossier "data" en remontant deux niveaux
        output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "data.csv"))
    data = []
    for name in molecule_names:
        print(f"Processing: {name}")
        smiles = get_smiles_from_name(name)
        if not smiles:
            print(f"  -> SMILES not found for {name}")
            data.append({"name": name, "smiles": None, "pKa": None})
            continue

        pka = get_pka_from_smiles(smiles)
        data.append({"name": name, "smiles": smiles, "pKa": pka})
        sleep(delay)

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")
