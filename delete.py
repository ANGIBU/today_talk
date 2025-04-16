import os
import shutil
import winreg
import subprocess

def stop_docker_service():
    try:
        print("Stopping Docker service...")
        subprocess.run(["sc", "stop", "docker"], check=True)
        print("Docker service stopped.")
    except subprocess.CalledProcessError:
        print("Docker service not running or already stopped.")

def delete_docker_files():
    paths = [
        r"C:\Program Files\Docker",
        r"C:\ProgramData\Docker",
        r"C:\Users\Public\Desktop\Docker Desktop.lnk",
        os.path.expanduser(r"~\AppData\Roaming\Docker"),
        os.path.expanduser(r"~\AppData\Local\Docker"),
        os.path.expanduser(r"~\AppData\Local\Docker Desktop"),
        os.path.expanduser(r"~\AppData\Roaming\Docker Desktop"),
    ]

    for path in paths:
        if os.path.exists(path):
            print(f"Deleting {path}...")
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
            print(f"Deleted {path}.")
        else:
            print(f"Path {path} does not exist.")

def delete_docker_registry():
    docker_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop",
        r"SOFTWARE\Docker Inc.",
        r"SOFTWARE\Classes\DockerDesktop",
    ]

    for key in docker_keys:
        try:
            print(f"Deleting registry key: {key}")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteKey(reg_key, "")
            print(f"Deleted registry key: {key}")
        except FileNotFoundError:
            print(f"Registry key not found: {key}")
        except Exception as e:
            print(f"Error deleting registry key {key}: {e}")

def clean_environment_variables():
    try:
        print("Cleaning Docker-related PATH environment variables...")
        env_var = os.environ["PATH"]
        paths = env_var.split(";")
        docker_paths = [p for p in paths if "Docker" in p]

        if docker_paths:
            new_paths = [p for p in paths if "Docker" not in p]
            new_env_var = ";".join(new_paths)

            # Update PATH
            os.environ["PATH"] = new_env_var

            # Update the registry for PATH
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_env_var)

            print("Removed Docker-related PATH entries.")
        else:
            print("No Docker-related PATH entries found.")
    except Exception as e:
        print(f"Error cleaning environment variables: {e}")

def main():
    stop_docker_service()
    delete_docker_files()
    delete_docker_registry()
    clean_environment_variables()
    print("Docker has been successfully removed. Please restart your system to apply changes.")

if __name__ == "__main__":
    main()
