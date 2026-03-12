import subprocess
import time
import os
import signal

def run_test():
    print("Testing wifi_signal_generator.py...")
    # Start generator
    gen_proc = subprocess.Popen(
        ["python3", "/home/amith-biju/hack/wifi_signal_generator.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send "n" to generator (no jammer)
    gen_proc.stdin.write("n\n")
    gen_proc.stdin.flush()
    
    time.sleep(3) # Let it generate signals.txt
    
    print("Signals.txt produced:")
    if os.path.exists("signals.txt"):
        with open("signals.txt", "r") as f:
            print(f.read())
    else:
        print("ERROR: signals.txt not found!")

    # Start Visualizer in non-interactive terminal mode if possible
    # We will pass inputs 
    inputs = [
        "/home/amith-biju/hack/floor_map.png", # image path
        "", # ap1 x
        "", # ap1 y
        "", # ap2 x
        "", # ap2 y
        "", # ap3 x
        "", # ap3 y
        "", # jammer x
        ""  # jammer y
    ]
    
    # To run Matplotlib without a display we need a different backend
    os.environ['MPLBACKEND'] = 'Agg'
    
    print("Testing wifi_heatmap_live.py...")
    vis_proc = subprocess.Popen(
        ["python3", "/home/amith-biju/hack/wifi_heatmap_live.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    for val in inputs:
        vis_proc.stdin.write(val + "\n")
        vis_proc.stdin.flush()
        
    time.sleep(5) # Let it run
    
    # Terminate logic
    gen_proc.send_signal(signal.SIGINT)
    vis_proc.send_signal(signal.SIGINT)
    
    time.sleep(2)
    
    gen_stdout, gen_stderr = gen_proc.communicate()
    vis_stdout, vis_stderr = vis_proc.communicate()
    
    print("\n--- Generator Output ---")
    print(gen_stdout[-500:])
    print("\n--- Generator Error ---")
    print(gen_stderr)
    
    print("\n--- Visualizer Output ---")
    print(vis_stdout[-500:])
    print("\n--- Visualizer Error ---")
    print(vis_stderr)
    
    if "Error" in vis_stderr or "Traceback" in vis_stderr:
        print("TEST FAILED")
    else:
        print("TEST PASSED")

if __name__ == "__main__":
    run_test()
