"""Local research staging graph, explicit provenance, exports and chart bootstrap."""
import argparse
from contextlib import closing
import csv
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path

from .db import connect, initialize

SCHEMA = """
CREATE TABLE IF NOT EXISTS research_subjects (
 id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, field TEXT, region TEXT,
 status TEXT NOT NULL CHECK(status='pending'), payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_event_leads (
 id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES research_subjects(id),
 event_type TEXT NOT NULL, date_start TEXT NOT NULL, date_end TEXT, date_precision TEXT NOT NULL,
 source_url TEXT NOT NULL, status TEXT NOT NULL CHECK(status='pending'), payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chart_runs (
 id TEXT PRIMARY KEY, person_id TEXT NOT NULL, purpose TEXT NOT NULL,
 input_json TEXT NOT NULL, profile_json TEXT NOT NULL, result_json TEXT NOT NULL,
 training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(training_eligible=0)
);
CREATE TABLE IF NOT EXISTS chart_placements (
 chart_id TEXT NOT NULL REFERENCES chart_runs(id), body TEXT NOT NULL,
 longitude REAL NOT NULL CHECK(longitude >= 0 AND longitude < 360),
 sign TEXT NOT NULL, degree_in_sign REAL NOT NULL,
 house INTEGER CHECK(house BETWEEN 1 AND 12), decan INTEGER NOT NULL CHECK(decan BETWEEN 1 AND 3),
 retrograde INTEGER, modern_sign_ruler TEXT NOT NULL, payload_json TEXT NOT NULL,
 PRIMARY KEY(chart_id,body)
);
CREATE TABLE IF NOT EXISTS graph_nodes (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN
 ('subject','source_lead','event_lead','chart','placement','sign','house')),
 label TEXT NOT NULL, status TEXT NOT NULL, properties_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS graph_edges (
 source_id TEXT NOT NULL REFERENCES graph_nodes(id),
 relation TEXT NOT NULL CHECK(relation IN
 ('HAS_SOURCE_LEAD','HAS_EVENT_LEAD','CHART_FOR','HAS_PLACEMENT','IN_SIGN','IN_HOUSE')),
 target_id TEXT NOT NULL REFERENCES graph_nodes(id), status TEXT NOT NULL,
 PRIMARY KEY(source_id,relation,target_id)
);
CREATE INDEX IF NOT EXISTS idx_placements_body ON chart_placements(body,sign,house);
CREATE INDEX IF NOT EXISTS idx_graph_target ON graph_edges(target_id,relation);
"""
TABLES = ("research_subjects", "research_event_leads", "chart_runs",
          "chart_placements", "graph_nodes", "graph_edges")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def initialize_graph(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    initialize(path)
    with closing(connect(path)) as db, db:
        db.executescript(SCHEMA)


def add_node(db, identifier, kind, label, status, properties):
    raw = canonical(properties)
    existing = db.execute("SELECT * FROM graph_nodes WHERE id=?", (identifier,)).fetchone()
    if existing:
        if (existing["kind"], existing["label"], existing["status"], existing["properties_json"]) != (kind, label, status, raw):
            raise ValueError(f"Node already exists with different contents: {identifier}")
        return
    db.execute("INSERT INTO graph_nodes VALUES (?,?,?,?,?)", (identifier,kind,label,status,raw))


def add_edge(db, source, relation, target, status):
    db.execute("INSERT OR IGNORE INTO graph_edges VALUES (?,?,?,?)", (source,relation,target,status))


def source_node(db, url):
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        raise ValueError("Research source requires an HTTP(S) URL")
    identifier = "source:" + sha256(url.encode()).hexdigest()[:24]
    add_node(db, identifier, "source_lead", url, "unverified_source",
             {"url":url, "remote_content_sha256":None,
              "note":"Discovery URL only; source content, permissions and claims require review."})
    return identifier


def import_candidates(path, candidates):
    initialize_graph(path)
    with closing(connect(path)) as db, db:
        for candidate in candidates:
            identifier, name = candidate["candidate_id"], candidate["name"]
            record = dict(candidate, status="pending", training_eligible=False)
            raw = canonical(record)
            same_name = db.execute("SELECT id FROM research_subjects WHERE name=?", (name,)).fetchone()
            if same_name and same_name["id"] != identifier:
                raise ValueError("Name already belongs to another candidate ID; resolve identity before importing")
            existing = db.execute("SELECT payload_json FROM research_subjects WHERE id=?", (identifier,)).fetchone()
            if existing and existing["payload_json"] != raw:
                raise ValueError("Candidate changed; append a reviewed revision instead of overwriting")
            db.execute("INSERT OR IGNORE INTO research_subjects VALUES (?,?,?,?,?,?)",
                       (identifier,name,candidate.get("field"),candidate.get("region"),"pending",raw))
            add_node(db, identifier, "subject", name, "pending", record)
            source = source_node(db, candidate["biography_url"])
            add_edge(db, identifier, "HAS_SOURCE_LEAD", source, "pending")
            if candidate.get("birth_record_url"):
                source = source_node(db, candidate["birth_record_url"])
                add_edge(db, identifier, "HAS_SOURCE_LEAD", source, "pending")


def import_events(path, events):
    initialize_graph(path)
    with closing(connect(path)) as db, db:
        for event in events:
            person = db.execute("SELECT id FROM research_subjects WHERE name=?", (event["person"],)).fetchone()
            if person is None:
                raise ValueError(f"Event subject not found: {event['person']}")
            record = dict(event, status="pending", training_eligible=False,
                          chart_status="awaiting_verified_birth_and_event_time")
            raw = canonical(record)
            existing = db.execute("SELECT payload_json FROM research_event_leads WHERE id=?", (event["event_id"],)).fetchone()
            if existing and existing["payload_json"] != raw:
                raise ValueError("Event changed; append a reviewed revision instead of overwriting")
            db.execute("INSERT OR IGNORE INTO research_event_leads VALUES (?,?,?,?,?,?,?,?,?)",
                       (event["event_id"],person["id"],event["event_type"],event["date_start"],
                        event.get("date_end"),event["date_precision"],event["source_url"],"pending",raw))
            add_node(db,event["event_id"],"event_lead",event.get("description",event["event_type"]),"pending",record)
            add_edge(db,person["id"],"HAS_EVENT_LEAD",event["event_id"],"pending")
            source = source_node(db,event["source_url"])
            add_edge(db,event["event_id"],"HAS_SOURCE_LEAD",source,"pending")


def export_graph(path):
    with closing(connect(path)) as db:
        nodes = [{"id":r["id"],"kind":r["kind"],"label":r["label"],"status":r["status"],
                  "properties":json.loads(r["properties_json"])}
                 for r in db.execute("SELECT * FROM graph_nodes ORDER BY id")]
        edges = [{"source":r["source_id"],"relation":r["relation"],
                  "target":r["target_id"],"status":r["status"]}
                 for r in db.execute("SELECT * FROM graph_edges ORDER BY source_id,relation,target_id")]
    return {"schema_version":1,"nodes":nodes,"edges":edges,
            "note":"Pending research leads, vocabulary and calculated placements have distinct statuses. Edges express provenance or calculated location, never causation."}


def export_tables(path, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    counts = {}
    with closing(connect(path)) as db:
        for table in TABLES:
            cursor = db.execute(f"SELECT * FROM {table} ORDER BY 1,2")
            columns = [d[0] for d in cursor.description]
            rows = [tuple(row) for row in cursor]
            with (output/(table+".csv")).open("w",newline="",encoding="utf-8-sig") as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                # Treat text as text in spreadsheet software, including untrusted source labels.
                writer.writerows(tuple("'" + v if isinstance(v,str) and v.lstrip().startswith(("=","+","-","@")) else v for v in row) for row in rows)
            counts[table] = len(rows)
    graph = export_graph(path)
    (output/"graph.json").write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    node_rows = "".join("<tr><td>"+escape(n["kind"])+"</td><td>"+escape(n["label"])+"</td><td>"+escape(n["status"])+"</td></tr>" for n in graph["nodes"])
    edge_rows = "".join("<tr><td>"+escape(e["source"])+"</td><td>"+escape(e["relation"])+"</td><td>"+escape(e["target"])+"</td></tr>" for e in graph["edges"])
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Cosmora knowledge graph</title><style>
body{background:#101827;color:#e8edf5;font:15px system-ui;margin:30px;max-width:1400px}
h1{color:#70ded0}input{padding:12px;min-width:320px}table{border-collapse:collapse;width:100%;margin-top:20px}
td,th{padding:8px;border-bottom:1px solid #334155;text-align:left;overflow-wrap:anywhere}
small{color:#b4bfd0}a{color:#70ded0}</style>
<h1>Cosmora · Local knowledge graph</h1>
<p>Provenance and calculated placement relationships. Pending leads are not verified evidence.</p>
"""
    page += "<p>"+escape(", ".join(f"{k}: {v}" for k,v in counts.items()))+"</p>"
    page += '<input id="search" aria-label="Filter graph records" placeholder="Search people, planets, signs, statuses…">'
    page += '<h2>Nodes</h2><table><thead><tr><th>Kind</th><th>Label</th><th>Status</th></tr></thead><tbody>'+node_rows+"</tbody></table>"
    page += '<h2>Relationships</h2><table><thead><tr><th>From</th><th>Relationship</th><th>To</th></tr></thead><tbody>'+edge_rows+"</tbody></table>"
    page += """<script>document.getElementById('search').addEventListener('input',function(){
const q=this.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});</script></html>"""
    (output/"graph.html").write_text(page,encoding="utf-8")
    return counts


def bootstrap(args):
    from .charts import calculate_chart, save_chart, render_svg
    root = Path(args.output)
    cohort = json.loads(Path(args.cohort).read_text(encoding="utf-8"))["candidates"]
    events = json.loads(Path(args.events).read_text(encoding="utf-8"))["events"]
    root.mkdir(parents=True, exist_ok=True)
    research_db = root/"research.db"
    personal_db = root/"personal.db"
    import_candidates(research_db,cohort)
    import_events(research_db,events)
    fixture = json.loads(Path(args.example).read_text(encoding="utf-8"))
    birth = dict(fixture["input"],person_id="user-confirmed-example")
    chart = calculate_chart(birth,args.ephe_path)
    # The human-confirmed run is a local regression reference, not an independent ephemeris.
    for body, expected in fixture["bodies"].items():
        actual = chart["placements"][body]["longitude"]
        delta = abs((actual-expected["longitude"]+180)%360-180)
        if delta > 1/3600:
            raise ValueError(f"Example regression mismatch greater than one arcsecond: {body}")
    for name, old in (("ASCENDANT","ascendant"),("MIDHEAVEN","midheaven")):
        if abs((chart["placements"][name]["longitude"]-fixture[old]["longitude"]+180)%360-180)>1/3600:
            raise ValueError(f"Example angle mismatch: {name}")
    chart["validation_status"] = "calculated_user_confirmed_example"
    chart["validation_note"] = "User confirmed the earlier displayed example; this is not independent astronomical validation."
    save_chart(personal_db,chart)
    personal = root/"personal"
    personal.mkdir(exist_ok=True)
    (personal/"natal.json").write_text(json.dumps(chart,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (personal/"natal.svg").write_text(render_svg(chart),encoding="utf-8")
    personal_counts = export_tables(personal_db,personal)
    research_counts = export_tables(research_db,root/"research")
    report = {"generated_at":datetime.now(timezone.utc).isoformat(),
              "profile":chart["profile"],"research_counts":research_counts,
              "personal_counts":personal_counts,"confirmed_example_regression":"passed within one arcsecond",
              "independent_ephemeris_validation":"not_performed",
              "verified_research_births":0,"queued_event_charts":len(events),
              "reason_event_charts_queued":"Birth records unverified; event precision does not establish an exact timestamp.",
              "chart_id":chart["chart_id"],"training_eligible":False}
    (root/"run.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    index = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Cosmora local research</title>
<style>body{background:#101827;color:#e8edf5;font:18px system-ui;max-width:950px;margin:50px auto}a{color:#70ded0}li{margin:18px}</style>
<h1>Cosmora · Local research workspace</h1>
<p>Personal calculations and pending historical research are stored separately.</p>
<ul><li><a href="personal/natal.svg">Saved natal chart wheel and placements</a></li>
<li><a href="personal/chart_placements.csv">Personal placement table (CSV)</a></li>
<li><a href="personal/graph.html">Explore personal chart graph</a></li>
<li><a href="research/graph.html">Explore research provenance graph</a></li>
<li><a href="research/research_subjects.csv">Candidate people (CSV)</a></li>
<li><a href="research/research_event_leads.csv">Event leads (CSV)</a></li>
<li><a href="run.json">Calculation profile and run summary</a></li></ul>
<p>Decan numbers are recorded; decan rulers remain unassigned. Modern sign rulers are enabled.
True and mean nodes are both retained. No research subject is approved for training.
Event charts remain queued until birth and event inputs support their calculation.</p></html>"""
    (root/"index.html").write_text(index,encoding="utf-8")
    print(json.dumps(report,indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command",required=True)
    run = sub.add_parser("bootstrap",help="Import local pending leads and calculate the human-confirmed example")
    for name in ("cohort","events","example","ephe-path","output"):
        run.add_argument("--"+name,required=True)
    args = parser.parse_args()
    bootstrap(args)


if __name__ == "__main__":
    main()
