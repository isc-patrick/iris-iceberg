from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker
from irisiceberg.utils import get_alchemy_engine, Configuration, Base
import pandas as pd
import sys 

app = FastAPI()
templates = Jinja2Templates(directory="/Users/psulin/projects/irisiceberg/templates")

# Load configuration
sys.path.append("/Users/psulin/projects/irisiceberg/configs")
import testing_configs

config = getattr(testing_configs, 'iris_src_local_target')
config = Configuration(**config)
print(f"CONFIG - {config}")
engine = get_alchemy_engine(config)
Session = sessionmaker(bind=engine)

exclude_tables = []
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    tables = []
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        if table_name in Base.metadata.tables:
            if table_name not in exclude_tables:
                tables.append({
                    "name": table_name,
                    "columns": [column['name'] for column in inspector.get_columns(table_name)]
                })

    return templates.TemplateResponse("index.html", {"request": request, "tables": tables})

@app.get("/search/{table_name}")
async def search_table(table_name: str, q: str = Query(None), limit: int = Query(500, ge=1, le=1000)):
    if table_name not in Base.metadata.tables:
        return JSONResponse(content={"error": "Table not found"}, status_code=404)

    with Session() as session:
        if q:
            query = f"""
            SELECT TOP :limit * FROM {table_name}
            WHERE {' OR '.join([f"LOWER(CAST({col['name']} AS VARCHAR)) LIKE :search" for col in inspect(engine).get_columns(table_name)])}
            """
            result = session.execute(text(query), {"search": f"%{q.lower()}%", "limit": limit})
        else:
            query = f"""
            SELECT TOP :limit * FROM {table_name}
            """
            print(query)
            result = session.execute(text(query), {"limit": limit})
        
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print(len(df.index))
        
        # Convert Timestamp columns to strings
        for col in df.select_dtypes(include=['datetime64']).columns:
            df[col] = df[col].astype(str)
        df = df.fillna(value="")
        print(df.info())
        return JSONResponse(content=df.to_dict(orient="records"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
