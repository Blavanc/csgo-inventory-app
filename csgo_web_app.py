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
        # 📌 Menu déroulant pour choisir un skin
        st.markdown("## 📈 Évolution du prix")
        st.divider ()
        skin_names = df["Nom du skin"].tolist()
        selected_skin = st.selectbox("📈 Choisissez un skin pour voir l'évolution du prix :", skin_names)

# 📌 On retrouve l'objet JSON complet correspondant à ce skin
        skin_data = next((item for item in data if selected_skin.lower() in item.get("marketname", "").lower()), None)

        if skin_data and "latest10steamsales" in skin_data:
            sales_data = skin_data["latest10steamsales"]
            sales_df = pd.DataFrame(sales_data, columns=["Date", "Prix (€)", "Nombre de ventes"])
            sales_df["Date"] = pd.to_datetime(sales_df["Date"])
            sales_df = sales_df.sort_values("Date")

            # 📊 Création du graphique interactif avec plotly
            fig = px.line(
                sales_df,
                x="Date",
                y="Prix (€)",
                title=f"Évolution du prix de : {selected_skin}",
                markers=True
            )

            # 🎨 Mise en forme améliorée
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Prix (€)",
                xaxis_tickformat="%Y-%m-%d",  # Format de date plus lisible
                template="plotly_white"
            )

            # 🖼️ Affichage dans Streamlit
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Pas de données de vente pour ce skin.") 

        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name='inventaire_csgo.csv',
            mime='text/csv'
        )
else:
        st.warning("Aucun item trouvé dans l'inventaire.")
