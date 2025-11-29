import json
from google.cloud import firestore
from google.oauth2 import service_account
import streamlit as st

# ================================
# Load Firebase Credentials
# ================================
key_dict = st.secrets["textkey"]

creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project=key_dict["project_id"])

dbNames = db.collection("movies")

# ============================
# Load dataset
# ============================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/mfigueiro/movie_deploy/main/movies.csv"
    return pd.read_csv(url)

movies_df = load_data()
st.write(movies_df.head())

#st.title("Netflix app")
#st.write("Done! (using st.cache)")

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
new_name = st.sidebar.text_input("Nombre del filme:", placeholder="Ingresa el título")

new_company = st.sidebar.selectbox(
    "Compañía",
    sorted(movies_df["company"].dropna().unique())
)

# Directors list gets updated automatically from DataFrame
director_list = sorted(movies_df["director"].dropna().unique())
new_director = st.sidebar.selectbox("Director", director_list + ["-- Nuevo Director --"])

# If user chooses "new director", show a text box
if new_director == "-- Nuevo Director --":
    new_director = st.sidebar.text_input("Agrega nuevo director:")

# Genres list
genre_list = sorted(movies_df["genre"].dropna().unique())
new_genre = st.sidebar.selectbox("Género", genre_list + ["-- Nuevo Género --"])

if new_genre == "-- Nuevo Género --":
    new_genre = st.sidebar.text_input("Agrega nuevo género:")

# --- Button ---
if st.sidebar.button("Agregar filme"):
    if new_name.strip() == "":
        st.sidebar.error("❌ El nombre del filme no puede estar vacío.")
    else:

        # ======== Save to Firestore ========
        doc_ref = db.collection("movies").document(new_name)
        doc_ref.set({
            "name": new_name,
            "company": new_company,
            "director": new_director,
            "genre": new_genre
        })

        # ======== Add to DataFrame ========
        new_row = {
            "name": new_name,
            "company": new_company,
            "director": new_director,
            "genre": new_genre
        }

        movies_df = pd.concat([movies_df, pd.DataFrame([new_row])], ignore_index=True)

        st.sidebar.success("✅ Filme agregado correctamente!")

        # Refresh the page so dropdown lists update
        st.rerun()

# ============================
# MAIN AREA — SHOW ALL
# ============================
if show_all:
    st.header("Todos los filmes")
    st.dataframe(movies_df.head(500))
