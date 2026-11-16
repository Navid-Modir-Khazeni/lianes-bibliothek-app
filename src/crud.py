from getpass import getpass

import pandas as pd
from sqlalchemy import URL, create_engine, text


def verbindung_herstellen(passwort=None):
    """Gibt die Verbindung (engine) zur Datenbank zurück.

    Ohne Passwort wird im Terminal danach gefragt (getpass).
    """
    if passwort is None:
        passwort = getpass("MySQL-Passwort: ")
    url = URL.create(
        drivername="mysql+pymysql",
        username="root",
        password=passwort,
        host="127.0.0.1",
        port=3306,
        database="lianes_bibliothek",
    )
    return create_engine(url)


def lese_uebersicht(engine):
    """READ: Gibt die komplette Bücherübersicht als Tabelle (DataFrame) zurück."""
    abfrage = text(
        "SELECT Titel, Autoren, Genre, AktuellerStandort, Status, Faelligkeitsdatum, "
        "CONCAT_WS(' ', Vorname, Nachname) AS Ausgeliehen_von, Telefon, "
        "Bewertung, Anzahl_Bewertungen "
        "FROM v_buchuebersicht ORDER BY Titel"
    )
    return pd.read_sql(abfrage, con=engine)


def lese_offene_leihgaben(engine):
    """READ: Gibt alle noch nicht zurückgegebenen Leihgaben (mit LeihID) zurück."""
    abfrage = text(
        "SELECT l.LeihID, b.Titel, CONCAT(f.Vorname, ' ', f.Nachname) AS Freund, "
        "l.Verleihdatum, l.Faelligkeitsdatum "
        "FROM Leihgaben l "
        "JOIN Buecher b ON b.BuchID = l.BuchID "
        "JOIN Freunde f ON f.FreundID = l.FreundID "
        "WHERE l.Rueckgabedatum IS NULL "
        "ORDER BY l.Faelligkeitsdatum"
    )
    return pd.read_sql(abfrage, con=engine)


def rueckgabe_eintragen(engine, leih_id):
    """UPDATE: Setzt das Rückgabedatum auf heute. Gibt die Anzahl geänderter Zeilen zurück."""
    befehl = text(
        "UPDATE Leihgaben SET Rueckgabedatum = CURDATE() "
        "WHERE LeihID = :leih_id AND Rueckgabedatum IS NULL"
    )
    with engine.begin() as verbindung:
        ergebnis = verbindung.execute(befehl, {"leih_id": leih_id})
        return ergebnis.rowcount


def lese_verfuegbare_buecher(engine):
    """READ: Gibt alle Bücher zurück, die gerade verliehen werden könnten (mit BuchID)."""
    abfrage = text(
        "SELECT BuchID, Titel, Autoren, AktuellerStandort "
        "FROM v_buchuebersicht WHERE Status = 'verfügbar' ORDER BY Titel"
    )
    return pd.read_sql(abfrage, con=engine)


def lese_freunde(engine):
    """READ: Gibt alle Freunde (mit FreundID) zurück."""
    abfrage = text(
        "SELECT FreundID, Vorname, Nachname, Telefon FROM Freunde ORDER BY Nachname"
    )
    return pd.read_sql(abfrage, con=engine)


def leihgabe_eintragen(engine, freund_id, buch_id, leihdauer_tage=28):
    """CREATE: Trägt eine neue Leihgabe ein (Verleihdatum = heute).

    Prüft vorher, ob das Buch verfügbar ist. Gibt (True/False, Meldung) zurück.
    """
    with engine.begin() as verbindung:
        status = verbindung.execute(
            text("SELECT Status FROM v_buchuebersicht WHERE BuchID = :buch_id"),
            {"buch_id": buch_id},
        ).scalar()
        if status is None:
            return False, "Dieses Buch gibt es nicht."
        if status != "verfügbar":
            return False, f"Das Buch ist nicht verfügbar (Status: {status})."

        freund_vorhanden = verbindung.execute(
            text("SELECT COUNT(*) FROM Freunde WHERE FreundID = :freund_id"),
            {"freund_id": freund_id},
        ).scalar()
        if freund_vorhanden == 0:
            return False, "Diesen Freund gibt es nicht."

        verbindung.execute(
            text(
                "INSERT INTO Leihgaben (FreundID, BuchID, Verleihdatum, Faelligkeitsdatum) "
                "VALUES (:freund_id, :buch_id, CURDATE(), "
                "DATE_ADD(CURDATE(), INTERVAL :tage DAY))"
            ),
            {"freund_id": freund_id, "buch_id": buch_id, "tage": leihdauer_tage},
        )
    return True, "Leihgabe wurde eingetragen."


