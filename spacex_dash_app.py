# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df["Launch Site"].unique()
dropdown_options = [{"label": "All Sites", "value": "ALL"}] + [{"label": site, "value": site} for site in launch_sites]
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=dropdown_options,
                                    value='ALL',  # Default value
                                    placeholder='Select a Launch Site Here',
                                    searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload)+1, 2000)}
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(entered_site):
    if entered_site == "ALL":
        # Contar los lanzamientos exitosos (class = 1) por cada sitio de lanzamiento
        site_success_counts = spacex_df[spacex_df["class"] == 1]["Launch Site"].value_counts().reset_index()
        site_success_counts.columns = ["Launch Site", "count"]
        # Crear gráfico de pastel para mostrar éxitos por sitio
        fig = px.pie(site_success_counts, values="count", names="Launch Site",
                     title="Total Successful Launches by Site")

    else:
        # Filtrar el dataframe por el sitio seleccionado
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        # Contar éxitos y fracasos en ese sitio
        success_failure_counts = filtered_df["class"].value_counts().reset_index()
        success_failure_counts.columns = ["class", "count"]
        # Crear gráfico de pastel para mostrar éxito vs. fracaso
        fig = px.pie(success_failure_counts, values="count", names="class",
                     title=f"Success vs. Failure for {entered_site}",
                     color="class", color_discrete_map={0: "red", 1: "green"})

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    # Filter by payload range
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= payload_range[0]) &
                            (spacex_df["Payload Mass (kg)"] <= payload_range[1])]

    if entered_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]

    fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
                     color="Booster Version Category",
                     title="Payload vs. Launch Outcome",
                     labels={"class": "Launch Success (1 = Success, 0 = Failure)"})
    
    return fig



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
