import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

# ============================
# Load dataset
# ============================
@st.cache_data
def load_data():
    return pd.read_csv("movies.csv")   # <-- change to your file
movies_df = load_data()

st.title("Netflix app")
st.write("Done! (using st.cache)")

# ============================
# SIDEBAR
# ============================
st.sidebar.header("Opciones")

# -------- Mostrar todos --------
show_all = st.sidebar.checkbox("Mostrar todos los filmes")

# -------- Buscar por título --------
st.sidebar.subheader("Título del filme :")
title_query = st.sidebar.text_input("")

if st.sidebar.button("Buscar filmes"):
    result = movies_df[movies_df["name"].str.contains(title_query, case=False, na=False)]
    total = len(result)

    st.subheader(f"Resultados para '{title_query}' — {total} filmes encontrados")
    st.dataframe(result)

# -------- Filtrar por director --------
st.sidebar.subheader("Seleccionar Director")

directors = sorted(movies_df["director"].dropna().unique())
selected_director = st.sidebar.selectbox(" ", directors)

if st.sidebar.button("Filtrar director"):
    result = movies_df[movies_df["director"] == selected_director]
    total = len(result)

    st.subheader(f"Filmes dirigidos por {selected_director} — {total} filmes encontrados")
    st.dataframe(result)

# ============================
# NEW FILM ENTRY
# ============================
st.sidebar.subheader("Nuevo filme")

# --- Input fields ---
new_name = st.sidebar.text_input("Name:", placeholder="Press Enter to apply")

new_company = st.sidebar.selectbox(
    "Company",
    sorted(movies_df["company"].dropna().unique())
)

new_director = st.sidebar.text_input("Director")
new_genre = st.sidebar.text_input("Genre")

# --- Add movie ---
if st.sidebar.button("Agregar filme"):
    if new_name.strip() == "":
        st.sidebar.error("El nombre del filme no puede estar vacío.")
    else:
        # Save to Firestore
        doc_ref = db.collection("movies").document(new_name)
        doc_ref.set({
            "name": new_name,
            "company": new_company,
            "director": new_director,
            "genre": new_genre
        })

        # Add to DataFrame
        new_row = {
            "name": new_name,
            "company": new_company,
            "director": new_director,
            "genre": new_genre
        }
        movies_df = pd.concat([movies_df, pd.DataFrame([new_row])], ignore_index=True)

        st.sidebar.success("Filme agregado correctamente!")

        # Force page refresh to show new movie in tables and dropdowns
        st.rerun()


# ============================
# MAIN AREA — SHOW ALL
# ============================
if show_all:
    st.header("Todos los filmes")
    st.dataframe(movies_df.head(500))