def lese_buecher(engine):
    """READ: Gibt alle Bücher (mit BuchID) in der Reihenfolge der BuchID zurück."""
    abfrage = text("SELECT BuchID, Titel, ISBN FROM Buecher ORDER BY BuchID")
    return pd.read_sql(abfrage, con=engine)


def buch_loeschen(engine, buch_id):
    """DELETE: Löscht ein Buch samt Autoren-Verknüpfungen, aber nur, wenn es nie verliehen wurde.

    Gibt (True/False, Meldung) zurück.
    """
    with engine.begin() as verbindung:
        titel = verbindung.execute(
            text("SELECT Titel FROM Buecher WHERE BuchID = :buch_id"),
            {"buch_id": buch_id},
        ).scalar()
        if titel is None:
            return False, "Dieses Buch gibt es nicht."

        anzahl = verbindung.execute(
            text("SELECT COUNT(*) FROM Leihgaben WHERE BuchID = :buch_id"),
            {"buch_id": buch_id},
        ).scalar()
        if anzahl > 0:
            return False, (
                f"'{titel}' kann nicht gelöscht werden: Es wurde {anzahl}-mal verliehen "
                "(die Leihhistorie bleibt erhalten)."
            )

        verbindung.execute(
            text("DELETE FROM Buecher WHERE BuchID = :buch_id"),
            {"buch_id": buch_id},
        )
    return True, f"'{titel}' wurde gelöscht."


def lese_genres(engine):
    """READ: Gibt alle Genres (mit GenreID) zurück."""
    return pd.read_sql(text("SELECT GenreID, Name FROM Genres ORDER BY Name"), con=engine)


def lese_standorte(engine):
    """READ: Gibt alle Standorte (mit StandortID) zurück."""
    abfrage = text("SELECT StandortID, Bezeichnung FROM Standorte ORDER BY Bezeichnung")
    return pd.read_sql(abfrage, con=engine)


def lese_autoren(engine):
    """READ: Gibt alle Autoren (mit AutorID) zurück."""
    abfrage = text(
        "SELECT AutorID, Vorname, Nachname FROM Autoren ORDER BY Nachname, Vorname"
    )
    return pd.read_sql(abfrage, con=engine)


def buch_hinzufuegen(
    engine, titel, isbn, autor_ids, neuer_autor, genre_id, standort_id, verleihbar
):
    """CREATE: Legt ein neues Buch samt Autoren-Verknüpfungen an.

    autor_ids: Liste der AutorIDs bereits vorhandener Autoren.
    neuer_autor: (Vorname, Nachname) eines neuen Autors oder None.
    Gibt (True/False, Meldung) zurück.
    """
    titel = titel.strip()
    if not titel:
        return False, "Bitte einen Titel eingeben."

    isbn = isbn.replace("-", "").replace(" ", "")
    if isbn and not (isbn.isdigit() and len(isbn) == 13):
        return False, "Die ISBN muss aus genau 13 Ziffern bestehen (oder leer bleiben)."

    if not autor_ids and neuer_autor is None:
        return False, "Bitte mindestens einen Autor auswählen oder neu eintragen."
    if neuer_autor is not None and not (neuer_autor[0] and neuer_autor[1]):
        return False, "Für einen neuen Autor bitte Vor- und Nachnamen eintragen."

    with engine.begin() as verbindung:
        if isbn:
            vorhanden = verbindung.execute(
                text("SELECT COUNT(*) FROM Buecher WHERE ISBN = :isbn"), {"isbn": isbn}
            ).scalar()
            if vorhanden > 0:
                return False, "Ein Buch mit dieser ISBN gibt es schon."

        alle_autor_ids = set(autor_ids)
        if neuer_autor is not None:
            vorname, nachname = neuer_autor
            autor_id = verbindung.execute(
                text("SELECT AutorID FROM Autoren WHERE Vorname = :v AND Nachname = :n"),
                {"v": vorname, "n": nachname},
            ).scalar()
            if autor_id is None:
                autor_id = verbindung.execute(
                    text("INSERT INTO Autoren (Vorname, Nachname) VALUES (:v, :n)"),
                    {"v": vorname, "n": nachname},
                ).lastrowid
            alle_autor_ids.add(autor_id)

        buch_id = verbindung.execute(
            text(
                "INSERT INTO Buecher (ISBN, Titel, GenreID, StandortID, Verleihbar) "
                "VALUES (:isbn, :titel, :genre_id, :standort_id, :verleihbar)"
            ),
            {
                "isbn": isbn or None,
                "titel": titel,
                "genre_id": genre_id,
                "standort_id": standort_id,
                "verleihbar": 1 if verleihbar else 0,
            },
        ).lastrowid

        for autor_id in alle_autor_ids:
            verbindung.execute(
                text("INSERT INTO Buch_Autor (BuchID, AutorID) VALUES (:buch_id, :autor_id)"),
                {"buch_id": buch_id, "autor_id": autor_id},
            )
    return True, f"'{titel}' wurde hinzugefügt."


