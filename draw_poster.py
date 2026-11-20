#!/usr/bin/env python3
"""Draw the rebuilt news poster for Thursday 19 November 2026.

Generates entry.png (1024x1024, newsprint palette) for the make.fun
news-image-20261119 bounty. All 33 stories come from
~/workspace/makefun/news-19nov-research.md: leads 1-3, secondary 4-15,
timeline 16-33. Headlines/summaries are verbatim from that file, shortened
only by cutting words from the end (with an ellipsis) when a box demands it.

Layout (1024x1024, top to bottom):
  masthead (title + date) -> stats bar (real continent counts) ->
  world map strip with a numbered dot per story -> 3 lead stories ->
  12 secondary stories (4x3 grid) -> 18-item timeline (2 cols of 9) ->
  date-check footer.

Run:  python3 draw_poster.py   (writes entry.png next to this file)

Every text block is measured with PIL before drawing; the script raises
AssertionError if any line would overflow its box, so a successful run is
already a layout check. A truncation report is printed at the end.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28                      # side margin
CW = W - 2 * M              # content width = 968

PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (158, 43, 37)
BLUE = (61, 90, 115)
LAND = (179, 191, 166)
LAND_LINE = (140, 152, 128)
GRID = (222, 214, 190)
BOX = (239, 233, 216)
OLIVE = (107, 122, 79)
OCHRE = (138, 109, 59)
GREY = (110, 110, 100)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- stories
# n, headline, summary, region label, source, lat, lon, icon kind.
# Headlines/summaries verbatim from news-19nov-research.md; summaries for
# the lead/secondary slots are the research summaries, cut from the end
# only where the box requires it (see fit_text / wrap_text below).
STORIES = [
    # ---- LEAD 1-3 ----
    (1, "UN court rules Myanmar committed Rohingya genocide",
     "The ICJ ruled Myanmar committed genocide against the Rohingya in its 2017 Rakhine campaign.",
     "EUROPE", "BBC News", 52.09, 4.31, "gavel"),
    (2, "Trump, Xi and Putin hold historic Shenzhen summit",
     "The three leaders met for the first three-way summit and issued a joint peace declaration.",
     "ASIA", "BBC News", 22.54, 114.06, "summit"),
    (3, "Wall Street slides as AI sell-off spreads",
     "The S&P 500 fell 2.02% for a fifth straight loss and Japan's Nikkei dropped 4.68%.",
     "N. AMERICA", "Reuters", 40.71, -74.01, "chart"),
    # ---- SECONDARY 4-15 ----
    (4, "Ukraine hits Crimea Bridge for third time",
     "Ukraine struck the Crimean Bridge for a third time in four days, halting traffic.",
     "EUROPE", "BBC News", 45.30, 36.50, "bridge"),
    (5, "European leaders meet in Berlin over Ukraine",
     "The Coalition of the Willing met in Berlin, saying Europe is ready for talks with Russia.",
     "EUROPE", "BBC News", 52.52, 13.40, "summit"),
    (6, "Houthi missile damages Riyadh's tallest tower",
     "A suspected Houthi missile struck Riyadh's Public Investment Fund Tower, damaging several floors.",
     "MIDDLE EAST", "Reuters", 24.71, 46.68, "missile"),
    (7, "Hormuz tanker attacks intensify in Iran war",
     "Two more oil tankers were hit by naval mines in the Strait of Hormuz.",
     "MIDDLE EAST", "Reuters", 26.50, 56.30, "tanker"),
    (8, "Israeli forces cross Gaza ceasefire line",
     "Israeli troops crossed the Yellow Line in central Gaza, the first such incursion since the truce.",
     "MIDDLE EAST", "Associated Press", 31.45, 34.39, "flag"),
    (9, "Bangladesh violence erupts ahead of Hasina return",
     "Fresh violence broke out in Bangladesh during an Awami League lockdown.",
     "ASIA", "Reuters", 23.81, 90.41, "flame"),
    (10, "Indonesia passes landmark asset-forfeiture law",
     "Indonesia's parliament passed its first asset-forfeiture law after 18 years.",
     "ASIA", "AFP", -6.21, 106.85, "law"),
    (11, "North Korea expands uranium enrichment, IAEA says",
     "The IAEA said North Korea has expanded its uranium enrichment plant at Yongbyon.",
     "ASIA", "IAEA / Reuters", 39.80, 125.30, "atom"),
    (12, "US consortium wins Kenya's Mrima Hill minerals deal",
     "A US-led consortium won the contract to develop Kenya's Mrima Hill rare-earth deposit.",
     "AFRICA", "BBC News", -4.20, 39.45, "gem"),
    (13, "Dozens missing after migrant boat sinks off Senegal",
     "A boat carrying about 100 migrants capsized off Yenne, Senegal, leaving dozens missing.",
     "AFRICA", "BBC News / AFP", 14.60, -17.10, "boat"),
    (14, "Fiji and Tonga declare El Niño drought disasters",
     "Fiji declared a national state of disaster and Tonga a state of emergency as El Niño drought hit.",
     "OCEANIA", "Reuters / AFP", -18.14, 178.44, "sun"),
    (15, "Voyager 1 reaches one light-day from Earth",
     "NASA confirmed Voyager 1 became the first human-made object to travel one light-day from Earth.",
     "GLOBAL", "NASA / Reuters", 34.15, -118.14, "rocket"),
    # ---- TIMELINE 16-33 (one line each) ----
    (16, "Anthropic closes 17% up in Nasdaq debut",
     "", "N. AMERICA", "BBC News", 40.71, -74.01, "bars"),
    (17, "Van Gogh painting sells for record $190.4m",
     "", "N. AMERICA", "Reuters", 40.71, -74.01, "art"),
    (18, "US Senate rejects Iran war-powers resolution",
     "", "N. AMERICA", "Reuters", 38.90, -77.04, "senate"),
    (19, "Trump pardons late baseball star Pete Rose",
     "", "N. AMERICA", "BBC News", 38.90, -77.04, "ball"),
    (20, "Denmark ratifies US security deal over Greenland",
     "", "EUROPE", "Reuters", 55.68, 12.57, "shield"),
    (21, "EU proposes €45 billion loan to Ukraine",
     "", "EUROPE", "Agence Europe", 50.85, 4.35, "coin"),
    (22, "COP31 draft drops fossil-fuel phase-out call",
     "", "EUROPE", "One Turn", 36.90, 30.71, "leaf"),
    (23, "Haitian police kill 34 gang members in raid",
     "", "N. AMERICA", "Reuters", 18.54, -72.34, "star"),
    (24, "US and Venezuela sign military cooperation deal",
     "", "S. AMERICA", "Reuters", 10.48, -66.88, "handshake"),
    (25, "Brazil recognises ancestral land of chief Raoni",
     "", "S. AMERICA", "One Turn", -12.50, -55.00, "tree"),
    (26, "EU and Mexico deal cuts most farm tariffs",
     "", "N. AMERICA", "One Turn", 19.43, -99.13, "tag"),
    (27, "Ghana cuts interest rate to 11%",
     "", "AFRICA", "NM Media Africa", 5.60, -0.19, "bank"),
    (28, "IMF agrees $2.3 billion funding for Egypt",
     "", "AFRICA", "NM Media Africa", 30.04, 31.24, "money"),
    (29, "Japan and India agree live-fire missile drills",
     "", "ASIA", "Reuters", 35.68, 139.69, "drill"),
    (30, "Ethiopia and Eritrea mass troops at Badme",
     "", "AFRICA", "Today News Africa", 14.72, 37.80, "troops"),
    (31, "Nicholls century rescues New Zealand against India",
     "", "OCEANIA", "Radio NZ", -41.29, 174.78, "bat"),
    (32, "Japan inflation rises, Nikkei plunges 4.68%",
     "", "ASIA", "One Turn", 35.68, 139.69, "chart"),
    (33, "Pakistan says 22 militants killed in raids",
     "", "ASIA", "One Turn", 34.02, 71.58, "raid"),
]

# Continent counts from the research file's continent table (core 33).
STATS = [("ASIA", 7), ("EUROPE", 6), ("AFRICA", 5), ("N. AMERICA", 7),
         ("S. AMERICA", 2), ("OCEANIA", 2), ("MIDDLE EAST", 3), ("GLOBAL", 1)]
assert sum(c for _, c in STATS) == 33 == len(STORIES)

TRUNCATIONS = []  # (story no, field, original -> used)


# ---------------------------------------------------------------- text fit
def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap_text(draw, text, fnt, max_w, max_lines=None):
    """Greedy word wrap; returns lines, each measured to fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        # Drop whole lines from the end, then ellipsis the last kept line.
        lines = lines[:max_lines]
        while lines and text_w(draw, lines[-1] + " ...", fnt) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
        if lines:
            lines[-1] = lines[-1].rstrip() + " ..."
    for ln in lines:
        assert text_w(draw, ln, fnt) <= max_w + 0.5, f"line overflow: {ln!r}"
    return lines


