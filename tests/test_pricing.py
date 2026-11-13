from math import exp
import numpy as np
import pytest
from equity_derivatives.pricing import bs_price,bs_greeks,mc_paths,mc_option,rr_butterfly,hedge_short_call

def test_parity():
    c=bs_price(101,100,.75,.025,.23)
    p=bs_price(101,100,.75,.025,.23,'put')
    assert c-p==pytest.approx(101-100*exp(-.025*.75))
def test_delta_greeks():
    g=bs_greeks(100,100,1,.03,.2)
    h=1e-3
    fd=(bs_price(100+h,100,1,.03,.2)-bs_price(100-h,100,1,.03,.2))/(2*h)
    assert g['delta']==pytest.approx(fd,abs=1e-7)
def test_mc_vanilla_is_close():
    paths=mc_paths(100,1,.03,.2,n_paths=40000)
    mean,se=mc_option(paths,100,1,.03,'vanilla')
    assert abs(mean-bs_price(100,100,1,.03,.2))<4*se
def test_knockout_below_vanilla():
    paths=mc_paths(100,1,.03,.2)
    assert mc_option(paths,100,1,.03,'up-and-out',125)[0]<=mc_option(paths,100,1,.03,'vanilla')[0]
def test_hedge_cost_reduces_pnl():
    path=mc_paths(100,1,.03,.2,n_paths=50)[3]
    assert hedge_short_call(path,100,1,.03,.2,10)<=hedge_short_call(path,100,1,.03,.2,0)
def test_rr():
    assert rr_butterfly(.25,.23,.28)['risk_reversal']==pytest.approx(-.05)
