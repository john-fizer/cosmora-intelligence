"""Five-person provisional natal/event-transit pilot with explicit time uncertainty."""
import argparse
from collections import Counter, defaultdict
from contextlib import closing
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import csv

from .charts import calculate_chart, canonical, placement, render_svg, save_chart
from .db import connect
from .knowledge import (add_edge, add_node, export_graph, export_tables,
                        import_candidates, import_events, initialize_graph)

ASPECTS = {"conjunction":0, "sextile":60, "square":90, "trine":120, "opposition":180}
ORB = 3.0
CATEGORIES = {"employment","publication","exhibition","award","public_appearance",
              "flight","organization","education","public_service"}


def event_window(event):
    """Conservative UTC envelope for unlocated civil dates; never an exact event time."""
    if event["date_precision"] not in ("day","day_range"):
        return None
    first = date.fromisoformat(event["date_start"])
    last = date.fromisoformat(event.get("date_end") or event["date_start"])
    if last < first:
        raise ValueError("Reversed event interval")
    if (last-first).days > 31:
        return None
    start = datetime.combine(first,time.min,tzinfo=timezone.utc)-timedelta(hours=14)
    end = datetime.combine(last+timedelta(days=1),time.min,tzinfo=timezone.utc)+timedelta(hours=14)
    return start,end


def sample_times(start,end):
    values=[]
    current=start
    while current < end:
        values.append(current)
        current += timedelta(hours=6)
    if not values or values[-1] != end:
        values.append(end)
    return values


def compare_positions(natal,transits):
    rows=[]
    for transit, moving in transits.items():
        for target, fixed in natal.items():
            separation=abs((moving["longitude"]-fixed["longitude"]+180)%360-180)
            for aspect, angle in ASPECTS.items():
                orb=abs(separation-angle)
                if orb <= ORB:
                    rows.append({"transit_body":transit,"natal_body":target,"aspect":aspect,
                                 "orb_deg":orb,"natal_house":fixed["house"],
                                 "transit_natal_house":moving["house"]})
    return rows


