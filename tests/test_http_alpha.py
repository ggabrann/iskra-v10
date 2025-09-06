from interface.http_alpha import app
def test_health():
    c = app.test_client()
    rv = c.get("/health"); assert rv.status_code==200 and rv.get_json().get("ok")
def test_invoke_require_text():
    c = app.test_client()
    rv = c.post("/invoke", json={"who":"iskra_core"}); assert rv.status_code==400
def test_invoke_ok():
    c = app.test_client()
    rv = c.post("/invoke", json={"who":"iskra_core","text":"Привет"}); 
    assert rv.status_code==200 and "slo" in rv.get_json()
