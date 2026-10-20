import copy
import unittest
from cosmora.collective import build_shared,query


def fixture():
    people=[{'person_key':p,'name':p,'provenance':{'source_url':'https://example.test/'+p}} for p in ('a','b')]
    charts={p:{'chart_id':'chart-'+p,'placements':{'SUN':{'longitude':10,'sign':'Aries','house':8}}} for p in ('a','b')}
    windows=[{'person_key':p,'window_id':'w'+str(i),'features':{'annual_profections':[],'releasing':{}}} for p in ('a','b') for i in (1,2)]
    contacts=[{'person_key':p,'window_id':'w1','transit_body':'JUPITER','natal_body':'SUN','aspect':'trine','natal_house':8,'transit_natal_houses':[4],'samples':12,'total_samples':12,'minimum_sampled_orb':0.1} for p in ('a','b')]
    labels=[{'person_key':p,'window_id':'w'+str(i),'category':'award','occurred':int(p=='a' and i==1),'source_url':'https://example.test/registry','year':2000+i,'split':'development' if p=='a' else 'holdout'} for p in ('a','b') for i in (1,2)]
    return people,charts,contacts,windows,labels


class CollectiveTests(unittest.TestCase):
    def test_shared_identity_merges_people_but_preserves_evidence(self):
        data=build_shared(*fixture())
        concepts=[n for n in data['concepts'] if n['kind']=='transit_pattern']
        self.assertEqual(len(concepts),1)
        node=concepts[0]
        self.assertEqual(node['distinct_people'],2)
        self.assertEqual(node['distinct_windows'],2)
        self.assertEqual(node['evidence_records'],2)
        self.assertEqual(set(node['case_keys']),{'a|w1','b|w1'})
        self.assertEqual({data['evidence'][i]['person_key'] for i in node['evidence_refs']},{'a','b'})
        self.assertNotIn('person',node['id'])

    def test_natal_concepts_are_shared_and_exact_degrees_stay_in_evidence(self):
        inputs=fixture();inputs[1]['b']['placements']['SUN']['longitude']=15
        data=build_shared(*inputs);node=next(n for n in data['concepts'] if n['kind']=='natal_configuration')
        self.assertEqual(node['distinct_people'],2)
        self.assertEqual({data['evidence'][i]['longitude'] for i in node['evidence_refs']},{10,15})

    def test_unique_windows_not_monthly_samples_and_four_cell_counts(self):
        node=next(n for n in build_shared(*fixture())['concepts'] if n['kind']=='transit_pattern')
        stats=node['descriptive_outcomes']['award']
        self.assertEqual((stats['present_event_windows'],stats['present_non_event_windows'],stats['absent_event_windows'],stats['absent_non_event_windows']),(1,1,0,2))
        self.assertEqual(stats['event_rate_when_present'],.5)
        self.assertEqual(stats['event_rate_when_absent'],0)

    def test_person_and_house_query_does_not_return_other_person_evidence(self):
        data=build_shared(*fixture());rows=query(data,house=4,person='a',minimum_people=2)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['case_keys'],['a|w1'])
        self.assertTrue(all(data['evidence'][i]['person_key']=='a' for i in rows[0]['evidence_refs']))
        self.assertEqual(query(data,house=9),[])

    def test_static_natal_placement_does_not_invent_absent_cases(self):
        node=next(n for n in build_shared(*fixture())['concepts'] if n['kind']=='natal_configuration')
        counts=node['descriptive_outcomes']['award']
        self.assertEqual(counts['present_windows'],4)
        self.assertEqual(counts['absent_windows'],0)
        self.assertIsNone(counts['event_rate_when_absent'])

    def test_dispositor_profiles_do_not_collapse_together(self):
        inputs=fixture();records=[]
        for person in ('a','b'):
            for profile in ('traditional','modern'):
                records.append({'person_key':person,'calculation':{'method_id':'dispositor-chains','profile_id':profile,'input_sha256':'fixture','result':{'rulership':profile,'chains':{'SUN':{'path':['SUN','SUN'],'cycle':['SUN']}}}}})
        data=build_shared(*inputs,calculations=records)
        chains=[n for n in data['concepts'] if n['kind']=='dispositor_configuration']
        self.assertEqual(len(chains),2)
        self.assertTrue(all(n['distinct_people']==2 for n in chains))
        self.assertEqual({n['profile_id'] for n in chains},{'traditional','modern'})

    def test_missing_outcome_is_not_negative(self):
        inputs=list(fixture());inputs[4]=inputs[4][:-1]
        with self.assertRaises(ValueError): build_shared(*inputs)

    def test_duplicate_contact_and_nonfinite_orb_rejected(self):
        inputs=list(fixture());inputs[2]=inputs[2]+[copy.deepcopy(inputs[2][0])]
        with self.assertRaises(ValueError): build_shared(*inputs)
        inputs=fixture();inputs[2][0]['minimum_sampled_orb']=float('nan')
        with self.assertRaises(ValueError): build_shared(*inputs)

    def test_references_resolve_and_graph_is_descriptive(self):
        data=build_shared(*fixture());ids={n['id'] for n in data['nodes']}
        self.assertEqual(len(ids),len(data['nodes']))
        self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in data['edges']))
        self.assertFalse(data['metadata']['training_eligible'])
        self.assertTrue(all(not n['training_eligible'] for n in data['concepts']))


if __name__=='__main__': unittest.main()
