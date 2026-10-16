"""Deterministic tropical Whole Sign charts; no interpretation or evidence approval."""
from contextlib import closing
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
RULERS = ("Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
          "Venus", "Pluto", "Jupiter", "Saturn", "Uranus", "Neptune")
PROFILE = {"zodiac": "tropical", "houses": "whole_sign",
           "coordinates": "geocentric_apparent_ecliptic_of_date",
           "rulership": "modern", "decans": "ten_degree_sections",
           "decan_rulership": "unassigned", "nodes": "true_and_mean",
           "chiron": True}
BODIES = ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN",
          "URANUS", "NEPTUNE", "PLUTO", "CHIRON", "TRUE_NODE", "MEAN_NODE")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def placement(longitude, ascendant_sign):
    if not math.isfinite(longitude):
        raise ValueError("Longitude must be finite")
    longitude %= 360
    sign_index = int(longitude // 30)
    return {"longitude": longitude, "sign": SIGNS[sign_index],
            "degree_in_sign": longitude % 30,
            "house": None if ascendant_sign is None else (sign_index - ascendant_sign) % 12 + 1,
            "decan": int((longitude % 30) // 10) + 1,
            "modern_sign_ruler": RULERS[sign_index], "decan_ruler": None}


def calculate_chart(birth, ephemeris_path):
    """Input requires explicit UTC, latitude, longitude and a stable person_id."""
    instant = datetime.fromisoformat(birth["utc"].replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.utcoffset().total_seconds() != 0:
        raise ValueError("utc must contain an explicit zero UTC offset")
    latitude, longitude = float(birth["latitude"]), float(birth["longitude"])
    if not (math.isfinite(latitude) and -90 < latitude < 90
            and math.isfinite(longitude) and -180 <= longitude <= 180):
        raise ValueError("Invalid geographic coordinates")
    if not birth.get("person_id"):
        raise ValueError("person_id is required")
    if not 1800 <= instant.year <= 2399:
        raise ValueError("This profile currently requires the 1800-2399 data set")
    directory = Path(ephemeris_path).resolve()
    files = {}
    for name in ("sepl_18.se1", "semo_18.se1", "seas_18.se1"):
        path = directory / name
        if not path.is_file():
            raise FileNotFoundError(f"Required ephemeris file missing: {path}")
        files[name] = sha256(path.read_bytes()).hexdigest()
    import swisseph as swe
    swe.set_ephe_path(str(directory))
    hour = instant.hour + instant.minute / 60 + (instant.second + instant.microsecond / 1e6) / 3600
    jd = swe.julday(instant.year, instant.month, instant.day, hour)
    cusps, angles = swe.houses(jd, latitude, longitude, b"W")
    asc_sign = int((angles[0] % 360) // 30)
    expected = tuple(((asc_sign + i) % 12) * 30.0 for i in range(12))
    if any(abs(a - b) > 1e-8 for a, b in zip(cusps, expected)):
        raise ValueError("Unexpected Whole Sign cusp result")
    positions = {}
    for body in BODIES:
        values, flags = swe.calc_ut(jd, getattr(swe, body), swe.FLG_SWIEPH | swe.FLG_SPEED)
        # Mean node is analytical, not a file-backed physical body.
        if body != "MEAN_NODE" and (not flags & swe.FLG_SWIEPH or flags & swe.FLG_MOSEPH):
            raise RuntimeError(f"Unexpected ephemeris fallback: {body}, flags={flags}")
        row = placement(values[0], asc_sign)
        row.update({"latitude": values[1], "distance_au": values[2],
                    "speed_deg_per_day": values[3], "retrograde": values[3] < 0,
                    "returned_flags": flags,
                    "calculation_kind": "analytical_node" if body == "MEAN_NODE" else "ephemeris"})
        positions[body] = row
    for prefix in ("TRUE", "MEAN"):
        north = positions[prefix + "_NODE"]
        row = placement(north["longitude"] + 180, asc_sign)
        row.update({"speed_deg_per_day": north["speed_deg_per_day"],
                    "retrograde": north["retrograde"], "calculation_kind": "opposite_north_node"})
        positions[prefix + "_SOUTH_NODE"] = row
    positions["ASCENDANT"] = placement(angles[0], asc_sign)
    positions["MIDHEAVEN"] = placement(angles[1], asc_sign)
    engine = {"name": "Swiss Ephemeris", "version": swe.version,
              "binding_version": swe.__version__, "file_sha256": files}
    inputs = dict(birth)
    inputs["utc"] = instant.astimezone(timezone.utc).isoformat()
    identity = {"input": inputs, "profile": PROFILE, "engine": engine}
    return {"chart_id": "chart-" + sha256(canonical(identity).encode()).hexdigest()[:24],
            **identity, "julian_day_ut": jd, "house_cusps": list(cusps),
            "placements": positions, "training_eligible": False,
            "validation_status": "calculated_unverified",
            "validation_note": "Calculated output; no user confirmation or independent astronomical validation."}


def save_chart(database, chart):
    from .knowledge import initialize_graph, add_node, add_edge
    from .db import connect
    initialize_graph(database)
    raw = canonical(chart)
    with closing(connect(database)) as db, db:
        existing = db.execute("SELECT result_json FROM chart_runs WHERE id=?", (chart["chart_id"],)).fetchone()
        if existing and existing["result_json"] != raw:
            raise ValueError("Chart identifier already exists with different contents")
        db.execute("INSERT OR IGNORE INTO chart_runs VALUES (?,?,?,?,?,?,0)",
                   (chart["chart_id"], chart["input"]["person_id"], "personal_example",
                    canonical(chart["input"]), canonical(chart["profile"]), raw))
        subject = "personal:" + chart["input"]["person_id"]
        add_node(db, subject, "subject", chart["input"]["person_id"], "user_provided", {})
        add_node(db, chart["chart_id"], "chart", "Natal chart", "calculated", chart["profile"])
        add_edge(db, chart["chart_id"], "CHART_FOR", subject, "calculated")
        for name, row in chart["placements"].items():
            db.execute("INSERT OR IGNORE INTO chart_placements VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (chart["chart_id"], name, row["longitude"], row["sign"], row["degree_in_sign"],
                        row["house"], row["decan"], row.get("retrograde"),
                        row["modern_sign_ruler"], canonical(row)))
            node = chart["chart_id"] + ":" + name
            add_node(db, node, "placement", name, "calculated", row)
            add_edge(db, chart["chart_id"], "HAS_PLACEMENT", node, "calculated")
            sign = "sign:" + row["sign"]
            add_node(db, sign, "sign", row["sign"], "vocabulary", {})
            add_edge(db, node, "IN_SIGN", sign, "calculated")
            if row["house"] is not None:
                house = chart["chart_id"] + ":house:" + str(row["house"])
                add_node(db, house, "house", "House " + str(row["house"]), "calculated", {})
                add_edge(db, node, "IN_HOUSE", house, "calculated")


def render_svg(chart):
    """Self-contained chart wheel plus exact placement table; labels do not overlap."""
    rows = chart["placements"]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850">',
           '<rect width="1200" height="850" fill="#101827"/>',
           '<g font-family="Arial,sans-serif" fill="#e8edf5">',
           '<text x="36" y="40" font-size="23">Cosmora · Tropical / Whole Sign</text>',
           f'<text x="36" y="68" font-size="14">{escape(str(chart["input"]["person_id"]))}</text>',
           '<text x="36" y="92" font-size="12">Calculated chart · Decan rulers unassigned · Not training evidence</text>']
    cx, cy, radius = 320, 430, 245
    asc_sign = int(rows.get("ASCENDANT", next(iter(rows.values())))["longitude"] // 30)
    # Whole Sign first-house cusp at the left; longitude increases counterclockwise.
    origin = asc_sign * 30
    def point(lon, r):
        angle = math.radians(180 - (lon - origin))
        return cx + r * math.cos(angle), cy + r * math.sin(angle)
    for r in (radius, radius - 45, radius - 95):
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#526582"/>')
    for i, sign in enumerate(SIGNS):
        x, y = point(i * 30, radius)
        ix, iy = point(i * 30, 0)
        svg.append(f'<line x1="{ix}" y1="{iy}" x2="{x}" y2="{y}" stroke="#526582"/>')
        x, y = point(i * 30 + 15, radius - 23)
        svg.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-size="11">{sign}</text>')
        x, y = point(i * 30 + 15, radius - 70)
        house = (i - asc_sign) % 12 + 1
        svg.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-size="12">H{house}</text>')
    for name, row in rows.items():
        x, y = point(row["longitude"], radius - 102)
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#70ded0"><title>{escape(name)} {row["longitude"]:.6f}°</title></circle>')
        x2, y2 = point(row["longitude"], radius - 88)
        svg.append(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#70ded0"/>')
    svg.append('<text x="630" y="130" font-size="14">Body / point          Position           House  Decan</text>')
    for index, (name, row) in enumerate(rows.items()):
        degree = row["degree_in_sign"]
        minutes = int(degree * 60)
        label = f'{name:18} {row["sign"]:11} {minutes//60:02}°{minutes%60:02}′  H{row["house"]}   D{row["decan"]}'
        if row.get("retrograde"):
            label += " R"
        svg.append(f'<text x="630" y="{165+index*30}" font-family="monospace" font-size="12">{escape(label)}</text>')
    svg.append('</g></svg>')
    return "\n".join(svg)
