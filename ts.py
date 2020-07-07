import base64
import sqlite3
import pandas as pd
import streamlit as st
import os

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.header('[Transparence santé](https://www.transparence.sante.gouv.fr)')
st.sidebar.warning("""
Version : **2020_06_27_04_00**
""")
st.sidebar.markdown("""
Vous pouvez grâce à cette application interroger la base de donnée *transparence-santé*
à disposition sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/transparence-sante-1/).

Cette application a été créée suite à [cet article paru sur 20minutes.fr](https://www.20minutes.fr/societe/2807951-20200626-coronavirus-simple-comme-chou-verifier-liens-entre-medecins-laboratoires-pharmaceutiques-comme-dit-didier-raoult).

Il y est notament rapporté qu'il est difficile d'exploiter la base de donnée *transparence-santé*.

Ca n'est maintenant plus le cas.



[A propos](#)

""")
#[![Foo](https://img.icons8.com/fluent/96/github.png)](http://google.com.au/)
db_path = "./"
if os.getenv("PROD"):
    db_path="/data/"
conn = sqlite3.connect(f'{db_path}transpa_sante.db')
cur = conn.cursor()


@st.cache
def denominations():
    cur.execute("select distinct denomination_sociale from avantage order by denomination_sociale")
    return [''] + [x[0] for x in cur.fetchall()]


def calcul_avantages(company):
    cur.execute(
        "SELECT SUM(avant_montant_ttc) from avantage where denomination_sociale = ?", (company,))
    return cur.fetchall()[0][0] or 0


def calcul_remunerations(company):
    cur.execute(
        "SELECT SUM(remu_montant_ttc) from remuneration where denomination_sociale = ?", (company,))
    return cur.fetchall()[0][0] or 0


def calcul_conventions(company):
    cur.execute(
        "select sum(conv_montant_ttc) from convention where denomination_sociale = ?", (company,))
    return cur.fetchall()[0][0] or 0

def get_table_download_link(df, table, name, firstname):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    if len(df.index) < 5000:
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        return f'<a download={name}_{firstname}_{table}.csv href="data:file/csv;base64,{b64}">Télécharger au format CSV</a>'
    return '*Fichier trop volumineux pour être téléchargé, veuillez affiner votre recherche*'



def calcul_beneficiaire(**kwargs):
    progress = 0
    my_bar = st.progress(progress)
    for table in ('convention', 'avantage', 'remuneration'):
        title = st.subheader(table.capitalize() + '...')
        qry = f"SELECT * FROM {table} WHERE "
        qry += "AND ".join([f"UPPER({k}) = ? " for k, v in kwargs.items() if v])
        qry = cur.execute(
            qry,
            ([v.upper() for v in kwargs.values() if v])
            )
        progress += 33
        my_bar.progress(progress)
        cols = [column[0] for column in qry.description]
        df = pd.DataFrame.from_records(
                data=qry.fetchall(),
                columns=cols
            )
        title.subheader(table.capitalize())
        st.markdown(get_table_download_link(df, table, name, firstname), unsafe_allow_html=True)
        st.write('Aperçu :')
        montant = str([x for x in df.columns if 'montant_ttc' in x][0])
        tdf = df[['benef_nom', 'benef_prenom', 'denomination_sociale', montant] + sorted(df.columns)]
        tdf.fillna('', inplace=True)
        st.write(tdf.iloc[:50,:])
        total = f"{'{:,}'.format(df[montant].sum())}".replace(
            ',', ' ').replace('.0', '')
        st.write(f'Total : {total} €')
    my_bar.text('')

st.subheader(
    'Saisissez le nom de la personne pour laquelle vous souhaitez interroger la base de donnée :'
)

company = st.selectbox(
    'Société',
    denominations())
name = st.text_input('Nom')
firstname = st.text_input('Prénom')
if name or firstname or company:
    calcul_beneficiaire(
        benef_nom=name,
        benef_prenom=firstname, 
        denomination_sociale=company
        )
