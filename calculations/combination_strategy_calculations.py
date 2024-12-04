import pandas as pd
import numpy as np

def analyze_salary_distribution_third_variation(df, min_employees_per_grade=2, output_csv=None):
    """
    Analyzes salary distribution and generates a salary range table with calculated metrics.

    Parameters:
        df (pd.DataFrame): Input dataframe containing 'Base Pay' and 'Grade'.
        min_employees_per_grade (int): Minimum number of employees per grade for calculations.
        output_csv (str): Optional. Path to save the output CSV file.

    Returns:
        pd.DataFrame: Dataframe containing the calculated salary ranges and related metrics.
    """
    # Ensure correct data types and drop invalid rows
    df['Base Pay'] = pd.to_numeric(df['Base Pay'], errors='coerce')
    df['Grade'] = pd.to_numeric(df['Grade'], errors='coerce').astype('Int64')
    df = df.dropna(subset=['Base Pay', 'Grade'])

    # Generate full list of grades
    all_grades = pd.DataFrame({'Grade': range(df['Grade'].min(), df['Grade'].max() + 1)})

    # Median of Base Pay per Grade (Calculation A)
    calc_a = df.groupby('Grade')['Base Pay'].median().reset_index()
    calc_a.rename(columns={'Base Pay': 'Mid_A'}, inplace=True)

    # Optimal midpoint (Calculation B)
    def find_optimal_mid(group):
        salaries = group['Base Pay'].dropna().values
        if len(salaries) >= min_employees_per_grade:
            candidate_mids = np.linspace(salaries.min(), salaries.max(), 100)
            optimal_mid = salaries.mean()
            max_count = 0
            for mid in candidate_mids:
                lower_bound = 0.8 * mid
                upper_bound = 1.2 * mid
                count = np.sum((salaries >= lower_bound) & (salaries <= upper_bound))
                if count > max_count:
                    max_count = count
                    optimal_mid = mid
            return optimal_mid
        return np.nan

    calc_b = df.groupby('Grade').apply(find_optimal_mid).reset_index()
    calc_b.columns = ['Grade', 'Mid_B']

    # Merge and calculate final midpoint
    mids = pd.merge(all_grades, calc_a, on='Grade', how='left')
    mids = pd.merge(mids, calc_b, on='Grade', how='left')
    mids['Mid'] = mids[['Mid_A', 'Mid_B']].min(axis=1)
    mids['Mid'] = mids['Mid'].interpolate(method='linear', limit_direction='both')

    # Ensure increasing mids for higher grades
    for i in range(1, len(mids)):
        if mids.loc[i, 'Mid'] <= mids.loc[i - 1, 'Mid']:
            mids.loc[i, 'Mid'] = mids.loc[i - 1, 'Mid'] * 1.03

    # Calculate range boundaries
    mids['Range Min'] = (0.8 * mids['Mid']).round(0).astype(int)
    mids['Range Max'] = (1.2 * mids['Mid']).round(0).astype(int)

    # Range Spread
    mids['Range Spread'] = ((mids['Range Max'] - mids['Range Min']) / mids['Range Min'] * 100).round(2)

    # Mid Point Differential (skip lowest grade, calculate for highest)
    mids['Mid Point Differential'] = (mids['Mid'].pct_change() * 100).round(2)
    mids.loc[0, 'Mid Point Differential'] = np.nan  # Lowest grade


    # Calculate Range Overlap
    numerator = mids['Range Max'] - mids['Range Min'].shift(-1)
    denominator = mids['Range Max'] - mids['Range Min']
    mids['Range Overlap'] = (numerator / denominator) * 100
    # Set Range Overlap to NaN for the last grade (highest grade)
    mids.loc[mids.index[-1], 'Range Overlap'] = np.nan

    # Finalize the output dataframe
    result_df = mids[['Grade', 'Range Min', 'Mid', 'Range Max', 'Range Spread',
                      'Mid Point Differential', 'Range Overlap']]
    result_df.rename(columns={'Mid': 'Range Mid'}, inplace=True)
    # Sort the DataFrame in descending order of 'Grade' before saving
    result_df = result_df.sort_values(by='Grade', ascending=False).reset_index(drop=True)

    # Save to CSV if required
    if output_csv:
        result_df.to_csv(output_csv, index=False)

    return result_df

def calculate(df):
    return analyze_salary_distribution_third_variation(df)
