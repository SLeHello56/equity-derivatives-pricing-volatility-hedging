from equity_derivatives.historical import fetch_fred
class FakeResponse:
    text='observation_date,SP500\n2026-01-01,6200.5\n2026-01-02,.\n'
    def raise_for_status(self):pass
def test_fred_equity(monkeypatch):
    monkeypatch.setattr('equity_derivatives.historical.requests.get',lambda *a,**kw:FakeResponse())
    frame=fetch_fred('SP500')
    assert len(frame)==1
    assert frame.value.iloc[0]==6200.5
