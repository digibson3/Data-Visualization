from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import circlify
import matplotlib.cm as cm
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    # --- Load trail and amenities data ---
    merged_df = pd.read_csv("data/merged_trails_2.csv")
    dog_parks_df = pd.read_csv("data/dog_parks.csv")
    dog_places_df = pd.read_csv("data/dog_friendly_places.csv")
    vets_df = pd.read_csv("data/veterinarians.csv")

    merged_df.columns = merged_df.columns.str.strip()
    dog_parks_df.columns = dog_parks_df.columns.str.strip()
    dog_places_df.columns = dog_places_df.columns.str.strip()
    vets_df.columns = vets_df.columns.str.strip()

    # --- Main Boulder Trails Map (with Dropdowns) ---
    dog_accesses = sorted(merged_df["dog_access"].dropna().unique())
    difficulties = sorted(merged_df["difficulty"].dropna().unique())

    traces = []
    trace_map = {}

    for da in dog_accesses:
        for diff in difficulties:
            subset = merged_df[(merged_df["dog_access"] == da) & (merged_df["difficulty"] == diff)]
            trace = go.Scattermapbox(
    lat=subset["latitude"],
    lon=subset["longitude"],
    mode='markers',
    marker=dict(
        size=12,
        color='#1a4040',
        opacity=0.8,
        symbol='circle'  # default
    ),  
                name=f"{da}_{diff}",
                text=subset["trail_name_y"],
                visible=(da == dog_accesses[0] and diff == difficulties[0])  # First one visible
            )
            trace_map[(da, diff)] = len(traces)
            traces.append(trace)

    dog_access_buttons = [
        dict(
            label=da.replace('_', ' ').title(),
            method="update",
            args=[
                {"visible": [i == trace_map[(da, difficulties[0])] for i in range(len(traces))]},
                
            ]
        )
        for da in dog_accesses
    ]

    difficulty_buttons = [
        dict(
            label=diff,
            method="update",
            args=[
                {"visible": [i == trace_map[(dog_accesses[0], diff)] for i in range(len(traces))]},
                
            ]
        )
        for diff in difficulties
    ]

    fig_map = go.Figure(data=traces)

    fig_map.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=merged_df['latitude'].mean(), lon=merged_df['longitude'].mean()),
            zoom=12
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        updatemenus=[
            dict(
                buttons=dog_access_buttons,
                direction="down",
                showactive=True,
                x=0.1,
                y=1.3,
                xanchor="right",
                yanchor="top"
            ),
            dict(
                buttons=difficulty_buttons,
                direction="down",
                showactive=True,
                x=0.25,
                y=1.3,
                xanchor="right",
                yanchor="top"
            )
        ]
    )

    map_plot = plot(fig_map, output_type='div', include_plotlyjs=False)



    # --- Dog Amenities Map ---
    fig_amenities = go.Figure()

    # Dog Parks
    fig_amenities.add_trace(go.Scattermapbox(
        lat=dog_parks_df['latitude'],
        lon=dog_parks_df['longitude'],
        mode='markers',
        marker=dict(size=18, color='#1a4040', symbol='circle'),
        name='Dog Parks',
        text=dog_parks_df['name']
    ))

    # Dog-Friendly Restaurants/Breweries
    fig_amenities.add_trace(go.Scattermapbox(
        lat=dog_places_df['latitude'],
        lon=dog_places_df['longitude'],
        mode='markers',
        marker=dict(size=18, color='#e29d12', symbol='circle'),
        name='Dog-Friendly Restaurants/Breweries',
        text=dog_places_df['name']
    ))

    # Veterinarians
    fig_amenities.add_trace(go.Scattermapbox(
        lat=vets_df['latitude'],
        lon=vets_df['longitude'],
        mode='markers',
        marker=dict(size=18, color='#684c6b', symbol='circle'),
        name='Veterinarians',
        text=vets_df['name']
    ))

    fig_amenities.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=40.015, lon=-105.27),
            zoom=13
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        title="Dog-Friendly Places Around Boulder"
    )

    amenities_map_plot = plot(fig_amenities, output_type='div', include_plotlyjs=False)

    # --- Pie Chart ---
    pie_summary = merged_df['dog_access'].value_counts().reset_index()
    pie_summary.columns = ['dog_access', 'count']
    pie_summary['dog_access'] = pie_summary['dog_access'].replace({
        'off_leash': 'Off-Leash Allowed',
        'leash_required': 'Leash Required',
        'no_dogs': 'No Dogs'
    })

    fig_pie = px.pie(
        pie_summary,
        names='dog_access',
        values='count',
        color='dog_access',
        color_discrete_map={
            'Off-Leash Allowed': '#add19e',
            'Leash Required': '#e29d12',
            'No Dogs': '#ada6a1'
        }
    )
    fig_pie.update_traces(textinfo='label+percent')
    pie_plot = plot(fig_pie, output_type='div', include_plotlyjs=False)

    # --- Circle Packing Chart ---
    columns_of_interest = {
        "Bicycles": "bicycles",
        "Horses": "horses",
        "Dogs": "dogs",
        "EBikes": "ebikes"
    }
    trail_use_counts = {
        key: (merged_df[col].str.strip().str.lower() == "yes").sum()
        for key, col in columns_of_interest.items()
    }
    total_count = sum(trail_use_counts.values())
    data = [{'id': k, 'datum': v} for k, v in trail_use_counts.items() if v > 0]

    circles = circlify.circlify(
        data,
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)

    circle_colors = {
        'Bicycles': '#add19e',
        'Horses': '#e29d12',
        'Dogs': '#ada6a1',
        'EBikes': '#6fa6c9'
    }

    for circle in circles:
        if circle.level != 1:
            continue
        x, y, r = circle.x, circle.y, circle.r
        label = circle.ex['id']
        value = int(circle.ex['datum'])
        percent = (value / total_count) * 100
        label_text = f"{label}\n{value} ({percent:.1f}%)"
        color = circle_colors.get(label, "#cccccc")
        ax.add_patch(plt.Circle((x, y), r, facecolor=color, alpha=0.7, edgecolor='black'))
        plt.text(x, y, label_text, ha='center', va='center', fontsize=18)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close(fig)
    buf.seek(0)
    circle_plot = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template(
        "index.html",
        map_plot=map_plot,
        pie_plot=pie_plot,
        circle_plot=circle_plot,
        amenities_map_plot=amenities_map_plot
    )

if __name__ == '__main__':
    app.run(debug=True)
