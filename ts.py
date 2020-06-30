import sqlite3
import pandas as pd
import streamlit as st


st.header('Transparance santé')

conn = sqlite3.connect('transpa_sante.db')
cur = conn.cursor()

@st.cache
def denominations():
    cur.execute("select distinct denomination_sociale from avantage")
    return [x[0] for x in cur.fetchall()]


def calcul_avantages(company):
    cur.execute("SELECT SUM(avant_montant_ttc) from avantage where denomination_sociale = ?", (company,))
    return cur.fetchall()[0][0] or 0


def calcul_remunerations(company):
    cur.execute("SELECT SUM(remu_montant_ttc) from remuneration where denomination_sociale = ?", (company,))
    return cur.fetchall()[0][0] or 0

def calcul_conventions(company):
    cur.execute("select sum(conv_montant_ttc) from convention where denomination_sociale = ?", (company,))
    return cur.fetchall()[0][0] or 0

def calcul_beneficiaire(name):
    qry = cur.execute(
        "SELECT SUM(conv_montant_ttc) "
        "FROM convention "
        "WHERE UPPER(benef_nom) LIKE ?",
         (name,)
         )
    cols = [column[0] for column in qry.description]
    df = pd.DataFrame.from_records(data = qry.fetchall(), columns = cols)
    return df


    df = pd.read_sql_query("select sum(conv_montant_ttc) from convention where UPPER(benef_nom) like ?{name}", (name,))
    return df

company = st.sidebar.selectbox(
    'Pour quelle société souhaitez vous interroger la base de données ?',
    denominations())

comp = st.subheader(f'Calculs en cours pour {company}...')   
av =  calcul_avantages(company)
remu = calcul_remunerations(company)
conv = calcul_remunerations(company)
comp.subheader(company)


'Avantages caca : ', f"{'{:,}'.format(av)}".replace(',', ' ') , ' €'
'Rémunérations : ', f"{'{:,}'.format(remu)}".replace(',', ' '), ' €'
'Conventions: ', f"{'{:,}'.format(conv)}".replace(',', ' '), ' €'
'Total : ', f"{'{:,}'.format(av + remu + conv)}".replace(',', ' '), ' €'

df = calcul_beneficiaire('gilead')
print(df)
st.write(df)

