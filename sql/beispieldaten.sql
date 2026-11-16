USE lianes_bibliothek;

-- Genres (GenreID 1-8)
INSERT INTO Genres (Name) VALUES
('Roman'),
('Klassiker'),
('Fantasy'),
('Krimi'),
('Horror'),
('Science-Fiction'),
('Sachbuch'),
('Historischer Roman');

-- Standorte (StandortID 1-4)
INSERT INTO Standorte (Bezeichnung) VALUES
('Regal Schlafzimmer'),
('Regal Wohnzimmer'),
('Regal im Büro'),
('Bücherkiste Keller');

-- Autoren (AutorID 1-42)
INSERT INTO Autoren (Vorname, Nachname) VALUES
('Franz', 'Kafka'),
('Michael', 'Ende'),
('Cornelia', 'Funke'),
('Patrick', 'Süskind'),
('Bernhard', 'Schlink'),
('Max', 'Frisch'),
('Friedrich', 'Dürrenmatt'),
('Daniel', 'Kehlmann'),
('Jostein', 'Gaarder'),
('Paulo', 'Coelho'),
('Stephen', 'King'),
('Bram', 'Stoker'),
('Mary', 'Shelley'),
('Umberto', 'Eco'),
('Ken', 'Follett'),
('J. R. R.', 'Tolkien'),
('J. K.', 'Rowling'),
('Douglas', 'Adams'),
('Frank', 'Herbert'),
('George', 'Orwell'),
('Ray', 'Bradbury'),
('William', 'Gibson'),
('Andy', 'Weir'),
('Margaret', 'Atwood'),
('Agatha', 'Christie'),
('Arthur', 'Conan Doyle'),
('Stieg', 'Larsson'),
('Dan', 'Brown'),
('Thomas', 'Harris'),
('Gillian', 'Flynn'),
('Yuval Noah', 'Harari'),
('Stephen', 'Hawking'),
('Daniel', 'Kahneman'),
('Steven', 'Levitt'),
('Stephen', 'Dubner'),
('J. D.', 'Salinger'),
('Ernest', 'Hemingway'),
('Jane', 'Austen'),
('Daniel', 'Glattauer'),
('George R. R.', 'Martin'),
('Terry', 'Pratchett'),
('Neil', 'Gaiman');

-- Bücher (BuchID 1-50)
-- ISBNs sind erfunden (formal gültige Prüfziffer); Verleihbar = 0 bedeutet Eigengebrauch
INSERT INTO Buecher (ISBN, Titel, GenreID, StandortID, Verleihbar) VALUES
('9783900000011', 'Die Verwandlung', 2, 1, 1),
('9783900000028', 'Der Prozess', 2, 1, 1),
('9783900000035', 'Momo', 3, 2, 1),
('9783900000042', 'Die unendliche Geschichte', 3, 2, 1),
('9783900000059', 'Jim Knopf und Lukas der Lokomotivführer', 3, 2, 1),
('9783900000066', 'Tintenherz', 3, 2, 1),
('9783900000073', 'Das Parfum', 5, 4, 1),
('9783900000080', 'Der Vorleser', 1, 1, 1),
('9783900000097', 'Homo Faber', 1, 1, 1),
('9783900000103', 'Die Physiker', 2, 1, 1),
('9783900000110', 'Die Vermessung der Welt', 8, 2, 1),
('9783900000127', 'Sophies Welt', 1, 1, 1),
('9783900000134', 'Der Alchimist', 1, 1, 1),
('9783900000141', 'Es', 5, 4, 1),
('9783900000158', 'Shining', 5, 4, 1),
('9783900000165', 'Dracula', 5, 4, 1),
('9783900000172', 'Frankenstein', 5, 4, 1),
('9783900000189', 'Der Name der Rose', 8, 2, 1),
('9783900000196', 'Die Säulen der Erde', 8, 2, 1),
('9783900000202', 'Der Herr der Ringe', 3, 2, 0),
('9783900000219', 'Der Hobbit', 3, 2, 1),
('9783900000226', 'Harry Potter und der Stein der Weisen', 3, 2, 1),
('9783900000233', 'Per Anhalter durch die Galaxis', 6, 2, 1),
('9783900000240', 'Dune – Der Wüstenplanet', 6, 2, 0),
('9783900000257', '1984', 6, 2, 1),
('9783900000264', 'Farm der Tiere', 2, 1, 1),
('9783900000271', 'Fahrenheit 451', 6, 2, 1),
('9783900000288', 'Neuromancer', 6, 2, 1),
('9783900000295', 'Der Marsianer', 6, 2, 1),
('9783900000301', 'Der Report der Magd', 6, 2, 1),
('9783900000318', 'Mord im Orient-Express', 4, 1, 1),
('9783900000325', 'Und dann gab''s keines mehr', 4, 1, 1),
('9783900000332', 'Der Hund der Baskervilles', 4, 1, 1),
('9783900000349', 'Verblendung', 4, 1, 1),
('9783900000356', 'Sakrileg', 4, 1, 1),
('9783900000363', 'Das Schweigen der Lämmer', 4, 1, 1),
('9783900000370', 'Gone Girl', 4, 1, 1),
('9783900000387', 'Eine kurze Geschichte der Menschheit', 7, 3, 1),
('9783900000394', 'Eine kurze Geschichte der Zeit', 7, 3, 0),
('9783900000400', 'Schnelles Denken, langsames Denken', 7, 3, 1),
('9783900000417', 'Freakonomics', 7, 3, 1),
('9783900000424', 'Homo Deus', 7, 3, 1),
('9783900000431', 'Der Fänger im Roggen', 2, 1, 1),
('9783900000448', 'Der alte Mann und das Meer', 2, 1, 1),
('9783900000455', 'Stolz und Vorurteil', 2, 1, 1),
('9783900000462', 'Gut gegen Nordwind', 1, 1, 1),
('9783900000479', 'Das Lied von Eis und Feuer', 3, 2, 1),
('9783900000486', 'Die Farben der Magie', 3, 2, 1),
('9783900000493', 'Ein gutes Omen', 3, 2, 1),
('9783900000509', 'Der Ozean am Ende der Straße', 3, 2, 1);

