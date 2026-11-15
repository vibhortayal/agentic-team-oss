import json,glob,os,datetime as dt
T='<folder of the agent session transcripts>/'
# Sessions not listed in 'arm' count as B (the full team). Any later session in the same folder would be counted there too, so run this on the build-off's sessions only.
arm={'afe65e651ae983fc7':'A','a671e674f41dc1d04':'A','a2cdf78b64dcf8bd5':'C','a5fde19dc985479b9':'C','adc4412e7df34941c':'D','a2c13af6f79f297e9':'D','aaea7fba25b352f5b':'D'}
# $/M: input, output, cache read, cache write (write assumed 1.25x input; haiku read assumed 10% of input)
P={'fable':(8,40,.20,10),'opus':(4,20,.20,5),'sonnet':(2,10,.10,2.5),'haiku':(.10,.50,.01,.125)}
tot={}
for f in sorted(glob.glob(T+'a*.output')):
    aid=os.path.basename(f)[:-7]; a=arm.get(aid,'B')
    u={'in':0,'out':0,'cr':0,'cw':0}; ts=[]; model=None
    for line in open(f):
        try: d=json.loads(line)
        except: continue
        if d.get('timestamp'): ts.append(dt.datetime.fromisoformat(d['timestamp'].replace('Z','+00:00')))
        m=d.get('message') or {}
        if d.get('type')=='assistant' and isinstance(m,dict) and m.get('usage') and m.get('model','').startswith('claude'):
            model=m['model']; x=m['usage']
            u['in']+=x.get('input_tokens') or 0; u['out']+=x.get('output_tokens') or 0; u['cr']+=x.get('cache_read_input_tokens') or 0; u['cw']+=x.get('cache_creation_input_tokens') or 0
    active=sum(min((b-a_).total_seconds(),300) if (b-a_).total_seconds()<600 else 0 for a_,b in zip(ts,ts[1:]))
    fam=[k for k in P if k in (model or '')][0]; p=P[fam]
    cost=(u['in']*p[0]+u['out']*p[1]+u['cr']*p[2]+u['cw']*p[3])/1e6
    t=tot.setdefault(a,{'n':0,'in':0,'out':0,'cr':0,'cw':0,'sec':0,'cost':0,'models':{}})
    t['n']+=1; t['sec']+=active; t['cost']+=cost; t['models'][fam]=t['models'].get(fam,0)+1
    for k in u: t[k]+=u[k]
for a in sorted(tot):
    t=tot[a]; print(a, 'sessions',t['n'],t['models'],'| new in+cache-write %.2fM'%((t['in']+t['cw'])/1e6),'| out %dk'%(t['out']/1e3),'| cache-read %.1fM'%(t['cr']/1e6),'| active min %.0f'%(t['sec']/60),'| est $%.2f'%t['cost'])
