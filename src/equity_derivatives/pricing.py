"""Black–Scholes, discretely monitored exotics, smile and delta hedging.

Prices assume risk-neutral GBM, European exercise, continuous rates; hedge P&L
assumes q=0 and no trading frictions unless specified. NOT executable quotes.
"""
from math import erf, exp, log, sqrt
import numpy as np

def normal_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))

def bs_price(spot, strike, maturity, rate, vol, option='call', dividend_yield=0.0):
    if min(spot,strike,maturity,vol) <= 0: raise ValueError('Positive spot, strike, maturity, vol required')
    if option not in ('call','put'): raise ValueError('option must be call or put')
    d1=(log(spot/strike)+(rate-dividend_yield+0.5*vol**2)*maturity)/(vol*sqrt(maturity))
    d2=d1-vol*sqrt(maturity)
    c=spot*exp(-dividend_yield*maturity)*normal_cdf(d1)-strike*exp(-rate*maturity)*normal_cdf(d2)
    return c if option=='call' else c-spot*exp(-dividend_yield*maturity)+strike*exp(-rate*maturity)

def bs_greeks(spot,strike,maturity,rate,vol,option='call',dividend_yield=0.0):
    if min(spot,strike,maturity,vol) <= 0: raise ValueError('Positive spot, strike, maturity, vol required')
    if option not in ('call','put'): raise ValueError('option must be call or put')
    d1=(log(spot/strike)+(rate-dividend_yield+0.5*vol**2)*maturity)/(vol*sqrt(maturity))
    d2=d1-vol*sqrt(maturity)
    pdf=exp(-0.5*d1*d1)/sqrt(2*np.pi)
    dfq=exp(-dividend_yield*maturity);dfr=exp(-rate*maturity)
    delta=dfq*normal_cdf(d1) if option=='call' else dfq*(normal_cdf(d1)-1)
    gamma=dfq*pdf/(spot*vol*sqrt(maturity))
    vega=spot*dfq*pdf*sqrt(maturity)
    theta_base=-(spot*dfq*pdf*vol)/(2*sqrt(maturity))
    if option=='call':
        theta=theta_base-rate*strike*dfr*normal_cdf(d2)+dividend_yield*spot*dfq*normal_cdf(d1)
    else:
        theta=theta_base+rate*strike*dfr*normal_cdf(-d2)-dividend_yield*spot*dfq*normal_cdf(-d1)
    return {'delta':delta,'gamma':gamma,'vega_per_1_vol':vega,'theta_per_year':theta}

def mc_paths(spot,maturity,rate,vol,steps=52,n_paths=10000,seed=11):
    if min(spot,maturity,vol)>0 and steps>=2 and n_paths>=2: pass
    else: raise ValueError('Invalid simulation inputs')
    rng=np.random.default_rng(seed)
    z=rng.standard_normal(((n_paths+1)//2,steps))
    z=np.concatenate((z,-z),axis=0)[:n_paths]
    dt=maturity/steps
    increments=(rate-0.5*vol**2)*dt + vol*sqrt(dt)*z
    return spot*np.column_stack((np.ones(n_paths),np.exp(np.cumsum(increments,axis=1))))

def mc_option(paths,strike,maturity,rate,product='asian',barrier=None):
    if paths.ndim!=2 or paths.shape[1]<3 or strike<=0 or maturity<=0: raise ValueError('Invalid paths')
    if product=='asian': reference=paths[:,1:].mean(axis=1)
    elif product in ('vanilla','up-and-out'): reference=paths[:,-1]
    else: raise ValueError('Unsupported product')
    payoff=np.maximum(reference-strike,0)
    if product=='up-and-out':
        if barrier is None or barrier<=0: raise ValueError('Barrier must be positive')
        payoff=payoff*(paths.max(axis=1)<barrier)
    values=payoff*exp(-rate*maturity)
    return float(values.mean()),float(values.std(ddof=1)/sqrt(len(values)))

def rr_butterfly(atm_iv,call_25d_iv,put_25d_iv):
    """Vol quoted in decimals; matching delta conventions are caller's responsibility."""
    if min(atm_iv,call_25d_iv,put_25d_iv)<=0: raise ValueError('IVs must be positive')
    return {'risk_reversal':call_25d_iv-put_25d_iv,'butterfly':0.5*(call_25d_iv+put_25d_iv)-atm_iv}

def hedge_short_call(path,strike,maturity,rate,vol,transaction_cost_bps=0.0):
    """Financed discrete short vanilla-call hedge; dividend yield 0, spreads approximated.

    Buys Δ shares against a short call, accrues cash at exp(r*dt).
    Returns hedged portfolio terminal P&L per option share.
    """
    if len(path)<3 or transaction_cost_bps<0: raise ValueError('Invalid hedge inputs')
    n=len(path)-1;dt=maturity/n
    delta=bs_greeks(path[0],strike,maturity,rate,vol)['delta']
    cash=bs_price(path[0],strike,maturity,rate,vol)-delta*path[0]
    cost=transaction_cost_bps/10000
    cash-=abs(delta)*path[0]*cost
    for i in range(1,n):
        cash*=exp(rate*dt)
        new_delta=bs_greeks(path[i],strike,maturity-i*dt,rate,vol)['delta']
        shares=new_delta-delta
        cash-=shares*path[i]+abs(shares)*path[i]*cost
        delta=new_delta
    cash*=exp(rate*dt)
    cash-=abs(delta)*path[-1]*cost  # liquidate shares at maturity
    payoff=max(path[-1]-strike,0)
    return float(cash+delta*path[-1]-payoff)
