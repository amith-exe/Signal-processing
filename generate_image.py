import numpy as np
import matplotlib.pyplot as plt

def create_dummy():
    # create a simple map image 
    img = np.ones((600, 800, 3), dtype=np.float32) * 0.9  # Light gray background
    
    # Draw some walls (dark gray)
    img[100:110, 100:700] = 0.2
    img[100:500, 100:110] = 0.2
    img[490:500, 100:700] = 0.2
    img[100:500, 690:700] = 0.2
    
    # Internal walls
    img[100:300, 400:410] = 0.2
    img[400:500, 300:310] = 0.2
    
    # Save as PNG
    plt.imsave("/home/amith-biju/hack/floor_map.png", img)
    print("Dummy floor map created at /home/amith-biju/hack/floor_map.png")

if __name__ == "__main__":
    create_dummy()
