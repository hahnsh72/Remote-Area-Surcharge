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

# --- Define rules: which countries use city vs postal ---
# Example: adjust this dictionary with your business logic
country_rules = {
    "france": "postal",   # France uses postal code
    "japan": "city",      # Japan uses city
    "germany": "postal",  # Germany uses postal code
    "italy": "city",      # Italy uses city
    # Add more as needed...
}

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

    rule = country_rules.get(country, "postal")  # default to postal if not defined

    if rule == "city" and city:
        df_city = df_country[df_country["City"].str.lower() == city]
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
st.title("FedEx Remote Area Surcharge Checker")

st.write("Enter a **country**. Depending on the country, you will be asked to enter either a **city** or a **postal code**.")

country = st.text_input("Country").strip().lower()

rule = country_rules.get(country, None)

if not country:
    st.info("Please enter a country.")
else:
    if rule == "city":
        city = st.text_input("City")
        postal_code = None
    elif rule == "postal":
        postal_code = st.text_input("Postal Code")
        city = None
    else:
        st.warning("This country is not configured in rules. Defaulting to postal code.")
        postal_code = st.text_input("Postal Code")
        city = None

    if st.button("Check Surcharge"):
        result = surcharge_applicable(country, city, postal_code)
        st.success(f"Surcharge applicable? **{result}**")



        st.success(f"Surcharge applicable? **{result}**")

