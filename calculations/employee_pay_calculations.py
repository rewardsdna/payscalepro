import pandas as pd
import numpy as np

def analyze_salary_distribution(df, min_employees_per_grade=2):
  """
  Analyzes the salary distribution and calculates salary ranges and related metrics.
  """
  # Ensure correct data types
  df['Base Pay'] = pd.to_numeric(df['Base Pay'], errors='coerce')
  df['Grade'] = pd.to_numeric(df['Grade'], errors='coerce').astype('Int64')
  df = df.dropna(subset=['Base Pay', 'Grade'])

  # Get list of all grades
  all_grades = pd.DataFrame({'Grade': range(df['Grade'].min(), df['Grade'].max() + 1)})

  # Calculate Range Mid values for grades with sufficient data
  def find_optimal_mid(group):
      salaries = group['Base Pay'].dropna().values
      if len(salaries) >= min_employees_per_grade:
          candidate_mids = np.linspace(salaries.min(), salaries.max(), 1000)
          max_count = 0
          optimal_mid = salaries.mean()
          for mid in candidate_mids:
              lower_bound = 0.8 * mid
              upper_bound = 1.2 * mid
              count = np.sum((salaries >= lower_bound) & (salaries <= upper_bound))
              if count > max_count:
                  max_count = count
                  optimal_mid = mid
          return optimal_mid
      else:
          return np.nan  # Insufficient data; will be interpolated

  # Apply the function to each grade
  mids = df.groupby('Grade').apply(find_optimal_mid).reset_index()
  mids.columns = ['Grade', 'Range Mid']

  # Merge with all grades to ensure all grades are included
  mids = pd.merge(all_grades, mids, on='Grade', how='left')

  # Flag to indicate how Range Mid was calculated
  mids['Mid_Calculation'] = np.where(mids['Range Mid'].notna(), 'Calculated', 'Interpolated')

  # Interpolate missing Range Mids
  mids['Range Mid'] = mids['Range Mid'].interpolate(method='linear', limit_direction='both')

  # Sort grades in ascending order (lowest grade first)
  mids.sort_values('Grade', ascending=True, inplace=True)
  mids.reset_index(drop=True, inplace=True)

  # Ensure that higher grades have higher Range Mids
  for i in range(1, len(mids)):
      if mids.at[i, 'Range Mid'] <= mids.at[i - 1, 'Range Mid']:
          # Compute 3% increase over the previous grade's Range Mid
          min_increase = 0.03 * mids.at[i - 1, 'Range Mid']
          increments = [min_increase]

          # Optionally consider half of the midpoint differential to the next grade
          if i < len(mids) - 1:
              midpoint_diff = mids.at[i + 1, 'Range Mid'] - mids.at[i - 1, 'Range Mid']
              half_midpoint_diff = midpoint_diff / 2
              if half_midpoint_diff > 0:
                  increments.append(half_midpoint_diff)

          # Choose the smallest positive increment
          positive_increments = [inc for inc in increments if inc > 0]
          min_increment = min(positive_increments) if positive_increments else min_increase

          # Adjust the current Range Mid
          mids.at[i, 'Range Mid'] = mids.at[i - 1, 'Range Mid'] + min_increment
          mids.at[i, 'Mid_Calculation'] = 'Adjusted'

  # Calculate Range Min and Range Max
  mids['Range Min'] = 0.8 * mids['Range Mid']
  mids['Range Max'] = 1.2 * mids['Range Mid']

  # Calculate Range Spread
  mids['Range Spread'] = ((mids['Range Max'] - mids['Range Min']) / mids['Range Min']) * 100

  # Calculate Mid Point Differential from the second lowest grade to the highest grade
  mids['Mid Point Differential'] = (mids['Range Mid'] / mids['Range Mid'].shift(1) - 1) * 100
  # Set Mid Point Differential to NaN for the first grade (lowest grade)
  mids.loc[mids.index[0], 'Mid Point Differential'] = np.nan

  # Calculate Range Overlap from the lowest grade to the second highest grade
  numerator = mids['Range Max'] - mids['Range Min'].shift(-1)
  denominator = mids['Range Max'] - mids['Range Min']
  mids['Range Overlap'] = (numerator / denominator) * 100
    # Set Range Overlap to NaN for the last grade (highest grade)
  mids.loc[mids.index[-1], 'Range Overlap'] = np.nan

  # Arrange columns and return result
  result_df = mids[['Grade', 'Range Min', 'Range Mid', 'Range Max', 'Range Spread',
                    'Mid Point Differential', 'Range Overlap']]
  result_df = result_df.sort_values(by='Grade', ascending=False).reset_index(drop=True)

  return result_df

def calculate(df):
  df_results = analyze_salary_distribution(df)
  return df_results

def display_salary_distribution(df_results):
  """
  Formats data for display without altering the underlying numeric data.
  """
  df_display = df_results.copy()

  # Format currency columns
  currency_cols = ['Range Min', 'Range Mid', 'Range Max']
  for col in currency_cols:
      df_display[col] = df_display[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else '')

  # Format percentage columns
  percentage_cols = ['Range Spread', 'Mid Point Differential', 'Range Overlap']
  for col in percentage_cols:
      df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else '')

  return df_display