-- Verknüpfung Buch <-> Autor (BuchID, AutorID)
INSERT INTO Buch_Autor (BuchID, AutorID) VALUES
(1, 1),
(2, 1),
(3, 2),
(4, 2),
(5, 2),
(6, 3),
(7, 4),
(8, 5),
(9, 6),
(10, 7),
(11, 8),
(12, 9),
(13, 10),
(14, 11),
(15, 11),
(16, 12),
(17, 13),
(18, 14),
(19, 15),
(20, 16),
(21, 16),
(22, 17),
(23, 18),
(24, 19),
(25, 20),
(26, 20),
(27, 21),
(28, 22),
(29, 23),
(30, 24),
(31, 25),
(32, 25),
(33, 26),
(34, 27),
(35, 28),
(36, 29),
(37, 30),
(38, 31),
(39, 32),
(40, 33),
(41, 34),
(41, 35),
(42, 31),
(43, 36),
(44, 37),
(45, 38),
(46, 39),
(47, 40),
(48, 41),
(49, 41),
(49, 42),
(50, 42);

-- Freunde (FreundID 1-8), Telefonnummern und E-Mails sind erfunden
INSERT INTO Freunde (Vorname, Nachname, Telefon, Email) VALUES
('Anna', 'Becker', '0151 1234501', 'anna.becker@example.com'),
('Max', 'Schneider', '0151 1234502', 'max.schneider@example.com'),
('Julia', 'Fischer', '0151 1234503', 'julia.fischer@example.com'),
('Tom', 'Weber', '0151 1234504', 'tom.weber@example.com'),
('Sabine', 'Wagner', '0151 1234505', 'sabine.wagner@example.com'),
('Jonas', 'Hoffmann', '0151 1234506', 'jonas.hoffmann@example.com'),
('Lena', 'Köhler', '0151 1234507', 'lena.koehler@example.com'),
('Markus', 'Braun', '0151 1234508', 'markus.braun@example.com');

