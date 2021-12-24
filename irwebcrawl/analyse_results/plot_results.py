import matplotlib.pyplot as plt
import numpy as np


def main():
    labels = ['Accuracy', 'F-measure', 'Precision', 'Recall']
    train_metrics = [0.932706, 0.925575, 0.982591, 0.874828]
    crawl_metrics = [0.856426, 0.832356, 0.799550, 0.867971]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x - width/2, train_metrics, width, label='Training dataset')
    ax.bar(x + width/2, crawl_metrics, width, label='Web crawl URLs')

    ax.set_ylabel('Metric values')
    ax.set_title('Model performance on different datasets')
    ax.set_xticks(x, labels)
    ax.legend()

    fig.tight_layout()

    plt.show()


if __name__ == '__main__':
    main()
