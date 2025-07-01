import matplotlib.pyplot as plt
import numpy as np

def show_black_plane():
    """Display an entirely black plane using matplotlib."""
    black = np.zeros((10, 10, 3))
    plt.imshow(black)
    plt.axis('off')
    plt.show()