def freund_hinzufuegen(engine, vorname, nachname, telefon, email):
    """CREATE: Legt einen neuen Freund an. Gibt (True/False, Meldung) zurück."""
    vorname = vorname.strip()
    nachname = nachname.strip()
    telefon = telefon.strip()
    email = email.strip()

    if not vorname or not nachname:
        return False, "Bitte Vor- und Nachnamen eingeben."
    if telefon and not all(zeichen in "0123456789 +-/()" for zeichen in telefon):
        return False, "Die Telefonnummer darf nur Ziffern, Leerzeichen und + - / ( ) enthalten."
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        return False, "Bitte eine gültige E-Mail-Adresse eingeben."

    with engine.begin() as verbindung:
        vorhanden = verbindung.execute(
            text("SELECT COUNT(*) FROM Freunde WHERE Vorname = :v AND Nachname = :n"),
            {"v": vorname, "n": nachname},
        ).scalar()
        if vorhanden > 0:
            return False, f"{vorname} {nachname} gibt es schon in der Freundesliste."

        verbindung.execute(
            text(
                "INSERT INTO Freunde (Vorname, Nachname, Telefon, Email) "
                "VALUES (:v, :n, :telefon, :email)"
            ),
            {"v": vorname, "n": nachname, "telefon": telefon or None, "email": email or None},
        )
    return True, f"{vorname} {nachname} wurde hinzugefügt."


def freund_loeschen(engine, freund_id):
    """DELETE: Löscht einen Freund, aber nur, wenn er nie ein Buch geliehen hat.

    Gibt (True/False, Meldung) zurück.
    """
    with engine.begin() as verbindung:
        zeile = verbindung.execute(
            text("SELECT Vorname, Nachname FROM Freunde WHERE FreundID = :freund_id"),
            {"freund_id": freund_id},
        ).first()
        if zeile is None:
            return False, "Diesen Freund gibt es nicht."
        name = f"{zeile[0]} {zeile[1]}"

        anzahl = verbindung.execute(
            text("SELECT COUNT(*) FROM Leihgaben WHERE FreundID = :freund_id"),
            {"freund_id": freund_id},
        ).scalar()
        if anzahl > 0:
            return False, (
                f"{name} kann nicht gelöscht werden: Es gibt {anzahl} Leihgabe(n) "
                "in der Leihhistorie, und die bleibt erhalten."
            )

        verbindung.execute(
            text("DELETE FROM Freunde WHERE FreundID = :freund_id"),
            {"freund_id": freund_id},
        )
    return True, f"{name} wurde gelöscht."


