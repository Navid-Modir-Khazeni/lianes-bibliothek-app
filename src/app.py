import streamlit as st

import stil
from crud import (
    bewertung_abgeben,
    buch_hinzufuegen,
    buch_loeschen,
    freund_hinzufuegen,
    freund_loeschen,
    lese_autoren,
    lese_buecher,
    lese_buecher_eines_freundes,
    lese_bewertungen,
    lese_freunde,
    lese_freunde_uebersicht,
    lese_genres,
    lese_offene_leihgaben,
    lese_standorte,
    lese_uebersicht,
    lese_verfuegbare_buecher,
    leihgabe_eintragen,
    rueckgabe_eintragen,
    verbindung_herstellen,
)

st.set_page_config(page_title="Lianes Bibliothek", page_icon="📚", layout="wide")
stil.anwenden()


@st.cache_resource
def hole_engine(passwort):
    """Baut die Datenbankverbindung nur einmal pro Passwort auf."""
    return verbindung_herstellen(passwort)


SEITEN = {
    "Bücher": "📚 Bücher",
    "Freunde": "📇 Freunde",
    "Leihgabe eintragen": "📤 Leihgabe eintragen",
    "Rückgabe eintragen": "📥 Rückgabe eintragen",
    "Bewertung abgeben": "⭐ Bewertung abgeben",
}
TITEL_HTML = (
    '<h1 class="haupttitel">📚 Lianes Bibliothek</h1>'
    '<p class="untertitel">Wer hat welches Buch? Hier ist die Antwort! ✨</p>'
)
START_TITEL_HTML = (
    '<h1 class="start-titel">📚 Lianes Bibliothek</h1>'
    '<p class="start-untertitel">Wer hat welches Buch? Hier ist die Antwort! ✨</p>'
)


def zeige_meldung(erfolg, meldung):
    """Zeigt das Ergebnis einer Aktion grün (Erfolg) oder rot (Fehler) an."""
    if erfolg:
        st.success(meldung)
    else:
        st.error(meldung)


# ---------- Anmeldung ----------
if "passwort" not in st.session_state:
    stil.anwenden_start()
    st.markdown(START_TITEL_HTML, unsafe_allow_html=True)
    _, mitte, _ = st.columns([1, 2, 1])
    with mitte:
        with st.form("anmeldung"):
            eingabe = st.text_input("🔑 MySQL-Passwort", type="password")
            angemeldet = st.form_submit_button("Anmelden")
        if angemeldet:
            try:
                with hole_engine(eingabe).connect():
                    pass
            except Exception:
                st.error("Anmeldung nicht möglich. Stimmt das Passwort, und läuft MySQL?")
            else:
                st.session_state["passwort"] = eingabe
                st.rerun()
    st.stop()

engine = hole_engine(st.session_state["passwort"])
seite = st.session_state.get("seite", "Start")

