"""Blinded chart experiments: prepare, commit, reveal, score, and export provenance.

The private ledger must never be mounted in the interpreting agent's environment.
Pseudonymization cannot prevent recognition of a famous planetary configuration.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import re
import sqlite3
from uuid import uuid4
from .charts import BODIES, PROFILE, placement
from .pilot import ASPECTS, ORB, compare_positions

SCHEMA = """
CREATE TABLE IF NOT EXISTS blind_studies (
 id TEXT PRIMARY KEY, protocol TEXT NOT NULL, cases TEXT NOT NULL,
 packet TEXT NOT NULL, created_at TEXT NOT NULL,
 predictions TEXT, prediction_hash TEXT, committed_at TEXT,
 labels TEXT, revealed_at TEXT
);
"""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def open_db(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def load(db, study):
    row = db.execute('SELECT * FROM blind_studies WHERE id=?', (study,)).fetchone()
    if row is None:
        raise ValueError('Unknown study')
    return dict(row)


def chart_only(chart):
    """Allow numeric placements only; never copy identifiers, dates or free text."""
    for key, value in chart.get('profile', {}).items():
        if key in PROFILE and value != PROFILE[key]:
            raise ValueError('Chart profile differs from the supported calculation profile')
    result = {}
    allowed = set(BODIES) | {'ASCENDANT', 'MIDHEAVEN', 'ASC', 'MC', 'TRUE_SOUTH_NODE', 'MEAN_SOUTH_NODE',
                              'TRUE_SOUTH', 'MEAN_SOUTH'}
    for body, value in chart['placements'].items():
        if body not in allowed:
            raise ValueError('Unknown chart point')
        longitude = value['longitude']
        if isinstance(longitude, bool) or not isinstance(longitude, (int, float)) or not math.isfinite(longitude):
            raise ValueError('Invalid chart longitude')
        item = placement(longitude, None)
        house = value.get('house')
        if house is not None and (type(house) is not int or not 1 <= house <= 12):
            raise ValueError('Invalid house')
        item['house'] = house
        speed = value.get('speed_deg_per_day')
        if speed is not None:
            if isinstance(speed, bool) or not isinstance(speed, (int, float)) or not math.isfinite(speed):
                raise ValueError('Invalid speed')
            item['speed_deg_per_day'] = speed
            item['retrograde'] = speed < 0
        result[body] = item
    if not result:
        raise ValueError('Empty chart')
    return {'profile': PROFILE, 'placements': result}


def create_study(path, protocol, cases):
    for key in ('version', 'rules', 'categories', 'window_selection', 'techniques', 'orb_policy'):
        if not protocol.get(key):
            raise ValueError('Missing protocol field: ' + key)
    if not isinstance(protocol['rules'], dict) or not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in protocol['rules'].items()):
        raise ValueError('Rules need stable IDs and explicit descriptions')
    categories = protocol['categories']
    if not isinstance(categories, list) or not all(isinstance(c, str) and re.fullmatch(r'[a-z][a-z0-9_]*', c) for c in categories) or len(set(categories)) != len(categories):
        raise ValueError('Categories must be unique controlled codes')
    threshold = protocol.get('threshold')
    if type(threshold) not in (int, float) or not math.isfinite(threshold) or not 0 < threshold < 1:
        raise ValueError('Threshold must be fixed between zero and one')
    if not cases or len({c['person_key'] for c in cases}) != len(cases):
        raise ValueError('One case per person; people cannot cross splits')
    if {c['split'] for c in cases} != {'development', 'holdout'}:
        raise ValueError('Both development and holdout people are required')
    public, private = [], []
    window_grid = None
    for case in cases:
        if not isinstance(case['person_key'], str) or not case['person_key'].strip():
            raise ValueError('Stable private person key required')
        windows = case['windows']
        ids = [w['id'] for w in windows]
        if not ids or len(set(ids)) != len(ids) or not all(re.fullmatch(r'w[0-9]+', x) for x in ids):
            raise ValueError('Use unique neutral window IDs such as w1')
        if window_grid is None:
            window_grid = ids
        if ids != window_grid:
            raise ValueError('All people need the same preselected window grid')
        natal = chart_only(case['natal'])
        safe_windows = []
        for window in windows:
            if not window['frames']:
                raise ValueError('Every window requires chart frames')
            frames = [chart_only(f) for f in window['frames']]
            safe_windows.append({'id': window['id'], 'frames': frames,
                                 'contacts_by_frame': [compare_positions(natal['placements'], f['placements']) for f in frames]})
        identifier = 'case-' + uuid4().hex
        public.append({'case_id': identifier, 'natal': natal, 'windows': safe_windows})
        private.append({'case_id': identifier, 'person_key': case['person_key'], 'split': case['split'],
                        'natal_chart_id': case['natal'].get('chart_id'),
                        'natal_artifact_sha256': sha256(canonical(case['natal']).encode()).hexdigest(),
                        'windows': [{'id': w['id'], 'metadata': {k: v for k, v in w.items() if k != 'frames'},
                                     'frame_artifact_sha256': [sha256(canonical(f).encode()).hexdigest() for f in w['frames']]} for w in windows]})
    # Explicit protocol fields only: operator must ensure rule text contains no identity clues.
    rulebook = {k: protocol[k] for k in ('version', 'rules', 'categories', 'threshold', 'techniques', 'orb_policy')}
    rulebook['computed_aspect_policy'] = {'angles': ASPECTS, 'orb_degrees': ORB}
    packet = {'schema': 'cosmora-blind-v1', 'rulebook': rulebook, 'cases': public,
              'agent_instructions': 'Use only this packet in an isolated session without tools, memory, sources or identities. Do not identify people. Return one probability for every case/window/category, rule_ids and rationale. Acknowledge recognition risk. Freeze output before any labels are disclosed.'}
    with closing(open_db(path)) as db, db:
        parent = protocol.get('parent_study')
        if parent:
            prior = load(db, parent)
            if not prior['labels'] or not protocol.get('revision_reason'):
                raise ValueError('Revision needs a revealed parent study and a reason')
        used = set()
        for row in db.execute('SELECT cases FROM blind_studies WHERE labels IS NOT NULL'):
            used.update(c['person_key'] for c in json.loads(row['cases']))
        if any(c['person_key'] in used for c in private if c['split'] == 'holdout'):
            raise ValueError('Revealed people cannot be fresh holdout subjects')
        identifier = 'study-' + uuid4().hex
        db.execute('INSERT INTO blind_studies(id,protocol,cases,packet,created_at) VALUES(?,?,?,?,?)',
                   (identifier, canonical(protocol), canonical(private), canonical(packet), stamp()))
    return identifier


def export_packet(path, study):
    with closing(open_db(path)) as db:
        return json.loads(load(db, study)['packet'])


def expected_keys(row, private=False):
    packet = json.loads(row['packet'])
    mapping = {c['case_id']: c['person_key'] for c in json.loads(row['cases'])}
    return {(mapping[c['case_id']] if private else c['case_id'], w['id'], category)
            for c in packet['cases'] for w in c['windows'] for category in packet['rulebook']['categories']}


def commit_predictions(path, study, report):
    raw = canonical(report)
    with closing(open_db(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = load(db, study)
        if row['predictions'] is not None:
            if row['predictions'] != raw:
                raise ValueError('Predictions are frozen; use a new study for revised rules')
            return row['prediction_hash']
        if row['labels'] or not report.get('agent') or report.get('acknowledges_blinding_limits') is not True:
            raise ValueError('An isolated agent and blinding-limit acknowledgment are required')
        holdout = {c['person_key'] for c in json.loads(row['cases']) if c['split'] == 'holdout'}
        for prior in db.execute('SELECT cases FROM blind_studies WHERE labels IS NOT NULL'):
            if holdout & {c['person_key'] for c in json.loads(prior['cases'])}:
                raise ValueError('Holdout people were exposed after study preparation')
        rules = json.loads(row['protocol'])['rules']
        keys = []
        for prediction in report['predictions']:
            keys.append((prediction['case_id'], prediction['window_id'], prediction['category']))
            p = prediction['probability']
            if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
                raise ValueError('Probability must be finite and between zero and one')
            refs = prediction['rule_ids']
            if not isinstance(refs, list) or not refs or any(r not in rules for r in refs) or not prediction.get('rationale'):
                raise ValueError('Prediction requires registered rule IDs and rationale')
        if len(keys) != len(set(keys)) or set(keys) != expected_keys(row):
            raise ValueError('Predictions must cover the complete case/window/category grid exactly once')
        digest = sha256(raw.encode()).hexdigest()
        db.execute('UPDATE blind_studies SET predictions=?,prediction_hash=?,committed_at=? WHERE id=?',
                   (raw, digest, stamp(), study))
        return digest


def reveal(path, study, report):
    raw = canonical(report)
    with closing(open_db(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = load(db, study)
        if not row['predictions']:
            raise ValueError('Commit complete predictions before revealing labels')
        if row['labels']:
            if row['labels'] != raw:
                raise ValueError('Labels are frozen; corrections require a separate study')
            return
        agent = json.loads(row['predictions'])['agent']
        if not report.get('reviewer') or report['reviewer'] == agent or report.get('independent_of_predictions') is not True:
            raise ValueError('Labels require an independent reviewer attestation')
        keys = []
        for label in report['labels']:
            keys.append((label['person_key'], label['window_id'], label['category']))
            if type(label['occurred']) is not int or label['occurred'] not in (0, 1):
                raise ValueError('Labels must be binary; unknown outcomes cannot be treated as absence')
            if not label.get('source_url', '').startswith(('https://', 'http://')) or not label.get('evidence_note'):
                raise ValueError('Both event and absence labels require a source and evidence/coverage note')
        if len(keys) != len(set(keys)) or set(keys) != expected_keys(row, private=True):
            raise ValueError('Labels must cover the complete grid exactly once')
        db.execute('UPDATE blind_studies SET labels=?,revealed_at=? WHERE id=?', (raw, stamp(), study))


def score(path, study):
    with closing(open_db(path)) as db:
        row = load(db, study)
    if not row['labels']:
        raise ValueError('Labels have not been revealed')
    protocol = json.loads(row['protocol'])
    people = {c['case_id']: c for c in json.loads(row['cases'])}
    labels = {(l['person_key'], l['window_id'], l['category']): l['occurred'] for l in json.loads(row['labels'])['labels']}
    observations = []
    for p in json.loads(row['predictions'])['predictions']:
        person = people[p['case_id']]
        observations.append(dict(p, person_key=person['person_key'], split=person['split'],
                                 y=labels[(person['person_key'], p['window_id'], p['category'])]))
    baseline = {}
    for category in protocol['categories']:
        ys = [o['y'] for o in observations if o['split'] == 'development' and o['category'] == category]
        baseline[category] = sum(ys) / len(ys)
    splits = {}
    for split in ('development', 'holdout'):
        rows = [o for o in observations if o['split'] == split]
        counts = dict(tp=0, tn=0, fp=0, fn=0)
        for o in rows:
            predicted = o['probability'] >= protocol['threshold']
            counts[('tp' if o['y'] else 'fp') if predicted else ('fn' if o['y'] else 'tn')] += 1
        tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
        splits[split] = dict(counts, cells=len(rows), people=len({o['person_key'] for o in rows}),
            brier=sum((o['probability']-o['y'])**2 for o in rows)/len(rows),
            baseline_brier=sum((baseline[o['category']]-o['y'])**2 for o in rows)/len(rows),
            precision=tp/(tp+fp) if tp+fp else None, recall=tp/(tp+fn) if tp+fn else None)
    holdout = [c['person_key'] for c in people.values() if c['split'] == 'holdout']
    held = [o for o in observations if o['split'] == 'holdout']
    # Exact person-block permutations for small studies; never present these as independent rows.
    null = []
    if len(holdout) <= 7:
        for permutation in itertools.permutations(holdout):
            mapping = dict(zip(holdout, permutation))
            null.append(sum((o['probability']-labels[(mapping[o['person_key']], o['window_id'], o['category'])])**2 for o in held)/len(held))
    return {'study_id': study, 'protocol_version': protocol['version'], 'prediction_sha256': row['prediction_hash'],
            'splits': splits, 'development_category_rates': baseline, 'person_block_null_brier': null,
            'null_status': 'exact_including_identity' if null else 'not_computed_more_than_seven_people',
            'validated_predictive_claim': False, 'training_eligible': False,
            'limits': 'Descriptive scores only. Labels are reviewer attestations, not independently verified evidence. No multiple-testing correction, power analysis or calibrated confidence interval. Charts may reveal identities. Local ledger is not tamper-proof preregistration.'}


def export_graph(path, study):
    with closing(open_db(path)) as db:
        row = load(db, study)
    protocol = json.loads(row['protocol'])
    nodes = [{'id': study, 'kind': 'blind_study', 'properties': {'protocol': protocol, 'prediction_sha256': row['prediction_hash'], 'created_at': row['created_at'], 'committed_at': row['committed_at'], 'revealed_at': row['revealed_at']}}]
    edges = []
    for rule, description in protocol['rules'].items():
        rid = study + ':rule:' + rule
        nodes.append({'id': rid, 'kind': 'interpretation_rule', 'properties': {'text': description}})
        edges.append({'source': study, 'relation': 'USES_RULE', 'target': rid})
    mapping = {c['case_id']: c['person_key'] for c in json.loads(row['cases'])}
    for case in json.loads(row['cases']):
        cid = study + ':' + case['case_id']
        nodes.append({'id': cid, 'kind': 'blind_case', 'properties': case})
        edges.append({'source': study, 'relation': 'HAS_BLIND_CASE', 'target': cid})
    prediction_ids = {}
    if row['predictions']:
        for i, p in enumerate(json.loads(row['predictions'])['predictions']):
            pid = study + ':prediction:' + str(i)
            nodes.append({'id': pid, 'kind': 'blind_prediction', 'properties': p})
            edges.append({'source': study, 'relation': 'HAS_FROZEN_PREDICTION', 'target': pid})
            prediction_ids[(mapping[p['case_id']], p['window_id'], p['category'])] = pid
            edges.append({'source': pid, 'relation': 'PREDICTS_FOR', 'target': study + ':' + p['case_id']})
            for rule in p['rule_ids']:
                edges.append({'source': pid, 'relation': 'DERIVED_USING_RULE', 'target': study + ':rule:' + rule})
    if row['labels']:
        for i, label in enumerate(json.loads(row['labels'])['labels']):
            lid = study + ':label:' + str(i)
            nodes.append({'id': lid, 'kind': 'event_label', 'properties': dict(label, status='reviewer_attested')})
            edges.append({'source': prediction_ids[(label['person_key'], label['window_id'], label['category'])],
                          'relation': 'EVALUATED_AGAINST', 'target': lid})
        nodes.append({'id': study + ':score', 'kind': 'blind_evaluation', 'properties': score(path, study)})
        edges.append({'source': study, 'relation': 'HAS_EVALUATION', 'target': study + ':score'})
    return {'nodes': nodes, 'edges': edges, 'private_export': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'packet', 'commit', 'reveal', 'score', 'graph'])
    parser.add_argument('--db', required=True)
    parser.add_argument('--study')
    parser.add_argument('--input', help='JSON protocol/cases manifest, predictions, or labels')
    parser.add_argument('--output', help='Write JSON result instead of stdout')
    args = parser.parse_args()
    if args.action in ('prepare', 'commit', 'reveal') and not args.input:
        parser.error('--input is required for this action')
    if args.action != 'prepare' and not args.study:
        parser.error('--study is required for this action')
    data = json.loads(Path(args.input).read_text(encoding='utf-8')) if args.input else None
    if args.action == 'prepare':
        result = {'study_id': create_study(args.db, data['protocol'], data['cases'])}
    elif args.action == 'commit':
        result = {'prediction_sha256': commit_predictions(args.db, args.study, data)}
    elif args.action == 'reveal':
        reveal(args.db, args.study, data)
        result = {'status': 'revealed'}
    else:
        result = {'packet': export_packet, 'score': score, 'graph': export_graph}[args.action](args.db, args.study)
    output = json.dumps(result, indent=2, allow_nan=False)
    if args.output:
        Path(args.output).write_text(output + '\n', encoding='utf-8')
    else:
        print(output)


if __name__ == '__main__':
    main()