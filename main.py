from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def raiz():
    return {"Saludo": "Hola profe como estas?"}