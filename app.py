import pandas as pd
import streamlit as st

# --- Load and prepare data ---
file_path = "Fedex_ODA_OPA_tiers_codes.xlsx"

# Load data with the right header offset
df_clean = pd.read_excel(file_path, sheet_name="Postal codes and tiers", skiprows=6)
df_data = df_clean.iloc[3:].reset_index(drop=True)
df_data.columns = [
    "Country", "City", "BeginPostal", "EndPostal",
    "ODA_IPS", "ODA_IFS", "OPA_IPS", "OPA_IFS", "Extra1", "Extra2"
]
df_data = df_data[["Country", "City", "BeginPostal", "EndPostal", "ODA_IPS", "ODA_IFS"]]

# --- Define function ---
def surcharge_applicable(country: str, city: str = None, postal_code: str = None) -> str:
    country = country.strip().lower()
    if city:
        city = city.strip().lower()
    if postal_code:
        postal_code = str(postal_code).strip()

    df_country = df_data[df_data["Country"].str.lower() == country]
    if df_country.empty:
        return "No"

    if city:
        df_city = df_country[df_country["City"].str.lower() == city]
        if not df_city.empty and (df_city["ODA_IPS"].notna().any() or df_city["ODA_IFS"].notna().any()):
            return "Yes"

    if postal_code:
        for _, row in df_country.iterrows():
            if pd.notna(row["BeginPostal"]) and pd.notna(row["EndPostal"]):
                if str(row["BeginPostal"]) <= postal_code <= str(row["EndPostal"]):
                    if pd.notna(row["ODA_IPS"]) or pd.notna(row["ODA_IFS"]):
                        return "Yes"

    return "No"

# --- Streamlit UI ---
st.title("FedEx Remote Area Surcharge Checker")

st.write("Enter a **country** and either a **city** OR a **postal code** to check if surcharge applies.")

country = st.text_input("Country")
city = st.text_input("City (leave empty if using postal code)")
postal_code = st.text_input("Postal Code (leave empty if using city)")

if st.button("Check Surcharge"):
    if not country:
        st.error("Please enter a country.")
    else:
        result = surcharge_applicable(country, city if city else None, postal_code if postal_code else None)
        st.success(f"Surcharge applicable? **{result}**")
