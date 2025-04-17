# app.py

from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot

app = Flask(__name__)

# Categorization function
def categorize_dog_policy(desc):
    if pd.isnull(desc):
        return None
    desc = desc.strip().lower()
    if "no dogs" in desc:
        return "no_dogs"
    elif "leash" in desc:
        return "leash_required"
    elif "voice and sight" in desc:
        return "off_leash"
    return None

@app.route('/')
def index():
    # Load merged trail data (with coordinates)
    merged_df = pd.read_csv("data/merged_trails.csv")
    merged_df.columns = merged_df.columns.str.strip()

    print("Columns in merged_df:", merged_df.columns.tolist())

    # Load original trails data (one row per trail)
    df = pd.read_csv('data/Trails.csv')
    df.columns = df.columns.str.strip()
    print("Columns in df:", df.columns.tolist())# Clean up column names

    # --- Categorize dog access for both dataframes ---
    merged_df['dog_access'] = merged_df['DOGREGDESC'].apply(categorize_dog_policy)
    df['dog_access'] = df['OSMPTrailsOSMPDOGREGDESC'].apply(categorize_dog_policy)

    # --- Interactive Map Plot ---
    off_leash = merged_df[merged_df['dog_access'] == 'off_leash']
    leash_required = merged_df[merged_df['dog_access'] == 'leash_required']
    no_dogs = merged_df[merged_df['dog_access'] == 'no_dogs']

    fig_map = go.Figure()

    fig_map.add_trace(go.Scattermapbox(
        lat=off_leash['latitude'],
        lon=off_leash['longitude'],
        mode='markers',
        marker=dict(size=8, color='green'),
        name='Off-Leash',
        text=off_leash['OSMPTrailsOSMPTRAILNAME'],
        visible=True
    ))

    fig_map.add_trace(go.Scattermapbox(
        lat=leash_required['latitude'],
        lon=leash_required['longitude'],
        mode='markers',
        marker=dict(size=8, color='orange'),
        name='Leash Required',
        text=leash_required['OSMPTrailsOSMPTRAILNAME'],
        visible=False
    ))

    fig_map.add_trace(go.Scattermapbox(
        lat=no_dogs['latitude'],
        lon=no_dogs['longitude'],
        mode='markers',
        marker=dict(size=8, color='red'),
        name='No Dogs',
        text=no_dogs['OSMPTrailsOSMPTRAILNAME'],
        visible=False
    ))

    fig_map.update_layout(
        title="Boulder Trails: Dog Access Map",
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=40.02, lon=-105.27),
            zoom=13
        ),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        updatemenus=[
            dict(
                buttons=[
                    dict(label="Off-Leash", method="update", args=[{"visible": [True, False, False]}, {"title": "Off-Leash Trails"}]),
                    dict(label="Leash Required", method="update", args=[{"visible": [False, True, False]}, {"title": "Leash Required Trails"}]),
                    dict(label="No Dogs", method="update", args=[{"visible": [False, False, True]}, {"title": "No Dogs Allowed Trails"}]),
                    dict(label="Show All", method="update", args=[{"visible": [True, True, True]}, {"title": "All Trails"}])
                ],
                direction="down",
                showactive=True,
                x=0.1,
                xanchor="left",
                y=0.95,
                yanchor="top"
            )
        ]
    )

    map_plot = plot(fig_map, output_type='div', include_plotlyjs=False)

    # --- Pie Chart ---
    filtered_df = df[df['dog_access'].notnull()]

    pie_summary = filtered_df['dog_access'].value_counts().reset_index()
    pie_summary.columns = ['Dog Access', 'Count']
    pie_summary['Dog Access'] = pie_summary['Dog Access'].replace({
        'off_leash': 'Off-Leash Allowed',
        'leash_required': 'Leash Required',
        'no_dogs': 'No Dogs'
    })

    fig_pie = px.pie(
        pie_summary,
        names='Dog Access',
        values='Count',
        title='Trails by Dog Access Policy',
        color='Dog Access',
        color_discrete_map={
            'Off-Leash Allowed': 'green',
            'Leash Required': 'orange',
            'No Dogs': 'red'
        }
    )
    fig_pie.update_traces(textinfo='label+percent')
    pie_plot = plot(fig_pie, output_type='div', include_plotlyjs=False)

    # Placeholder divs for bar and histogram plots (if needed)
    bar_plot = "<div></div>"
    hist_plot = "<div></div>"

    return render_template("index.html", map_plot=map_plot, bar_plot=bar_plot, hist_plot=hist_plot, pie_plot=pie_plot)


if __name__ == '__main__':
    app.run(debug=True)



    mileage_data = df['MILEAGE'].dropna()
    mileage_data = mileage_data[mileage_data > 0]
    mileage_data_qcut, bin_edges = pd.qcut(
        mileage_data, q=20, retbins=True, precision=2, duplicates='drop'
    )
    bin_counts = mileage_data_qcut.value_counts(sort=False)
    bin_midpoints = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    mileage_gdist = pd.DataFrame({
        "Mileage Bin (mi)": bin_midpoints,
        "Trail Count": bin_counts.values
    })
    fig_line = px.line(
        mileage_gdist,
        x="Mileage Bin (mi)",
        y="Trail Count",
        title="🐾 Trail Mileage Distribution",
        markers=True,
        line_shape="spline",
        labels={
            "Mileage Bin (mi)": "Trail Mileage (mi)",
            "Trail Count": "Number of Trails"
        },
        template="plotly_white"
    )
    fig_line.update_layout(
        title_font_size=22,
        title_x=0.5,
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14))
    )
    fig_line.update_traces(
        marker=dict(size=6, color="#6BA368"),
        line=dict(color="#6BA368")
    )
    line_plot = plot(fig_line, output_type='div', include_plotlyjs=True)
    return render_template("index.html", map_plot=map_plot, pie_plot=pie_plot, line_plot=line_plot, bar_plot="<div></div>", hist_plot="<div></div>")

