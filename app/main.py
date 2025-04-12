# aoo/
# ├── .env                    # Environment variables
# ├── .gitignore
# ├── pyproject.toml          # Modern Python project config
# ├── README.md
# ├── requirements/           # Split requirements (dev/prod)
# │   ├── base.txt
# │   ├── dev.txt
# │   └── prod.txt
# ├── src/
# │   └── app/
# │       ├── __init__.py
# │       ├── main.py         # App factory and entrypoint
# │       ├── core/           # Core configurations
# │       │   ├── config.py
# │       │   ├── logging.py
# │       │   └── security.py
# │       ├── api/            # Versioned API endpoints
# │       │   ├── __init__.py
# │       │   ├── v1/         # API version 1
# │       │   │   ├── __init__.py
# │       │   │   ├── endpoints/
# │       │   │   │   ├── __init__.py
# │       │   │   │   ├── health.py
# │       │   │   │   └── items.py
# │       │   │   └── routers.py
# │       │   └── v2/         # API version 2 (future)
# │       ├── models/         # Pydantic models
# │       │   ├── __init__.py
# │       │   ├── base.py
# │       │   └── schemas.py
# │       ├── services/       # Business logic
# │       └── utils/          # Utility functions
# ├── tests/                  # Test suite
# │   ├── __init__.py
# │   ├── conftest.py
# │   └── api/
# │       └── v1/
# │           ├── test_health.py
# │           └── test_items.py

def init():
    """
    Initialize the application by:
    1. Generating environment variables from configuration
    2. Loading the application configuration
    3. Setting up database control
    4. Managing database migrations
    
    Returns:
        dict: The loaded configuration from the YAML file
    """
    from services.storage.local import local_db_controller, DatabaseService, DatabaseCommand
    from services.env.obfuscator_service import env_obfuscator
    from controls.db_mng import db_mng_control
    from core.flow.config_loader import load_config
    # Define the path to the database configuration YAML file
    # This file contains database connection parameters and other settings
    config_file = "app/db.yml"
    
    # # Generate environment variables (.env file) from the configuration
    # # Arguments:
    # #   - "-c": Flag indicating a config file will follow
    # #   - config_file: Path to the configuration file
    # #   - "-e .env": Output environment file path
    # run_env_gen(["-c "] + [config_file] + ["-e dbstack/.env.gen"])
    
    # Load the configuration from the YAML file into a dictionary
    # This will be used throughout the application for various settings
    config = load_config(config_file=config_file)
    # Return the loaded configuration for use by other parts of the application

    # Examples of using the controller
    result1 = local_db_controller.initialize_stack("SecurePassword123")
    result2 = local_db_controller.start_service(DatabaseService.POSTGRES)
    result3 = local_db_controller.manage_service(DatabaseService.POSTGRES, DatabaseCommand.CONNECT)  # Connect to Postgres CLI
    # result4 = local_db_controller.backup_all_databases()
    
    print("Results:", result1, result2, result3)
    # Provision databases using the default config
    success = db_mng_control.provision_databases(config_file=config_file)
    print(f"Provision result: {success}")
   

def serve():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from dotenv import load_dotenv
    from rest.v1.routers import api_v1_router
    from core.config import settings  # Contains environment-specific settings

    load_dotenv("dbstack/.env")

    def create_application() -> FastAPI:
        application = FastAPI(
            title=settings.PROJECT_NAME,                # Project title from config
            description=settings.PROJECT_DESCRIPTION,   # Project description from config
            version=settings.VERSION,                   # Version number
            debug=settings.DEBUG,                       # Enable/disable debug mode
            docs_url="/docs" if settings.DOCS else None,     # Enable Swagger UI if docs are enabled
            redoc_url="/redoc" if settings.DOCS else None     # Enable ReDoc if docs are enabled
        )

        # Configure Cross-Origin Resource Sharing (CORS) if any origins are allowed
        if settings.BACKEND_CORS_ORIGINS:
            application.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],  # Allowed origins list
                allow_credentials=True,     # Allow sending cookies and credentials
                allow_methods=["*"],        # Allow all HTTP methods
                allow_headers=["*"],        # Allow all headers
            )
        application.include_router(api_v1_router, prefix=settings.API_V1_STR)
        return application

    app = create_application()

    import uvicorn
     # Add command line argument parsing for host/port configuration
    import argparse
    parser = argparse.ArgumentParser(description="Start the Database and Environment Management API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable hot reloading for development")
    
    args = parser.parse_args()
    
    uvicorn.run(
        app,  
        host=args.host,
        port=args.port,
        reload=args.reload
    )

# Entry point: run the `serve` function only if this file is executed directly (not imported)
if __name__ == '__main__':
    serve()



