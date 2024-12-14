# combination_strategy_chart.py 
    # This is currently not in use becase 
    # pay ranges based on market data and employee distribution has not been 
    # separately calculated saved. This can be done from combination strategy calculation page.

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

# Set the default template to 'simple_white'
pio.templates.default = "simple_white"

def create_chart(df, pay_ranges_df):
  """
  Creates a plot of employee base pay against grades with pay ranges.

  Parameters:
  - df: DataFrame containing employee data.
  - pay_ranges_df: DataFrame containing pay ranges.

  Returns:
  - fig: Plotly Figure object.
  """
  # Check for 'Base Pay' column
  if 'Base Pay' in df.columns:
      # Handle NaNs, remove commas, and convert to integer
      df["Base Pay"] = df["Base Pay"].fillna("0").astype(str)
      df["Base Pay"] = df["Base Pay"].str.replace(",", "").astype(int)
  else:
      # Optionally, raise an error or handle missing column
      raise KeyError("Column 'Base Pay' is missing in the dataset.")

  # Ensure the 'Grade' column is present in both DataFrames
  if 'Job Grade' in df.columns:
      df = df.rename(columns={'Job Grade': 'Grade'})
  elif 'Grade' not in df.columns:
      raise KeyError("Column 'Grade' or 'Job Grade' is missing in the employee data.")

  if 'Job Grade' in pay_ranges_df.columns:
      pay_ranges_df = pay_ranges_df.rename(columns={'Job Grade': 'Grade'})
  elif 'Grade' not in pay_ranges_df.columns:
      raise KeyError("Column 'Grade' or 'Job Grade' is missing in the pay ranges data.")

  # Merge the original data with the calculated ranges per Grade
  merged_df = pd.merge(df, pay_ranges_df[['Grade', 'Range Min', 'Range Mid', 'Range Max']], on='Grade', how='left')

  # Saving merged df as CSV for using with other pages (charts and calculations)
  merged_df.to_csv('data_csv/merged_data.csv', index=False)

  # Ensure that the grades are in ascending order for plotting
  pay_ranges_df = pay_ranges_df.sort_values('Grade')

  # Create the figure
  fig = go.Figure()

  # Prepare customdata array for the salary data points
  columns_needed = ['Employee ID', 'Base Pay', 'Range Min', 'Range Mid', 'Range Max']
  for col in columns_needed:
      if col not in merged_df.columns:
          merged_df[col] = ''  # or np.nan

  customdata = np.stack((
      merged_df['Employee ID'],
      merged_df['Base Pay'],
      merged_df['Range Min'],
      merged_df['Range Mid'],
      merged_df['Range Max']
  ), axis=-1)

  # Add individual salary data points with merged tooltips
  fig.add_trace(go.Scatter(
      x=merged_df['Grade'],
      y=merged_df['Base Pay'],
      mode='markers',
      name='Salaries',
      marker=dict(color='blue', size=6, opacity=0.6),
      customdata=customdata,
      hovertemplate=(
          '<b>Employee ID</b>: %{customdata[0]}<br>'
          '<b>Base Pay</b>: %{customdata[1]:,}<br>'
          '<b>Range Min</b>: %{customdata[2]:,}<br>'
          '<b>Mid</b>: %{customdata[3]:,}<br>'
          '<b>Range Max</b>: %{customdata[4]:,}<extra></extra>'
      ),
      hoverlabel=dict(
          bgcolor="rgba(255, 255, 255, 0.9)",  # Light background with less transparency
          bordercolor="rgba(0, 0, 0, 0)",       # No border
          font=dict(color='black')              # Black text for visibility
      )
  ))

  # Get unique grades in ascending order
  grades = sorted(pay_ranges_df['Grade'].unique())

  # Prepare horizontal lines for Range Min, Mid, and Range Max
  for idx, grade in enumerate(grades):
      # Define the x-range for the horizontal lines around each grade
      x_start = grade - 0.3
      x_end = grade + 0.3
      x_vals = np.linspace(x_start, x_end, num=10)

      # Extract the Range Min, Mid, and Max for the current grade
      range_min = pay_ranges_df.loc[pay_ranges_df['Grade'] == grade, 'Range Min'].values[0]
      mid = pay_ranges_df.loc[pay_ranges_df['Grade'] == grade, 'Range Mid'].values[0]
      range_max = pay_ranges_df.loc[pay_ranges_df['Grade'] == grade, 'Range Max'].values[0]

      # Add horizontal line for Range Min (green, solid line)
      fig.add_trace(go.Scatter(
          x=x_vals,
          y=[range_min] * len(x_vals),
          mode='lines',
          line=dict(color='green', width=1),
          name='Range Min' if idx == 0 else None,
          hoverinfo='skip',
          showlegend=(idx == 0)
      ))

      # Add horizontal line for Mid (orange, dotted line)
      fig.add_trace(go.Scatter(
          x=x_vals,
          y=[mid] * len(x_vals),
          mode='lines',
          line=dict(color='orange', dash='dot', width=1),
          name='Mid' if idx == 0 else None,
          hoverinfo='skip',
          showlegend=(idx == 0)
      ))

      # Add horizontal line for Range Max (green, solid line)
      fig.add_trace(go.Scatter(
          x=x_vals,
          y=[range_max] * len(x_vals),
          mode='lines',
          line=dict(color='green', width=1),
          name='Range Max' if idx == 0 else None,
          hoverinfo='skip',
          showlegend=(idx == 0)
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
          dtick=1,
          gridcolor='lightgrey',
          zerolinecolor='lightgrey'
      ),
      yaxis=dict(
          gridcolor='lightgrey',
          zerolinecolor='lightgrey'
      ),
      legend=dict(
          bordercolor='white',
          borderwidth=0.5
      ),
      hovermode='closest',
      width=900,
      height=600,
      font=dict(
          family='Arial',
          size=10
      )
  )

  return fig