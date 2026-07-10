import socket
import subprocess
import sys
import time
import requests


class ProcessManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None

    def start_backend(self):
        """Start FastAPI backend"""
        print("Starting FastAPI backend...")
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
            print(f" Backend failed to start: {e}")
            return False

    def start_frontend(self):
        """Start HTTP server for JavaScript frontend"""
        print("Starting JavaScript frontend...")
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", "8080",
                "--directory", "frontend"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except Exception as e:
            print(f" Frontend failed to start: {e}")
            return False

    def wait_for_backend(self, timeout=30):
        """Wait until backend is ready"""
        print("Waiting for backend to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = requests.get("http://localhost:8000/ping", timeout=2)
                if res.status_code == 200:
                    print(" Backend is ready!")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass

            # Check if backend process is still running
            if self.backend_process and self.backend_process.poll() is not None:
                print(" Backend process exited unexpectedly")
                stdout, stderr = self.backend_process.communicate()
                print(f"Backend stdout: {stdout}")
                print(f"Backend stderr: {stderr}")
                return False

            time.sleep(1)

        print(" Backend failed to start in time.")
        return False

    def wait_for_frontend(self, timeout=30):
        """Wait until frontend is ready"""
        print("Waiting for frontend to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = requests.get("http://localhost:8080", timeout=2)
                if res.status_code == 200:
                    print(" Frontend is ready!")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass

            # Check if frontend process is still running
            if self.frontend_process and self.frontend_process.poll() is not None:
                print(" Frontend process exited unexpectedly")
                stdout, stderr = self.frontend_process.communicate()
                print(f"Frontend stdout: {stdout}")
                print(f"Frontend stderr: {stderr}")
                return False

            time.sleep(1)

        print(" Frontend failed to start in time.")
        return False

    def cleanup(self):
        """Clean up processes"""
        print("\nCleaning up processes...")
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
        print(f"Warning: Ports {ports_in_use} are already in use!")
        print("   Stop other services using these ports, or update the ports in run.py and backend/main.py.")
        return False
    return True


def check_packages():
    """Check if all required packages are installed."""
    required_packages = [
        # Core
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests",
        # Data generation
        "faker",
        "pandas",
        "yaml",          # pyyaml
        "pyarrow",       # parquet support
        # DB seeding
        "sqlalchemy",
        "psycopg2",      # PostgreSQL
        "pymysql",       # MySQL
        # Format support
        "openpyxl",      # xlsx (optional but good to have)
    ]

    # Some packages are imported under a different name
    import_name_map = {
        "yaml"    : "yaml",
        "psycopg2": "psycopg2",
        "pymysql" : "pymysql",
        "pyarrow" : "pyarrow",
        "openpyxl": "openpyxl",
    }

    missing = []
    for package in required_packages:
        import_name = import_name_map.get(package, package)
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)

    return missing


def main():
    """Main runner"""
    print("Mock Data Generator v2.0")
    print("=" * 50)

    # Check packages
    missing_packages = check_packages()
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return

    print(" All packages found.")

    # Check ports
    if not check_ports():
        print("Cannot start — resolve port conflicts first.")
        return

    manager = ProcessManager()

    try:
        # Start backend
        if not manager.start_backend():
            return

        if not manager.wait_for_backend():
            manager.cleanup()
            return

        # Start frontend
        if not manager.start_frontend():
            manager.cleanup()
            return

        if not manager.wait_for_frontend():
            manager.cleanup()
            return

        print("\n" + "=" * 50)
        print("MOCK DATA GENERATOR v2.0 IS READY!")
        print("=" * 50)
        print("Frontend UI  : http://localhost:8080")
        print("Backend API  : http://localhost:8000")
        print("API Docs     : http://localhost:8000/docs")
        print("API Redoc    : http://localhost:8000/redoc")
        print("=" * 50)
        print("New in v2.0:")
        print("→ Relational data generation with FK integrity")
        print("→ Schema-driven generation (user-defined tables)")
        print("→ Domain-based generation (ecommerce, hr, healthcare...)")
        print("→ Direct database seeding (PostgreSQL, MySQL, SQLite)")
        print("=" * 50)
        print(" Press Ctrl+C to stop all services.")
        print("=" * 50)

        # Keep alive + health monitor
        while True:
            time.sleep(1)

            if manager.backend_process and manager.backend_process.poll() is not None:
                print(" Backend process stopped unexpectedly.")
                break

            if manager.frontend_process and manager.frontend_process.poll() is not None:
                print(" Frontend process stopped unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n Shutting down Mock Data Generator...")

    finally:
        manager.cleanup()
        print("All processes stopped. Goodbye!")


if __name__ == "__main__":
    main()