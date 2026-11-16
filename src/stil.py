"""Styling für Lianes Bibliothek: Farben, Bücherregal-Hintergrund, Cover und Karten."""

import base64
import html
import io
import json
import random
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st

STATUS_EMOJI = {
    "verfügbar": "✅ verfügbar",
    "verliehen": "📖 verliehen",
    "überfällig": "⏰ überfällig",
    "Eigengebrauch": "🔒 Eigengebrauch",
}
STATUS_KLASSE = {
    "verfügbar": "gruen",
    "verliehen": "blau",
    "überfällig": "rot",
    "Eigengebrauch": "lila",
}
# Genre: (Farbe des Covers, Emoji auf dem Cover)
GENRE_STIL = {
    "Roman": ("#FF6B9D", "📖"),
    "Klassiker": ("#8E6CFF", "🏛️"),
    "Fantasy": ("#2EC4B6", "🧙"),
    "Krimi": ("#3D5A80", "🔍"),
    "Horror": ("#6A1B9A", "👻"),
    "Science-Fiction": ("#00A8E8", "🚀"),
    "Sachbuch": ("#FF9F1C", "🧠"),
    "Historischer Roman": ("#E4572E", "🏰"),
}


def _als_daten_uri(svg):
    """Verpackt eine SVG-Grafik so, dass sie direkt in HTML oder CSS stehen kann."""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


HINTERGRUND_FOTO = Path(__file__).with_name("hintergrund.jpg")


def regal_hintergrund():
    """Zeichnet ein klassisches Bücherregal (dunkles Holz, Buchrücken in Leder- und Stofffarben)."""
    zufall = random.Random(7)
    farben = [
        "#6D1A2B", "#1E4D3B", "#1F3556", "#5B3A21", "#B07D2B",
        "#2F5D62", "#4A2545", "#5C6B2E", "#8A3B1E", "#D9C9A3",
    ]
    breite_kachel, hoehe_regal = 900, 250
    teile = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{breite_kachel}" height="{hoehe_regal * 2}" '
        f'viewBox="0 0 {breite_kachel} {hoehe_regal * 2}">',
        "<defs>"
        '<linearGradient id="rund" x1="0" x2="1" y1="0" y2="0">'
        '<stop offset="0" stop-color="#000" stop-opacity="0.45"/>'
        '<stop offset="0.35" stop-color="#fff" stop-opacity="0.16"/>'
        '<stop offset="0.7" stop-color="#000" stop-opacity="0.12"/>'
        '<stop offset="1" stop-color="#000" stop-opacity="0.5"/></linearGradient>'
        '<linearGradient id="holz" x1="0" x2="0" y1="0" y2="1">'
        '<stop offset="0" stop-color="#8B5A2B"/><stop offset="0.15" stop-color="#6B4423"/>'
        '<stop offset="1" stop-color="#3B2412"/></linearGradient>'
        '<linearGradient id="schatten" x1="0" x2="0" y1="0" y2="1">'
        '<stop offset="0" stop-color="#000" stop-opacity="0.65"/>'
        '<stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
        "</defs>",
    ]
    for reihe in range(2):
        oben = reihe * hoehe_regal
        boden = oben + 222
        teile.append(f'<rect x="0" y="{oben}" width="{breite_kachel}" height="{hoehe_regal}" fill="#24150C"/>')
        x = 6
        while x < breite_kachel - 40:
            if zufall.random() < 0.08:  # kleine Lücke im Regal
                x += zufall.randint(14, 30)
                continue
            breite = zufall.randint(20, 44)
            hoehe = zufall.randint(115, 190)
            farbe = zufall.choice(farben)
            y = boden - hoehe
            kippen = ""
            if zufall.random() < 0.05:  # ein Buch lehnt sich an
                kippen = f' transform="rotate({zufall.choice([-7, 7])} {x + breite / 2} {boden})"'
            teile.append(f"<g{kippen}>")
            teile.append(f'<rect x="{x}" y="{y}" width="{breite}" height="{hoehe}" rx="3" fill="{farbe}"/>')
            teile.append(f'<rect x="{x}" y="{y}" width="{breite}" height="{hoehe}" rx="3" fill="url(#rund)"/>')
            teile.append(f'<rect x="{x}" y="{y + 12}" width="{breite}" height="4" fill="#C9A227" opacity="0.85"/>')
            teile.append(f'<rect x="{x}" y="{y + hoehe - 16}" width="{breite}" height="4" fill="#C9A227" opacity="0.85"/>')
            if zufall.random() < 0.55 and breite > 26:
                teile.append(
                    f'<rect x="{x + 5}" y="{y + hoehe * 0.35:.0f}" width="{breite - 10}" height="{hoehe * 0.25:.0f}" '
                    'rx="2" fill="#E8D9B0" opacity="0.8"/>'
                )
            teile.append("</g>")
            x += breite + zufall.randint(0, 2)
        teile.append(f'<rect x="0" y="{oben}" width="{breite_kachel}" height="46" fill="url(#schatten)"/>')
        teile.append(f'<rect x="0" y="{boden}" width="{breite_kachel}" height="{hoehe_regal - 222}" fill="url(#holz)"/>')
        teile.append(f'<rect x="0" y="{boden}" width="{breite_kachel}" height="3" fill="#B98A4E" opacity="0.7"/>')
    teile.append("</svg>")
    return "".join(teile)


