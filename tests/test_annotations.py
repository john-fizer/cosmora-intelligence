import unittest
from cosmora.annotations import validate_observation


class AnnotationReferenceTests(unittest.TestCase):
    def test_altered_agent_orb_is_rejected(self):
        contact={"transit_body":"SUN","natal_body":"MOON","aspect":"trine","minimum_sampled_orb":0.1,
                 "contact_samples":2,"total_samples":10,"natal_house":8,"transit_natal_houses":[4]}
        self.assertEqual(validate_observation(dict(contact),[contact]),contact)
        with self.assertRaises(ValueError):
            validate_observation(dict(contact,minimum_sampled_orb=0.2),[contact])




class InvalidObservationTests(unittest.TestCase):
    def test_nonfinite_agent_orb_is_rejected(self):
        contact={"transit_body":"SUN","natal_body":"MOON","aspect":"trine","minimum_sampled_orb":0.1,
                 "contact_samples":2,"total_samples":10,"natal_house":8,"transit_natal_houses":[4]}
        with self.assertRaises(ValueError):
            validate_observation(dict(contact,minimum_sampled_orb=float("nan")),[contact])



class TimingSensitivityTests(unittest.TestCase):
    def test_agent_cannot_reverse_timing_sensitivity(self):
        contact={"transit_body":"MOON","natal_body":"SUN","aspect":"square","minimum_sampled_orb":0.1,
                 "contact_samples":1,"total_samples":10,"natal_house":8,"transit_natal_houses":[4],
                 "timing_sensitive_in_samples":True}
        with self.assertRaises(ValueError):
            validate_observation(dict(contact,timing_sensitive_in_samples=False),[contact])

if __name__=="__main__":
    unittest.main()
