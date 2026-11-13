from equity_derivatives.pricing import bs_price,bs_greeks,mc_paths,mc_option,hedge_short_call
p=mc_paths(100,1,.03,.25,n_paths=6000)
print('Black–Scholes call',round(bs_price(100,100,1,.03,.25),4))
print('Greeks',bs_greeks(100,100,1,.03,.25))
print('Asian call',mc_option(p,100,1,.03))
print('Discrete short-call hedge P&L',round(hedge_short_call(p[0],100,1,.03,.25,1),4))
