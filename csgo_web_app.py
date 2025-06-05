import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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
            tags = item.get("tags", [])
            collection = next(
    (
        tag["localized_tag_name"]   
        for tag in tags               
        if tag["category"] == "ItemSet"  
    ),
    "Inconnue"                         
)
            type_tag = next((tag["localized_tag_name"] for tag in tags if tag["category"] == "Type"), "Inconnu")
            skins.append({
                "Nom du skin": name,
                "Type": type_tag,
                "Collection": collection,
                "Prix unitaire (€)": round(price, 2),
                "Quantité": count,
                "Total (€)": round(total, 2)
            })

        df = pd.DataFrame(skins)
        df = df.sort_values("Total (€)", ascending=False)      
   
   # Checkbox pour filtrer uniquement les armes
        if st.checkbox("Afficher uniquement les skins d'armes"):
            df = df[~df['Type'].isin(['Graffiti', 'Sticker', 'Container'])].reset_index(drop=True)
            total_value = df["Total (€)"].sum()

        st.success(f"💰 Valeur totale estimée de l'inventaire : **{round(total_value, 2)} €**")
        st.dataframe(df.reset_index(drop=True))
        skin_names = df["Nom du skin"].tolist()
        selected_skin = st.selectbox("📈 Choisissez un skin pour voir l'évolution du prix :", skin_names)

        @st.cache_data
        def load_price_history():
            try:
                return pd.read_csv("data/csgo_prices.csv")
            except FileNotFoundError:
                st.warning("Le fichier historique de prix est introuvable.")
                return pd.DataFrame()

        price_df = load_price_history()

        if not price_df.empty and selected_skin in price_df["Nom du skin"].values:
            skin_row = price_df[price_df["Nom du skin"] == selected_skin]

            history = skin_row.drop(columns=["Nom du skin"]).T.reset_index()
            history.columns = ["Date", "Prix"]
            history["Plateforme"] = history["Date"].apply(lambda x: "Steam" if "Steam" in x else "SkinBaron" if "SkinBaron" in x else "Autre")
            history["Date"] = history["Date"].str.replace("Steam - ", "").str.replace("SkinBaron - ", "")
            history["Date"] = pd.to_datetime(history["Date"], errors="coerce")
            history = history.dropna(subset=["Date", "Prix"])

            fig = px.line(
                history,
                x="Date",
                y="Prix",
                color="Plateforme",
                title=f"Évolution du prix (Steam vs SkinBaron) : {selected_skin}",
                markers=True
            )
            fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Prix (€)")
            st.plotly_chart(fig, use_container_width=True)

    else:
                st.warning("Aucun item trouvé dans l'inventaire.")