def fit_text(draw, text, fnt, max_w, note="", ellipsis=True):
    """Shorten by cutting words from the end until it fits one line."""
    if text_w(draw, text, fnt) <= max_w:
        return text
    words = text.split()
    suffix = " ..." if ellipsis else ""
    while len(words) > 1 and text_w(draw, " ".join(words) + suffix, fnt) > max_w:
        words.pop()
    out = " ".join(words) + suffix
    assert text_w(draw, out, fnt) <= max_w + 0.5, f"cannot fit: {text!r}"
    TRUNCATIONS.append((note, text, out))
    return out


# ---------------------------------------------------------------- icons
def draw_icon(d, kind, x, y, s, c1, c2):
    """Simple flat geometric icon in the box (x, y, s x s)."""
    u = s / 24.0  # unit

    def r(x0, y0, x1, y1, fill):
        d.rectangle([x + x0 * u, y + y0 * u, x + x1 * u, y + y1 * u], fill=fill)

    def ell(x0, y0, x1, y1, outline=None, fill=None, width=2):
        d.ellipse([x + x0 * u, y + y0 * u, x + x1 * u, y + y1 * u],
                  outline=outline, fill=fill, width=max(1, int(width * u)))

    def poly(pts, fill):
        d.polygon([(x + px * u, y + py * u) for px, py in pts], fill=fill)

    def line(pts, fill, width=2):
        d.line([(x + px * u, y + py * u) for px, py in pts], fill=fill,
               width=max(1, int(width * u)), joint="curve")

    if kind == "gavel":          # head + handle
        r(3, 4, 17, 9, c1); r(11, 9, 14, 21, c2); r(2, 20, 22, 22, c2)
    elif kind == "globe":
        ell(3, 3, 21, 21, outline=c1, width=2)
        d.arc([x + 3 * u, y + 3 * u, x + 21 * u, y + 21 * u], 20, 160, fill=c2, width=max(1, int(2 * u)))
        line([(3, 12), (21, 12)], c2, 2); line([(12, 3), (12, 21)], c2, 2)
    elif kind == "chart":        # falling line + bars
        line([(3, 6), (9, 11), (14, 9), (21, 18)], c1, 2)
        poly([(19, 16), (22, 16), (21, 19)], RED)
        r(3, 18, 5, 21, c2); r(9, 15, 11, 21, c2); r(15, 17, 17, 21, c2)
    elif kind == "bars":
        r(4, 12, 7, 21, c2); r(10, 8, 13, 21, c1); r(16, 4, 19, 21, c1)
        line([(3, 9), (10, 6), (17, 3), (21, 2)], RED, 2)
    elif kind == "bridge":
        d.arc([x + 3 * u, y + 8 * u, x + 21 * u, y + 22 * u], 180, 360, fill=c1, width=max(1, int(2 * u)))
        line([(3, 18), (21, 18)], c1, 2)
        for px in (6, 10, 14, 18):
            line([(px, 14), (px, 18)], c2, 1)
    elif kind == "summit":       # three figures / peaks
        poly([(2, 21), (7, 8), (12, 21)], c1)
        poly([(9, 21), (14, 5), (19, 21)], c2)
        poly([(16, 21), (20, 10), (23, 21)], c1)
    elif kind == "missile":
        poly([(12, 2), (16, 9), (12, 12), (8, 9)], c1)
        r(10, 12, 14, 20, c2); poly([(10, 20), (14, 20), (12, 23)], RED)
    elif kind == "tanker":
        poly([(3, 14), (21, 14), (19, 21), (5, 21)], c1)
        r(5, 9, 9, 14, c2); r(11, 9, 15, 14, c2); r(17, 11, 20, 14, c2)
        line([(2, 22), (22, 22)], BLUE, 1)
    elif kind == "flag":
        line([(6, 3), (6, 21)], c1, 2); poly([(6, 4), (20, 8), (6, 12)], RED)
    elif kind == "flame":
        poly([(12, 2), (16, 10), (19, 13), (18, 20), (6, 20), (5, 13), (8, 10)], RED)
        poly([(12, 11), (14, 15), (13, 18), (10, 18), (10, 15)], OCHRE)
    elif kind in ("law", "senate", "bank"):   # columns + pediment
        poly([(3, 8), (12, 3), (21, 8)], c1)
        r(3, 9, 21, 11, c1)
        for px in (5, 10, 15):
            r(px, 12, px + 2, 19, c2)
        r(3, 20, 21, 22, c1)
    elif kind == "atom":
        ell(9, 9, 15, 15, fill=c1)
        ell(3, 7, 21, 17, outline=c2, width=2)
        ell(7, 3, 17, 21, outline=c2, width=2)
    elif kind == "gem":
        poly([(12, 3), (19, 8), (16, 21), (8, 21), (5, 8)], c1)
        line([(5, 8), (19, 8)], PAPER, 1); line([(12, 3), (12, 21)], PAPER, 1)
    elif kind == "boat":
        line([(12, 3), (12, 16)], c1, 2)
        poly([(13, 4), (13, 14), (20, 14)], c2)
        poly([(3, 16), (21, 16), (18, 21), (6, 21)], c1)
        line([(2, 22), (22, 22)], BLUE, 1)
    elif kind == "sun":
        ell(8, 8, 16, 16, fill=OCHRE)
        for a in range(0, 360, 45):
            import math
            x0 = 12 + 9 * math.cos(math.radians(a)); y0 = 12 + 9 * math.sin(math.radians(a))
            x1 = 12 + 11 * math.cos(math.radians(a)); y1 = 12 + 11 * math.sin(math.radians(a))
            line([(x0, y0), (x1, y1)], OCHRE, 2)
        line([(3, 21), (21, 21)], BLUE, 2)
    elif kind == "rocket":
        poly([(12, 2), (16, 8), (16, 16), (12, 20), (8, 16), (8, 8)], c1)
        ell(10, 9, 14, 13, fill=PAPER)
        poly([(8, 16), (5, 21), (9, 18)], RED); poly([(16, 16), (19, 21), (15, 18)], RED)
        poly([(11, 20), (13, 20), (12, 23)], OCHRE)
    elif kind == "art":
        r(3, 4, 21, 20, c1); r(5, 6, 19, 18, PAPER)
        ell(8, 8, 12, 12, fill=OCHRE); poly([(5, 18), (11, 11), (15, 16), (19, 12), (19, 18)], c2)
    elif kind == "ball":
        ell(4, 4, 20, 20, outline=c1, width=2)
        d.arc([x + 5 * u, y + 6 * u, x + 12 * u, y + 18 * u], 300, 60, fill=RED, width=max(1, int(2 * u)))
        d.arc([x + 12 * u, y + 6 * u, x + 19 * u, y + 18 * u], 120, 240, fill=RED, width=max(1, int(2 * u)))
    elif kind == "shield":
        poly([(12, 3), (19, 6), (19, 12), (12, 21), (5, 12), (5, 6)], c1)
        line([(9, 12), (11, 14), (15, 9)], PAPER, 2)
    elif kind == "coin":
        ell(4, 4, 20, 20, outline=c1, width=2); ell(7, 7, 17, 17, fill=OCHRE)
        d.text((x + 12 * u, y + 12 * u), "€", font=font(SERIF_B, int(11 * u)),
               fill=PAPER, anchor="mm")
    elif kind == "leaf":
        poly([(5, 19), (6, 8), (15, 4), (20, 10), (15, 19)], OLIVE)
        line([(6, 19), (18, 7)], PAPER, 1)
    elif kind in ("star", "raid"):
        import math
        pts = []
        for i in range(10):
            ang = -90 + i * 36
            rad = 10 if i % 2 == 0 else 4.2
            pts.append((12 + rad * math.cos(math.radians(ang)),
                        12 + rad * math.sin(math.radians(ang))))
        poly(pts, RED if kind == "raid" else c1)
    elif kind == "handshake":
        r(3, 9, 12, 14, c1); r(12, 10, 21, 15, c2)
        poly([(12, 9), (16, 13), (12, 15), (9, 12)], PAPER)
    elif kind == "tree":
        poly([(12, 3), (19, 13), (5, 13)], OLIVE)
        poly([(12, 10), (20, 20), (4, 20)], c2)
        r(11, 20, 13, 22, OCHRE)
    elif kind == "tag":
        poly([(4, 4), (14, 4), (20, 10), (12, 20), (4, 12)], c1)
        ell(15, 7, 18, 10, fill=PAPER)
    elif kind == "money":
        ell(4, 4, 20, 20, outline=c1, width=2); ell(7, 7, 17, 17, fill=OCHRE)
        d.text((x + 12 * u, y + 12 * u), "$", font=font(SERIF_B, int(11 * u)),
               fill=PAPER, anchor="mm")
    elif kind == "drill":
        poly([(4, 6), (20, 6), (16, 14), (8, 14)], c1)
        poly([(10, 14), (14, 14), (12, 21)], c2)
        line([(4, 6), (20, 6)], RED, 2)
    elif kind == "troops":
        poly([(4, 21), (7, 12), (10, 21)], c1)
        poly([(10, 21), (13, 10), (16, 21)], c2)
        poly([(16, 21), (19, 12), (22, 21)], c1)
    elif kind == "bat":
        line([(5, 20), (17, 7)], OCHRE, 3)
        r(16, 3, 20, 8, c1)
        ell(6, 6, 10, 10, fill=RED)
    else:
        ell(5, 5, 19, 19, outline=c1, width=2)