def lese_freunde_uebersicht(engine):
    """READ: Gibt alle Freunde mit Kontaktdaten und ihren aktuell geliehenen Büchern zurück."""
    abfrage = text(
        "SELECT CONCAT(f.Vorname, ' ', f.Nachname) AS Name, "
        "f.Telefon, "
        "f.Email AS `E-Mail`, "
        "COUNT(l.LeihID) AS Ausgeliehen, "
        "CAST(COALESCE(SUM(l.Faelligkeitsdatum < CURDATE()), 0) AS SIGNED) AS `Überfällig`, "
        "GROUP_CONCAT(b.Titel ORDER BY l.Faelligkeitsdatum SEPARATOR ', ') "
        "AS `Aktuell geliehene Bücher` "
        "FROM Freunde f "
        "LEFT JOIN Leihgaben l ON l.FreundID = f.FreundID AND l.Rueckgabedatum IS NULL "
        "LEFT JOIN Buecher b ON b.BuchID = l.BuchID "
        "GROUP BY f.FreundID, f.Vorname, f.Nachname, f.Telefon, f.Email "
        "ORDER BY f.Nachname, f.Vorname"
    )
    return pd.read_sql(abfrage, con=engine)


def lese_buecher_eines_freundes(engine, freund_id):
    """READ: Gibt alle Bücher zurück, die dieser Freund schon einmal geliehen hatte."""
    abfrage = text(
        "SELECT DISTINCT b.BuchID, b.Titel "
        "FROM Leihgaben l JOIN Buecher b ON b.BuchID = l.BuchID "
        "WHERE l.FreundID = :freund_id ORDER BY b.Titel"
    )
    return pd.read_sql(abfrage, con=engine, params={"freund_id": freund_id})


def lese_bewertungen(engine):
    """READ: Gibt alle Bewertungen zurück, die neuesten zuerst."""
    abfrage = text(
        "SELECT b.Titel, CONCAT(f.Vorname, ' ', f.Nachname) AS Freund, "
        "be.Sterne, be.Kommentar, be.Datum "
        "FROM Bewertungen be "
        "JOIN Buecher b ON b.BuchID = be.BuchID "
        "JOIN Freunde f ON f.FreundID = be.FreundID "
        "ORDER BY be.Datum DESC, be.BewertungID DESC"
    )
    return pd.read_sql(abfrage, con=engine)


def bewertung_abgeben(engine, freund_id, buch_id, sterne, kommentar):
    """CREATE/UPDATE: Speichert die Bewertung eines Freundes für ein Buch.

    Nur Bücher, die der Freund geliehen hatte, dürfen bewertet werden. Bewertet er
    dasselbe Buch noch einmal, wird seine alte Bewertung ersetzt.
    Gibt (True/False, Meldung) zurück.
    """
    if sterne not in (1, 2, 3, 4, 5):
        return False, "Bitte 1 bis 5 Sterne auswählen."
    kommentar = kommentar.strip()
    if len(kommentar) > 500:
        return False, "Der Kommentar darf höchstens 500 Zeichen lang sein."

    with engine.begin() as verbindung:
        geliehen = verbindung.execute(
            text("SELECT COUNT(*) FROM Leihgaben WHERE FreundID = :freund_id AND BuchID = :buch_id"),
            {"freund_id": freund_id, "buch_id": buch_id},
        ).scalar()
        if geliehen == 0:
            return False, "Dieser Freund hat das Buch nie geliehen und kann es nicht bewerten."

        ergebnis = verbindung.execute(
            text(
                "INSERT INTO Bewertungen (FreundID, BuchID, Sterne, Kommentar, Datum) "
                "VALUES (:freund_id, :buch_id, :sterne, :kommentar, CURDATE()) "
                "ON DUPLICATE KEY UPDATE Sterne = :sterne, Kommentar = :kommentar, Datum = CURDATE()"
            ),
            {
                "freund_id": freund_id,
                "buch_id": buch_id,
                "sterne": sterne,
                "kommentar": kommentar or None,
            },
        )
    if ergebnis.rowcount == 1:
        return True, "Bewertung wurde gespeichert."
    return True, "Die frühere Bewertung wurde aktualisiert."


if __name__ == "__main__":
    engine = verbindung_herstellen()
    print(lese_uebersicht(engine).to_string(index=False))
    engine.dispose()