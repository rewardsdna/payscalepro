import pandas as pd
import numpy as np
import plotly.graph_objects as go

def ensure_no_inversions(df):
  """
  Ensures that higher grades have higher target pay than lower grades.
  Adjusts target pay to eliminate inversions based on specified rules.
  """
  df = df.sort_values('Grade', ascending=False).reset_index(drop=True)
  for i in range(len(df)-1):
      current_pay = df.at[i, 'Target Pay']
      lower_pay = df.at[i+1, 'Target Pay']
      if current_pay <= lower_pay:
          # Option 1: Minimum of 3% above lower grade's Target Pay
          min_increase = lower_pay * 1.03

          # Option 2: Half of the midpoint differential to the upper grade
          if i > 0:
              upper_pay = df.at[i-1, 'Target Pay']
              midpoint_diff = (upper_pay / current_pay) - 1
              half_midpoint_diff = current_pay * (1 + midpoint_diff / 2)
              option_two = max(current_pay, half_midpoint_diff)
          else:
              # If there's no upper grade, set option_two to current_pay
              option_two = current_pay

          # Choose the least of the two options
          adjusted_pay = min(min_increase, option_two)

          # Ensure adjusted_pay is still higher than lower_pay
          if adjusted_pay <= lower_pay:
              adjusted_pay = lower_pay * 1.03  # At least 3% higher than lower grade

          df.at[i, 'Target Pay'] = adjusted_pay
  return df

def extrapolate_missing_grades(df):
  """
  Extrapolates target pay for missing grades using geometric interpolation.
  """
  df = df.sort_values('Grade', ascending=False).reset_index(drop=True)
  existing_grades = df['Grade'].values
  existing_pays = df['Target Pay'].values

  # Create a mapping from grade to target pay
  grade_pay_map = dict(zip(existing_grades, existing_pays))

  # Find all grades between min and max
  min_grade = int(existing_grades.min())
  max_grade = int(existing_grades.max())
  all_grades = np.arange(max_grade, min_grade - 1, -1)
  missing_grades = [grade for grade in all_grades if grade not in existing_grades]

  for grade in missing_grades:
      # Find the nearest grades above and below
      grades_above = existing_grades[existing_grades > grade]
      grades_below = existing_grades[existing_grades < grade]

      if len(grades_above) > 0 and len(grades_below) > 0:
          grade_above = grades_above.min()
          grade_below = grades_below.max()
          pay_above = grade_pay_map[grade_above]
          pay_below = grade_pay_map[grade_below]
          # Geometric interpolation
          ratio = np.log(pay_above / pay_below) / (grade_above - grade_below)
          pay_grade = pay_below * np.exp(ratio * (grade - grade_below))
      elif len(grades_above) >= 2:
          # Extrapolate using the top two grades
          sorted_above = np.sort(grades_above)
          grade1, grade2 = sorted_above[0], sorted_above[1]
          pay1, pay2 = grade_pay_map[grade1], grade_pay_map[grade2]
          ratio = np.log(pay2 / pay1) / (grade2 - grade1)
          pay_grade = pay1 * np.exp(ratio * (grade - grade1))
      elif len(grades_below) >= 2:
          # Extrapolate using the bottom two grades
          sorted_below = np.sort(grades_below)
          grade1, grade2 = sorted_below[-2], sorted_below[-1]
          pay1, pay2 = grade_pay_map[grade1], grade_pay_map[grade2]
          ratio = np.log(pay2 / pay1) / (grade2 - grade1)
          pay_grade = pay1 * np.exp(ratio * (grade - grade1))
      else:
          # Cannot extrapolate accurately; use closest available pay
          if len(grades_above) > 0:
              closest_grade = grades_above.min()
          else:
              closest_grade = grades_below.max()
          pay_grade = grade_pay_map[closest_grade]

      # Add the new grade and pay to the mapping
      grade_pay_map[grade] = pay_grade

  # Create a new DataFrame from the mapping
  df_extrapolated = pd.DataFrame({
      'Grade': list(grade_pay_map.keys()),
      'Target Pay': list(grade_pay_map.values())
  })
  # Sort the DataFrame
  df_extrapolated = df_extrapolated.sort_values('Grade', ascending=False).reset_index(drop=True)
  return df_extrapolated

