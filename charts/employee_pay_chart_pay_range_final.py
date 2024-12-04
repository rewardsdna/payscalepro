# employee_pay_chart_pay_range_final.py

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

# Load pay range data
pay_ranges_df = pd.read_csv("data_csv/pay_range_final.csv")

# Set the default template to 'simple_white'
pio.templates.default = "simple_white"

def create_chart(df, pay_ranges_df):

    # Ensure 'Base Pay' column exists and process it
    if 'Base Pay' in df.columns:
        df["Base Pay"] = df["Base Pay"].fillna("0").astype(str).str.replace(",", "").astype(int)
    else:
        raise KeyError("Column 'Base Pay' is missing in the dataset.")

    # Rename and validate 'Grade' column
    if 'Job Grade' in df.columns:
        df = df.rename(columns={'Job Grade': 'Grade'})
    elif 'Grade' not in df.columns:
        raise KeyError("Column 'Grade' or 'Job Grade' is missing in the employee data.")

    if 'Job Grade' in pay_ranges_df.columns:
        pay_ranges_df = pay_ranges_df.rename(columns={'Job Grade': 'Grade'})
    elif 'Grade' not in pay_ranges_df.columns:
        raise KeyError("Column 'Grade' or 'Job Grade' is missing in the pay ranges data.")

    # Merge employee data with pay ranges
    merged_df = pd.merge(
        df,
        pay_ranges_df[['Grade', 'Range Min', 'Range Mid', 'Range Max']],
        on='Grade',
        how='left'
    )

    # Calculate additional metrics
    merged_df['Compa-Ratio'] = merged_df['Base Pay'] / merged_df['Range Mid']
    merged_df['Range Penetration'] = (
        (merged_df['Base Pay'] - merged_df['Range Min']) /
        (merged_df['Range Max'] - merged_df['Range Min'])
    )

    # Create figure
    fig = go.Figure()

    # Prepare customdata for tooltips
    customdata = np.stack((
        merged_df['Employee ID'],
        merged_df['Base Pay'],
        merged_df['Range Min'],
        merged_df['Range Mid'],
        merged_df['Range Max'],
        merged_df['Compa-Ratio'],
        merged_df['Range Penetration']
    ), axis=-1)

    # Add salary data points
    fig.add_trace(go.Scatter(
        x=merged_df['Grade'],
        y=merged_df['Base Pay'],
        mode='markers',
        name='Employee',
        marker=dict(color='blue', size=6, opacity=0.6),
        customdata=customdata,
        hovertemplate=(
            '<b>Employee ID</b>: %{customdata[0]}<br>'
            '<b>Base Pay</b>: %{customdata[1]:,.0f}<br>'
            '<b>Range Min</b>: %{customdata[2]:,.0f}<br>'
            '<b>Mid</b>: %{customdata[3]:,.0f}<br>'
            '<b>Range Max</b>: %{customdata[4]:,.0f}<br>'
            '<b>Compa-Ratio</b>: %{customdata[5]:.1%}<br>'
            '<b>Range Penetration</b>: %{customdata[6]:.1%}<extra></extra>'
        )
    ))

    # Add pay range lines
    grades = sorted(pay_ranges_df['Grade'].unique())
    for idx, grade in enumerate(grades):
        x_vals = [grade - 0.3, grade + 0.3]

        range_min = pay_ranges_df.loc[pay_ranges_df['Grade'] == grade, 'Range Min'].values[0]
        mid = pay_ranges_df.loc[pay_ranges_df['Grade'] == grade, 'Range Mid'].values[0]
        range_max = pay_ranges_df.loc[pay_ranges_df['Grade'] == grade, 'Range Max'].values[0]

        # Add Range Min
        fig.add_trace(go.Scatter(
            x=x_vals, y=[range_min] * 2,
            mode='lines', line=dict(color='green', width=1),
            name='Range Min' if idx == 0 else None,  # Add legend only for first instance
            showlegend=(idx == 0), hoverinfo='skip'
        ))

        # Add Mid
        fig.add_trace(go.Scatter(
            x=x_vals, y=[mid] * 2,
            mode='lines', line=dict(color='orange', dash='dot', width=1),
            name='Mid' if idx == 0 else None,  # Add legend only for first instance
            showlegend=(idx == 0), hoverinfo='skip'
        ))

        # Add Range Max
        fig.add_trace(go.Scatter(
            x=x_vals, y=[range_max] * 2,
            mode='lines', line=dict(color='green', width=1),
            name='Range Max' if idx == 0 else None,  # Add legend only for first instance
            showlegend=(idx == 0), hoverinfo='skip'
        ))

    # Update layout
    fig.update_layout(
        title='Employee Distribution Across Pay Ranges',
        xaxis_title='Grade',
        yaxis_title='Base Pay',
        xaxis=dict(
            tickmode='array',
            tickvals=grades,
            ticktext=[str(grade) for grade in grades],
            gridcolor='lightgrey'
        ),
        yaxis=dict(
            gridcolor='lightgrey',
            tickformat=','
        ),
        hovermode='closest',
        legend=dict(
            
            bordercolor="lightgrey",
            borderwidth=1
        )
    )

    return fig
