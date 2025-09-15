# Meteorite Landings Interactive Map 🌠

An interactive global map visualizing meteorite landing sites, built with Python. This project processes data from NASA and generates a feature-rich HTML map using Folium, combining data analytics with a beautiful, custom-styled interface.

It's a perfect example of how to blend creativity with intellect to turn raw data into an engaging story.

<img width="2559" height="1245" alt="image" src="https://github.com/user-attachments/assets/19b46dbf-9851-4bf9-a4a7-d7a4deb97bdb" />


---

## ✨ Features

- **Interactive Global Map**: Explore thousands of meteorite landings on a sleek, dark-themed map.
- **Dual View Modes**:
    - **Cluster View**: All meteorites are grouped into clusters for a clear overview and great performance. Zoom in to reveal individual glowing markers.
    - **Animated Heatmap**: Switch to a heatmap view with a time slider to visualize the intensity of meteorite falls and finds throughout history.
- **Live Statistics Panel**: A stylish dashboard in the corner displays key metrics: total count, total mass, the largest and oldest recorded meteorites, and a breakdown of "falls" vs. "finds".
- **Custom UI**: The map features custom-styled, animated UI elements for a polished and professional user experience, including a helpful hint to guide users.

---

## 🛠️ Tech Stack

- **Python**: For data processing and map generation.
- **Pandas**: For loading, cleaning, and manipulating the dataset.
- **Folium**: For creating the interactive Leaflet.js map.
- **Jinja2**: For templating custom HTML/CSS elements to inject into the map.

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/qoparu/meteor_landinds_map.git](https://github.com/qoparu/meteor_landinds_map.git)
    cd meteorite-map
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download the dataset:**
    Download the `meteorite-landings.csv` dataset from Kaggle (NASA) and place it in the same directory as the `create_map.py` script.

4.  **Run the script:**
    ```bash
    python create_map.py
    ```
    This will generate the `meteorite_map_final_with_stats.html` file. Open this file in your web browser to explore the map.

---

## 📊 Data Source

This project uses the Meteorite Landings dataset, maintained by The Meteoritical Society and provided by NASA.

-   **Source**: [NASA Open Data Portal](https://data.nasa.gov/Space-Science/Meteorite-Landings/gh4g-9sfh)
-   **Kaggle Mirror**: [Kaggle Dataset](https://www.kaggle.com/datasets/nasa/meteorite-landings)

---

<div align="center"> <h3>✨ Crafted with ❤️ by <a href="https://github.com/qoparu">Aru</a> ✨</h3> <img src="https://img.shields.io/badge/Java-Expert-important?logo=java" alt="Python Expert"> </div> 

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
