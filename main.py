from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import uvicorn
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Erro: index.html não encontrado</h1>"

@app.post("/processar-planilha")
async def processar_planilha(file: UploadFile = File(...), consumo_padrao: float = Form(...)):
    try:
        content = await file.read()
        # Suporta Excel (.xlsx) e CSV
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # Padroniza nomes das colunas
        df.columns = [c.lower().strip() for c in df.columns]
        
        if 'origem' not in df.columns or 'destino' not in df.columns:
            raise HTTPException(status_code=400, detail="Planilha sem colunas 'Origem' e 'Destino'.")

        total_viagens = len(df)
        gargalos = []
        
        # Simulação de Inteligência BI (Analisa as linhas e calcula desperdício fictício baseado no KM)
        # Em um cenário real, você usaria colunas de KM e Consumo Real da planilha
        for i, row in df.head(10).iterrows():
            perda = round(50 + (i * 12.5), 2)
            gargalos.append({
                "rota": f"{row['origem']} -> {row['destino']}",
                "status": "Inércia Crítica" if perda > 100 else "Fluxo Regular",
                "perda_estimada": f"R$ {perda}"
            })

        return {
            "resumo": {
                "total_viagens": total_viagens,
                "viagens_analisadas": len(gargalos),
                "prejuizo_total_frota": f"R$ {sum([float(g['perda_estimada'].replace('R$ ','')) for g in gargalos]):.2f}"
            },
            "gargalos_identificados": gargalos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
