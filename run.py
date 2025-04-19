import os
import argparse
import uvicorn

def run_backend():
    """Run the backend API server."""
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

def run_frontend():
    """Run the Streamlit frontend."""
    os.system("streamlit run frontend/main.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DocuMind application")
    parser.add_argument(
        "--component",
        type=str,
        choices=["backend", "frontend", "all"],
        default="all",
        help="Component to run (backend, frontend, or all)"
    )
    
    args = parser.parse_args()
    
    if args.component == "backend":
        run_backend()
    elif args.component == "frontend":
        run_frontend()
    else:
        # Run both in separate processes
        import multiprocessing
        
        backend_process = multiprocessing.Process(target=run_backend)
        frontend_process = multiprocessing.Process(target=run_frontend)
        
        backend_process.start()
        frontend_process.start()
        
        backend_process.join()
        frontend_process.join()
