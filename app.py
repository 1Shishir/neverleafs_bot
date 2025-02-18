from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from modules.qa import router as qa_router
from modules.products import router as products_router
from modules.find_plant import router as find_plant_router
from modules.maintenance import router as maintenance_router
from modules.cart import router as cart_router  # Import Cart router
from fastapi.staticfiles import StaticFiles
from modules.orderstatus import router as orderstatus_router

app = FastAPI()

origins = [
    "https://chatbottest-production.up.railway.app",  # VERY IMPORTANT
]


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the index.html file on the root URL
@app.get("/")
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))

# Mount the static directory to serve images, CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(orderstatus_router)
app.include_router(qa_router)
app.include_router(products_router)
app.include_router(find_plant_router)
app.include_router(maintenance_router)
app.include_router(cart_router)  # Include cart API

@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join("static", "images"))

