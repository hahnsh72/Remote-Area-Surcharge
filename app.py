import pandas as pd
import streamlit as st

# --- Load and prepare data ---
file_path = "Fedex_ODA_OPA_tiers_codes.xlsx"

df_clean = pd.read_excel(file_path, sheet_name="Postal codes and tiers", skiprows=6)
df_data = df_clean.iloc[3:].reset_index(drop=True)
df_data.columns = [
    "Country", "City", "BeginPostal", "EndPostal",
    "ODA_IPS", "ODA_IFS", "OPA_IPS", "OPA_IFS", "Extra1", "Extra2"
]
df_data = df_data[["Country", "City", "BeginPostal", "EndPostal", "ODA_IPS", "ODA_IFS"]]

# --- Detect rules automatically ---
country_rules = {}
for country, group in df_data.groupby(df_data["Country"].str.strip().str.lower()):
    has_postal = group["BeginPostal"].notna().any() and group["EndPostal"].notna().any()
    has_city = group["City"].notna().any()
    if has_postal:
        country_rules[country] = "postal"
    elif has_city:
        country_rules[country] = "city"
    else:
        country_rules[country] = "unknown"

# --- Core function ---
def surcharge_applicable(country: str, city: str = None, postal_code: str = None) -> str:
    country = country.strip().lower()
    if city:
        city = city.strip().lower()
    if postal_code:
        postal_code = str(postal_code).strip()

    df_country = df_data[df_data["Country"].str.strip().str.lower() == country]
    if df_country.empty:
        return "No"

    rule = country_rules.get(country, "unknown")

    if rule == "city" and city:
        df_city = df_country[df_country["City"].str.strip().str.lower() == city]
        if not df_city.empty and (df_city["ODA_IPS"].notna().any() or df_city["ODA_IFS"].notna().any()):
            return "Yes"

    if rule == "postal" and postal_code:
        for _, row in df_country.iterrows():
            if pd.notna(row["BeginPostal"]) and pd.notna(row["EndPostal"]):
                if str(row["BeginPostal"]) <= postal_code <= str(row["EndPostal"]):
                    if pd.notna(row["ODA_IPS"]) or pd.notna(row["ODA_IFS"]):
                        return "Yes"

    return "No"

# --- Streamlit UI ---
st.title("FedEx International Out-of-Delivery Area (ODA) Checker")

st.write("Select a **country**. Depending on the country, you will be asked to enter either a **city** or a **postal code**.")

all_countries = sorted(df_data["Country"].dropna().unique())
country = st.selectbox("Country", options=[""] + list(all_countries))

if country:
    rule = country_rules.get(country.strip().lower(), "unknown")

    if rule == "city":
        city = st.text_input("City")
        postal_code = None
    elif rule == "postal":
        postal_code = st.text_input("Postal Code")
        city = None
    else:
        st.warning("This country has no clear rule (no city or postal code data found).")
        city = postal_code = None

    if st.button("Check Surcharge"):
        result = surcharge_applicable(country, city, postal_code)
        st.success(f"Surcharge applicable? **{result}**")
else:
    st.info("Please select a country.")




