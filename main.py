from api import app

@app.get("/")
def root():
    return {"msg": "root"}