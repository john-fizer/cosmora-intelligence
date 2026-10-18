"""Versioned technique arithmetic and source-attributed doctrine registry.

These helpers operate on supplied positions. They do not validate birth evidence,
calculate a sidereal ephemeris, or establish interpretive/predictive validity.
"""
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from fractions import Fraction
import json
import math
from pathlib import Path
from .charts import SIGNS

ROOT=Path(__file__).resolve().parents[1]
TRADITIONAL=('MARS','VENUS','MERCURY','MOON','SUN','MERCURY','VENUS','MARS','JUPITER','SATURN','SATURN','JUPITER')
MODERN=('MARS','VENUS','MERCURY','MOON','SUN','MERCURY','VENUS','PLUTO','JUPITER','SATURN','URANUS','NEPTUNE')
ZR_YEARS=(15,8,20,25,19,20,8,15,12,27,30,12)
DASHA_LORDS=('KETU','VENUS','SUN','MOON','MARS','RAHU','JUPITER','SATURN','MERCURY')
DASHA_YEARS=(7,20,6,10,7,18,16,19,17)


def number(value):
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError('A finite numeric value is required')
    return value


def _lower_float(value):
    # Preserve half-open boundaries when rational arithmetic rounds upward.
    result=float(value)
    return math.nextafter(result,-math.inf) if Fraction(result)>value else result


def longitude(value):
    return _lower_float(Fraction(number(value))%360)


def sign_index(value):
    if type(value) is not int or not 0<=value<12:
        raise ValueError('Sign index must be an integer Aries=0 through Pisces=11')
    return value


def rulers(profile):
    if profile not in ('traditional','modern'):
        raise ValueError('Choose traditional or modern domicile rulers')
    return TRADITIONAL if profile=='traditional' else MODERN


