"""Canonical cross-person concepts with traceable cases and descriptive counts.

This is a post-reveal exploratory graph, not a new prediction experiment.
"""
import argparse
import ast
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import csv
import math

SIGNS=('Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False,ensure_ascii=False)


def descriptive_stats(present,universe,labels,categories):
    present=set(present)&set(universe);universe=set(universe);absent=universe-present
    result={}
    for category in categories:
        observed={key:labels[(key,category)] for key in universe}
        event_with=sum(observed[k] for k in present)
        event_without=sum(observed[k] for k in absent)
        result[category]={'present_event_windows':event_with,'present_non_event_windows':len(present)-event_with,
                          'absent_event_windows':event_without,'absent_non_event_windows':len(absent)-event_without,
                          'present_windows':len(present),'absent_windows':len(absent),
                          'event_rate_when_present':event_with/len(present) if present else None,
                          'event_rate_when_absent':event_without/len(absent) if absent else None}
    return result


def build_shared(people,charts,contacts,windows,outcomes,calculations=None):
    """Inputs are provisional saved artifacts, never promoted to approved facts."""
    person_map={p['person_key']:p for p in people}
    if set(charts)!=set(person_map): raise ValueError('Every person requires one natal chart')
    if len(person_map)!=len(people): raise ValueError('Duplicate person keys')
    cases={}
    for w in windows:
        person=w['person_key'];wid=w['window_id'];key=person+'|'+wid
        if person not in person_map or key in cases: raise ValueError('Unknown person or duplicate case')
        cases[key]={'person_key':person,'window_id':wid,'features':w['features'],'labels':{}}
    labels={};categories=sorted({o['category'] for o in outcomes})
    if not categories: raise ValueError('Outcome categories are required')
    for o in outcomes:
        key=o['person_key']+'|'+o['window_id'];pair=(key,o['category'])
        if key not in cases or pair in labels or type(o['occurred']) is not int or o['occurred'] not in (0,1):
            raise ValueError('Unknown, duplicated or nonbinary outcome')
        if not o.get('source_url'): raise ValueError('Labels require provenance')
        labels[pair]=o['occurred'];cases[key]['labels'][o['category']]={'occurred':o['occurred'],'source_url':o['source_url']}
        cases[key]['year']=o['year'];cases[key]['split']=o['split']
    if set(labels)!={(key,c) for key in cases for c in categories}: raise ValueError('Missing labels remain unknown; complete grid required')
    nodes={};edges={};evidence=[]
    def node(id,kind,label,**props):
        if id not in nodes: nodes[id]={'id':id,'kind':kind,'label':label,**props,'_cases':set(),'_people':set(),'_refs':set(),'_house_cases':defaultdict(set)}
        return nodes[id]
    def edge(a,relation,b,**props):
        key=(a,relation,b)
        if key not in edges: edges[key]={'source':a,'relation':relation,'target':b,**props}
    def attach(n,person,key,reference,houses=()):
        n['_people'].add(person)
        if key: n['_cases'].add(key)
        n['_refs'].add(reference)
        for h in houses:
            if key: n['_house_cases'][str(h)].add(key)
    for h in range(1,13): node('house:'+str(h),'house','House '+str(h),house=h)
    for sign in SIGNS: node('sign:'+sign,'sign',sign,sign=sign)
    for category in categories: node('event:'+category,'event_category',category.replace('_',' '),category=category)
    for person,p in person_map.items(): node('person:'+person,'person',p['name'],person_key=person)
    for key,c in cases.items():
        node('case:'+key,'case',str(c['year'])+' / '+person_map[c['person_key']]['name'],case_key=key,**{k:v for k,v in c.items() if k!='features'})
        edge('person:'+c['person_key'],'HAS_WINDOW','case:'+key)
        for category,label in c['labels'].items():
            edge('case:'+key,'HAS_POSITIVE_LABEL' if label['occurred'] else 'HAS_NEGATIVE_LABEL','event:'+category,source_url=label['source_url'],status='registry_extracted_independent_review_partial')
    person_cases={p:{key for key,c in cases.items() if c['person_key']==p} for p in person_map}
    for person,chart in charts.items():
        if person not in person_map: raise ValueError('Unknown chart owner')
        chart_id=chart['chart_id'];node(chart_id,'natal_chart',person_map[person]['name']+' natal',person_key=person)
        edge('person:'+person,'HAS_NATAL_CHART',chart_id)
        for body,row in chart['placements'].items():
            h=row['house'];sign=row['sign']
            if type(h) is not int or not 1<=h<=12 or sign not in SIGNS: raise ValueError('Invalid natal placement')
            node('point:'+body,'point',body.replace('_',' ').title(),point=body)
            id='natal:'+body+':'+sign+':H'+str(h)
            n=node(id,'natal_configuration',body.replace('_',' ').title()+' in '+sign+' / House '+str(h),house=h,point=body,sign=sign,method='natal_placement')
            ref=len(evidence);evidence.append({'kind':'natal_placement','person_key':person,'chart_id':chart_id,'body':body,'longitude':row['longitude'],'source_file':'charts/'+person+'/natal.json','birth_source_url':person_map[person].get('provenance',{}).get('source_url'),'source_status':'publisher_reference_primary_uninspected'})
            for key in person_cases[person]: attach(n,person,key,ref,[h])
            edge(chart_id,'INSTANTIATES',id);edge(id,'NATAL_POINT','point:'+body);edge(id,'IN_HOUSE','house:'+str(h));edge(id,'IN_SIGN','sign:'+sign)
    counters=defaultdict(int);seen_contacts=set()
    for index,row in enumerate(contacts):
        person=row['person_key'];wid=row['window_id'];key=person+'|'+wid
        if key not in cases: raise ValueError('Contact has unknown case')
        t,natal,aspect=row['transit_body'],row['natal_body'],row['aspect'];h=int(row['natal_house'])
        pair=(key,t,natal,aspect)
        if pair in seen_contacts: raise ValueError('Duplicate aggregated contact pair in one window')
        seen_contacts.add(pair)
        samples,total=int(row['samples']),int(row['total_samples']);orb=float(row['minimum_sampled_orb'])
        if not 1<=samples<=total or not math.isfinite(orb) or not 0<=orb<=3: raise ValueError('Invalid sampled contact values')
        hs=row['transit_natal_houses'];hs=ast.literal_eval(hs) if isinstance(hs,str) else hs
        if not 1<=h<=12 or any(type(v) is not int or not 1<=v<=12 for v in hs): raise ValueError('Invalid house')
        if natal not in charts[person]['placements']: raise ValueError('Unknown natal point')
        for body in (t,natal): node('point:'+body,'point',body.replace('_',' ').title(),point=body)
        node('aspect:'+aspect,'aspect',aspect,aspect=aspect)
        id='pattern:'+t+':'+aspect+':'+natal+':H'+str(h)
        n=node(id,'transit_pattern',t.replace('_',' ').title()+' '+aspect+' natal '+natal.replace('_',' ').title()+' / House '+str(h),house=h,transit_point=t,natal_point=natal,aspect=aspect,method='sampled_transit_aspect')
        local_index=counters[key];counters[key]+=1;ref=len(evidence)
        evidence.append({'kind':'sampled_contact','person_key':person,'window_id':wid,'case_key':key,'source_csv_row':index+2,'source_file':'contacts/'+person+'/'+wid+'.json','source_index':local_index,'transit_body':t,'natal_body':natal,'aspect':aspect,'natal_house':h,'transit_natal_houses':hs,'samples':int(row['samples']),'total_samples':int(row['total_samples']),'minimum_sampled_orb':float(row['minimum_sampled_orb'])})
        attach(n,person,key,ref,set([h]+hs));edge(id,'PRESENT_IN','case:'+key)
        edge(id,'TRANSIT_POINT','point:'+t);edge(id,'NATAL_POINT','point:'+natal);edge(id,'ASPECT_TYPE','aspect:'+aspect);edge(id,'TO_NATAL_HOUSE','house:'+str(h))
        for th in hs: edge(id,'THROUGH_NATAL_HOUSE','house:'+str(th))
    for key,c in cases.items():
        person=c['person_key'];f=c['features']
        for pf in f['annual_profections']:
            h=pf['house'];id='profection:H'+str(h)+':'+pf['sign']+':'+pf['lord']
            n=node(id,'profection_configuration','House '+str(h)+' profection / '+pf['sign']+' / '+pf['lord'].title(),house=h,sign=pf['sign'],point=pf['lord'],method='annual-profections')
            node('point:'+pf['lord'],'point',pf['lord'].title(),point=pf['lord'])
            ref=len(evidence);evidence.append({'kind':'annual_profection','person_key':person,'case_key':key,'window_id':c['window_id'],'source_file':'window-features.json','feature':pf})
            attach(n,person,key,ref,[h]);edge(id,'PRESENT_IN','case:'+key);edge(id,'ACTIVATES_NATAL_HOUSE','house:'+str(h));edge(id,'IN_SIGN','sign:'+pf['sign']);edge(id,'TIME_LORD','point:'+pf['lord'])
        for lot,periods in f['releasing'].items():
            for p in periods:
                id='releasing:'+lot+':L'+str(p['level'])+':'+p['sign']
                n=node(id,'releasing_configuration',lot.title()+' releasing L'+str(p['level'])+' / '+p['sign'],sign=p['sign'],point=p['ruler'],method='zodiacal-releasing',release_lot=lot,level=p['level'])
                node('point:'+p['ruler'],'point',p['ruler'].title(),point=p['ruler'])
                ref=len(evidence);evidence.append({'kind':'releasing_interval','person_key':person,'case_key':key,'window_id':c['window_id'],'source_file':'window-features.json','feature':p,'release_lot':lot,'house_reference':'fortune_relative_not_natal'})
                attach(n,person,key,ref);edge(id,'PRESENT_IN','case:'+key);edge(id,'IN_SIGN','sign:'+p['sign']);edge(id,'TIME_LORD','point:'+p['ruler'])
    for record_index,record in enumerate(calculations or []):
        run=record['calculation']
        if run['method_id']!='dispositor-chains': continue
        person=record['person_key'];profile=run['profile_id']
        if person not in person_map: raise ValueError('Unknown calculation owner')
        for body,chain in run['result']['chains'].items():
            path=chain['path'];id='dispositor:'+profile+':'+':'.join(path)
            n=node(id,'dispositor_configuration',run['result']['rulership'].title()+' '+ ' → '.join(path),point=body,path=path,cycle=chain['cycle'],profile_id=profile,method='dispositor-chains')
            ref=len(evidence);evidence.append({'kind':'dispositor_chain','person_key':person,'source_file':'calculation-records-complete.json','source_index':record_index,'starting_point':body,'path':path,'profile_id':profile,'input_sha256':run['input_sha256']})
            h=charts[person]['placements'][body]['house']
            for key in person_cases[person]: attach(n,person,key,ref,[h]);edge(id,'PRESENT_IN','case:'+key)
            for point in path:
                node('point:'+point,'point',point.replace('_',' ').title(),point=point)
                edge(id,'CHAIN_POINT','point:'+point)
            edge(id,'NATAL_HOUSE_EVIDENCE','house:'+str(h))
    for n in list(nodes.values()):
        if n.get('method'):
            mid='method:'+n['method'];node(mid,'calculation_method',n['method'].replace('_',' ').replace('-',' '),method=n['method']);edge(n['id'],'USES_METHOD',mid)
        if n.get('profile_id'):
            pid='profile:'+n['profile_id'];node(pid,'tradition_profile',n['profile_id'],profile_id=n['profile_id']);edge(n['id'],'USES_PROFILE',pid)
    for key,c in cases.items():
        for label in c['labels'].values():
            url=label['source_url'];sid='source:'+sha256(url.encode()).hexdigest()[:20]
            node(sid,'source_reference',url,source_url=url,review_status='coordinator_extracted_independent_review_partial')
            edge('case:'+key,'LABEL_SOURCE',sid)
    concepts=[]
    for n in nodes.values():
        n['case_keys']=sorted(n.pop('_cases'));n['person_keys']=sorted(n.pop('_people'));n['evidence_refs']=sorted(n.pop('_refs'));n['house_case_keys']={h:sorted(keys) for h,keys in n.pop('_house_cases').items()}
        n['distinct_people']=len(n['person_keys']);n['distinct_windows']=len(n['case_keys']);n['evidence_records']=len(n['evidence_refs'])
        if n['kind'] in ('natal_configuration','transit_pattern','profection_configuration','releasing_configuration','dispositor_configuration'):
            n['descriptive_outcomes']=descriptive_stats(n['case_keys'],cases,labels,categories)
            n['status']='exploratory_post_reveal';n['training_eligible']=False;concepts.append(n)
    ids=set(nodes)
    if any(e['source'] not in ids or e['target'] not in ids for e in edges.values()): raise AssertionError('Unresolved graph reference')
    metadata={'version':'collective-v1','people':len(people),'windows':len(cases),'concepts':len(concepts),'shared_concepts':sum(n['distinct_people']>=2 for n in concepts),'source_contact_records':len(contacts),'categories':categories,'aggregation':'Canonical concept identity excludes person; distinct cases and people are retained. Multiple samples of a pair in one year are one contact record, not independent events.','validation':'Descriptive post-reveal exploration; repeated windows/people are dependent. No significance, causation, ML fitting, fresh holdout or predictive improvement is claimed.','nominal_birth_times_only':True,'training_eligible':False}
    return {'metadata':metadata,'nodes':sorted(nodes.values(),key=lambda n:n['id']),'edges':sorted(edges.values(),key=lambda e:(e['source'],e['relation'],e['target'])),'concepts':concepts,'evidence':evidence,'cases':cases}


def build_from_directory(directory):
    root=Path(directory)
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8-sig'))
    people=read('birth-inputs.json');charts={p['person_key']:read(Path('charts')/p['person_key']/'natal.json') for p in people}
    with (root/'all-window-contacts.csv').open(encoding='utf-8-sig',newline='') as f: contacts=list(csv.DictReader(f))
    outcomes=read('results.json')
    if set(read('protocol.json')['categories'])!={o['category'] for o in outcomes}: raise ValueError('Entire outcome category is missing')
    result=build_shared(people,charts,contacts,read('window-features.json'),outcomes,read('calculation-records-complete.json'))
    paths=[root/'birth-inputs.json',root/'all-window-contacts.csv',root/'window-features.json',root/'results.json',root/'calculation-records-complete.json']+[root/'charts'/p['person_key']/'natal.json' for p in people]
    paths += sorted((root/'sources').glob('nobel-*.json'))
    result['metadata']['scope']='Five-person Western pilot only; earlier cohorts require protocol-aware adapters.'
    result['metadata']['source_sha256']={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in paths}
    return result


def export(result,directory):
    root=Path(directory);root.mkdir(parents=True,exist_ok=True)
    files={'graph.json':{'metadata':result['metadata'],'nodes':result['nodes'],'edges':result['edges']},
           'concepts.json':{'metadata':result['metadata'],'nodes':result['concepts']},'evidence.json':result['evidence'],'cases.json':result['cases'],'manifest.json':result['metadata']}
    for name,obj in files.items(): (root/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    with (root/'retrieval-documents.jsonl').open('w',encoding='utf-8') as f:
        for n in result['concepts']:
            document={'id':n['id'],'text':n['label']+'. Present in '+str(n['distinct_windows'])+' person-year windows across '+str(n['distinct_people'])+' people. '+canonical(n['descriptive_outcomes'])+'. Descriptive sample co-occurrence only.','metadata':{k:n[k] for k in ('kind','person_keys','case_keys','evidence_refs','status')},'training_eligible':False}
            f.write(canonical(document)+'\n')


def query(result,house=None,person=None,topic=None,minimum_people=1,limit=20):
    cases=result['cases'];universe={k for k,c in cases.items() if person is None or c['person_key']==person}
    categories=result['metadata']['categories']
    if topic is not None and topic not in categories: raise ValueError('Unknown outcome category')
    labels={(k,t):v['occurred'] for k,c in cases.items() for t,v in c['labels'].items()}
    rows=[]
    for n in result['concepts']:
        if n['distinct_people']<minimum_people: continue
        keys=set(n['house_case_keys'].get(str(house),[])) if house is not None else set(n['case_keys'])
        keys &= universe
        if not keys: continue
        counts=descriptive_stats(keys,universe,labels,[topic] if topic else categories)
        rows.append({'id':n['id'],'label':n['label'],'people':len({cases[k]['person_key'] for k in keys}),'windows':len(keys),'case_keys':sorted(keys),'descriptive_outcomes':counts,'evidence_refs':[i for i in n['evidence_refs'] if (result['evidence'][i].get('case_key') in keys or (result['evidence'][i]['kind']=='natal_placement' and result['evidence'][i]['person_key'] in {cases[k]['person_key'] for k in keys})) and (house is None or result['evidence'][i]['kind']!='sampled_contact' or result['evidence'][i]['natal_house']==house or house in result['evidence'][i]['transit_natal_houses'])],'cohort_people':n['distinct_people'],'status':'post_reveal_exploratory'})
    rows.sort(key=lambda r:(-r['people'],-r['windows'],r['id']))
    return rows[:limit]


def render_explorer(result,directory):
    """Create a self-contained local explorer; no private data are shipped in assets."""
    root=Path(directory)
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8-sig'))
    people=[{'key':p['person_key'],'name':p['name']} for p in read('birth-inputs.json')]
    with (root/'all-window-contacts.csv').open(encoding='utf-8-sig',newline='') as f: raw=list(csv.DictReader(f))
    points=sorted({r[k] for r in raw for k in ('transit_body','natal_body')})
    aspects=sorted({r['aspect'] for r in raw});person_index={p['key']:i for i,p in enumerate(people)}
    contacts=[[person_index[r['person_key']],int(r['window_id'][1:])-1,points.index(r['transit_body']),points.index(r['natal_body']),aspects.index(r['aspect']),int(r['natal_house']),sum(1<<(h-1) for h in ast.literal_eval(r['transit_natal_houses'])),int(r['samples']),float(r['minimum_sampled_orb'])] for r in raw]
    data={'collective':{'metadata':result['metadata'],'nodes':result['concepts']},'rows':read('results.json'),'windows':read('window-features.json'),'run':read('run.json'),'audits':read('calculation-audit.json'),'people':people,'points':points,'aspects':aspects,'contacts':contacts,'contact_columns':['person_index','window_index_zero_based','transit_point_index','natal_point_index','aspect_index','natal_house','transit_house_bitmask','monthly_samples','minimum_sampled_orb']}
    assets=Path(__file__).resolve().parents[1]/'web/collective'
    page=(assets/'explorer.html').read_text(encoding='utf-8')
    page=page.replace('__DATA__',canonical(data).replace('<','\\u003c')).replace('__STYLE__',(assets/'explorer.css').read_text(encoding='utf-8')).replace('__SCRIPT__',(assets/'explorer.js').read_text(encoding='utf-8')+'\n'+(assets/'collective-explorer.js').read_text(encoding='utf-8'))
    (root/'index.html').write_text(page,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('build','query'));parser.add_argument('--input',required=True);parser.add_argument('--output');parser.add_argument('--dashboard',action='store_true');parser.add_argument('--house',type=int,choices=range(1,13));parser.add_argument('--person');parser.add_argument('--topic');parser.add_argument('--minimum-people',type=int,default=1);parser.add_argument('--limit',type=int,default=20)
    args=parser.parse_args();result=build_from_directory(args.input)
    if args.command=='build':
        destination=Path(args.output) if args.output else Path(args.input)/'collective'
        if args.dashboard and destination.resolve()!=(Path(args.input)/'collective').resolve(): raise ValueError('Dashboard links require the default collective output folder')
        export(result,destination)
        if args.dashboard: render_explorer(result,args.input)
        print(canonical(result['metadata']))
    else: print(json.dumps(query(result,args.house,args.person,args.topic,args.minimum_people,args.limit),indent=2,ensure_ascii=False))


if __name__=='__main__': main()
