import math
import unittest
from datetime import datetime, timedelta, timezone
from cosmora import techniques as t


class TechniqueArithmeticTests(unittest.TestCase):
    def test_lots_reverse_by_sect_and_preserve_named_nonreversal(self):
        self.assertEqual(t.lots(130,20,80,'day')['fortune'],190)
        self.assertEqual(t.lots(130,20,80,'night')['fortune'],70)
        self.assertEqual(t.lots(130,20,80,'night')['spirit'],190)
        with self.assertRaises(ValueError): t.lots(130,20,80,'unknown')

    def test_profection_counts_completed_age_and_traditional_ruler(self):
        self.assertEqual(t.profection(4,26),{'completed_age':26,'house':3,'sign':'Libra','sign_index':6,'lord':'VENUS'})
        self.assertEqual(t.profection(4,27)['lord'],'MARS')
        with self.assertRaises(ValueError): t.profection(4,26.5)

    def test_dispositors_find_terminal_and_mutual_cycle_without_fake_dominance(self):
        result=t.dispositors({'SUN':45,'VENUS':75,'MERCURY':5,'MARS':10})
        self.assertEqual(result['sole_final_dispositor'],'MARS')
        result=t.dispositors({'MARS':45,'VENUS':5})
        self.assertIsNone(result['sole_final_dispositor'])
        self.assertEqual(set(result['chains']['MARS']['cycle']),{'MARS','VENUS'})
        with self.assertRaises(ValueError): t.dispositors({'SUN':45})

    def test_modern_and_traditional_rulers_are_distinct_profiles(self):
        longitudes={'SUN':305,'SATURN':280,'URANUS':305}
        self.assertEqual(t.dispositors(longitudes,'traditional')['chains']['SUN']['terminal'],'SATURN')
        self.assertEqual(t.dispositors(longitudes,'modern')['chains']['SUN']['terminal'],'URANUS')

    def test_decan_schools_and_half_open_boundaries(self):
        self.assertEqual(t.decans(45,'chaldean')['ruler'],'MOON')
        self.assertEqual(t.decans(45,'triplicity')['ruler'],'MERCURY')
        self.assertEqual(t.decans(10,'chaldean')['decan'],2)
        self.assertEqual(t.decans(359.9,'chaldean')['ruler'],'MARS')

    def test_twelfth_parts_start_from_occupied_sign_not_absolute_harmonic(self):
        result=t.twelfth_parts(349)
        self.assertEqual(result['longitude'],198)
        self.assertEqual(result['sign'],'Libra')

    def test_nakshatra_and_navamsa_boundaries(self):
        result=t.nakshatra(50/3)
        self.assertEqual((result['index'],result['pada']),(2,2))
        self.assertEqual(t.navamsa(50/3)['sign'],'Virgo')
        self.assertEqual(t.navamsa(58)['sign'],'Virgo')
        self.assertEqual(t.nakshatra(0)['index'],1)
        self.assertEqual(t.nakshatra(360)['index'],1)

    def test_karaka_variants_reverse_only_rahu_and_stop_on_unresolved_tie(self):
        planets={'SUN':28,'MOON':25,'MARS':21,'MERCURY':18,'JUPITER':14,'VENUS':9,'SATURN':3,'RAHU':1}
        self.assertEqual(t.chara_karakas(planets,'seven')['roles']['AK'],'SUN')
        self.assertEqual(t.chara_karakas(planets,'eight')['roles']['AK'],'RAHU')
        with self.assertRaises(ValueError): t.chara_karakas(dict(planets,MOON=28),'seven')

    def test_rasi_aspects_are_symmetric_and_exclude_adjacent_fixed(self):
        self.assertEqual(t.rasi_drishti(3),[1,7,10])
        self.assertEqual(t.rasi_drishti(5),[2,8,11])
        for sign in range(12):
            for target in t.rasi_drishti(sign): self.assertIn(sign,t.rasi_drishti(target))

    def test_named_arudha_exception_is_tenth_from_raw_result(self):
        self.assertEqual(t.arudha(0,2)['final_sign_index'],4)
        self.assertEqual(t.arudha(0,0)['final_sign_index'],9)
        self.assertEqual(t.arudha(0,3)['final_sign_index'],3)
        self.assertEqual(t.arudha(0,6)['final_sign_index'],9)

    def test_vimshottari_uses_full_parent_before_birth_for_subperiods(self):
        result=t.vimshottari_balance(50/3)
        self.assertEqual(result['lord'],'VENUS')
        self.assertAlmostEqual(result['balance_years'],15)
        self.assertAlmostEqual(result['elapsed_years'],5)
        self.assertAlmostEqual(result['antardashas'][0]['duration_years'],10/3)
        self.assertTrue(result['antardashas'][0]['ends_before_birth'])

    def test_rejects_nonfinite_positions(self):
        for value in [float('nan'),float('inf')]:
            with self.assertRaises(ValueError): t.navamsa(value)


