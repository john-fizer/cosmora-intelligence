"""Validate agent references and attach pending annotations to the local pilot graph."""
import argparse
from contextlib import closing
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import re
from .charts import canonical
from .db import connect
from .pilot import extra_edge, extra_node, write_json, write_csv


def validate_observation(observation, contacts):
    keys=("transit_body","natal_body","aspect")
    matches=[r for r in contacts if all(r[k]==observation[k] for k in keys)]
    if len(matches)!=1:
        raise ValueError("Agent observation does not identify one saved contact")
    match=matches[0]
    if not math.isfinite(observation["minimum_sampled_orb"]):
        raise ValueError("Agent orb must be finite")
    if abs(match["minimum_sampled_orb"]-observation["minimum_sampled_orb"])>1e-9:
        raise ValueError("Agent orb differs from calculated result")
    for key in ("contact_samples","total_samples","natal_house","transit_natal_houses"):
        if match[key]!=observation[key]:
            raise ValueError("Agent observation changed "+key)
    expected_sensitive=match["contact_samples"]!=match["total_samples"]
    if observation.get("timing_sensitive_in_samples",expected_sensitive)!=expected_sensitive:
        raise ValueError("Agent timing-sensitivity flag differs from calculated result")
    return match


def run(args):
    root=Path(args.output)
    report=json.loads(Path(args.annotations).read_text(encoding="utf-8"))
    entries=report["annotations"]
    checked=[]
    for entry in entries:
        for key in ("subject_id","event_id","annotation_id"):
            if not re.fullmatch(r"[a-z0-9-]+",entry[key]):
                raise ValueError("Unsafe annotation identifier")
        event_path=root/entry["subject_id"]/entry["event_id"]/"event.json"
        event=json.loads(event_path.read_text(encoding="utf-8"))
        natal=json.loads((root/entry["subject_id"]/"natal.json").read_text(encoding="utf-8"))
        if natal["chart_id"]!=entry["natal_chart_id"]:
            raise ValueError("Annotation references a different natal chart")
        if event["source_url"]!=entry["source_url"]:
            raise ValueError("Annotation source does not match event source")
        verified_observations=[]
        for observation in entry["computed_observations"]:
            matched=validate_observation(observation,event["contacts"])
            fields=("transit_body","natal_body","aspect","minimum_sampled_orb","contact_samples","total_samples","natal_house","transit_natal_houses")
            checked_observation={key:matched[key] for key in fields}
            checked_observation["timing_sensitive_in_samples"]=matched["contact_samples"]!=matched["total_samples"]
            verified_observations.append(checked_observation)
        record=dict(entry,computed_observations=verified_observations,status="agent_annotation_pending_review",training_eligible=False,
                    numeric_reference_check="passed_against_saved_computation",
                    event_artifact_sha256=sha256(event_path.read_bytes()).hexdigest(),
                    agent="pilot_analyst",independent_evidence_approval=False)
        checked.append(record)
    with closing(connect(root/"pilot.db")) as db,db:
        db.execute("""CREATE TABLE IF NOT EXISTS pilot_agent_annotations (
          id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES research_subjects(id),
          event_id TEXT NOT NULL REFERENCES research_event_leads(id),
          natal_chart_id TEXT NOT NULL REFERENCES chart_runs(id), report_json TEXT NOT NULL)""")
        for record in checked:
            raw=canonical(record)
            old=db.execute("SELECT report_json FROM pilot_agent_annotations WHERE id=?",
                           (record["annotation_id"],)).fetchone()
            if old and old["report_json"]!=raw:
                raise ValueError("Changed annotation requires a new revision ID")
            db.execute("INSERT OR IGNORE INTO pilot_agent_annotations VALUES (?,?,?,?,?)",
                       (record["annotation_id"],record["subject_id"],record["event_id"],record["natal_chart_id"],raw))
            extra_node(db,record["annotation_id"],"agent_annotation",record["event_id"]+" analyst annotation",record)
            extra_edge(db,record["annotation_id"],"ANNOTATES_EVENT",record["event_id"])
            extra_edge(db,record["annotation_id"],"REFERENCES_NATAL",record["natal_chart_id"])
            for number,observation in enumerate(record["computed_observations"]):
                identifier=record["annotation_id"]+":observation:"+str(number)
                extra_node(db,identifier,"agent_computed_observation",
                           observation["transit_body"]+" "+observation["aspect"]+" natal "+observation["natal_body"],
                           dict(observation,status="calculation_reference_checked",event_id=record["event_id"]))
                extra_edge(db,record["annotation_id"],"HAS_OBSERVATION",identifier)
                extra_edge(db,identifier,"REFERENCES_NATAL_PLACEMENT",record["natal_chart_id"]+":"+observation["natal_body"])
                extra_edge(db,identifier,"DERIVED_FROM_EVENT_SAMPLES",record["event_id"])
    with closing(connect(root/"pilot.db")) as db:
        for table in ("pilot_agent_annotations","pilot_extra_nodes","pilot_extra_edges"):
            cursor=db.execute("SELECT * FROM "+table)
            write_csv(root/(table+".csv"),[dict(r) for r in cursor],[d[0] for d in cursor.description])
    write_json(root/"agent-annotations.json",dict(report,annotations=checked))
    graph=json.loads((root/"graph.json").read_text(encoding="utf-8"))
    ids={r["id"] for r in graph["nodes"]}
    edges={(r["source"],r["relation"],r["target"]) for r in graph["edges"]}
    with closing(connect(root/"pilot.db")) as db:
        for row in db.execute("SELECT * FROM pilot_extra_nodes"):
            if row["id"] not in ids:
                properties=json.loads(row["properties_json"])
                graph["nodes"].append({"id":row["id"],"kind":row["kind"],"label":row["label"],
                                       "status":properties.get("status","provisional"),"properties":properties})
                ids.add(row["id"])
        for row in db.execute("SELECT * FROM pilot_extra_edges"):
            triple=(row["source_id"],row["relation"],row["target_id"])
            if triple not in edges:
                if triple[0] not in ids or triple[2] not in ids:
                    raise ValueError("Unresolved annotation graph reference")
                graph["edges"].append({"source":triple[0],"relation":triple[1],"target":triple[2],
                                       "status":"pending_review","properties":json.loads(row["properties_json"])})
                edges.add(triple)
    write_json(root/"graph.json",graph)
    page="""<!doctype html><html lang="en"><meta charset="utf-8"><title>Cosmora analyst annotations</title>
<style>body{background:#101827;color:#edf3fa;font:17px system-ui;max-width:1100px;margin:40px auto}a{color:#75e1d0}article{padding:20px;margin:20px 0;background:#223047}li{margin:10px 0}</style>
<h1>Agent annotations · pending review</h1><p>Numerical references checked against saved calculations. Historical evidence and interpretations remain unverified; no statistical correlation or predictive validity is established.</p>"""
    for record in checked:
        page+="<article><h2>"+escape(record["subject_id"])+"</h2><p>"+escape(record["event_summary"])+"</p>"
        page+='<p><a href="'+escape(record["source_url"],quote=True)+'">Event source</a></p><ul>'
        for obs in record["computed_observations"]:
            text=f'{obs["transit_body"]} {obs["aspect"]} natal {obs["natal_body"]}: minimum sampled orb {obs["minimum_sampled_orb"]:.3f}°, {obs["contact_samples"]}/{obs["total_samples"]} samples, natal house {obs["natal_house"]}.'
            page+="<li>"+escape(text)+"</li>"
        page+="</ul><p>"+escape(record["timeline_summary"])+"</p><p><strong>Untested hypothesis:</strong> "+escape(record["hypothesis"])+"</p></article>"
    page+="<h2>Not calculated</h2><p>Dispositor chains, progressions, annual profections, zodiacal releasing/Loosing of the Bond, decan rulers and statistical correlation tests remain separate work.</p></html>"
    (root/"agent-annotations.html").write_text(page,encoding="utf-8")
    index=root/"index.html"
    text=index.read_text(encoding="utf-8")
    if 'href="agent-annotations.html"' not in text:
        text=text.replace("<h2>Natal charts</h2>",'<p><a href="agent-annotations.html">Read pending analyst annotations</a></p><h2>Natal charts</h2>')
        index.write_text(text,encoding="utf-8")
    summary=json.loads((root/"run.json").read_text(encoding="utf-8"))
    summary.update(agent_annotations=len(checked),annotation_numeric_references_checked=sum(len(r["computed_observations"]) for r in checked),
                   graph_nodes=len(graph["nodes"]),graph_edges=len(graph["edges"]))
    write_json(root/"run.json",summary)
    print(json.dumps({"agent_annotations":len(checked),"checked_observations":sum(len(r["computed_observations"]) for r in checked),
                      "graph_nodes":len(graph["nodes"]),"graph_edges":len(graph["edges"])}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True)
    parser.add_argument("--annotations",required=True)
    run(parser.parse_args())


if __name__=="__main__":
    main()