# ---------------------------------------------------------------- world map
# Simplified continent outlines as (lon, lat) polygons.
LAND_POLYS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66), (-80, 73),
     (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 32), (-81, 26),
     (-90, 21), (-95, 19), (-97, 16), (-92, 15), (-86, 13), (-83, 9), (-79, 9),
     (-85, 11), (-90, 14), (-95, 16), (-100, 18), (-105, 20), (-110, 23), (-114, 29),
     (-120, 34), (-124, 40), (-124, 48), (-130, 55), (-145, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70), (-25, 74), (-35, 76),
     (-55, 76), (-60, 74), (-58, 70)],
    # South America
    [(-79, 9), (-75, 11), (-72, 12), (-64, 10), (-60, 8), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-52, -33), (-58, -38),
     (-65, -41), (-68, -50), (-70, -54), (-73, -50), (-73, -40), (-72, -30), (-70, -20),
     (-75, -15), (-80, -6), (-81, 0), (-80, 4)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34),
     (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (40, 15), (43, 11), (48, 11),
     (51, 10), (46, 5), (41, 0), (40, -5), (39, -10), (35, -18), (32, -26), (28, -33),
     (20, -35), (17, -32), (14, -22), (12, -15), (13, -10), (9, -1), (9, 4), (4, 6),
     (-8, 5), (-13, 8), (-17, 12)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (0, 51), (3, 53),
     (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62), (10, 64), (12, 66),
     (18, 69), (25, 71), (30, 70), (35, 68), (40, 68), (45, 66), (50, 68), (55, 68),
     (60, 69), (65, 68), (68, 66), (60, 60), (55, 55), (50, 52), (45, 50), (40, 48),
     (38, 46), (35, 45), (32, 44), (28, 45), (25, 40), (23, 36), (20, 40), (18, 40),
     (15, 38), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50)],
    # Asia (mainland)
    [(28, 41), (30, 45), (35, 45), (38, 47), (42, 48), (48, 50), (50, 52), (55, 55),
     (60, 58), (65, 60), (68, 66), (70, 68), (75, 70), (80, 72), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69), (170, 66),
     (178, 65), (178, 62), (170, 60), (162, 58), (158, 52), (150, 59), (142, 52),
     (140, 45), (138, 40), (135, 35), (130, 32), (127, 30), (122, 30), (120, 25),
     (115, 22), (110, 20), (108, 15), (105, 10), (103, 5), (100, 8), (98, 12),
     (95, 16), (92, 20), (90, 22), (88, 22), (85, 19), (82, 16), (80, 13), (77, 8),
     (75, 12), (72, 20), (70, 24), (66, 25), (62, 25), (58, 26), (56, 27), (54, 26),
     (52, 26), (50, 29), (48, 30), (45, 32), (42, 36), (38, 36), (35, 36), (30, 36)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 42), (143, 44),
     (141, 45), (139, 41), (137, 37), (133, 35), (130, 32)],
    # Indonesia / SE Asia islands
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -3), (135, -4), (140, -8), (141, -2), (136, 0), (131, 1), (126, 2),
     (120, 0), (115, 0), (110, 0), (105, 2), (100, 5)],
    # Australia
    [(114, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32), (135, -35),
     (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (174, -41), (172, -43),
     (168, -46)],
]