@st.cache_resource
def _foto_als_daten_uri(pfad, aenderungszeit):
    """Verkleinert ein eigenes Hintergrundfoto, damit die Seite schnell bleibt."""
    from PIL import Image

    bild = Image.open(pfad).convert("RGB")
    bild.thumbnail((1800, 1200))
    puffer = io.BytesIO()
    bild.save(puffer, "JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(puffer.getvalue()).decode("ascii")


def hintergrund_css():
    """Gibt die CSS-Zeilen für den Seitenhintergrund zurück (Foto, falls vorhanden, sonst Zeichnung)."""
    if HINTERGRUND_FOTO.exists():
        adresse = _foto_als_daten_uri(str(HINTERGRUND_FOTO), HINTERGRUND_FOTO.stat().st_mtime)
        return (
            "background-image: linear-gradient(rgba(20, 10, 5, var(--abdunkeln, 0.5)), rgba(20, 10, 5, var(--abdunkeln, 0.5))), "
            f'url("{adresse}");'
            "background-size: cover; background-position: center; background-attachment: fixed;"
        )
    return (
        "background-image: linear-gradient(rgba(10, 5, 2, 0.25), rgba(10, 5, 2, 0.25)), "
        f'url("{_als_daten_uri(regal_hintergrund())}");'
        "background-size: 900px 500px;"
    )


def cover_uri(titel, autoren, genre):
    """Erzeugt ein buntes Buchcover (SVG) aus Titel, Autor und Genre."""
    farbe, emoji = GENRE_STIL.get(genre, ("#FF6B9D", "📚"))
    zeilen = textwrap.wrap(textwrap.shorten(titel, 60, placeholder="…"), width=14, break_long_words=False)[:4]
    groesse = max(9, min(16, int(100 / (0.6 * max(len(z) for z in zeilen)))))
    titel_svg = "".join(
        f'<text x="62" y="{82 + i * (groesse + 4)}" text-anchor="middle" font-size="{groesse}" '
        f'font-weight="900" fill="white">{html.escape(z)}</text>'
        for i, z in enumerate(zeilen)
    )
    zufall = random.Random(titel)
    punkte = "".join(
        f'<circle cx="{zufall.randint(15, 115)}" cy="{zufall.randint(10, 160)}" r="{zufall.randint(3, 9)}" '
        f'fill="white" opacity="0.18"/>'
        for _ in range(9)
    )
    autor = html.escape(textwrap.shorten(str(autoren), 22, placeholder="…"))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="124" height="176" viewBox="0 0 124 176" '
        'font-family="Trebuchet MS, Arial, sans-serif">'
        f'<rect width="124" height="176" rx="8" fill="{farbe}"/>'
        f"{punkte}"
        '<rect width="12" height="176" rx="4" fill="black" opacity="0.2"/>'
        '<rect x="22" y="10" width="92" height="3" rx="2" fill="white" opacity="0.7"/>'
        f'<text x="68" y="52" text-anchor="middle" font-size="30">{emoji}</text>'
        f"{titel_svg}"
        f'<text x="68" y="166" text-anchor="middle" font-size="10" font-weight="700" fill="white" opacity="0.9">{autor}</text>'
        "</svg>"
    )
    return _als_daten_uri(svg)


