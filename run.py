import subprocess
import sys
import time
import requests
import socket

class ProcessManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
    
    def start_backend(self):
        """Start FastAPI backend"""
        print("🚀 Starting FastAPI backend...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "backend.main:app",
                "--host", "127.0.0.1",
                "--port", "8000",
                "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except Exception as e:
            print(f"❌ Backend failed to start: {e}")
            return False
    
    def start_frontend(self):
        """Start HTTP server for JavaScript frontend"""
        print("🎨 Starting JavaScript frontend...")
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", "8080",
                "--directory", "frontend"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except Exception as e:
            print(f"❌ Frontend failed to start: {e}")
            return False
    
    def wait_for_backend(self, timeout=30):
        """Wait until backend is ready"""
        print("⏳ Waiting for backend to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = requests.get("http://localhost:8000/ping", timeout=2)
                if res.status_code == 200:
                    print("✅ Backend is ready!")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            
            # Check if backend process is still running
            if self.backend_process and self.backend_process.poll() is not None:
                print("❌ Backend process exited unexpectedly")
                stdout, stderr = self.backend_process.communicate()
                print(f"Backend stdout: {stdout}")
                print(f"Backend stderr: {stderr}")
                return False
            
            time.sleep(1)
        
        print("❌ Backend failed to start in time.")
        return False
    
    def wait_for_frontend(self, timeout=30):
        """Wait until frontend is ready"""
        print("⏳ Waiting for frontend to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = requests.get("http://localhost:8080", timeout=2)
                if res.status_code == 200:
                    print("✅ Frontend is ready!")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            
            # Check if frontend process is still running
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("❌ Frontend process exited unexpectedly")
                stdout, stderr = self.frontend_process.communicate()
                print(f"Frontend stdout: {stdout}")
                print(f"Frontend stderr: {stderr}")
                return False
            
            time.sleep(1)
        
        print("❌ Frontend failed to start in time.")
        return False
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up processes...")
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()

def check_ports():
    """Check if ports are already in use"""
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    ports_in_use = []
    if is_port_in_use(8000):
        ports_in_use.append(8000)
    if is_port_in_use(8080):
        ports_in_use.append(8080)
    
    if ports_in_use:
        print(f"⚠️ Warning: Ports {ports_in_use} are already in use!")
        print("You may need to stop other services or change ports.")
        return False
    return True

def main():
    """Main runner"""
    print("🎲 Mock Data Generator")
    print("=" * 50)
    
    # Check if required packages are installed
    required_packages = [
        "fastapi", "uvicorn", "faker", "pandas", "pydantic", "requests"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return
    
    # Check if ports are available
    if not check_ports():
        print("🛑 Cannot start services due to port conflicts.")
        return
    
    manager = ProcessManager()
    
    try:
        # Start backend
        if not manager.start_backend():
            return
        
        # Wait for backend to be ready
        if not manager.wait_for_backend():
            manager.cleanup()
            return
        
        # Start frontend
        if not manager.start_frontend():
            manager.cleanup()
            return
        
        # Wait for frontend to be ready
        if not manager.wait_for_frontend():
            manager.cleanup()
            return
        
        print("\n" + "=" * 50)
        print("🎉 BOTH SERVICES ARE READY!")
        print("📍 Backend API: http://localhost:8000")
        print("🌐 Frontend UI: http://localhost:8080")
        print("📚 API Docs: http://localhost:8000/docs")
        print("=" * 50)
        print("💡 Open http://localhost:8080 in your browser")
        print("🛑 Press Ctrl+C to stop all services")
        print("=" * 50)
        
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if manager.backend_process and manager.backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if manager.frontend_process and manager.frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
    
    except KeyboardInterrupt:
        print("\n👋 Shutting down Mock Data Generator...")
    
    finally:
        manager.cleanup()
        print("Thank you for using Mock Data Generator!")

if __name__ == "__main__":
    main()
# ```

# ### Key Changes
# 1. **Frontend Startup (`start_frontend`)**:
#    - Changed from starting Streamlit (`streamlit run`) to starting a Python HTTP server (`python -m http.server 8080 --directory frontend`).
#    - The `--directory frontend` flag ensures the server serves files from the `frontend` directory, where `index.html` (from the previous response) should be located.
#    - The frontend now runs on port 8080 instead of 8501.

# 2. **Frontend Wait Logic (`wait_for_frontend`)**:
#    - Updated to check `http://localhost:8080` instead of `http://localhost:8501` to verify the frontend is ready.

# 3. **Port Checking (`check_ports`)**:
#    - Modified to check port 8080 (for the HTTP server) instead of 8501 (Streamlit's default port).

# 4. **Required Packages**:
#    - Removed `streamlit` from the `required_packages` list since the frontend is now HTML/CSS/JavaScript-based.

# 5. **Output Messages**:
#    - Updated the success message to reflect the new frontend URL (`http://localhost:8080`).

# ### Assumptions
# - The `index.html` file (from the previous response) is located in a `frontend` directory relative to `main.py`.
# - The FastAPI backend is structured as `backend.main:app` (as per the original script).
# - The backend still uses port 8000 and has a `/ping` endpoint for health checks.

# ### Setup Instructions
# 1. **Directory Structure**:
#    Ensure your project directory is structured as follows:
#    ```
#    project_root/
#    ├── backend/
#    │   └── main.py  # FastAPI backend
#    ├── frontend/
#    │   └── index.html  # HTML/CSS/JS frontend from previous response
#    ├── main.py  # This script
#    └── requirements.txt
#    ```

# 2. **Install Dependencies**:
#    Ensure the required packages are installed:
#    ```bash
#    pip install fastapi uvicorn faker pandas pydantic requests
#    ```

# 3. **Run the Application**:
#    Run the updated `main.py`:
#    ```bash
#    python main.py
#    ```

# 4. **Access the Application**:
#    - Backend API: `http://localhost:8000`
#    - Frontend UI: `http://localhost:8080`
#    - API Docs: `http://localhost:8000/docs`

# 5. **Verify**:
#    - The script will start the FastAPI backend and the Python HTTP server.
#    - It will wait for both services to be ready and print confirmation messages.
#    - Open `http://localhost:8080` in your browser to access the JavaScript-based frontend.
#    - Use `Ctrl+C` to stop both services cleanly.

# ### Notes
# - The Python HTTP server (`http.server`) is a simple development server. For production, consider using a more robust server like Nginx or serving the frontend via a CDN.
# - Ensure the `index.html` file from the previous response (with the updated Plotly.js CDN link to version 2.35.2) is in the `frontend` directory.
# - If your backend's `main.py` or directory structure differs, adjust the `subprocess.Popen` command in `start_backend` accordingly (e.g., change `"backend.main:app"` to the correct module path).
# - If you need a different port for the frontend, update the port number in `start_frontend` and `check_ports` to match.

# If you encounter any issues or need further modifications (e.g., different directory structure, additional error handling, or a specific production server), let me know!