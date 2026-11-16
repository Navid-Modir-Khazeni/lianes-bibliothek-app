-- Datenbank (Schema) für Lianes Bibliothek anlegen und auswählen
CREATE SCHEMA lianes_bibliothek;
USE lianes_bibliothek;

-- Nachschlagetabelle: Genres (z. B. Fantasy, Krimi, Horror)
CREATE TABLE Genres (
    GenreID INT AUTO_INCREMENT PRIMARY KEY,
    Name    VARCHAR(50) NOT NULL UNIQUE          -- jedes Genre nur einmal
);

-- Nachschlagetabelle: Standorte (wo steht das Buch normalerweise?)
CREATE TABLE Standorte (
    StandortID  INT AUTO_INCREMENT PRIMARY KEY,
    Bezeichnung VARCHAR(100) NOT NULL UNIQUE     -- z. B. 'Regal Schlafzimmer'
);

-- Autoren
CREATE TABLE Autoren (
    AutorID  INT AUTO_INCREMENT PRIMARY KEY,
    Vorname  VARCHAR(100) NOT NULL,
    Nachname VARCHAR(100) NOT NULL,
    UNIQUE (Vorname, Nachname)                   -- derselbe Autor nicht doppelt
);

-- Bücher (eine Zeile = eine konkrete Ausgabe im Regal)
CREATE TABLE Buecher (
    BuchID     INT AUTO_INCREMENT PRIMARY KEY,
    ISBN       VARCHAR(13) UNIQUE,               -- ISBN-13 ohne Bindestriche; optional (ältere Bücher haben oft keine)
    Titel      VARCHAR(255) NOT NULL,
    GenreID    INT NOT NULL,
    StandortID INT NOT NULL,                     -- Heimatplatz des Buchs
    Verleihbar TINYINT(1) NOT NULL DEFAULT 1,    -- 1 = darf verliehen werden, 0 = Eigengebrauch

    FOREIGN KEY (GenreID)    REFERENCES Genres(GenreID),
    FOREIGN KEY (StandortID) REFERENCES Standorte(StandortID),
    CHECK (Verleihbar IN (0, 1))
);

-- Brückentabelle: Ein Buch kann mehrere Autoren haben, ein Autor mehrere Bücher
CREATE TABLE Buch_Autor (
    BuchID  INT NOT NULL,
    AutorID INT NOT NULL,
    PRIMARY KEY (BuchID, AutorID),               -- zusammengesetzter Primärschlüssel

    -- Wird ein Buch oder Autor gelöscht, verschwinden auch die Verknüpfungen
    FOREIGN KEY (BuchID)  REFERENCES Buecher(BuchID) ON DELETE CASCADE,
    FOREIGN KEY (AutorID) REFERENCES Autoren(AutorID) ON DELETE CASCADE
);

-- Freunde, die sich Bücher leihen
CREATE TABLE Freunde (
    FreundID INT AUTO_INCREMENT PRIMARY KEY,
    Vorname  VARCHAR(100) NOT NULL,
    Nachname VARCHAR(100) NOT NULL,
    Telefon  VARCHAR(30),                        -- VARCHAR, damit führende Null und + erhalten bleiben
    Email    VARCHAR(255)
);

-- Leihgaben (eine Zeile = ein Buch, das an einen Freund verliehen wurde)
CREATE TABLE Leihgaben (
    LeihID            INT AUTO_INCREMENT PRIMARY KEY,
    FreundID          INT NOT NULL,              -- an wen?
    BuchID            INT NOT NULL,              -- welches Buch?
    Verleihdatum      DATE NOT NULL,
    Faelligkeitsdatum DATE NOT NULL,             -- voraussichtliche Rückgabe
    Rueckgabedatum    DATE NULL,                 -- NULL = Buch ist noch nicht zurück

    -- Kein ON DELETE CASCADE: Die Leihhistorie soll erhalten bleiben
    FOREIGN KEY (FreundID) REFERENCES Freunde(FreundID),
    FOREIGN KEY (BuchID)   REFERENCES Buecher(BuchID),

    -- Datumslogik absichern
    CHECK (Faelligkeitsdatum >= Verleihdatum),
    CHECK (Rueckgabedatum IS NULL OR Rueckgabedatum >= Verleihdatum)
);