def position(value):
    value=longitude(value)
    index=int(value//30)
    return {'longitude':value,'sign':SIGNS[index],'sign_index':index,'degree_in_sign':value%30}


def lots(ascendant,sun,moon,sect):
    a,s,m=map(longitude,(ascendant,sun,moon))
    if sect not in ('day','night'):
        raise ValueError('Sect must be independently determined as day or night')
    f,p=(a+m-s)%360,(a+s-m)%360
    if sect=='night': f,p=p,f
    return {'fortune':f,'spirit':p,'sect':sect,'formula_profile':'sect-reversed-hermetic-v1'}


def profection(asc_sign_index,completed_age):
    asc=sign_index(asc_sign_index)
    if type(completed_age) is not int or completed_age<0:
        raise ValueError('Supply nonnegative completed calendar age, not elapsed days/365.25')
    index=(asc+completed_age)%12
    return {'completed_age':completed_age,'house':completed_age%12+1,
            'sign':SIGNS[index],'sign_index':index,'lord':TRADITIONAL[index]}


def dispositors(longitudes,rulership='traditional'):
    table=rulers(rulership)
    if not longitudes: raise ValueError('At least one position is required')
    edges={body:table[int(longitude(value)//30)] for body,value in longitudes.items()}
    missing=set(edges.values())-set(edges)
    if missing: raise ValueError('Missing ruler positions: '+','.join(sorted(missing)))
    chains={}
    for body in edges:
        seen=[];current=body
        while current not in seen:
            seen.append(current);current=edges[current]
        cycle=seen[seen.index(current):]
        chains[body]={'path':seen+[current],'cycle':cycle,'terminal':current if len(cycle)==1 else None}
    terminals={row['terminal'] for row in chains.values()}
    sole=next(iter(terminals)) if len(terminals)==1 and None not in terminals else None
    return {'rulership':rulership,'edges':edges,'chains':chains,'sole_final_dispositor':sole}


def decans(value,system,rulership='traditional'):
    p=position(value);d=int(p['degree_in_sign']//10)
    if system=='chaldean': ruler=('MARS','SUN','VENUS','MERCURY','MOON','SATURN','JUPITER')[(3*p['sign_index']+d)%7]
    elif system=='triplicity': ruler=rulers(rulership)[(p['sign_index']+4*d)%12]
    else: raise ValueError('Choose chaldean or triplicity decans')
    return dict(p,decan=d+1,system=system,ruler=ruler,rulership='traditional' if system=='chaldean' else rulership)


def twelfth_parts(value):
    p=position(value)
    return dict(position(30*p['sign_index']+12*p['degree_in_sign']),
                method='own-sign-expanded-twelfth-parts',source_longitude=p['longitude'])


def nakshatra(value):
    exact=Fraction(number(value))%360
    scaled=exact*3/40
    index=int(scaled)
    return {'index':index+1,'pada':int(exact*3//10)%4+1,
            'fraction_elapsed':_lower_float(scaled-index),'lord':DASHA_LORDS[index%9],
            'longitude':_lower_float(exact),'scheme':'27-nakshatras-sidereal-input'}


def navamsa(value):
    exact=Fraction(number(value))%360
    return dict(position(_lower_float((9*exact)%360)),source_longitude=_lower_float(exact),
                kind='derived_divisional_position',division=9)


def chara_karakas(longitudes,scheme='seven'):
    if scheme not in ('seven','eight'): raise ValueError('Select seven or eight karakas')
    seven=('SUN','MOON','MARS','MERCURY','JUPITER','VENUS','SATURN')
    if set(longitudes)-set(seven)-{'RAHU','KETU'}:
        raise ValueError('Outer planets/Chiron are not eligible classical karakas; supply a separate overlay')
    eligible=seven+(('RAHU',) if scheme=='eight' else ())
    if not set(eligible)<=set(longitudes): raise ValueError('Missing eligible graha longitude')
    ranked=[]
    for body in eligible:
        degree=longitude(longitudes[body])%30
        ranked.append((30-degree if body=='RAHU' else degree,body))
    ranked.sort(reverse=True)
    if any(abs(a[0]-b[0])<=1e-9 for a,b in zip(ranked,ranked[1:])):
        raise ValueError('Unresolved degree tie: this conservative profile stops; choose a separately sourced tie procedure')
    names=('AK','AmK','BK','MK','PK','GK','DK') if scheme=='seven' else ('AK','AmK','BK','MK','PiK','PK','GK','DK')
    return {'scheme':scheme,'roles':dict(zip(names,[body for _,body in ranked])),
            'ranking':[{'body':body,'advancement_degrees':value} for value,body in ranked],
            'tie_policy':'halt_within_1e-9_degree','excluded_bodies':sorted(set(longitudes)-set(eligible))}


def rasi_drishti(reference_sign_index):
    ref=sign_index(reference_sign_index)
    group=ref%3
    if group==0: return [s for s in range(12) if s%3==1 and s!=(ref+1)%12]
    if group==1: return [s for s in range(12) if s%3==0 and s!=(ref-1)%12]
    return [s for s in range(12) if s%3==2 and s!=ref]


def arudha(source_sign_index,lord_sign_index):
    source,lord=sign_index(source_sign_index),sign_index(lord_sign_index)
    raw=(lord+(lord-source)%12)%12
    exception=(raw-source)%12 in (0,6)
    final=(raw+9)%12 if exception else raw
    return {'source_sign_index':source,'lord_sign_index':lord,'raw_sign_index':raw,
            'exception_triggered':exception,'final_sign_index':final,'final_sign':SIGNS[final],
            'profile':'pvr-textbook-9.2-tenth-from-raw','lord_resolution':'caller_supplied_no_automatic_colord'}


def vimshottari_balance(moon_longitude):
    nak=nakshatra(moon_longitude);idx=(nak['index']-1)%9
    years=DASHA_YEARS[idx];elapsed=nak['fraction_elapsed']*years
    sub=[];cursor=0.0
    for i in range(9):
        j=(idx+i)%9;duration=years*DASHA_YEARS[j]/120
        sub.append({'lord':DASHA_LORDS[j],'duration_years':duration,
                    'start_years_from_birth':cursor-elapsed,'end_years_from_birth':cursor+duration-elapsed,
                    'ends_before_birth':cursor+duration<=elapsed})
        cursor+=duration
    return {'lord':DASHA_LORDS[idx],'elapsed_years':elapsed,'balance_years':years-elapsed,
            'full_major_years':years,'antardashas':sub,'nakshatra':nak,
            'year_model':'abstract_dasha_years_no_calendar_dates','dates_generated':False}


def zodiacal_releasing(start_utc,days,fortune_longitude,spirit_longitude,release_lot,levels=2,max_periods=10000):
    start=datetime.fromisoformat(start_utc.replace('Z','+00:00'))
    if start.tzinfo is None or start.utcoffset()!=timedelta(0): raise ValueError('Explicit UTC start is required')
    days=number(days)
    if not 0<days<=365250: raise ValueError('Requested days must be positive and at most365250')
    if type(levels) is not int or not 1<=levels<=4: raise ValueError('Levels must be1 through4')
    if type(max_periods) is not int or not 1<=max_periods<=100000: raise ValueError('Invalid period count limit')
    if release_lot not in ('fortune','spirit'): raise ValueError('Release from fortune or spirit')
    fortune,spirit=longitude(fortune_longitude),longitude(spirit_longitude)
    fs,ss=int(fortune//30),int(spirit//30)
    adjusted=release_lot=='spirit' and fs==ss
    seed=fs if release_lot=='fortune' else (ss+int(adjusted))%12
    requested_end=start+timedelta(days=days)
    periods=[];units=(31104000,2592000,216000,18000)
    def sequence(level,parent_id,seed_sign,begin,parent_end):
        cursor=begin;sign=seed_sign;index=0;lob_done=False
        while cursor<min(parent_end,requested_end):
            lob=False
            if level>1 and index==12 and not lob_done:
                sign=(seed_sign+6)%12;lob=True;lob_done=True
            nominal_seconds=ZR_YEARS[sign]*units[level-1]
            nominal_end=cursor+timedelta(seconds=nominal_seconds)
            end=min(nominal_end,parent_end,requested_end)
            identifier=(parent_id+'/' if parent_id else '')+f'L{level}:{index}'
            if len(periods)>=max_periods: raise ValueError('Period limit reached; reduce horizon or levels; no partial result returned')
            row={'id':identifier,'parent_id':parent_id,'level':level,'sign':SIGNS[sign],
                 'sign_index':sign,'ruler':TRADITIONAL[sign],'start':cursor.isoformat(),'end':end.isoformat(),
                 'start_day':(cursor-start).total_seconds()/86400,'end_day':(end-start).total_seconds()/86400,
                 'duration_days':(end-cursor).total_seconds()/86400,'nominal_duration_days':nominal_seconds/86400,
                 'truncated_by_parent':parent_end<nominal_end,'truncated_by_request':requested_end<min(nominal_end,parent_end),
                 'is_lob':lob,'fortune_relative_house':1+(sign-fs)%12,'fortune_angular':(sign-fs)%12 in (0,3,6,9)}
            periods.append(row)
            if level<levels: sequence(level+1,identifier,sign,cursor,min(nominal_end,parent_end))
            cursor=end;sign=(sign+1)%12;index+=1
    sequence(1,None,seed,start,datetime.max.replace(tzinfo=timezone.utc))
    return {'profile':'brennan-schaim-360day-reconstruction-v1','release_lot':release_lot,
            'natal_fortune_longitude':fortune,'natal_spirit_longitude':spirit,
            'effective_start_sign':SIGNS[seed],'same_sign_adjustment':adjusted,'year_days':360,
            'interval_policy':'half-open','periods':periods}


def catalog():
    return json.loads((ROOT/'methods/catalog.json').read_text(encoding='utf-8'))


def execute(method_id,inputs,profile_id):
    data=catalog();methods={m['id']:m for m in data['methods']}
    if method_id not in methods or profile_id not in data['profiles']: raise ValueError('Unknown method or profile')
    method=methods[method_id];profile=data['profiles'][profile_id]
    if method['status']!='implemented_arithmetic': raise ValueError('Method is not executable: '+method['status'])
    if profile_id not in method['profiles']: raise ValueError('Method and tradition profile are incompatible')
    args=dict(inputs)
    if profile['zodiac']=='sidereal':
        provenance=[args.pop('ayanamsha_id',None),args.pop('longitude_source',None)]
        if not all(isinstance(value,str) and value.strip() for value in provenance):
            raise ValueError('Precomputed sidereal inputs require named ayanamsha and longitude provenance')
    if method['backend']=='chara_karakas' and args.get('scheme','seven')=='eight':
        if args.pop('node_mode',None) not in ('mean','true'):
            raise ValueError('Eight-karaka execution requires mean or true node_mode')
    for key,value in method.get('fixed_parameters',{}).items():
        if key in args and args[key]!=value: raise ValueError('Input conflicts with the versioned method parameters')
        args[key]=value
    if method['backend'] in ('dispositors','decans'):
        if 'rulership' in args and args['rulership']!=profile['rulership']: raise ValueError('Ruler table conflicts with profile')
        args['rulership']=profile['rulership']
    backends={f.__name__:f for f in (lots,profection,dispositors,decans,twelfth_parts,nakshatra,navamsa,chara_karakas,rasi_drishti,arudha,vimshottari_balance,zodiacal_releasing)}
    if method['backend'] in ('decans','twelfth_parts','nakshatra','navamsa') and 'longitude' in args:
        if 'value' in args: raise ValueError('Supply longitude once')
        args['value']=args.pop('longitude')
    result=backends[method['backend']](**args)
    implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest()
    raw=json.dumps({'method_definition':method,'profile_definition':profile,'inputs':inputs,'implementation_sha256':implementation_sha256},sort_keys=True,allow_nan=False,separators=(',',':'))
    return {'kind':'technique_calculation','method_id':method_id,'method_version':method['version'],
            'profile_id':profile_id,'profile':profile,'inputs':inputs,'input_sha256':sha256(raw.encode()).hexdigest(),
            'source_ids':method['source_ids'],'result':result,'implementation_sha256':implementation_sha256,'source_review_status':'pending',
            'calculation_validation':'synthetic_reference_cases_only','empirical_validation':False,'training_eligible':False}


def registry_graph():
    data=catalog();nodes=[];edges=[]
    for sid,source in data['sources'].items(): nodes.append({'id':'method-source:'+sid,'kind':'doctrine_source_reference','properties':source})
    for pid,profile in data['profiles'].items(): nodes.append({'id':'method-profile:'+pid,'kind':'tradition_profile','properties':profile})
    for method in data['methods']:
        mid='method:'+method['id']
        nodes.append({'id':mid,'kind':'doctrine_method_definition','status':'pending_source_review','properties':method})
        for sid in method['source_ids']: edges.append({'source':mid,'relation':'ATTRIBUTED_TO','target':'method-source:'+sid})
        for pid in method['profiles']: edges.append({'source':mid,'relation':'USES_PROFILE','target':'method-profile:'+pid})
    return {'nodes':nodes,'edges':edges,'graph_role':'pending_doctrine_methods','empirical_validation':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['list','show','calculate','graph'])
    parser.add_argument('--method');parser.add_argument('--profile');parser.add_argument('--input');parser.add_argument('--output')
    args=parser.parse_args()
    if args.command=='list': result=catalog()
    elif args.command=='graph': result=registry_graph()
    elif args.command=='show':
        matches=[m for m in catalog()['methods'] if m['id']==args.method]
        if not matches: parser.error('Choose a known --method')
        result=matches[0]
    else:
        if not all((args.method,args.profile,args.input)): parser.error('calculate requires --method, --profile and --input JSON file')
        result=execute(args.method,json.loads(Path(args.input).read_text(encoding='utf-8')),args.profile)
    raw=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if args.output: Path(args.output).write_text(raw,encoding='utf-8')
    else: print(raw)


if __name__=='__main__': main()