class ReleasingTests(unittest.TestCase):
    def test_gemini_lob_after_full_6330_day_circuit_and_parent_truncation(self):
        result=t.zodiacal_releasing('2000-01-01T00:00:00Z',7200,10,70,'spirit',2)
        children=[p for p in result['periods'] if p['level']==2]
        self.assertEqual(children[0]['sign'],'Gemini')
        self.assertEqual(children[12]['sign'],'Sagittarius')
        self.assertTrue(children[12]['is_lob'])
        self.assertEqual(children[12]['start_day'],6330)
        self.assertEqual(children[-1]['duration_days'],510)
        self.assertEqual(children[-1]['end_day'],7200)
        self.assertEqual(sum(p['is_lob'] for p in children),1)

    def test_capricorn_is_27_and_same_sign_adjustment_is_spirit_only(self):
        fortune=t.zodiacal_releasing('2000-01-01T00:00:00Z',9720,280,281,'fortune',1)
        self.assertEqual(fortune['periods'][0]['nominal_duration_days'],9720)
        self.assertFalse(fortune['same_sign_adjustment'])
        spirit=t.zodiacal_releasing('2000-01-01T00:00:00Z',100,280,281,'spirit',1)
        self.assertEqual(spirit['effective_start_sign'],'Aquarius')
        self.assertEqual(spirit['natal_spirit_longitude'],281)
        self.assertTrue(spirit['same_sign_adjustment'])

    def test_request_boundaries_and_no_invented_timezone(self):
        with self.assertRaises(ValueError): t.zodiacal_releasing('2000-01-01',10,10,70,'spirit',2)
        result=t.zodiacal_releasing('2000-01-01T00:00:00Z',10,10,70,'spirit',4)
        self.assertTrue(all(p['end_day']<=10 for p in result['periods']))


class MethodRegistryTests(unittest.TestCase):
    def test_research_only_methods_cannot_silently_execute(self):
        with self.assertRaises(ValueError): t.execute('jaimini-chara-dasha',{},'jaimini-sidereal-v1')

    def test_jyotish_rejects_tropical_profile_and_requires_ayanamsha_provenance(self):
        with self.assertRaises(ValueError): t.execute('navamsa',{'longitude':58},'modern-tropical-v1')
        with self.assertRaises(ValueError): t.execute('navamsa',{'longitude':58},'jaimini-sidereal-v1')
        result=t.execute('navamsa',{'longitude':58,'ayanamsha_id':'SE_SIDM_LAHIRI','longitude_source':'synthetic_sidereal_fixture'},'jaimini-sidereal-v1')
        self.assertEqual(result['result']['sign'],'Virgo')
        self.assertFalse(result['training_eligible'])
        self.assertFalse(result['empirical_validation'])
        self.assertEqual(len(result['input_sha256']),64)

    def test_export_graph_does_not_promote_doctrine_to_observation(self):
        graph=t.registry_graph()
        self.assertNotIn('historical_event',{n['kind'] for n in graph['nodes']})
        ids={n['id'] for n in graph['nodes']}
        self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in graph['edges']))


class BoundaryRegressionTests(unittest.TestCase):
    def test_pada_boundaries_and_neighboring_float_are_not_rounded(self):
        self.assertEqual(t.nakshatra(20)['pada'],3)
        self.assertEqual(t.nakshatra(30)['pada'],2)
        self.assertEqual(t.nakshatra(60)['pada'],3)
        self.assertEqual(t.nakshatra(math.nextafter(20,0))['pada'],2)

    def test_request_clipping_is_not_mislabelled_as_parent_boundary(self):
        result=t.zodiacal_releasing('2000-01-01T00:00:00Z',6331,10,70,'spirit',2)
        root=next(p for p in result['periods'] if p['level']==1)
        last=[p for p in result['periods'] if p['level']==2][-1]
        self.assertFalse(root['truncated_by_parent'])
        self.assertTrue(root['truncated_by_request'])
        self.assertFalse(last['truncated_by_parent'])
        self.assertTrue(last['truncated_by_request'])
        self.assertEqual(last['start_day'],6330)
        self.assertEqual(last['duration_days'],1)

    def test_period_limit_rejects_instead_of_returning_partial_schedule(self):
        with self.assertRaises(ValueError):
            t.zodiacal_releasing('2000-01-01T00:00:00Z',7200,10,70,'spirit',4,max_periods=1)

    def test_ayanamsha_provenance_must_be_text_not_boolean(self):
        with self.assertRaises(ValueError):
            t.execute('navamsa',{'longitude':58,'ayanamsha_id':True,'longitude_source':'fixture'},'jaimini-sidereal-v1')
