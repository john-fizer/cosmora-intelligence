import copy
import json
from pathlib import Path
import tempfile
import unittest
from cosmora import blinded


class BlindedStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'study.db'
        self.protocol = {'version': 'rules-v1', 'rules': {'r1': 'Synthetic test rule'},
                         'categories': ['career'], 'threshold': 0.5,
                         'window_selection': 'Fixed annual windows including non-events',
                         'techniques': ['natal', 'transits'], 'orb_policy': '3 degrees'}
        chart = {'input': {'name': 'Secret Name', 'person_id': 'secret-id', 'utc': '2000-01-01'},
                 'chart_id': 'identifiable', 'profile': {'houses': 'whole_sign'},
                 'placements': {'SUN': {'longitude': 12.0, 'house': 1, 'sign': 'Aries',
                                        'decan': 2, 'name': 'Secret Name'}},
                 'source_url': 'https://secret.example'}
        self.cases = [{'person_key': p, 'split': split, 'natal': copy.deepcopy(chart),
                       'windows': [{'id': 'w1', 'frames': [copy.deepcopy(chart)]}]} for p, split in
                      [('person-a', 'development'), ('person-b', 'holdout'), ('person-c', 'holdout')]]
        self.study = blinded.create_study(self.db, self.protocol, self.cases)
        self.packet = blinded.export_packet(self.db, self.study)

    def predictions(self):
        return {'agent': 'isolated-agent-v1', 'acknowledges_blinding_limits': True,
                'predictions': [{'case_id': c['case_id'], 'window_id': 'w1', 'category': 'career',
                                 'probability': p, 'rule_ids': ['r1'], 'rationale': 'Synthetic rationale'}
                                for c, p in zip(self.packet['cases'], [0.8, 0.7, 0.2])]}

    def labels(self):
        return {'reviewer': 'independent-labeler', 'independent_of_predictions': True,
                'labels': [{'person_key': p, 'window_id': 'w1', 'category': 'career',
                            'occurred': y, 'source_url': 'https://example.org/evidence',
                            'evidence_note': 'Synthetic fixture; absence requires coverage.'}
                           for p, y in [('person-a', 1), ('person-b', 1), ('person-c', 0)]]}

    def test_packet_excludes_identity_sources_dates_and_split(self):
        text = json.dumps(self.packet)
        for secret in ['Secret Name', 'person-a', 'secret-id', 'identifiable', '2000-01-01',
                       'https://secret.example', 'development', 'holdout']:
            self.assertNotIn(secret, text)
        self.assertEqual(self.packet['cases'][0]['natal']['placements']['SUN']['longitude'], 12.0)

    def test_predictions_are_frozen_and_cannot_be_revised(self):
        report = self.predictions()
        digest = blinded.commit_predictions(self.db, self.study, report)
        self.assertEqual(blinded.commit_predictions(self.db, self.study, report), digest)
        report['predictions'][0]['probability'] = 0.1
        with self.assertRaises(ValueError):
            blinded.commit_predictions(self.db, self.study, report)

    def test_reveal_requires_complete_predictions(self):
        with self.assertRaises(ValueError):
            blinded.reveal(self.db, self.study, self.labels())
        report = self.predictions()
        report['predictions'].pop()
        with self.assertRaises(ValueError):
            blinded.commit_predictions(self.db, self.study, report)

    def test_rejects_nonfinite_probability_and_unknown_rule(self):
        for change in [{'probability': float('nan')}, {'probability': 1.1}, {'rule_ids': ['invented']}]:
            report = self.predictions()
            report['predictions'][0].update(change)
            with self.assertRaises(ValueError):
                blinded.commit_predictions(self.db, self.study, report)

    def test_scoring_includes_absence_and_development_only_baseline(self):
        blinded.commit_predictions(self.db, self.study, self.predictions())
        blinded.reveal(self.db, self.study, self.labels())
        score = blinded.score(self.db, self.study)
        holdout = score['splits']['holdout']
        self.assertAlmostEqual(holdout['brier'], 0.065)
        self.assertAlmostEqual(holdout['baseline_brier'], 0.5)
        self.assertEqual((holdout['tp'], holdout['tn'], holdout['fp'], holdout['fn']), (1, 1, 0, 0))
        self.assertFalse(score['validated_predictive_claim'])
        self.assertEqual(len(score['person_block_null_brier']), 2)
        self.assertAlmostEqual(score['person_block_null_brier'][1], 0.565)

    def test_labels_must_be_complete_binary_independent_and_immutable(self):
        blinded.commit_predictions(self.db, self.study, self.predictions())
        for mutate in [lambda x: x['labels'].pop(),
                       lambda x: x['labels'][0].update(occurred=0.5),
                       lambda x: x.update(independent_of_predictions=False)]:
            labels = self.labels()
            mutate(labels)
            with self.assertRaises(ValueError):
                blinded.reveal(self.db, self.study, labels)
        labels = self.labels()
        blinded.reveal(self.db, self.study, labels)
        labels['labels'][0]['occurred'] = 0
        with self.assertRaises(ValueError):
            blinded.reveal(self.db, self.study, labels)

    def test_revised_rules_require_fresh_holdout_people(self):
        blinded.commit_predictions(self.db, self.study, self.predictions())
        blinded.reveal(self.db, self.study, self.labels())
        revised = dict(self.protocol, version='rules-v2', parent_study=self.study,
                       revision_reason='Development-only hypothesis')
        with self.assertRaises(ValueError):
            blinded.create_study(self.db, revised, self.cases)
        cases = copy.deepcopy(self.cases)
        cases[1]['person_key'] = 'fresh-person-b'
        cases[2]['person_key'] = 'fresh-person-c'
        second = blinded.create_study(self.db, revised, cases)
        self.assertNotEqual(second, self.study)

    def test_person_cannot_cross_splits_and_schedule_is_required(self):
        cases = copy.deepcopy(self.cases)
        cases[1]['person_key'] = 'person-a'
        with self.assertRaises(ValueError):
            blinded.create_study(self.db, self.protocol, cases)
        with self.assertRaises(ValueError):
            blinded.create_study(self.db, dict(self.protocol, window_selection=''), self.cases)

    def test_graph_export_has_prediction_and_rule_provenance(self):
        blinded.commit_predictions(self.db, self.study, self.predictions())
        blinded.reveal(self.db, self.study, self.labels())
        graph = blinded.export_graph(self.db, self.study)
        kinds = {n['kind'] for n in graph['nodes']}
        self.assertTrue({'blind_study', 'blind_prediction', 'event_label', 'interpretation_rule'} <= kinds)
        ids = {n['id'] for n in graph['nodes']}
        for edge in graph['edges']:
            self.assertIn(edge['source'], ids)
            self.assertIn(edge['target'], ids)


