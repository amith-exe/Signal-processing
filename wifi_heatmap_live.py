#!/usr/bin/env python3
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class WiFiSimulator:
    def __init__(self, width, height, loss_factor=None):
        self.width = width
        self.height = height
        self.aps = []
        self.jammer = None
        self.loss_factor = loss_factor if loss_factor else 100.0 / min(width, height)

    def update_ap(self, name, x, y, power):
        """Add or update an Access Point with live signals."""
        for ap in self.aps:
            if ap['name'] == name:
                ap['power'] = power
                return
        self.aps.append({'name': name, 'x': x, 'y': y, 'power': power})
        
    def set_jammer(self, x, y, power):
        """Set a jammer that increases noise and reduces signal."""
        self.jammer = {'x': x, 'y': y, 'power': power}

    def calculate_coverage(self):
        """Calculate the signal coverage heatmap."""
        X, Y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        # Start heatmap initialized as zeroes
        heatmap = np.zeros((self.height, self.width))
        
        for ap in self.aps:
            dist = np.sqrt((X - ap['x'])**2 + (Y - ap['y'])**2)
            # signal cannot drop below 0
            signal = np.maximum(ap['power'] - (dist * self.loss_factor), 0)
            heatmap = np.maximum(heatmap, signal)
            
        if self.jammer:
            dist_jammer = np.sqrt((X - self.jammer['x'])**2 + (Y - self.jammer['y'])**2)
            jammer_effect = np.maximum(self.jammer['power'] - (dist_jammer * self.loss_factor), 0)
            heatmap = np.maximum(heatmap - jammer_effect, 0)
            
        return heatmap

def read_signals(filename="signals.txt"):
    """Reads the live signals from the GNU Radio script output."""
    signals = {}
    if not os.path.exists(filename):
        return signals
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 2:
                    signals[parts[0]] = float(parts[1])
    except Exception:
        pass
    return signals

def main():
    print("=" * 40)
    print(" Live WiFi Signal Coverage Heatmap")
    print("=" * 40)
    
    image_path = input("\nEnter the path to the building floor map image (PNG/JPG): ").strip()
    if not os.path.exists(image_path):
        print(f"Error: Could not find image at '{image_path}'")
        sys.exit(1)
        
    try:
        img = plt.imread(image_path)
        if len(img.shape) == 2:
            height, width = img.shape
        else:
            height, width = img.shape[:2]
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)
        
    print(f"Loaded image '{image_path}' ({width}x{height} pixels)")
    
    simulator = WiFiSimulator(width, height)
    
    # Prompt locations for the three APs
    print("\nDefine locations for AP1, AP2, AP3 (or press Enter for defaults):")
    ap_locations = {}
    for ap_name, default_ratio in zip(['AP1', 'AP2', 'AP3'], [(0.2, 0.2), (0.8, 0.2), (0.5, 0.8)]):
        x_in = input(f"{ap_name} X coordinate (0 to {width}): ").strip()
        y_in = input(f"{ap_name} Y coordinate (0 to {height}): ").strip()
        try:
            x, y = float(x_in), float(y_in)
            ap_locations[ap_name] = (x, y)
        except ValueError:
            print(f"Using default location for {ap_name}")
            ap_locations[ap_name] = (width * default_ratio[0], height * default_ratio[1])
            
    # Jammer location
    print("\nDefine location for Jammer (or press Enter for default):")
    jx_in = input("Jammer X coordinate: ").strip()
    jy_in = input("Jammer Y coordinate: ").strip()
    try:
        jammer_loc = (float(jx_in), float(jy_in))
    except ValueError:
        print("Using default location for Jammer")
        jammer_loc = (width / 2, height / 2)

    # Enable Matplotlib interactive mode
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ["#1a1a1a", "yellow", "red"]
    cmap = LinearSegmentedColormap.from_list("wifi_cmap", colors)
    
    print("\nStarting live heatmap plot. Reading from 'signals.txt'...")
    print("Make sure 'wifi_signal_generator.py' is running in another terminal!")
    print("Close the plot window or press Ctrl+C to exit.")
    
    im = None
    colorbar = None
    
    try:
        while plt.fignum_exists(fig.number):
            # 1. Read latest signals
            signals = read_signals("signals.txt")
            
            if not signals:
                plt.pause(1.0)
                continue
                
            # 2. Update simulator with live feed
            for ap_name, (x, y) in ap_locations.items():
                if ap_name in signals:
                    simulator.update_ap(ap_name, x, y, signals[ap_name])
                
            if 'JAMMER' in signals:
                simulator.set_jammer(jammer_loc[0], jammer_loc[1], signals['JAMMER'])
            else:
                simulator.jammer = None
                
            # 3. Calculate new Heatmap
            heatmap = simulator.calculate_coverage()
            
            # 4. Render
            ax.clear()
            
            # Matplotlib coordinates config 
            ax.set_xlim(0, width)
            ax.set_ylim(height, 0)
            
            ax.imshow(img, extent=[0, width, height, 0])
            
            # Use fixed limits vmin=0 and vmax=100 so the colors stay consistent
            im = ax.imshow(heatmap, cmap=cmap, alpha=0.6, extent=[0, width, height, 0], vmin=0, vmax=100)
            
            if colorbar is None:
                colorbar = fig.colorbar(im, ax=ax, label='Live Signal Strength')
            
            # Mark points
            for i, ap in enumerate(simulator.aps):
                ax.plot(ap['x'], ap['y'], marker='^', color='cyan', markersize=12, label='AP' if i == 0 else "")
                ax.text(ap['x'], ap['y'] - height*0.03, f"{ap['name']}: {ap['power']:.0f}dB", color='white', fontweight='bold', ha='center')
                
            if simulator.jammer:
                ax.plot(simulator.jammer['x'], simulator.jammer['y'], marker='X', color='lime', markersize=14, label='Jammer')
                
            # Add weak signal zone contours
            weak_threshold = 20.0
            min_sig, max_sig = np.min(heatmap), np.max(heatmap)
            if min_sig < weak_threshold and max_sig > min_sig:
                try:
                    cs = ax.contour(heatmap, levels=[weak_threshold], colors='white', alpha=0.7, linestyles='dashed', extent=[0, width, height, 0])
                    ax.clabel(cs, inline=True, fontsize=10, fmt='Weak Zone')
                except Exception:
                    pass
                    
            ax.set_title('Live WiFi Signal Coverage Heatmap')
            ax.legend(loc='upper right')
            
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(1.0) # wait 1 sec to match the GNU Radio refresh rate
            
    except KeyboardInterrupt:
        print("\nExiting live heatmap...")
        
if __name__ == "__main__":
    main()
