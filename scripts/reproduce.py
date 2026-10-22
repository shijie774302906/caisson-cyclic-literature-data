"""Recompute published metrics and refit all 30 whole-case LOO models.

Run from any directory: python scripts/reproduce.py
Only the generated/ directory is written. Archived release files are read-only.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear, minimize_scalar

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'generated'

def growth(n,a,ref):
    return np.expm1(a*np.log(np.asarray(n)))/np.expm1(a*np.log(ref))

def predict(c,n,p,model):
    if model=='Proposed model':
        return (p['c0']+p['c1']*c['X'])*growth(n,p['alpha'],c['N_ref'])
    return p['b']*(np.asarray(n)/c['N_ref'])**p['beta']

def refit(train,model):
    if model=='Proposed model':
        s=np.array([c['calibration_scale'] for c in train])
        x=np.array([c['X'] for c in train])
        y=np.array([c['r_ref'] for c in train])
        opt=lsq_linear(np.c_[np.ones(len(s)),x]*s[:,None],s*y,bounds=(0,np.inf),tol=1e-12)
        assert opt.success
        def loss(a):
            return np.mean([np.mean((c['y']/c['r_ref']-growth(c['n'],a,c['N_ref']))**2) for c in train])
        options={} if train[0]['dataset']=='Luo2020' else {'xatol':1e-9}
        fit=minimize_scalar(loss,bounds=(.01,2),method='bounded',options=options)
        _,alpha=min([(fit.fun,fit.x),(loss(.01),.01),(loss(2),2)])
        return dict(c0=float(opt.x[0]),c1=float(opt.x[1]),alpha=float(alpha))
    ns=[];ys=[];weights=[]
    for c in train:
        ns.extend(c['n']/c['N_ref']);ys.extend(c['y'])
        weights.extend(np.repeat(1/(len(train)*len(c['n'])*c['r_ref']**2),len(c['n'])))
    ns,ys,w=map(np.asarray,(ns,ys,weights))
    def profile(beta,details=False):
        v=ns**beta;b=max(0.,float(np.sum(w*v*ys)/np.sum(w*v*v)))
        loss=float(np.sum(w*(b*v-ys)**2))
        return (loss,b) if details else loss
    candidates=[(profile(.01),.01),(profile(2),2)]
    if train[0]['dataset']=='Luo2020':
        fit=minimize_scalar(profile,bounds=(.01,2),method='bounded')
        candidates.append((fit.fun,fit.x))
    else:
        grid=np.linspace(.01,2,161);losses=[profile(b) for b in grid]
        for j in range(1,len(grid)-1):
            if losses[j]<=losses[j-1] and losses[j]<=losses[j+1]:
                fit=minimize_scalar(profile,bounds=(grid[j-1],grid[j+1]),method='bounded',options={'xatol':1e-12})
                candidates.append((fit.fun,fit.x))
    _,beta=min(candidates)
    return dict(b=profile(beta,True)[1],beta=float(beta))

def evaluate(c,p,model):
    pred=predict(c,c['eval_n'],p,model)
    end=float(predict(c,c['N_end'],p,model))
    return dict(dataset=c['dataset'],case=c['case'],model=model,
        process_nrmse_pct=100*np.sqrt(np.mean((pred-c['eval_y'])**2))/abs(c['r_ref']),
        terminal_total_ratio_ape_pct=100*abs(end-c['r_end'])/(c['theta0_over_theta_s']+c['r_end']),
        r_end_predicted=end)

def main():
    OUT.mkdir(exist_ok=True)
    states=pd.read_csv(ROOT/'data/cases.csv')
    points=pd.read_csv(ROOT/'data/evaluation_points.csv')
    curves=pd.read_csv(ROOT/'data/cyclic_histories.csv')
    archived=pd.read_csv(ROOT/'results/case_metrics.csv')
    saved_points=pd.read_csv(ROOT/'results/predictions.csv')
    folds=json.loads((ROOT/'results/folds.json').read_text(encoding='utf-8'))
    assert states.groupby('dataset').size().to_dict()==dict(Li2021=7,Luo2020=5,Zhu2013=3)
    assert len(states[states.foundation=='HSC'])==3 and len(folds)==30
    cases={}
    for row in states.to_dict('records'):
        key=(row['dataset'],row['case'])
        g=points[(points.dataset==key[0])&(points['case']==key[1])].sort_values('N')
        raw=curves[(curves.dataset==key[0])&(curves['case']==key[1])].sort_values('N')
        assert np.isfinite(raw[['N','r_observed']]).all().all() and np.all(np.diff(raw.N)>0)
        assert np.isclose(row['r_ref'],np.interp(np.log(row['N_ref']),np.log(raw.N),raw.r_observed),rtol=0,atol=1e-10)
        interpolated=np.interp(np.log(g.N),np.log(raw.N),raw.r_observed)
        np.testing.assert_allclose(interpolated,g.r_observed,rtol=0,atol=1e-10)
        row['eval_n']=g.N.to_numpy();row['eval_y']=g.r_observed.to_numpy()
        mask=row['eval_n']<=row['N_ref']
        row['n']=row['eval_n'][mask];row['y']=row['eval_y'][mask]
        cases[key]=row
    saved=[];fresh=[];refitted_folds=[];point_diffs=[]
    for f in folds:
        ds=f['dataset'];target=f['held_out'];model=f['model'];c=cases[(ds,target)]
        assert target not in f['training']
        assert set(f['training'])=={key[1] for key in cases if key[0]==ds and key[1]!=target}
        saved.append(evaluate(c,f['parameters'],model))
        expected=saved_points[(saved_points.dataset==ds)&(saved_points['case']==target)&(saved_points.model==model)].sort_values('N')
        actual=predict(c,expected.N.to_numpy(),f['parameters'],model)
        point_diffs.append(float(np.max(abs(actual-expected.r_predicted.to_numpy()))))
        p=refit([cases[(ds,k)] for k in f['training']],model)
        fresh.append(evaluate(c,p,model))
        refitted_folds.append({**f,'parameters':p})
    saved=pd.DataFrame(saved);fresh=pd.DataFrame(fresh)
    cols=['process_nrmse_pct','terminal_total_ratio_ape_pct','r_end_predicted']
    expected=archived.rename(columns={'r_end_predicted':'r_end_predicted'}).set_index(['dataset','case','model'])
    diffs={}
    for name,table,tol in [('saved',saved,1e-7),('refit',fresh,5e-4)]:
        ordered=table.set_index(['dataset','case','model']).loc[expected.index]
        delta=abs(ordered[cols]-expected[cols])
        diffs[name]=delta.max().to_dict()
        assert delta.to_numpy().max()<tol,(name,diffs[name])
        table.to_csv(OUT/(name+'_case_metrics.csv'),index=False)
    assert max(point_diffs)<1e-8
    summaries=[]
    for (ds,model),g in saved.groupby(['dataset','model'],sort=False):
        for subset in (['all','without_CA1_scoring_only'] if ds=='Luo2020' else ['all']):
            h=g if subset=='all' else g[g['case']!='CA1']
            summaries.append(dict(dataset=ds,model=model,scoring_subset=subset,n_cases=len(h),
                process_nrmse_pct=h.process_nrmse_pct.mean(),terminal_total_ratio_mape_pct=h.terminal_total_ratio_ape_pct.mean()))
    summary=pd.DataFrame(summaries)
    original=pd.read_csv(ROOT/'results/summary_metrics.csv')
    key=['dataset','model','scoring_subset']
    np.testing.assert_allclose(summary.set_index(key).loc[original.set_index(key).index].select_dtypes('number'),original.set_index(key).select_dtypes('number'),rtol=0,atol=1e-7)
    summary.to_csv(OUT/'summary_metrics.csv',index=False)
    (OUT/'refitted_folds.json').write_text(json.dumps(refitted_folds,indent=2)+'\n',encoding='utf-8')
    checks=dict(cases=15,folds=30,observations_are_digitized_not_raw=True,
        all_folds_exclude_target=True,all_cases_retained=True,archived_point_max_difference=max(point_diffs),
        maximum_metric_differences=diffs,passed=True)
    (OUT/'verification.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    print(summary.to_string(index=False))
    print(json.dumps(checks,indent=2))

if __name__=='__main__':
    main()
