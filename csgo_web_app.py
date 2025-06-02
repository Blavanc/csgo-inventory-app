import streamlit as st
import requests
import pandas as pd

API_KEY = "CL6CY4P85IIOQI5B"

# Interface pour streamlit
st.title("🎒 Inventaire CS:GO • Évaluation de valeur")

steam_id = st.text_input("🆔 Entrez votre SteamID64 :", value="")

if steam_id:
    @st.cache_data
    def get_inventory(steam_id, api_key):
        url = f"https://www.steamwebapi.com/steam/api/inventory?key={api_key}&steam_id={steam_id}"
        response = requests.get(url)
        if response.status_code != 200:
            st.error("Erreur lors de la récupération de l'inventaire.")
            return []
        return response.json()

    data = get_inventory(steam_id, API_KEY)

    if data:
        skins = []
        total_value = 0.0

        for item in data:
            name = item.get("marketname") or item.get("markethashname") or item.get("name", "Inconnu")
            price = item.get("pricelatest", 0.0)
            count = item.get("count", 1)
            total = price * count
            total_value += total
            skins.append({
                "Nom du skin": name,
                "Prix unitaire (€)": round(price, 2),
                "Quantité": count,
                "Total (€)": round(total, 2)
            })

        df = pd.DataFrame(skins)
        df = df.sort_values("Total (€)", ascending=False)

        
        st.success(f"💰 Valeur totale estimée de l'inventaire : **{round(total_value, 2)} €**")
        st.dataframe(df.reset_index(drop=True))

        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name='inventaire_csgo.csv',
            mime='text/csv'
        )
    else:
        st.warning("Aucun item trouvé dans l'inventaire.")
