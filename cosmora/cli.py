from contextlib import closing
import argparse, hashlib, json
from datetime import datetime, timezone
from .db import initialize, connect
from .quality import audit

def demo(path):
    initialize(path)
    now=datetime.now(timezone.utc).isoformat()
    with closing(connect(path)) as db, db:
        db.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?,?,?,?)',
                   ('demo-source','demo://fictional','Fictional demonstration',now,hashlib.sha256(b'fictional').hexdigest(),'not a real source',None))
        db.execute('INSERT OR IGNORE INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                   ('demo-event-claim','historical','fictional-person','experienced','fictional award','demo-source','Invented for a software test','pending',None,now,None,1))
        db.execute('INSERT OR IGNORE INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                   ('demo-doctrine-claim','doctrine','10th house','traditional_association','career','demo-source','Invented example of a doctrine statement','pending',None,now,None,1))
        db.execute('INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?,?)',
                   ('demo-event','fictional-person','award_received','2020-01-01',None,'day','demo-event-claim',1))
        db.execute('INSERT OR IGNORE INTO hypotheses VALUES (?,?,?,?,?,?)',
                   ('demo-hypothesis','demo-doctrine-claim','demo-event','demo-agent','proposed','Fictional; untested; not a discovery'))
    return audit(path)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['init','demo','audit'])
    p.add_argument('--db',default='cosmora.db')
    a=p.parse_args()
    if a.command=='init': initialize(a.db); print('Database initialized:',a.db)
    elif a.command=='demo': print(json.dumps(demo(a.db),indent=2))
    else: initialize(a.db); print(json.dumps(audit(a.db),indent=2))
if __name__=='__main__': main()