-- Bewertungen (ein Freund bewertet ein Buch, höchstens einmal pro Freund und Buch)
CREATE TABLE Bewertungen (
    BewertungID INT AUTO_INCREMENT PRIMARY KEY,
    FreundID    INT NOT NULL,
    BuchID      INT NOT NULL,
    Sterne      TINYINT NOT NULL,                -- 1 bis 5
    Kommentar   VARCHAR(500),                    -- optional
    Datum       DATE NOT NULL,

    UNIQUE (FreundID, BuchID),                   -- pro Freund und Buch nur eine Bewertung

    FOREIGN KEY (FreundID) REFERENCES Freunde(FreundID),
    FOREIGN KEY (BuchID)   REFERENCES Buecher(BuchID),
    CHECK (Sterne BETWEEN 1 AND 5)
);

-- Bewertungen (ein Freund bewertet ein Buch, höchstens einmal pro Freund und Buch)
CREATE TABLE Bewertungen (
    BewertungID INT AUTO_INCREMENT PRIMARY KEY,
    FreundID    INT NOT NULL,
    BuchID      INT NOT NULL,
    Sterne      TINYINT NOT NULL,                -- 1 bis 5
    Kommentar   VARCHAR(500),                    -- optional
    Datum       DATE NOT NULL,

    UNIQUE (FreundID, BuchID),                   -- pro Freund und Buch nur eine Bewertung

    FOREIGN KEY (FreundID) REFERENCES Freunde(FreundID),
    FOREIGN KEY (BuchID)   REFERENCES Buecher(BuchID),
    CHECK (Sterne BETWEEN 1 AND 5)
);

-- View: Übersicht mit berechnetem Status (wird nicht gespeichert, sondern bei jeder Abfrage neu berechnet)
CREATE VIEW v_buchuebersicht AS
SELECT
    b.BuchID,
    b.Titel,
    (SELECT GROUP_CONCAT(CONCAT(a.Vorname, ' ', a.Nachname) SEPARATOR ', ')
       FROM Buch_Autor ba
       JOIN Autoren a ON a.AutorID = ba.AutorID
      WHERE ba.BuchID = b.BuchID) AS Autoren,
    g.Name        AS Genre,
    s.Bezeichnung AS Heimatplatz,                    -- wo das Buch normalerweise steht
    CASE
        WHEN l.LeihID IS NOT NULL THEN CONCAT('bei ', f.Vorname, ' ', f.Nachname)
        ELSE s.Bezeichnung
    END           AS AktuellerStandort,              -- wo das Buch gerade wirklich ist
    CASE
        WHEN b.Verleihbar = 0                        THEN 'Eigengebrauch'
        WHEN l.LeihID IS NULL                        THEN 'verfügbar'
        WHEN l.Faelligkeitsdatum < CURDATE()         THEN 'überfällig'
        ELSE 'verliehen'
    END           AS Status,
    f.Vorname,                                       -- Freund, der das Buch gerade hat (sonst NULL)
    f.Nachname,
    f.Telefon,
    l.Faelligkeitsdatum,
    (SELECT ROUND(AVG(be.Sterne), 1) FROM Bewertungen be WHERE be.BuchID = b.BuchID) AS Bewertung,
    (SELECT COUNT(*) FROM Bewertungen be WHERE be.BuchID = b.BuchID) AS Anzahl_Bewertungen
FROM Buecher b
JOIN Genres    g ON g.GenreID    = b.GenreID
JOIN Standorte s ON s.StandortID = b.StandortID
LEFT JOIN Leihgaben l ON l.BuchID = b.BuchID AND l.Rueckgabedatum IS NULL
LEFT JOIN Freunde   f ON f.FreundID = l.FreundID;