# ---------- Startseite mit Menü ----------
if seite == "Start":
    stil.anwenden_start()
    st.markdown(START_TITEL_HTML, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(key="menue"):
        spalten = st.columns(len(SEITEN))
        for spalte, name in zip(spalten, SEITEN):
            with spalte:
                if st.button(SEITEN[name], key=f"menue_{name}"):
                    st.session_state["seite"] = name
                    st.rerun()
    st.stop()

# ---------- Unterseiten ----------
if st.button("← Zurück zum Menü", key="zurueck"):
    st.session_state["seite"] = "Start"
    st.rerun()
st.markdown(TITEL_HTML, unsafe_allow_html=True)

# ===== Bücher =====
if seite == "Bücher":
    st.header("📚 Bücher")
    uebersicht = lese_uebersicht(engine)

    alle_status = ["verfügbar", "verliehen", "überfällig", "Eigengebrauch"]
    spalte_links, spalte_rechts = st.columns(2)
    with spalte_links:
        status_auswahl = st.multiselect(
            "Status", alle_status, default=alle_status, placeholder="Status auswählen …"
        )
    with spalte_rechts:
        genre_auswahl = st.selectbox(
            "Genre", ["Alle"] + sorted(uebersicht["Genre"].unique())
        )

    gefiltert = uebersicht[uebersicht["Status"].isin(status_auswahl)]
    if genre_auswahl != "Alle":
        gefiltert = gefiltert[gefiltert["Genre"] == genre_auswahl]

    tab_regal, tab_tabelle, tab_neu, tab_loeschen = st.tabs(
        ["🖼️ Bücherregal", "📋 Tabelle", "➕ Buch hinzufügen", "🗑️ Buch löschen"]
    )

    with tab_regal:
        st.caption(f"{len(gefiltert)} von {len(uebersicht)} Büchern")
        if gefiltert.empty:
            st.info("Keine Bücher gefunden 🤷")
        else:
            with st.spinner("📚 Hole die Cover … (beim ersten Mal dauert das etwas)"):
                covers = stil.lade_covers(gefiltert)
            regal_daten = gefiltert.copy()
            regal_daten["AktuellerStandort"] = [
                f"{ort} · 📞 {telefon}" if isinstance(telefon, str) and telefon else ort
                for ort, telefon in zip(regal_daten["AktuellerStandort"], regal_daten["Telefon"])
            ]
            st.markdown(stil.karten_html(regal_daten, covers), unsafe_allow_html=True)

    with tab_tabelle:
        st.caption(f"{len(gefiltert)} von {len(uebersicht)} Büchern")
        if gefiltert.empty:
            st.info("Keine Bücher gefunden 🤷")
        else:
            tabelle = gefiltert.copy()
            tabelle["Status"] = tabelle["Status"].map(stil.STATUS_EMOJI)
            tabelle = tabelle.rename(
                columns={
                    "AktuellerStandort": "Aktueller Standort",
                    "Faelligkeitsdatum": "Fällig am",
                    "Ausgeliehen_von": "Ausgeliehen von",
                    "Bewertung": "Bewertung ⭐",
                    "Anzahl_Bewertungen": "Anzahl Bewertungen",
                }
            )
            st.dataframe(tabelle, hide_index=True)

    with tab_neu:
        genre_optionen = {z.Name: z.GenreID for z in lese_genres(engine).itertuples()}
        standort_optionen = {
            z.Bezeichnung: z.StandortID for z in lese_standorte(engine).itertuples()
        }
        autor_optionen = {
            f"{z.Vorname} {z.Nachname}": z.AutorID for z in lese_autoren(engine).itertuples()
        }

        with st.form("buch_formular"):
            titel = st.text_input("Titel")
            isbn = st.text_input("ISBN (optional, 13 Ziffern)")
            autor_namen = st.multiselect(
                "Autor(en), bereits vorhanden",
                list(autor_optionen),
                placeholder="Autor(en) auswählen …",
            )
            st.caption("Falls der Autor noch nicht in der Liste steht (optional):")
            spalte_vorname, spalte_nachname = st.columns(2)
            with spalte_vorname:
                neuer_vorname = st.text_input("Vorname des neuen Autors")
            with spalte_nachname:
                neuer_nachname = st.text_input("Nachname des neuen Autors")
            genre_name = st.selectbox("Genre", list(genre_optionen), key="neu_genre")
            standort_name = st.selectbox("Standort", list(standort_optionen))
            verleihbar = st.checkbox("Darf verliehen werden", value=True)
            abgeschickt = st.form_submit_button("Buch hinzufügen")

        if abgeschickt:
            neuer_autor = None
            if neuer_vorname.strip() or neuer_nachname.strip():
                neuer_autor = (neuer_vorname.strip(), neuer_nachname.strip())
            zeige_meldung(
                *buch_hinzufuegen(
                    engine,
                    titel,
                    isbn,
                    [int(autor_optionen[name]) for name in autor_namen],
                    neuer_autor,
                    int(genre_optionen[genre_name]),
                    int(standort_optionen[standort_name]),
                    verleihbar,
                )
            )

    with tab_loeschen:
        st.caption("Gelöscht werden können nur Bücher, die noch nie verliehen wurden.")
        buch_optionen = {
            f"{zeile.Titel} (Nr. {zeile.BuchID})": zeile.BuchID
            for zeile in lese_buecher(engine).itertuples()
        }
        with st.form("loeschen_formular"):
            buch_name = st.selectbox("Welches Buch soll gelöscht werden?", list(buch_optionen))
            sicher = st.checkbox("Ja, ich möchte dieses Buch wirklich löschen")
            abgeschickt = st.form_submit_button("Buch löschen")

        if abgeschickt:
            if not sicher:
                st.warning("Bitte erst bestätigen, dass das Buch gelöscht werden soll.")
            else:
                zeige_meldung(*buch_loeschen(engine, int(buch_optionen[buch_name])))

# ===== Freunde =====
elif seite == "Freunde":
    st.header("📇 Freunde")
    tab_liste, tab_neu, tab_loeschen = st.tabs(
        ["📇 Liste", "➕ Freund hinzufügen", "🗑️ Freund löschen"]
    )

    with tab_liste:
        freunde_tabelle = lese_freunde_uebersicht(engine)
        suche = st.text_input("🔍 Freund suchen", placeholder="Name eingeben …")
        if suche.strip():
            treffer = freunde_tabelle["Name"].str.contains(suche.strip(), case=False, regex=False)
            freunde_tabelle = freunde_tabelle[treffer]

        st.caption(f"{len(freunde_tabelle)} Treffer")
        if freunde_tabelle.empty:
            st.info("Keinen Freund gefunden 🤷")
        else:
            st.dataframe(freunde_tabelle, hide_index=True)

    with tab_neu:
        with st.form("freund_formular"):
            spalte_vorname, spalte_nachname = st.columns(2)
            with spalte_vorname:
                vorname = st.text_input("Vorname")
            with spalte_nachname:
                nachname = st.text_input("Nachname")
            telefon = st.text_input("Telefon (optional)")
            email = st.text_input("E-Mail (optional)")
            abgeschickt = st.form_submit_button("Freund hinzufügen")

        if abgeschickt:
            zeige_meldung(*freund_hinzufuegen(engine, vorname, nachname, telefon, email))

    with tab_loeschen:
        st.caption("Gelöscht werden können nur Freunde, die noch nie ein Buch geliehen haben.")
        loesch_optionen = {
            f"{zeile.Vorname} {zeile.Nachname}": zeile.FreundID
            for zeile in lese_freunde(engine).itertuples()
        }
        with st.form("freund_loeschen_formular"):
            freund_name = st.selectbox("Welcher Freund soll gelöscht werden?", list(loesch_optionen))
            sicher = st.checkbox("Ja, ich möchte diesen Freund wirklich löschen")
            abgeschickt = st.form_submit_button("Freund löschen")

        if abgeschickt:
            if not sicher:
                st.warning("Bitte erst bestätigen, dass der Freund gelöscht werden soll.")
            else:
                zeige_meldung(*freund_loeschen(engine, int(loesch_optionen[freund_name])))

# ===== Leihgabe eintragen =====
elif seite == "Leihgabe eintragen":
    st.header("📤 Leihgabe eintragen")
    buecher = lese_verfuegbare_buecher(engine)
    freunde = lese_freunde(engine)

    if buecher.empty:
        st.warning("Es ist gerade kein Buch verfügbar.")
        st.stop()

    buch_optionen = {
        f"{zeile.Titel} ({zeile.Autoren})": zeile.BuchID
        for zeile in buecher.itertuples()
    }
    freund_optionen = {
        f"{zeile.Vorname} {zeile.Nachname}": zeile.FreundID
        for zeile in freunde.itertuples()
    }

    with st.form("leihgabe_formular"):
        buch_name = st.selectbox("Buch", list(buch_optionen))
        freund_name = st.selectbox("Freund", list(freund_optionen))
        leihdauer = st.number_input("Leihdauer in Tagen", min_value=1, max_value=365, value=28)
        abgeschickt = st.form_submit_button("Leihgabe eintragen")

    if abgeschickt:
        zeige_meldung(
            *leihgabe_eintragen(
                engine,
                int(freund_optionen[freund_name]),
                int(buch_optionen[buch_name]),
                int(leihdauer),
            )
        )

# ===== Rückgabe eintragen =====
elif seite == "Rückgabe eintragen":
    st.header("📥 Rückgabe eintragen")
    offene = lese_offene_leihgaben(engine)

    if offene.empty:
        st.info("Es sind gerade keine Bücher verliehen.")
        st.stop()

    leih_optionen = {
        f"{zeile.Titel} – {zeile.Freund} "
        f"(fällig am {zeile.Faelligkeitsdatum.strftime('%d.%m.%Y')})": zeile.LeihID
        for zeile in offene.itertuples()
    }

    with st.form("rueckgabe_formular"):
        leih_name = st.selectbox("Welches Buch kommt zurück?", list(leih_optionen))
        abgeschickt = st.form_submit_button("Rückgabe eintragen")

    if abgeschickt:
        if rueckgabe_eintragen(engine, int(leih_optionen[leih_name])) == 1:
            st.success("Rückgabe wurde eingetragen. 🎉")
            st.balloons()
        else:
            st.error("Keine offene Leihgabe mit dieser ID gefunden.")

# ===== Bewertung abgeben =====
elif seite == "Bewertung abgeben":
    st.header("⭐ Bewertung abgeben")
    tab_neu, tab_alle = st.tabs(["⭐ Neue Bewertung", "📝 Alle Bewertungen"])

    with tab_neu:
        freund_optionen = {
            f"{zeile.Vorname} {zeile.Nachname}": zeile.FreundID
            for zeile in lese_freunde(engine).itertuples()
        }
        freund_name = st.selectbox("Wer bewertet?", list(freund_optionen), key="bewerter")
        geliehene = lese_buecher_eines_freundes(engine, int(freund_optionen[freund_name]))

        if geliehene.empty:
            st.info("Dieser Freund hat noch kein Buch geliehen und kann deshalb nichts bewerten.")
        else:
            buch_optionen = {zeile.Titel: zeile.BuchID for zeile in geliehene.itertuples()}
            with st.form("bewertung_formular"):
                buch_name = st.selectbox("Welches Buch?", list(buch_optionen))
                sterne = st.radio(
                    "Sterne",
                    [5, 4, 3, 2, 1],
                    index=1,
                    horizontal=True,
                    format_func=lambda anzahl: "⭐" * anzahl,
                )
                kommentar = st.text_area(
                    "Kommentar (optional)", placeholder="Wie war das Buch?", max_chars=500
                )
                abgeschickt = st.form_submit_button("Bewertung abschicken")

            if abgeschickt:
                erfolg, meldung = bewertung_abgeben(
                    engine,
                    int(freund_optionen[freund_name]),
                    int(buch_optionen[buch_name]),
                    int(sterne),
                    kommentar,
                )
                zeige_meldung(erfolg, meldung)
                if erfolg:
                    st.balloons()

    with tab_alle:
        bewertungen = lese_bewertungen(engine)
        if bewertungen.empty:
            st.info("Es gibt noch keine Bewertungen.")
        else:
            anzeige = bewertungen.copy()
            anzeige["Sterne"] = anzeige["Sterne"].map(lambda anzahl: "⭐" * int(anzahl))
            st.caption(f"{len(anzeige)} Bewertungen")
            st.dataframe(anzeige, hide_index=True)