def write_json(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def write_csv(path,rows,columns):
    with Path(path).open("w",newline="",encoding="utf-8-sig") as file:
        writer=csv.DictWriter(file,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def initialize_pilot(db_path):
    initialize_graph(db_path)
    with closing(connect(db_path)) as db,db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS pilot_birth_inputs (
          subject_id TEXT PRIMARY KEY REFERENCES research_subjects(id),
          input_json TEXT NOT NULL, provenance_json TEXT NOT NULL,
          primary_verified INTEGER NOT NULL DEFAULT 0 CHECK(primary_verified=0));
        CREATE TABLE IF NOT EXISTS pilot_events (
          event_id TEXT PRIMARY KEY REFERENCES research_event_leads(id),
          category TEXT NOT NULL, calculation_status TEXT NOT NULL, sample_count INTEGER NOT NULL,
          window_json TEXT NOT NULL, deconstruction_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pilot_transit_frames (
          id TEXT PRIMARY KEY REFERENCES chart_runs(id), event_id TEXT NOT NULL REFERENCES pilot_events(event_id),
          natal_chart_id TEXT NOT NULL REFERENCES chart_runs(id), sample_utc TEXT NOT NULL,
          sample_role TEXT NOT NULL CHECK(sample_role='uncertainty_sample'));
        CREATE TABLE IF NOT EXISTS pilot_aspect_samples (
          frame_id TEXT NOT NULL REFERENCES pilot_transit_frames(id), transit_body TEXT NOT NULL,
          natal_body TEXT NOT NULL, aspect TEXT NOT NULL, orb_deg REAL NOT NULL,
          natal_house INTEGER NOT NULL, transit_natal_house INTEGER NOT NULL,
          PRIMARY KEY(frame_id,transit_body,natal_body,aspect));
        CREATE TABLE IF NOT EXISTS pilot_extra_nodes (
          id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL, properties_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pilot_extra_edges (
          source_id TEXT NOT NULL, relation TEXT NOT NULL, target_id TEXT NOT NULL,
          properties_json TEXT NOT NULL, PRIMARY KEY(source_id,relation,target_id));
        """)


def guard_policy(path,policy):
    """Refuse to mix comparison/sampling policies in one output database."""
    with closing(connect(path)) as db,db:
        db.execute("CREATE TABLE IF NOT EXISTS pilot_run_policy (id INTEGER PRIMARY KEY CHECK(id=1), payload_json TEXT NOT NULL)")
        row=db.execute("SELECT payload_json FROM pilot_run_policy WHERE id=1").fetchone()
        encoded=canonical(policy)
        if row:
            if row["payload_json"] != encoded:
                raise ValueError("Comparison policy changed; use a new output directory")
            return
        if db.execute("SELECT COUNT(*) FROM pilot_transit_frames").fetchone()[0]:
            report=Path(path).parent/"run.json"
            if not report.is_file():
                raise ValueError("Existing comparisons lack policy provenance; use a new output directory")
            legacy=json.loads(report.read_text(encoding="utf-8"))
            expected={"angles":policy["angles"],"orb_degrees":policy["orb_degrees"]}
            if legacy.get("aspect_policy") != expected:
                raise ValueError("Existing comparison policy does not match")
            for item in db.execute("SELECT window_json FROM pilot_events"):
                window=json.loads(item["window_json"])
                if window.get("sample_step_hours") != policy["sample_hours"] or "14" not in window.get("policy","") or policy["envelope_hours"] != 14:
                    raise ValueError("Existing sampling policy does not match")
        db.execute("INSERT INTO pilot_run_policy VALUES (1,?)",(encoded,))


def extra_node(db,identifier,kind,label,properties):
    db.execute("INSERT OR IGNORE INTO pilot_extra_nodes VALUES (?,?,?,?)",
               (identifier,kind,label,canonical(properties)))


def extra_edge(db,source,relation,target,properties=None):
    db.execute("INSERT OR IGNORE INTO pilot_extra_edges VALUES (?,?,?,?)",
               (source,relation,target,canonical(properties or {})))


def run(args):
    root=Path(args.output)
    root.mkdir(parents=True,exist_ok=True)
    inputs=json.loads(Path(args.people).read_text(encoding="utf-8"))
    people=inputs["people"]
    events=json.loads(Path(args.events).read_text(encoding="utf-8"))["events"]
    if len(people)!=5 or len({p["candidate_id"] for p in people})!=5:
        raise ValueError("Pilot requires five distinct subjects")
    if any(e["category"] not in CATEGORIES for e in events):
        raise ValueError("Unknown independently defined event category")
    names={p["name"] for p in people}
    counts=Counter(e["person"] for e in events)
    if set(counts)!=names or any(counts[name]!=5 for name in names):
        raise ValueError("This first batch requires five documented event leads per subject")
    db_path=root/"pilot.db"
    initialize_pilot(db_path)
    guard_policy(db_path,{"angles":ASPECTS,"orb_degrees":ORB,"sample_hours":6,"envelope_hours":14})
    import_candidates(db_path,people)
    imported=[dict(e,event_id=e["id"]) for e in events]
    import_events(db_path,imported)
    natals={}
    for person in people:
        identifier=person["candidate_id"]
        birth=person["birth"]
        local=datetime.fromisoformat(birth["local_datetime"])
        expected=(local-timedelta(seconds=birth["source_offset_seconds"])).replace(tzinfo=timezone.utc)
        if expected!=datetime.fromisoformat(birth["utc"].replace("Z","+00:00")):
            raise ValueError("Source offset does not reproduce supplied UT")
        chart=calculate_chart(birth,args.ephe_path)
        chart["kind"]="Provisional natal chart"
        chart["validation_status"]="publisher_reported_AA_primary_record_uninspected"
        chart["validation_note"]="Working calculation from indexed publisher metadata; not an approved historical birth."
        chart["birth_provenance"]=person["provenance"]
        save_chart(db_path,chart,purpose="research_provisional_natal",subject_id=identifier)
        natals[person["name"]]=chart
        person_dir=root/identifier
        person_dir.mkdir(exist_ok=True)
        write_json(person_dir/"natal.json",chart)
        (person_dir/"natal.svg").write_text(render_svg(chart),encoding="utf-8")
        with closing(connect(db_path)) as db,db:
            db.execute("INSERT OR IGNORE INTO pilot_birth_inputs VALUES (?,?,?,0)",
                       (identifier,canonical(birth),canonical(person["provenance"])))
    event_reports=[]
    all_contacts=[]
    frame_total=0
    for event in events:
        natal=natals[event["person"]]
        person_id=natal["input"]["person_id"]
        event_id=event["id"]
        event_dir=root/person_id/event_id
        event_dir.mkdir(exist_ok=True)
        window=event_window(event)
        times=sample_times(*window) if window else []
        deconstruction={"event_type":event["event_type"],"category":event["category"],
            "classification_basis":"documented public event, independent of chart placements",
            "date_role":event["date_role"],"date_precision":event["date_precision"],
            "participation_note":event.get("source_notes",""),
            "interpretation":"none","training_eligible":False}
        window_record={"policy":"civil-date envelope expanded by14hours on both sides because timezone is unverified",
                       "start":window[0].isoformat() if window else None,
                       "end":window[1].isoformat() if window else None,
                       "sample_step_hours":6,"exact_event_time_known":False,
                       "continuous_interval_guarantee":False}
        status="sampled_provisional" if times else "queued_needs_finer_date"
        with closing(connect(db_path)) as db,db:
            db.execute("INSERT OR IGNORE INTO pilot_events VALUES (?,?,?,?,?,?)",
                       (event_id,event["category"],status,len(times),canonical(window_record),canonical(deconstruction)))
            category="category:"+event["category"]
            extra_node(db,category,"event_category",event["category"],{"classification":"event ontology, not house doctrine"})
            extra_edge(db,event_id,"HAS_CATEGORY",category)
            extra_edge(db,event_id,"COMPARED_WITH_NATAL",natal["chart_id"])
        asc_sign=int(natal["placements"]["ASCENDANT"]["longitude"]//30)
        contacts=defaultdict(list)
        frame_links=[]
        for number,instant in enumerate(times):
            raw=calculate_chart({"person_id":person_id,"utc":instant.isoformat(),
                                  "latitude":natal["input"]["latitude"],"longitude":natal["input"]["longitude"]},args.ephe_path)
            rows={body:dict(row,**placement(row["longitude"],asc_sign))
                  for body,row in raw["placements"].items() if body not in ("ASCENDANT","MIDHEAVEN")}
            identity={"event":event_id,"sample_utc":instant.isoformat(),"natal":natal["chart_id"],
                      "engine":raw["engine"],"profile":raw["profile"],"sampling":window_record}
            frame={"chart_id":"transit-"+sha256(canonical(identity).encode()).hexdigest()[:24],
                   "input":{"person_id":person_id,"utc":instant.isoformat(),
                            "event_id":event_id,"timestamp_role":"uncertainty_sample"},
                   "profile":dict(raw["profile"],houses="natal_whole_sign_overlay"),
                   "engine":raw["engine"],"kind":"Transit sample through natal houses",
                   "natal_chart_id":natal["chart_id"],"natal_ascendant_sign":asc_sign,
                   "placements":rows,"natal_placements":natal["placements"],
                   "window":window_record,"training_eligible":False,"validation_status":"provisional_uncertainty_sample"}
            save_chart(db_path,frame,purpose="research_provisional_transit_sample",subject_id=person_id)
            compared=compare_positions(natal["placements"],rows)
            with closing(connect(db_path)) as db,db:
                db.execute("INSERT OR IGNORE INTO pilot_transit_frames VALUES (?,?,?,?,?)",
                           (frame["chart_id"],event_id,natal["chart_id"],instant.isoformat(),"uncertainty_sample"))
                extra_edge(db,frame["chart_id"],"SAMPLED_FOR_EVENT",event_id)
                extra_edge(db,frame["chart_id"],"OVERLAYS_NATAL",natal["chart_id"])
                for row in compared:
                    db.execute("INSERT OR IGNORE INTO pilot_aspect_samples VALUES (?,?,?,?,?,?,?)",
                               (frame["chart_id"],row["transit_body"],row["natal_body"],row["aspect"],
                                row["orb_deg"],row["natal_house"],row["transit_natal_house"]))
                    extra_edge(db,frame["chart_id"]+":"+row["transit_body"],"ASPECT_"+row["aspect"].upper(),
                               natal["chart_id"]+":"+row["natal_body"],{"orb_deg":row["orb_deg"],"event_id":event_id,"sample_utc":instant.isoformat()})
                    contacts[(row["transit_body"],row["natal_body"],row["aspect"])].append(row)
            filename=f"sample-{number:03}"
            write_json(event_dir/(filename+".json"),frame)
            display=dict(frame,input=dict(frame["input"],person_id=event_id+" | sample "+instant.isoformat()))
            (event_dir/(filename+".svg")).write_text(render_svg(display),encoding="utf-8")
            frame_links.append({"utc":instant.isoformat(),"svg":filename+".svg","json":filename+".json"})
            frame_total+=1
        summary=[]
        for (transit,target,aspect),hits in contacts.items():
            row={"event_id":event_id,"person":event["person"],"category":event["category"],
                 "transit_body":transit,"natal_body":target,"aspect":aspect,
                 "natal_house":hits[0]["natal_house"],
                 "transit_natal_houses":sorted({h["transit_natal_house"] for h in hits}),
                 "minimum_sampled_orb":min(h["orb_deg"] for h in hits),
                 "contact_samples":len(hits),"total_samples":len(times),
                 "timing_sensitive_in_samples":len(hits)!=len(times),
                 "statistical_significance":None,"training_eligible":False}
            summary.append(row)
        all_contacts.extend(summary)
        report={**event,"calculation_status":status,"window":window_record,
                "deconstruction":deconstruction,"frames":frame_links,"contacts":summary}
        write_json(event_dir/"event.json",report)
        event_reports.append(dict(report,person_id=person_id,folder=person_id+"/"+event_id))
    graph=export_graph(db_path)
    with closing(connect(db_path)) as db:
        for row in db.execute("SELECT * FROM pilot_extra_nodes ORDER BY id"):
            graph["nodes"].append({"id":row["id"],"kind":row["kind"],"label":row["label"],
                                   "status":"provisional","properties":json.loads(row["properties_json"])})
        for row in db.execute("SELECT * FROM pilot_extra_edges ORDER BY source_id,relation,target_id"):
            graph["edges"].append({"source":row["source_id"],"relation":row["relation"],
                                  "target":row["target_id"],"status":"provisional",
                                  "properties":json.loads(row["properties_json"])})
    node_ids={n["id"] for n in graph["nodes"]}
    if any(e["source"] not in node_ids or e["target"] not in node_ids for e in graph["edges"]):
        raise ValueError("Graph has unresolved references")
    write_json(root/"graph.json",graph)
    export_tables(db_path,root/"tables")
    with closing(connect(db_path)) as db:
        for table in ("pilot_birth_inputs","pilot_events","pilot_transit_frames","pilot_aspect_samples","pilot_extra_nodes","pilot_extra_edges"):
            cursor=db.execute("SELECT * FROM "+table)
            columns=[d[0] for d in cursor.description]
            write_csv(root/(table+".csv"),[dict(r) for r in cursor],columns)
    write_json(root/"event-comparisons.json",all_contacts)
    columns=["event_id","person","category","transit_body","natal_body","aspect","natal_house",
             "transit_natal_houses","minimum_sampled_orb","contact_samples","total_samples","timing_sensitive_in_samples"]
    write_csv(root/"event-comparisons.csv",all_contacts,columns)
    summary={"people":5,"natal_charts":5,"event_leads":len(events),
             "event_series":sum(bool(e["frames"]) for e in event_reports),
             "queued_events":sum(not e["frames"] for e in event_reports),"transit_samples":frame_total,
             "computed_contact_groups":len(all_contacts),"graph_nodes":len(graph["nodes"]),
             "graph_edges":len(graph["edges"]),"aspect_policy":{"angles":ASPECTS,"orb_degrees":ORB},
             "primary_birth_records_verified":0,"independent_events_verified":0,"training_eligible":False,
             "scale_gate_passed":False,"sampling_note":"Six-hour samples do not prove continuous-interval aspect stability; sample frequency is not confidence or significance. True and mean nodes are alternative representations, not independent evidence.",
             "next_gate":"Inspect underlying births and event evidence, obtain adequate timing, add controls and independent calculation checks before scaling."}
    write_json(root/"run.json",summary)
    render_index(root,people,event_reports,all_contacts,summary)
    print(json.dumps(summary,indent=2))


def render_index(root,people,events,contacts,summary):
    page="""<!doctype html><html lang="en"><meta charset="utf-8"><title>Cosmora five-person pilot</title>
<style>body{background:#101827;color:#edf3fa;font:15px system-ui;margin:30px}a{color:#75e1d0}button,select{padding:9px;margin:4px}
table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:9px;border-bottom:1px solid #334155}
.notice{background:#273449;padding:18px;border-radius:10px}details{margin:12px 0}small{color:#bdcadb}</style>
<h1>Cosmora · Five-person working pilot</h1>
<p class="notice">Provisional charts from publisher-reported AA metadata. Primary birth images and event claims remain unverified.
These are computed contacts, not established correlations. Event timestamps are uncertainty samples; decan rulers remain unassigned.</p>"""
    page+="<p>"+escape(f'5 natal charts · {summary["event_series"]} event series · {summary["transit_samples"]} transit samples · {summary["queued_events"]} events awaiting finer dates')+"</p><h2>Natal charts</h2><ul>"
    for p in people:
        page+=f'<li><a href="{escape(p["candidate_id"])}/natal.svg">{escape(p["name"])}</a> · <a href="{escape(p["candidate_id"])}/natal.json">placements/provenance</a></li>'
    page+='</ul><h2>Event transit series</h2>'
    for event in events:
        page+=f'<details><summary>{escape(event["person"])} · {escape(event["description"])} · {len(event["frames"])} samples</summary>'
        page+=f'<p>{escape(event["date_start"])} · {escape(event["date_precision"])} · {escape(event["category"])} · {escape(event["calculation_status"])}</p>'
        page+=f'<a href="{escape(event["folder"])}/event.json">Evidence and deconstruction</a><ul>'
        for frame in event["frames"]:
            page+=f'<li><a href="{escape(event["folder"])}/{frame["svg"]}">{escape(frame["utc"])} — uncertainty sample</a></li>'
        page+='</ul></details>'
    page+='<h2>Explore computed contacts by natal house</h2><p>House filter matches the natal target house or the houses occupied by the transiting body at contact samples.</p><button onclick="house=null;draw()">All houses</button>'
    for house in range(1,13):
        page+=f'<button onclick="house={house};draw()">House {house}</button>'
    page+='<select id="person" aria-label="Person"><option value="">All people</option>'
    for person in people:
        page+='<option>'+escape(person["name"])+'</option>'
    page+='</select><select id="category" aria-label="Event category"><option value="">All categories</option>'
    for category in sorted({e["category"] for e in events}):
        page+='<option>'+escape(category)+'</option>'
    page+='</select><p id="count"></p><table><thead><tr><th>Person / event</th><th>Category</th><th>Computed contact</th><th>Natal house</th><th>Min sampled orb</th><th>Samples</th></tr></thead><tbody id="rows"></tbody></table>'
    payload=json.dumps(contacts,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    page+='<script>const data='+payload+''';let house=null;
function draw(){const person=document.getElementById('person').value,category=document.getElementById('category').value;
const rows=data.filter(r=>(!person||r.person===person)&&(!category||r.category===category)&&(house===null||r.natal_house===house||r.transit_natal_houses.includes(house)));
document.getElementById('count').textContent=rows.length+' computed contact groups; no statistical significance established';
const body=document.getElementById('rows');body.replaceChildren();rows.forEach(r=>{const tr=document.createElement('tr');
[r.person+' / '+r.event_id,r.category,r.transit_body+' '+r.aspect+' natal '+r.natal_body,r.natal_house,r.minimum_sampled_orb.toFixed(3)+'°',r.contact_samples+'/'+r.total_samples].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)});body.appendChild(tr)})}
document.getElementById('person').onchange=draw;document.getElementById('category').onchange=draw;draw();</script></html>'''
    (root/"index.html").write_text(page,encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("people","events","ephe-path","output"):
        parser.add_argument("--"+name,required=True)
    run(parser.parse_args())


if __name__=="__main__":
    main()
