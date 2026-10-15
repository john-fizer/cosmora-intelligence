from contextlib import closing
import tempfile, unittest
from pathlib import Path
from cosmora.cli import demo
from cosmora.db import connect
from cosmora.quality import GateError, check_claim_for_training

class QualityTests(unittest.TestCase):
    def test_fictional_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test.db'; result=demo(path)
            self.assertEqual(result['eligible_historical_claims'],[])
            self.assertEqual(len(result['blocked']),1)
    def test_doctrine_cannot_be_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test.db'; demo(path)
            with closing(connect(path)) as db, db:
                with self.assertRaisesRegex(GateError,'doctrine'):
                    check_claim_for_training(db,'demo-doctrine-claim')
    def test_unverified_real_claim_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test.db'; demo(path)
            with closing(connect(path)) as db, db:
                db.execute("UPDATE claims SET fictional=0 WHERE id='demo-event-claim'")
                with self.assertRaisesRegex(GateError,'independently verified'):
                    check_claim_for_training(db,'demo-event-claim')
if __name__=='__main__': unittest.main()
