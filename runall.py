import subprocess
import sys
import webbrowser
import time
import os
import signal
import requests
from pathlib import Path

# Configuration
FLASK_URL = "http://127.0.0.1:5000"
STREAMLIT_URL = "http://localhost:8501"
FLASK_PORT = 5000
STREAMLIT_PORT = 8501

class ProcessManager:
    def __init__(self):
        self.flask_process = None
        self.streamlit_process = None
        self.processes = []
    
    def check_port_available(self, port):
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except socket.error:
                return False
    
    def kill_process_on_port(self, port):
        """Kill any process running on specified port"""
        try:
            if sys.platform == "win32":
                # Windows
                os.system(f"netstat -ano | findstr :{port}")
                os.system(f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port}\') do taskkill /f /pid %a')
            else:
                # Unix/Linux/Mac
                os.system(f"lsof -ti:{port} | xargs kill -9")
            time.sleep(2)
        except Exception as e:
            print(f"Warning: Could not kill process on port {port}: {e}")
    
    def wait_for_server(self, url, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url + "/health" if "5000" in url else url)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def start_flask_backend(self):
        """Start Flask backend server"""
        print("🚀 Starting Flask backend...")
        
        # Check if port is available
        if not self.check_port_available(FLASK_PORT):
            print(f"⚠️  Port {FLASK_PORT} is busy. Attempting to free it...")
            self.kill_process_on_port(FLASK_PORT)
        
        # Find the correct path for app.py
        backend_paths = [
            "app.py",
            "backend/app.py", 
            os.path.join(os.getcwd(), "app.py")
        ]
        
        app_path = None
        for path in backend_paths:
            if os.path.exists(path):
                app_path = path
                break
        
        if not app_path:
            print("❌ Could not find Flask app.py file")
            return False
        
        try:
            self.flask_process = subprocess.Popen(
                [sys.executable, app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(self.flask_process)
            
            # Wait for Flask to start
            if self.wait_for_server(FLASK_URL):
                print(f"✅ Backend running at {FLASK_URL}")
                return True
            else:
                print("❌ Backend failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Flask backend: {e}")
            return False
    
    def start_streamlit_frontend(self):
        """Start Streamlit frontend"""
        print("🎨 Starting Streamlit frontend...")
        
        # Check if port is available
        if not self.check_port_available(STREAMLIT_PORT):
            print(f"⚠️  Port {STREAMLIT_PORT} is busy. Attempting to free it...")
            self.kill_process_on_port(STREAMLIT_PORT)
        
        # Find the correct path for frontend app.py
        frontend_paths = [
            "frontend/app.py",
            "streamlit_app.py",
            "app_frontend.py"
        ]
        
        # Check if there are multiple app.py files
        current_dir = os.getcwd()
        app_files = list(Path(current_dir).glob("**/app.py"))
        
        # Use the frontend app.py (usually the larger one for Streamlit)
        app_path = None
        if len(app_files) > 1:
            # Find the larger file (Streamlit app is usually larger)
            largest_file = max(app_files, key=lambda f: f.stat().st_size)
            app_path = str(largest_file)
        elif len(app_files) == 1:
            app_path = str(app_files[0])
        
        # Fallback to predefined paths
        if not app_path:
            for path in frontend_paths:
                if os.path.exists(path):
                    app_path = path
                    break
        
        if not app_path:
            print("❌ Could not find Streamlit app.py file")
            return False
        
        try:
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", app_path,
                "--server.port", str(STREAMLIT_PORT),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ])
            self.processes.append(self.streamlit_process)
            
            # Wait a bit for Streamlit to start
            time.sleep(5)
            
            print(f"✅ Frontend running at {STREAMLIT_URL}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting Streamlit frontend: {e}")
            return False
    
    def open_browser(self):
        """Open the application in default browser"""
        try:
            print(f"🌐 Opening browser at {STREAMLIT_URL}")
            webbrowser.open(STREAMLIT_URL)
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"Please open {STREAMLIT_URL} manually in your browser")
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🛑 Shutting down servers...")
        
        for process in self.processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"Warning: Error terminating process: {e}")
        
        # Force kill on ports if needed
        self.kill_process_on_port(FLASK_PORT)
        self.kill_process_on_port(STREAMLIT_PORT)
        
        print("✅ Cleanup completed")

def main():
    """Main function to run the application"""
    manager = ProcessManager()
    
    try:
        # Setup signal handlers for clean shutdown
        def signal_handler(signum, frame):
            manager.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("🎯 Resume Relevance Check - Application Launcher")
        print("=" * 50)
        
        # Start Flask backend
        if not manager.start_flask_backend():
            print("❌ Failed to start backend. Exiting...")
            return
        
        # Start Streamlit frontend
        if not manager.start_streamlit_frontend():
            print("❌ Failed to start frontend. Exiting...")
            manager.cleanup()
            return
        
        # Open browser
        manager.open_browser()
        
        print("\n" + "=" * 50)
        print("🎉 Application started successfully!")
        print(f"🔗 Frontend: {STREAMLIT_URL}")
        print(f"🔗 Backend API: {FLASK_URL}")
        print("Press Ctrl+C to stop the application")
        print("=" * 50)
        
        # Keep the script running
        try:
            while True:
                # Check if processes are still running
                if manager.flask_process and manager.flask_process.poll() is not None:
                    print("⚠️  Backend process stopped unexpectedly")
                    break
                
                if manager.streamlit_process and manager.streamlit_process.poll() is not None:
                    print("⚠️  Frontend process stopped unexpectedly")
                    break
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n📱 Received interrupt signal")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()