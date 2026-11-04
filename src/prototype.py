"""游戏用户 Kaplan–Meier 生存分析 — deterministic numerical prototype."""
import argparse,json
from pathlib import Path
import numpy as np

def finite(a,ndim=None):
 a=np.asarray(a,dtype=float)
 if not np.isfinite(a).all() or not a.size or (ndim is not None and a.ndim!=ndim): raise ValueError('Invalid shape, empty or nonfinite input')
 return a
def process(durations, events):
 durations = finite(durations, 1)
 events = np.asarray(events)
 if events.shape != durations.shape or np.any(durations < 0) or not np.isin(events, [0, 1]).all():
  raise ValueError('Invalid duration/event inputs')

 # Group all observations by time so a tied censor still contributes to the
 # risk set for an event at that time. Only emit points at event times.
 times, groups, counts = np.unique(durations, return_inverse=True, return_counts=True)
 deaths = np.bincount(groups[events == 1], minlength=times.size)
 at_risk = np.cumsum(counts[::-1])[::-1]
 event_times = deaths > 0
 survival = np.cumprod(1 - deaths[event_times] / at_risk[event_times])
 return np.concatenate(([0.], times[event_times])), np.concatenate(([1.], survival))

def demo():
 tx,sy=process([1,2,3,4],[1,1,0,1]);assert np.allclose(sy,[1,.75,.5,0])
 rng=np.random.default_rng(42);actual=rng.exponential(25,500);censor=rng.uniform(10,50,500);durations=np.minimum(actual,censor);events=(actual<=censor).astype(int);x,y=process(durations,events)
 assert np.all(np.diff(y)<=0) and np.all((y>=0)&(y<=1))
 return x,{'Kaplan-Meier survival':y,'Generating survival (synthetic)':np.exp(-x/25)},{'players':500,'observed_events':int(events.sum()),'censored':int((1-events).sum())}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('artifacts'));args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 x,series,metrics=demo()
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 if x is None:
  fig,axes=plt.subplots(1,len(series),figsize=(14,4),layout='constrained');axes=np.atleast_1d(axes)
  for ax,(label,values) in zip(axes,series.items()):ax.imshow(values,cmap='viridis');ax.set_title(label);ax.set_axis_off()
 else:
  fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
  for label,values in series.items():ax.plot(x,values,label=label)
  ax.legend();ax.grid(alpha=.2)
 fig.suptitle('Synthetic prototype validation — not field measurements')
 fig.savefig(args.output/'result.png',dpi=140);plt.close(fig)
 np.savez_compressed(args.output/'results.npz',**{str(i):v for i,v in enumerate(series.values())})
 (args.output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
