import matplotlib.pyplot as plt


def draw_plot(data, label, image_path):
    assert label.lower() in ["retransmission", "latency", "jitter"], "Please choose label from [retransmission, latency, jitter]"
    
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(data)+1), data, marker="o")
    plt.ylabel(label.capitalize())
    plt.xlabel("Stream Number")
    plt.title(f"{label.capitalize()} vs Stream number")
    
    plt.savefig(image_path, dpi=150, bbox_inches="tight")
    plt.show()
    