class IsolationRegressionTests(unittest.TestCase):
    setUp = BlindedStudyTests.setUp
    predictions = BlindedStudyTests.predictions
    labels = BlindedStudyTests.labels
    def test_saved_pipeline_angles_and_nodes_are_supported(self):
        cases = copy.deepcopy(self.cases)
        for case in cases:
            case['natal']['placements']['ASCENDANT'] = {'longitude': 15.0, 'house': 1}
            case['natal']['placements']['MIDHEAVEN'] = {'longitude': 285.0, 'house': 10}
            case['natal']['placements']['TRUE_SOUTH_NODE'] = {'longitude': 180.0, 'house': 7}
        study = blinded.create_study(self.db, self.protocol, cases)
        packet = blinded.export_packet(self.db, study)
        self.assertIn('ASCENDANT', packet['cases'][0]['natal']['placements'])

    def test_chart_profile_cannot_be_silently_relabelled(self):
        cases = copy.deepcopy(self.cases)
        cases[0]['natal']['profile']['houses'] = 'placidus'
        with self.assertRaises(ValueError):
            blinded.create_study(self.db, self.protocol, cases)

    def test_prepared_study_cannot_commit_after_holdout_exposure(self):
        second = blinded.create_study(self.db, self.protocol, self.cases)
        blinded.commit_predictions(self.db, self.study, self.predictions())
        blinded.reveal(self.db, self.study, self.labels())
        packet = blinded.export_packet(self.db, second)
        report = self.predictions()
        for p, case in zip(report['predictions'], packet['cases']):
            p['case_id'] = case['case_id']
        with self.assertRaises(ValueError):
            blinded.commit_predictions(self.db, second, report)

    def test_complete_cli_handoff(self):
        import subprocess
        import sys
        root = Path(self.temp.name)
        def invoke(action, data=None):
            command = [sys.executable, '-m', 'cosmora.blinded', action, '--db', str(root/'cli.db')]
            if action != 'prepare':
                command += ['--study', study]
            if data is not None:
                path = root/(action+'.json')
                path.write_text(json.dumps(data), encoding='utf-8')
                command += ['--input', str(path)]
            return json.loads(subprocess.check_output(command, text=True))
        study = invoke('prepare', {'protocol': self.protocol, 'cases': self.cases})['study_id']
        packet = invoke('packet')
        report = self.predictions()
        for prediction, case in zip(report['predictions'], packet['cases']):
            prediction['case_id'] = case['case_id']
        self.assertEqual(len(invoke('commit', report)['prediction_sha256']), 64)
        self.assertEqual(invoke('reveal', self.labels())['status'], 'revealed')
        self.assertAlmostEqual(invoke('score')['splits']['holdout']['brier'], 0.065)
        self.assertTrue(invoke('graph')['private_export'])
class PacketCalculationTests(unittest.TestCase):
    setUp = BlindedStudyTests.setUp

    def test_packet_computes_aspects_and_keeps_chart_hashes_private(self):
        cases = copy.deepcopy(self.cases)
        for case in cases:
            case['windows'][0]['frames'][0]['placements']['SUN']['longitude'] = 72.0
        study = blinded.create_study(self.db, self.protocol, cases)
        packet = blinded.export_packet(self.db, study)
        contact = packet['cases'][0]['windows'][0]['contacts_by_frame'][0][0]
        self.assertEqual(contact['aspect'], 'sextile')
        self.assertEqual(contact['orb_deg'], 0.0)
        self.assertNotIn('artifact_sha256', json.dumps(packet))
        graph = blinded.export_graph(self.db, study)
        case = next(n for n in graph['nodes'] if n['kind'] == 'blind_case')
        self.assertEqual(len(case['properties']['natal_artifact_sha256']), 64)