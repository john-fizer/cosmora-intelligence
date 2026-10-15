from contextlib import closing
from .db import connect

class GateError(ValueError):
    pass

def check_claim_for_training(db, claim_id):
    claim = db.execute('SELECT * FROM claims WHERE id=?', (claim_id,)).fetchone()
    if claim is None: raise GateError('claim not found')
    if claim['graph'] != 'historical': raise GateError('doctrine is not outcome evidence')
    if claim['fictional']: raise GateError('fictional example excluded')
    if claim['status'] != 'verified' or not claim['reviewer']:
        raise GateError('claim not independently verified')
    source = db.execute('SELECT * FROM sources WHERE id=?',(claim['source_id'],)).fetchone()
    if not source or not source['content_sha256'] or not claim['evidence_quote']:
        raise GateError('missing evidence provenance')
    return True

def audit(path):
    with closing(connect(path)) as db, db:
        counts = {r['graph']: r['n'] for r in db.execute('SELECT graph,COUNT(*) n FROM claims GROUP BY graph')}
        eligible=[]; blocked=[]
        for row in db.execute('SELECT id FROM claims WHERE graph="historical"'):
            try: check_claim_for_training(db,row['id']); eligible.append(row['id'])
            except GateError as exc: blocked.append({'claim_id':row['id'],'reason':str(exc)})
        return {'claims':counts,'eligible_historical_claims':eligible,'blocked':blocked,
                'hypotheses':db.execute('SELECT COUNT(*) FROM hypotheses').fetchone()[0]}