class CliAndIdentityTests(unittest.TestCase):
    def test_calculation_identity_binds_profile_definition(self):
        import copy
        from unittest.mock import patch
        original=t.catalog()
        changed=copy.deepcopy(original)
        changed['profiles']['modern-tropical-v1']['coordinate_note']='different documented profile convention'
        args={'longitudes':{'SUN':125}}
        first=t.execute('dispositor-chains',args,'modern-tropical-v1')
        with patch.object(t,'catalog',return_value=changed):
            second=t.execute('dispositor-chains',args,'modern-tropical-v1')
        self.assertNotEqual(first['input_sha256'],second['input_sha256'])

    def test_eight_karaka_execution_requires_node_mode(self):
        args={'longitudes':{'SUN':28,'MOON':25,'MARS':21,'MERCURY':18,'JUPITER':14,'VENUS':9,'SATURN':3,'RAHU':1},'scheme':'eight','ayanamsha_id':'SE_SIDM_LAHIRI','longitude_source':'synthetic_sidereal_fixture'}
        with self.assertRaises(ValueError): t.execute('chara-karakas',args,'jaimini-sidereal-v1')
        result=t.execute('chara-karakas',dict(args,node_mode='mean'),'jaimini-sidereal-v1')
        self.assertEqual(result['result']['roles']['AK'],'RAHU')

    def test_cli_calculates_and_research_entries_fail(self):
        import json
        from pathlib import Path
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            input_path=Path(folder)/'input.json'
            input_path.write_text(json.dumps({'asc_sign_index':4,'completed_age':26}),encoding='utf-8')
            base=[sys.executable,'-m','cosmora.techniques']
            result=json.loads(subprocess.check_output(base+['calculate','--method','annual-profections','--profile','hellenistic-traditional-v1','--input',str(input_path)],text=True))
            self.assertEqual(result['result']['lord'],'VENUS')
            graph=json.loads(subprocess.check_output(base+['graph'],text=True))
            self.assertEqual(graph['graph_role'],'pending_doctrine_methods')
            failure=subprocess.run(base+['calculate','--method','jaimini-chara-dasha','--profile','jaimini-sidereal-v1','--input',str(input_path)],capture_output=True,text=True)
            self.assertNotEqual(failure.returncode,0)
            self.assertIn('not executable',failure.stderr)
class PackagedExampleTests(unittest.TestCase):
    def test_all_implemented_methods_have_runnable_synthetic_examples(self):
        import json
        for method in t.catalog()['methods']:
            if method['status']!='implemented_arithmetic': continue
            with self.subTest(method=method['id']):
                path=t.ROOT/'methods/examples'/(method['id']+'.json')
                inputs=json.loads(path.read_text(encoding='utf-8'))
                result=t.execute(method['id'],inputs,method['profiles'][0])
                self.assertEqual(result['kind'],'technique_calculation')
                self.assertFalse(result['empirical_validation'])
                self.assertFalse(result['training_eligible'])

class ExactBoundaryRegressionTests(unittest.TestCase):
    def test_subdivision_neighbors_across_zodiac(self):
        from fractions import Fraction
        for step in range(1,108):
            boundary=Fraction(step*10,3)
            for value in (math.nextafter(float(boundary),0),float(boundary),math.nextafter(float(boundary),360)):
                exact=Fraction(value)
                row=t.nakshatra(value)
                self.assertEqual(row['index'],int(exact*3//40)+1,(step,value))
                self.assertEqual(row['pada'],int(exact*3//10)%4+1,(step,value))
                self.assertEqual(t.navamsa(value)['sign_index'],int(((exact*9)%360)//30),(step,value))

    def test_negative_tiny_longitude_stays_in_last_sign(self):
        value=-1e-20
        self.assertTrue(0<=t.longitude(value)<360)
        self.assertEqual(t.position(value)['sign_index'],11)
        self.assertEqual(t.nakshatra(value)['index'],27)


if __name__=='__main__': unittest.main()