def analyze_salary_structure(df, range_min_pct=0.8, range_max_pct=1.2):
  """
  Analyzes the salary structure and calculates required metrics.
  """
  df = df.copy()
  df = ensure_no_inversions(df)
  df = extrapolate_missing_grades(df)
  df = df.sort_values('Grade', ascending=False).reset_index(drop=True)
  results = []
  for i, row in df.iterrows():
      grade = row['Grade']
      range_mid = row['Target Pay']
      range_min = range_mid * range_min_pct
      range_max = range_mid * range_max_pct
      range_spread = (range_max / range_min) - 1
      if i < len(df) - 1:
          lower_mid = df.at[i+1, 'Target Pay']
          mid_point_diff = (range_mid / lower_mid) - 1
      else:
          mid_point_diff = np.nan  # No midpoint differential for lowest grade
      if i > 0:
          upper_range_min = df.at[i-1, 'Target Pay'] * range_min_pct
          range_overlap = (range_max / upper_range_min) - 1
      else:
          range_overlap = np.nan  # No range overlap for highest grade
      results.append({
          'Grade': grade,
          'Range Min': range_min,
          'Range Mid': range_mid,
          'Range Max': range_max,
          'Range Spread': range_spread * 100,
          'Mid Point Differential': mid_point_diff * 100,
          'Range Overlap': range_overlap * 100
      })
  df_results = pd.DataFrame(results)
  return df_results

def create_salary_structure_bar_chart(df_results):
  # Sort by Grade ascending
  df_plot = df_results.sort_values('Grade', ascending=True).reset_index(drop=True)
  # Grades as integers
  grades = df_plot['Grade'].astype(int)
  # Extract the Range Min, Mid, Max
  range_min = df_plot['Range Min']
  range_mid = df_plot['Range Mid']
  range_max = df_plot['Range Max']

  # Create figure with 'Simple White' template
  fig = go.Figure(layout=go.Layout(template='simple_white'))

  # Add invisible bars from 0 to Range Min (dummy bars)
  fig.add_trace(go.Bar(
      x=grades,
      y=range_min,
      marker_color='rgba(0,0,0,0)',  # Invisible bars
      hoverinfo='skip',              # Exclude from tooltip
      showlegend=False
  ))

  # Add bars from Range Min to Range Max (actual salary range)
  fig.add_trace(go.Bar(
      x=grades,
      y=range_max - range_min,
      base=range_min,
      marker_color='rgba(119, 152, 191, 0.7)',  # Light blue
      name='Pay Range',
      customdata=np.stack((range_mid,), axis=-1),
      hovertemplate='Min: %{base:,.0f}<br>Mid: %{customdata[0]:,.0f}<br>Max: %{y:,.0f}<extra></extra>'
  ))

  # Add midpoints as a line connecting markers
  fig.add_trace(go.Scatter(
      x=grades,
      y=range_mid,
      mode='lines+markers',
      line=dict(color='green', width=2),
      marker=dict(color='green', size=8),
      name='Midpoint',
      hoverinfo='skip'  # Hover info is included in the bar's tooltip
  ))

  # Update hover label styling
  fig.update_traces(hoverlabel=dict(
      bgcolor='rgba(255,255,204,0.9)',  # Light yellow background
      font_size=12,
      font_color='black'
  ))

  # Update layout
  fig.update_layout(
      title='Pay Progression',
      xaxis_title='Grade',
      yaxis_title='Base Pay',
      yaxis_tickformat=',.0f',
      xaxis=dict(
          tickmode='linear',
          tick0=grades.min(),
          dtick=1,
          categoryorder='array',
          categoryarray=grades
      ),
      legend_title='',
      hovermode='x',
      barmode='stack'  # Stack the bars
  )

  # Show the figure
  return fig

def calculate(df):
  df_results = analyze_salary_structure(df)
  return df_results

def show(df_results):
  """
  Formats data for display without altering the underlying numeric data.
  """
  # Create a copy for display formatting
  df_display = df_results.copy()

  # Format percentages with 1 decimal place
  df_display['Range Spread'] = df_display['Range Spread'].apply(lambda x: f"{x:.1f}%" if not pd.isnull(x) else '')
  df_display['Mid Point Differential'] = df_display['Mid Point Differential'].apply(lambda x: f"{x:.1f}%" if not pd.isnull(x) else '')
  df_display['Range Overlap'] = df_display['Range Overlap'].apply(lambda x: f"{x:.1f}%" if not pd.isnull(x) else '')

  # Remove decimals from Range Min, Mid, and Max
  df_display['Range Min'] = df_display['Range Min'].apply(lambda x: f"{x:,.0f}")
  df_display['Range Mid'] = df_display['Range Mid'].apply(lambda x: f"{x:,.0f}")
  df_display['Range Max'] = df_display['Range Max'].apply(lambda x: f"{x:,.0f}")

  # Display results
  print("Here are your pay ranges. Use as is or do a bit of fine-tuning.")
  print(df_display)

  # Generate analytics using raw numeric data
  fig = create_salary_structure_bar_chart(df_results)
  return fig