CACHE_DATEI = Path(__file__).with_name("cover-cache-v2.json")


def _hole_json(adresse):
    """Ruft eine Internetadresse ab und gibt die Antwort als Python-Daten zurück."""
    anfrage = Request(adresse, headers={"User-Agent": "LianesBibliothek/1.0 (Lernprojekt)"})
    with urlopen(anfrage, timeout=8) as antwort:
        return json.load(antwort)


def _woerter(text):
    """Zerlegt einen Titel in kleine Wörter ohne Satzzeichen (für den Vergleich)."""
    return {wort.strip(".,:;–-—()\"'!?").lower() for wort in text.split()}


def _passt(gesucht, gefunden):
    """Prüft grob, ob ein gefundener Titel zum gesuchten Titel passt."""
    gemeinsam = _woerter(gesucht) & _woerter(gefunden)
    return len(gemeinsam) >= max(1, len(_woerter(gesucht)) // 2)


def _suche_google_books(titel, autor):
    """Sucht ein Cover bei Google Books (gut für deutsche Ausgaben). Gibt die Adresse oder "" zurück."""
    nachname = autor.split()[-1] if autor.split() else ""
    for sprache in ("de", None):  # erst deutsche Ausgaben, dann alle Sprachen
        parameter = {
            "q": f'intitle:"{titel}" inauthor:{nachname}',
            "maxResults": 5,
            "printType": "books",
            "fields": "items(volumeInfo(title,imageLinks))",
        }
        if sprache:
            parameter["langRestrict"] = sprache
        daten = _hole_json("https://www.googleapis.com/books/v1/volumes?" + urlencode(parameter))
        for treffer in daten.get("items", []):
            info = treffer.get("volumeInfo", {})
            bild = info.get("imageLinks", {}).get("thumbnail")
            if bild and _passt(titel, info.get("title", "")):
                return bild.replace("http://", "https://").replace("&edge=curl", "")
    return ""


def _suche_open_library(titel, autor):
    """Sucht ein Cover bei Open Library. Gibt die Adresse oder "" zurück."""
    parameter = urlencode({"title": titel, "author": autor, "limit": 5, "fields": "cover_i"})
    daten = _hole_json("https://openlibrary.org/search.json?" + parameter)
    for treffer in daten.get("docs", []):
        if treffer.get("cover_i"):
            return f"https://covers.openlibrary.org/b/id/{treffer['cover_i']}-M.jpg"
    return ""


def _suche_cover(titel, autor):
    """Sucht zuerst bei Google Books, dann bei Open Library.

    Gibt die Bild-Adresse zurück oder "" (kein Cover gefunden).
    Wirft OSError oder ValueError, wenn die Suche nicht zuverlässig funktioniert hat.
    """
    google_fehler = False
    try:
        adresse = _suche_google_books(titel, autor)
    except (OSError, ValueError):
        adresse, google_fehler = "", True
    if adresse:
        return adresse
    adresse = _suche_open_library(titel, autor)
    if not adresse and google_fehler:
        raise OSError("Google Books war nicht erreichbar")  # nicht als 'kein Cover' merken
    return adresse


def lade_covers(uebersicht):
    """Gibt {Titel: Bild-Adresse} zurück ("" = kein echtes Cover gefunden).

    Jedes Buch wird nur einmal gesucht, das Ergebnis steht danach in der Datei cover-cache.json.
    """
    try:
        cache = json.loads(CACHE_DATEI.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}

    fehlend = []
    for zeile in uebersicht.itertuples():
        paar = (zeile.Titel, str(zeile.Autoren))
        if f"{paar[0]}|{paar[1]}" not in cache and paar not in fehlend:
            fehlend.append(paar)

    def suche(paar):
        try:
            return paar, _suche_cover(paar[0], paar[1].split(",")[0])
        except (OSError, ValueError):
            return paar, None  # Suche hat nicht geklappt, wird beim nächsten Mal erneut versucht

    if fehlend:
        erstes_ergebnis = suche(fehlend[0])
        ergebnisse = [erstes_ergebnis]
        if erstes_ergebnis[1] is not None:  # Internet funktioniert, den Rest suchen
            with ThreadPoolExecutor(max_workers=3) as helfer:
                ergebnisse += list(helfer.map(suche, fehlend[1:]))
        for paar, adresse in ergebnisse:
            if adresse is not None:
                cache[f"{paar[0]}|{paar[1]}"] = adresse
        try:
            CACHE_DATEI.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            pass

    return {zeile.Titel: cache.get(f"{zeile.Titel}|{zeile.Autoren}", "") for zeile in uebersicht.itertuples()}


def karten_html(uebersicht, covers=None):
    """Baut aus der Übersicht ein Bücherregal aus Karten mit Cover (HTML).

    covers: {Titel: Bild-Adresse}. Gibt es kein echtes Cover, wird ein gezeichnetes genommen.
    """
    covers = covers or {}
    karten = []
    for zeile in uebersicht.itertuples():
        klasse = STATUS_KLASSE.get(zeile.Status, "lila")
        status = html.escape(STATUS_EMOJI.get(zeile.Status, zeile.Status))
        ort = html.escape(str(zeile.AktuellerStandort))
        faellig = ""
        if pd.notna(zeile.Faelligkeitsdatum):
            faellig = f" · bis {zeile.Faelligkeitsdatum.strftime('%d.%m.%Y')}"
        bewertung = ""
        if "Bewertung" in uebersicht.columns and pd.notna(zeile.Bewertung):
            sterne_text = str(zeile.Bewertung).replace(".", ",")
            bewertung = f'<div class="autor">⭐ {sterne_text} ({zeile.Anzahl_Bewertungen})</div>'
        bild = covers.get(zeile.Titel) or cover_uri(zeile.Titel, zeile.Autoren, zeile.Genre)
        karten.append(
            '<div class="karte">'
            f'<img src="{html.escape(bild)}" alt="Cover" loading="lazy">'
            f'<div class="titel">{html.escape(zeile.Titel)}</div>'
            f'<div class="autor">{html.escape(str(zeile.Autoren))}</div>'
            f'{bewertung}'
            f'<span class="plakette {klasse}">{status}</span>'
            f'<div class="ort">📍 {ort}{faellig}</div>'
            "</div>"
        )
    return '<div class="regal">' + "".join(karten) + "</div>"


CSS = """
<style>
html { font-size: 17px; }
.stApp { __HINTERGRUND__ }
[data-testid="stHeader"] { background: transparent; }
.block-container {
    background: rgba(255, 251, 242, 0.97);
    color: #2B1B12;
    border: 3px solid #C9A227;
    border-radius: 18px;
    padding: 2rem 2.5rem !important;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 34px rgba(0, 0, 0, 0.45);
}
h1, h2, h3 {
    font-family: Georgia, "Palatino Linotype", "Times New Roman", serif !important;
    font-weight: 800 !important;
    color: #4A1020 !important;
}
.haupttitel {
    font-family: Georgia, "Palatino Linotype", "Times New Roman", serif;
    font-size: 3.2rem;
    font-weight: 800;
    color: #4A1020;
    margin: 0;
    padding-bottom: 6px;
    border-bottom: 4px solid #C9A227;
    display: inline-block;
}
.untertitel { font-family: Georgia, serif; font-size: 1.25rem; font-style: italic; color: #7B5B2A; margin-top: 8px; }
[data-testid="stWidgetLabel"] p { font-weight: 700; font-size: 1.05rem; color: #2B1B12; }
[data-testid="InputInstructions"] { display: none; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #3A0D1A, #6D1A2B); }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] .stRadio p {
    color: #FFF3D6 !important;
    font-weight: 700 !important;
    font-size: 1.05rem;
}
.stButton button, [data-testid="stFormSubmitButton"] button {
    background: #7B1E3A;
    color: #FFF3D6;
    font-weight: 800;
    border: 2px solid #C9A227;
    border-radius: 10px;
    padding: 0.55rem 1.8rem;
    transition: transform 0.15s, background 0.15s;
}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: #C9A227;
    color: #2B1B12;
    border-color: #7B1E3A;
    transform: translateY(-2px);
}
.regal { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 18px; margin-top: 10px; }
.karte {
    background: #FFF8E7;
    border: 2px solid #C9A227;
    border-radius: 14px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 5px 14px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s;
}
.karte:hover { transform: translateY(-5px); border-color: #7B1E3A; }
.karte img { width: 124px; height: 176px; object-fit: cover; border-radius: 6px; box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.35); }
.karte .titel { font-family: Georgia, serif; font-weight: 800; font-size: 1.05rem; margin-top: 8px; line-height: 1.2; color: #2B1B12; }
.karte .autor { font-size: 0.9rem; color: #6B5A45; margin-bottom: 4px; }
.karte .ort { font-size: 0.85rem; margin-top: 6px; color: #4A3B2A; }
.plakette { display: inline-block; padding: 3px 10px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; color: white; margin-top: 4px; }
.gruen { background: #2E7D4F; }
.blau { background: #2F5D9E; }
.rot { background: #B3261E; }
.lila { background: #6B4E9B; }
</style>
"""


def anwenden():
    """Schaltet das bunte Design für die ganze App ein."""
    css = CSS.replace("__HINTERGRUND__", hintergrund_css())
    st.markdown(css, unsafe_allow_html=True)  
    
START_CSS = """
<style>
.stApp { --abdunkeln: 0.18; }
.block-container {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    max-width: 1300px;
    padding-top: 7vh !important;
}
.start-titel {
    text-align: center;
    font-family: Georgia, "Palatino Linotype", "Times New Roman", serif;
    font-size: 4.2rem;
    font-weight: 800;
    color: #FFF3D6 !important;
    text-shadow: 0 3px 14px rgba(0, 0, 0, 0.9);
    margin: 0;
}
.start-untertitel {
    text-align: center;
    font-family: Georgia, serif;
    font-style: italic;
    font-size: 1.5rem;
    color: #FFF3D6;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
    margin: 6px 0 30px 0;
}
.start-abschnitt {
    text-align: center;
    color: #FFD97A;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95);
    margin: 26px 0 10px 0;
}
.st-key-menue [data-testid="stButton"], .st-key-menue .stButton,
.st-key-menue [data-testid="stElementContainer"] { width: 100% !important; }
.st-key-menue button {
    width: 100%;
    height: 110px;
    padding: 0 14px;
    white-space: normal !important;
    background: rgba(30, 12, 6, 0.78);
    border: 2px solid #C9A227;
    border-radius: 16px;
    backdrop-filter: blur(4px);
}
.st-key-menue button div, .st-key-menue [data-testid="stMarkdownContainer"] {
    overflow: visible !important;
}
.st-key-menue button p {
    font-family: Georgia, "Palatino Linotype", serif;
    font-weight: 800;
    font-size: 1.45rem;
    line-height: 1.2;
    text-align: center;
    color: #FFF3D6;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}
.st-key-menue button:hover {
    background: #C9A227;
    border-color: #FFF3D6;
    transform: translateY(-4px) scale(1.02);
}
.st-key-menue button:hover p { color: #2B1B12; }
[data-testid="stForm"] {
    background: rgba(30, 12, 6, 0.78);
    border: 2px solid #C9A227;
    border-radius: 16px;
    padding: 24px;
}
[data-testid="stForm"] [data-testid="stWidgetLabel"] p { color: #FFF3D6; }
</style>
"""


def anwenden_start():
    """Zusätzliches Design für die Startseite: Hintergrund frei, Menü als große Kacheln."""
    st.markdown(START_CSS, unsafe_allow_html=True)