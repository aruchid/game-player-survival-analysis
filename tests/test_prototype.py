import sys,unittest
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import prototype as p
class PrototypeTests(unittest.TestCase):
 def test_reference_recovery(self):
  _,_,metrics=p.demo()
  self.assertTrue(metrics)
 def test_invalid_data(self):
  with self.assertRaises(ValueError):p.finite([float('nan')])
  with self.assertRaises(ValueError):p.finite([])
 def test_reject_invalid_process_input(self):
  with self.assertRaises(ValueError):p.process([1],[-1])

 def test_ties_zero_time_and_censored_only(self):
  x,y=p.process([0,0,2,2,5],[1,0,1,0,0])
  np.testing.assert_array_equal(x,[0,0,2])
  np.testing.assert_allclose(y,[1,4/5,(4/5)*(2/3)])
  x,y=p.process([0,1,2],[0,0,0])
  np.testing.assert_array_equal(x,[0])
  np.testing.assert_array_equal(y,[1])

 def test_grouped_risk_sets_match_direct_counts(self):
  rng=np.random.default_rng(42)
  for n in (1,10,100,1000):
   durations=rng.integers(0,40,n)
   events=rng.integers(0,2,n)
   times=np.unique(durations[events==1])
   expected=[1.]
   for time in times:
    risk=np.count_nonzero(durations>=time)
    deaths=np.count_nonzero((durations==time)&(events==1))
    expected.append(expected[-1]*(1-deaths/risk))
   x,y=p.process(durations,events)
   np.testing.assert_array_equal(x,np.concatenate(([0],times)))
   np.testing.assert_allclose(y,expected)