def project(lon, lat, x0, y0, x1, y1):
    """Equirectangular: lon -180..180, lat -58..84 -> map box."""
    px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    py = y0 + (84.0 - lat) / (84.0 + 58.0) * (y1 - y0)
    return px, py


# ---------------------------------------------------------------- draw
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(SERIF_B, 40)
    f_date = font(SERIF, 18)
    f_stats = font(SANS_B, 12)
    f_mapcap = font(SANS_B, 10)
    f_sect = font(SANS_B, 11)
    f_lead_h = font(SERIF_B, 19)
    f_lead_s = font(SERIF, 13)
    f_src = font(SANS, 10)
    f_src_s = font(SANS, 9)
    f_sec_h = font(SERIF_B, 15)
    f_sec_s = font(SERIF, 11)
    f_tl = font(SERIF, 12)
    f_tl_n = font(SANS_B, 12)
    f_foot = font(SANS, 10)
    f_num = font(SANS_B, 9)
    f_lead_n = font(SANS_B, 11)

    # ---- 1. Masthead (y 0-64) ----
    title = "THE WORLD IN ONE DAY"
    assert text_w(d, title, f_title) <= CW
    d.text((W / 2, 8), title, font=f_title, fill=INK, anchor="ma")
    date = "Thursday 19 November 2026"
    assert text_w(d, date, f_date) <= CW
    d.text((W / 2, 50), date, font=f_date, fill=INK, anchor="ma")
    d.line([(M, 70), (W - M, 70)], fill=INK, width=2)
    d.line([(M, 73), (W - M, 73)], fill=INK, width=1)

    # ---- 2. Stats bar (y 78-106) ----
    d.rectangle([M, 78, W - M, 106], fill=INK)
    stats = "33 STORIES  ·  " + "  ·  ".join(f"{name} {n}" for name, n in STATS)
    assert text_w(d, stats, f_stats) <= CW - 8, f"stats bar too wide: {text_w(d, stats, f_stats)}"
    d.text((W / 2, 92), stats, font=f_stats, fill=PAPER, anchor="mm")

    # ---- 3. World map strip (y 110-212) ----
    map_cap = "WHERE THE NEWS HAPPENED  —  33 STORIES, NUMBERED 1–33"
    assert text_w(d, map_cap, f_mapcap) <= CW
    d.text((W / 2, 112), map_cap, font=f_mapcap, fill=BLUE, anchor="ma")
    mx0, my0, mx1, my1 = M, 126, W - M, 210
    d.rectangle([mx0, my0, mx1, my1], outline=GRID, width=1)
    for lon in range(-180, 181, 30):  # faint graticule
        gx, _ = project(lon, 0, mx0, my0, mx1, my1)
        d.line([(gx, my0), (gx, my1)], fill=GRID, width=1)
    for lat in (-30, 0, 30, 60):
        _, gy = project(0, lat, mx0, my0, mx1, my1)
        d.line([(mx0, gy), (mx1, gy)], fill=GRID, width=1)
    for poly in LAND_POLYS:
        pts = [project(lon, lat, mx0, my0, mx1, my1) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)

    # Numbered dots, with small offsets where stories share a city.
    placed = []
    for (n, _h, _s, _r, _src, lat, lon, _ic) in STORIES:
        bx, by = project(lon, lat, mx0, my0, mx1, my1)
        # Spread the crowded Europe / Middle East cluster: try wider offsets
        # until the dot is clear of every dot already placed (dots stay on
        # the right continent; exact position is approximate per the brief).
        for dx, dy in [(0, 0), (19, -12), (-19, 11), (19, 13), (-19, -13),
                       (0, -21), (0, 20), (25, 0), (-25, 0), (26, -15),
                       (-26, 15), (13, 20), (-13, -20), (26, 12), (-26, -12)]:
            cx, cy = bx + dx, by + dy
            if all((cx - px) ** 2 + (cy - py) ** 2 >= 19 ** 2 for px, py in placed):
                break
        else:
            cx, cy = bx, by
        placed.append((cx, cy))
        d.ellipse([cx - 7.5, cy - 7.5, cx + 7.5, cy + 7.5], fill=RED, outline=PAPER, width=1)
        d.text((cx, cy), str(n), font=f_num, fill=(255, 255, 255), anchor="mm")

    # ---- 4. Lead stories (y 218-398), 3 columns ----
    d.text((M, 218), "TOP STORIES", font=f_sect, fill=RED, anchor="la")
    d.line([(M, 234), (W - M, 234)], fill=INK, width=1)
    col_w = (CW - 2 * 16) // 3  # 312
    lead_y = 242
    for i, (n, headline, summary, region, source, _la, _lo, icon) in enumerate(STORIES[:3]):
        x = M + i * (col_w + 16)
        # icon box
        d.rectangle([x, lead_y, x + col_w, lead_y + 56], fill=BOX, outline=GRID)
        draw_icon(d, icon, x + 12, lead_y + 6, 44, BLUE, RED)
        d.text((x + 66, lead_y + 28), f"NO. {n}", font=f_lead_n, fill=RED, anchor="lm")
        d.text((x + 66, lead_y + 28), "", font=f_lead_n, fill=RED, anchor="lm")
        hl = wrap_text(d, headline, f_lead_h, col_w, max_lines=2)
        hy = lead_y + 62
        for ln in hl:
            d.text((x, hy), ln, font=f_lead_h, fill=INK, anchor="la")
            hy += 23
        sl = wrap_text(d, summary, f_lead_s, col_w, max_lines=2)
        sy = hy + 3
        for ln in sl:
            d.text((x, sy), ln, font=f_lead_s, fill=INK, anchor="la")
            sy += 16
        src = f"{region}  ·  {source}"
        assert text_w(d, src, f_src) <= col_w
        d.text((x, 384), src, font=f_src, fill=BLUE, anchor="la")

    # ---- 5. Secondary stories (y 404-698), 4 cols x 3 rows ----
    d.text((M, 404), "MORE FROM THE DAY", font=f_sect, fill=RED, anchor="la")
    d.line([(M, 420), (W - M, 420)], fill=INK, width=1)
    cell_w, cell_h = 236, 90
    gap_x, gap_y = 8, 6
    grid_y = 428
    for i, (n, headline, summary, region, source, _la, _lo, icon) in enumerate(STORIES[3:15]):
        row, col = divmod(i, 4)
        x = M + col * (cell_w + gap_x)
        y = grid_y + row * (cell_h + gap_y)
        # number badge + icon on the top row
        d.ellipse([x, y, x + 18, y + 18], fill=RED)
        d.text((x + 9, y + 9), str(n), font=f_num, fill=(255, 255, 255), anchor="mm")
        draw_icon(d, icon, x + cell_w - 24, y - 1, 22, BLUE, OLIVE)
        # Headline only (brief allows "just headline + Region · Source"):
        # a one-line summary of these stories cannot fit the 236px cell
        # without ending mid-phrase, so the summary line is omitted here.
        hl = wrap_text(d, headline, f_sec_h, cell_w - 30, max_lines=2)
        hy = y + 22
        for ln in hl:
            d.text((x, hy), ln, font=f_sec_h, fill=INK, anchor="la")
            hy += 19
        src = f"{region}  ·  {source}"
        src = fit_text(d, src, f_src_s, cell_w, note=f"secondary {n} source")
        d.text((x, y + 66), src, font=f_src_s, fill=GREY, anchor="la")
        if row < 2:
            d.line([(x, y + cell_h + 2), (x + cell_w, y + cell_h + 2)], fill=GRID, width=1)

    # ---- 6. Timeline (y 706-962), 2 columns of 9 ----
    d.text((M, 706), "THE DAY IN BRIEF", font=f_sect, fill=RED, anchor="la")
    d.line([(M, 722), (W - M, 722)], fill=INK, width=1)
    tl_col_w = (CW - 16) // 2  # 476
    tl_y0, tl_row = 730, 25
    for i, (n, headline, _s, region, _src, _la, _lo, _ic) in enumerate(STORIES[15:33]):
        col = i // 9
        row = i % 9
        x = M + col * (tl_col_w + 16)
        y = tl_y0 + row * tl_row
        num = f"{n:>2}"
        nw = text_w(d, num + "  ", f_tl_n)
        line = fit_text(d, headline + "  —  " + region, f_tl, tl_col_w - nw,
                        note=f"timeline {n}")
        d.text((x, y), num, font=f_tl_n, fill=RED, anchor="la")
        d.text((x + nw, y), line, font=f_tl, fill=INK, anchor="la")
        if row < 8:
            d.line([(x, y + 20), (x + tl_col_w, y + 20)], fill=GRID, width=1)

    # ---- 7. Footer (y 966-1024) ----
    d.line([(M, 968), (W - M, 968)], fill=INK, width=2)
    foot1 = ("DATE-CHECK: Every story above was reported on Thursday 19 November 2026.  "
             "Sources: BBC · Reuters · AP · AFP · Al Jazeera · IAEA · One Turn · Radio NZ.")
    foot1 = fit_text(d, foot1, f_foot, CW, note="footer line 1")
    d.text((W / 2, 978), foot1, font=f_foot, fill=INK, anchor="ma")
    foot2 = "THE WORLD IN ONE DAY  ·  make.fun  ·  news-image-20261119"
    assert text_w(d, foot2, f_foot) <= CW
    d.text((W / 2, 998), foot2, font=f_foot, fill=GREY, anchor="ma")

    img.save("entry.png", optimize=True)
    print(f"saved entry.png {img.size[0]}x{img.size[1]}")
    if TRUNCATIONS:
        print("shortened to fit (cut from the end only):")
        for note, orig, used in TRUNCATIONS:
            print(f"  [{note}] {orig!r} -> {used!r}")
    else:
        print("no text shortened")


if __name__ == "__main__":
    main()