-- Leihgaben: FreundID, BuchID, Verleihdatum, Faelligkeitsdatum, Rueckgabedatum
-- NULL bei Rueckgabedatum = Buch ist noch nicht zurück
INSERT INTO Leihgaben (FreundID, BuchID, Verleihdatum, Faelligkeitsdatum, Rueckgabedatum) VALUES
(3, 22, '2026-06-20', '2026-07-18', '2026-07-15'),  -- Harry Potter: pünktlich zurück
(1, 3, '2026-07-02', '2026-07-30', '2026-07-28'),   -- Momo: pünktlich zurück
(2, 7, '2026-07-10', '2026-08-07', '2026-08-20'),   -- Das Parfum: zu spät zurückgegeben
(4, 31, '2026-08-01', '2026-08-29', '2026-08-27'),  -- Mord im Orient-Express: pünktlich zurück
(5, 14, '2026-08-12', '2026-09-09', '2026-09-09'),  -- Es: am Fälligkeitstag zurück
(6, 38, '2026-08-25', '2026-09-22', '2026-09-18'),  -- Eine kurze Geschichte der Menschheit: pünktlich zurück
(1, 23, '2026-09-05', '2026-10-03', NULL),          -- Per Anhalter durch die Galaxis: überfällig
(7, 40, '2026-09-10', '2026-10-08', '2026-10-06'),  -- Schnelles Denken, langsames Denken: pünktlich zurück
(3, 34, '2026-09-14', '2026-10-12', NULL),          -- Verblendung: überfällig
(8, 25, '2026-09-20', '2026-10-18', NULL),          -- 1984: überfällig
(2, 3, '2026-10-02', '2026-10-30', '2026-10-29'),   -- Momo: erneut verliehen, pünktlich zurück
(6, 11, '2026-10-15', '2026-12-01', NULL),          -- Die Vermessung der Welt: noch nicht fällig
(4, 29, '2026-10-22', '2026-12-03', NULL),          -- Der Marsianer: noch nicht fällig
(5, 48, '2026-10-28', '2026-12-09', NULL),          -- Die Farben der Magie: noch nicht fällig
(7, 6, '2026-11-01', '2026-12-13', NULL),           -- Tintenherz: noch nicht fällig
(2, 15, '2026-09-08', '2026-10-06', NULL),          -- Shining: überfällig
(5, 2, '2026-09-25', '2026-10-23', NULL),           -- Der Prozess: überfällig
(8, 19, '2026-10-01', '2026-10-29', NULL),          -- Die Säulen der Erde: überfällig
(3, 13, '2026-10-20', '2026-12-08', NULL),          -- Der Alchimist: noch nicht fällig
(4, 36, '2026-10-24', '2026-12-05', NULL),          -- Das Schweigen der Lämmer: noch nicht fällig
(6, 41, '2026-10-30', '2026-12-10', NULL),          -- Freakonomics: noch nicht fällig
(1, 9, '2026-11-02', '2026-12-14', NULL),           -- Homo Faber: noch nicht fällig
(7, 45, '2026-11-04', '2026-12-16', NULL);          -- Stolz und Vorurteil: noch nicht fällig

-- Bewertungen: FreundID, BuchID, Sterne, Kommentar, Datum (nur Bücher, die der Freund geliehen hatte)
INSERT INTO Bewertungen (FreundID, BuchID, Sterne, Kommentar, Datum) VALUES
(3, 22, 5, 'Zauberhaft, ich habe es in zwei Tagen gelesen!', '2026-07-16'),
(1, 3, 5, 'Ein Klassiker, der nie alt wird.', '2026-07-29'),
(2, 7, 4, 'Düster und sehr atmosphärisch.', '2026-08-21'),
(4, 31, 4, 'Spannend bis zur letzten Seite.', '2026-08-28'),
(5, 14, 3, 'Gut, aber ziemlich lang.', '2026-09-10'),
(6, 38, 5, 'Hat meinen Blick auf die Geschichte verändert.', '2026-09-19'),
(7, 40, 4, 'Dicht, aber lehrreich.', '2026-10-07'),
(2, 3, 4, 'Auch beim zweiten Mal schön.', '2026-10-30'),
(1, 23, 5, 'Zum Totlachen!', '2026-10-20'),
(8, 25, 4, 'Beklemmend aktuell.', '2026-10-10'),
(3, 34, 5, 'Konnte es nicht weglegen.', '2026-10-12'),
(6, 11, 3, NULL, '2026-11-05'),
(7, 6, 5, 'Wunderschön, mein Lieblingsbuch dieses Jahr.', '2026-11-10');

-- Kontrolle 1: Gesamtübersicht über die View
SELECT * FROM v_buchuebersicht ORDER BY Status, Titel;

-- Kontrolle 2: Alle verliehenen und überfälligen Bücher, wer sie hat und wann sie fällig sind
SELECT Titel, Status, Vorname, Nachname, Telefon, Faelligkeitsdatum
FROM v_buchuebersicht
WHERE Status IN ('verliehen', 'überfällig')
ORDER BY Faelligkeitsdatum;

-- Kontrolle 3: Alle Horror-Bücher mit aktuellem Standort und Status
SELECT Titel, Autoren, AktuellerStandort, Status
FROM v_buchuebersicht
WHERE Genre = 'Horror';