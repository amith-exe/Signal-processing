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
        for ap in self.aps:
            if ap['name'] == name:
                ap['power'] = power
                return
        self.aps.append({'name': name, 'x': x, 'y': y, 'power': power})
        
    def set_jammer(self, x, y, power):
        self.jammer = {'x': x, 'y': y, 'power': power}

    def calculate_coverage(self):
        X, Y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        heatmap = np.zeros((self.height, self.width))
        
        for ap in self.aps:
            dist = np.sqrt((X - ap['x'])**2 + (Y - ap['y'])**2)
            signal = np.maximum(ap['power'] - (dist * self.loss_factor), 0)
            heatmap = np.maximum(heatmap, signal)
            
        if self.jammer:
            dist_jammer = np.sqrt((X - self.jammer['x'])**2 + (Y - self.jammer['y'])**2)
            jammer_effect = np.maximum(self.jammer['power'] - (dist_jammer * self.loss_factor), 0)
            heatmap = np.maximum(heatmap - jammer_effect, 0)
            
        return heatmap

def main():
    image_path = "/home/amith-biju/hack/tes.jpeg"
    if not os.path.exists(image_path):
        print("Image not found!")
        return
        
    img = plt.imread(image_path)
    if len(img.shape) == 2:
        height, width = img.shape
    else:
        height, width = img.shape[:2]
        
    simulator = WiFiSimulator(width, height)
    
    # We will simulate the signals with a Jammer present
    signals = {"AP1": 100, "AP2": 76, "AP3": 58, "JAMMER": 100}

    ap_locations = {
        'AP1': (width * 0.2, height * 0.2),
        'AP2': (width * 0.8, height * 0.2),
        'AP3': (width * 0.5, height * 0.8)
    }
    
    # Jammer location in the middle
    jammer_loc = (width * 0.5, height * 0.5)

    for ap_name, (x, y) in ap_locations.items():
        if ap_name in signals:
            simulator.update_ap(ap_name, x, y, signals[ap_name])
            
    if 'JAMMER' in signals:
        simulator.set_jammer(jammer_loc[0], jammer_loc[1], signals['JAMMER'])

    heatmap = simulator.calculate_coverage()

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#1a1a1a", "yellow", "red"]
    cmap = LinearSegmentedColormap.from_list("wifi_cmap", colors)

    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.imshow(img, extent=[0, width, height, 0])
    
    im = ax.imshow(heatmap, cmap=cmap, alpha=0.6, extent=[0, width, height, 0], vmin=0, vmax=100)
    fig.colorbar(im, ax=ax, label='Signal Strength')

    for i, ap in enumerate(simulator.aps):
        ax.plot(ap['x'], ap['y'], marker='^', color='cyan', markersize=12)
        ax.text(ap['x'], ap['y'] - height*0.03, f"{ap['name']}: {ap['power']:.0f}dB", color='white', fontweight='bold', ha='center')

    if simulator.jammer:
        ax.plot(simulator.jammer['x'], simulator.jammer['y'], marker='X', color='lime', markersize=14)
        ax.text(simulator.jammer['x'], simulator.jammer['y'] - height*0.03, f"JAMMER", color='lime', fontweight='bold', ha='center')

    weak_threshold = 20.0
    min_sig, max_sig = np.min(heatmap), np.max(heatmap)
    if min_sig < weak_threshold and max_sig > min_sig:
        try:
            cs = ax.contour(heatmap, levels=[weak_threshold], colors='white', alpha=0.7, linestyles='dashed', extent=[0, width, height, 0])
            ax.clabel(cs, inline=True, fontsize=10, fmt='Weak Zone')
        except Exception:
            pass

    ax.set_title('WiFi Signal Coverage + Jammer Snapshot')
    output_path = "/home/amith-biju/hack/heatmap_jammer_output.png"
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    print(f"Saved snapshot to {output_path}")

if __name__ == "__main__":
    main()
