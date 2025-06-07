import subprocess
import time
import os

def find_pid(process_name):
    """Find the PID of the process by name."""
    try:
        output = subprocess.check_output(['pgrep', '-f', process_name])
        pids = output.decode().strip().split('\n')
        return [int(pid) for pid in pids]
    except subprocess.CalledProcessError:
        return []

def kill_processes(pids):
    """Kill the given PIDs."""
    for pid in pids:
        try:
            print(f"Killing PID: {pid}")
            os.kill(pid, 9)
        except ProcessLookupError:
            print(f"Process {pid} already exited.")

def switch_console(vt):
    """Switch to the given virtual terminal."""
    subprocess.run(['sudo', 'chvt', str(vt)])

if __name__ == "__main__":
    print("Looking for main_ui.py process...")
    pids = find_pid("main_ui.py")

    if pids:
        kill_processes(pids)
    else:
        print("No main_ui.py process found.")

    print("Waiting briefly...")
    time.sleep(1)

    print("Switching to tty7...")
    switch_console(7)