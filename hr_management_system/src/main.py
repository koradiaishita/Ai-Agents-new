import os
import sys
import logging
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

# Establish consistent logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Path resolution with runtime validation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "ui", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "ui", "templates")
ROOT_DIR = os.path.dirname(BASE_DIR)

# Ensure static asset directories exist
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "img"), exist_ok=True)

# Create minimal CSS file if it doesn't exist
css_file_path = os.path.join(STATIC_DIR, "css", "main.css")
if not os.path.exists(css_file_path):
    with open(css_file_path, "w") as f:
        f.write("""
:root {
    --primary-color: #4285F4;
    --primary-dark: #3367D6;
    --secondary-color: #34A853;
    --warning-color: #FBBC05;
    --error-color: #EA4335;
    --background-color: #F8F9FA;
    --card-color: #FFFFFF;
    --text-primary: #202124;
    --text-secondary: #5F6368;
    --border-color: #DADCE0;
    --sidebar-width: 250px;
    --header-height: 64px;
    --shadow-sm: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
    --shadow-md: 0 2px 6px 2px rgba(60, 64, 67, 0.15), 0 1px 2px 0 rgba(60, 64, 67, 0.3);
    --border-radius: 8px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.5;
}

/* Layout */
.app-container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: var(--sidebar-width);
    background-color: var(--card-color);
    box-shadow: var(--shadow-sm);
    padding: 20px 0;
    position: fixed;
    height: 100vh;
    z-index: 10;
}

.sidebar-header {
    padding: 0 20px 20px;
    border-bottom: 1px solid var(--border-color);
}

.sidebar-header h1 {
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--primary-color);
}

.sidebar-header p {
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.sidebar-nav {
    margin-top: 20px;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    color: var(--text-secondary);
    text-decoration: none;
    transition: background-color 0.2s;
}

.nav-item:hover {
    background-color: rgba(66, 133, 244, 0.08);
}

.nav-item.active {
    background-color: rgba(66, 133, 244, 0.12);
    color: var(--primary-color);
    font-weight: 500;
}

.nav-item span {
    margin-right: 12px;
}

.main-content {
    flex: 1;
    margin-left: var(--sidebar-width);
}

.main-header {
    height: var(--header-height);
    background-color: var(--card-color);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    position: sticky;
    top: 0;
    z-index: 5;
}

/* Basic responsive styles */
@media (max-width: 768px) {
    .sidebar {
        width: 60px;
    }
    .main-content {
        margin-left: 60px;
    }
    .sidebar-header h1, .sidebar-header p, .nav-item span:not(.material-icons) {
        display: none;
    }
}
        """)
    logger.info(f"Created minimal CSS file at {css_file_path}")

# Create minimal JavaScript file if it doesn't exist
js_file_path = os.path.join(STATIC_DIR, "js", "main.js")
if not os.path.exists(js_file_path):
    with open(js_file_path, "w") as f:
        f.write("""
// Core JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('HR Management System initialized');
});
        """)
    logger.info(f"Created minimal JavaScript file at {js_file_path}")

# Configure application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management with proper resource handling"""
    # Startup phase
    logger.info("Application starting up")
    try:
        # Load environment configuration
        env_path = os.path.join(ROOT_DIR, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment configuration from {env_path}")
        else:
            logger.warning(f"No .env file found at {env_path}")
            
        # Future integration point: Initialize AI services
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
    
    yield  # Application execution
    
    # Shutdown phase
    logger.info("Application shutting down")
    try:
        # Future integration point: Clean up resources
        pass
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

# Initialize FastAPI application with metadata
app = FastAPI(
    title="HR Management System",
    description="AI-powered human resources management system with Gemini integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Mount static assets with explicit directory
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals.update(url_for=lambda name, filename: f"/{name}/{filename}")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with structured response"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with logging"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    """Fallback error handler with graceful degradation"""
    logger.error(f"Internal server error: {str(exc)}")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Management System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            .error-container { max-width: 800px; margin: 40px auto; }
            h1 { color: #4285F4; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>HR Management System</h1>
            <p>The system encountered an error. Please try again in a moment.</p>
        </div>
    </body>
    </html>
    """, status_code=500)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """System health verification endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# UI routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render dashboard homepage"""
    try:
        return templates.TemplateResponse(
            "base.html", 
            {"request": request, "active_page": "dashboard", "page_title": "Dashboard"}
        )
    except Exception as e:
        logger.error(f"Template rendering error: {str(e)}")
        raise HTTPException(status_code=500, detail="Template rendering failed")

@app.get("/recruitment", response_class=HTMLResponse)
async def recruitment(request: Request):
    """Render recruitment management page"""
    try:
        return templates.TemplateResponse(
            "base.html", 
            {"request": request, "active_page": "recruitment", "page_title": "Recruitment"}
        )
    except Exception as e:
        logger.error(f"Template rendering error: {str(e)}")
        raise HTTPException(status_code=500, detail="Template rendering failed")

@app.get("/performance", response_class=HTMLResponse)
async def performance(request: Request):
    """Render performance tracking page"""
    try:
        return templates.TemplateResponse(
            "base.html", 
            {"request": request, "active_page": "performance", "page_title": "Performance"}
        )
    except Exception as e:
        logger.error(f"Template rendering error: {str(e)}")
        raise HTTPException(status_code=500, detail="Template rendering failed")

@app.get("/feedback", response_class=HTMLResponse)
async def feedback(request: Request):
    """Render feedback analysis page"""
    try:
        return templates.TemplateResponse(
            "base.html", 
            {"request": request, "active_page": "feedback", "page_title": "Feedback"}
        )
    except Exception as e:
        logger.error(f"Template rendering error: {str(e)}")
        raise HTTPException(status_code=500, detail="Template rendering failed")

# Application execution entry point
if __name__ == "__main__":
    logger.info("Initializing HR Management System")
    
    # Capture runtime configuration with fallback defaults
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    logger.info(f"Server configuration: host={host}, port={port}, debug={debug}")
    
    # Launch application server with hot reload for development workflows
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )