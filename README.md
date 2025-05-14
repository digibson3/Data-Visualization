
# Data-Visualization
# Boulder Dog Trails – Interactive Visualization App

Flask application built to visualize and explore hiking trails in Boulder, Colorado, based on dog accessibility. Using real trail data from Boulder’s open data portal, the app lets users interact with maps and charts to quickly find which trails allow dogs off-leash, which require leashes, and which prohibit dogs altogether.

We built this to combine data cleaning, visualization, and web deployment into one interactive tool that’s actually useful for locals and visitors with pets.

## Features

- **Interactive Map**  
  Mapbox visualization of trailheads, color-coded by dog policy. Use a dropdown to toggle between off-leash, leash-required, and no-dog trails.

- **Pie Chart Summary**  
  Quickly see what percentage of Boulder’s trails fall under each dog access category.

- **Mileage Distribution**  
  A line chart showing how trail lengths are distributed—most are surprisingly short.


## Tools Used

- **Python (Flask)** – handles routing and data processing  
- **Pandas** – for data cleanup and transformations  
- **Plotly** – used for both the map and interactive charts  
- **HTML/CSS** – simple static front-end rendered with Flask templates  


## File Structure

```
📦 boulder-dog-trails/
├── app.py                  # Main Flask application
├── templates/
│   └── index.html          # Front-end layout with injected charts
├── data/
│   ├── Trails.csv          # Original trails dataset
│   └── merged_trails.csv   # Cleaned dataset with GPS coordinates
```


## How to Run It Locally

1. Clone this repo and install the dependencies:
   ```bash
   pip install flask pandas plotly
   ```

2. Create a folder named `data/` and drop in:
   - `Trails.csv`
   - `merged_trails.csv`

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser and go to:  
   `http://localhost:5000`

---

## Data Prep

The app reads in two datasets:
- One for trail descriptions and dog regulations  
- One merged version that includes GPS coordinates for mapping  

We added a simple categorization function to group trails into:  
- `off_leash`  
- `leash_required`  
- `no_dogs`  

These categories are then used to build visual layers and charts.

---