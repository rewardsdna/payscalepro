import pandas as pd

def calculate_pay_metrics(pay_range_file, user_data_file):
    # Load data
    user_loaded_data = pd.read_csv(user_data_file)
    pay_range_final = pd.read_csv(pay_range_file)

    # Check if Base Pay exists
    if 'Base Pay' not in user_loaded_data.columns:
        raise ValueError("Base Pay column not found in user data.")
    
    # Ensure Base Pay is numeric
    user_loaded_data['Base Pay'] = pd.to_numeric(user_loaded_data['Base Pay'], errors='coerce')

    # Merge the DataFrames on 'Grade'
    merged_df = pd.merge(user_loaded_data, pay_range_final, on='Grade')

    # Calculate 'Compa-Ratio'
    merged_df['Compa-Ratio'] = merged_df['Base Pay'] / merged_df['Range Mid']
    # Calculate 'Range Penetration'
    merged_df['Range Penetration'] = (merged_df['Base Pay'] - merged_df['Range Min']) / (merged_df['Range Max'] - merged_df['Range Min'])

    # Calculate the required metrics
    count_below_range_min = (merged_df['Base Pay'] < merged_df['Range Min']).sum()
    count_above_range_max = (merged_df['Base Pay'] > merged_df['Range Max']).sum()
    pay_gap_sum = merged_df.apply(lambda x: x['Range Min'] - x['Base Pay'] if x['Base Pay'] < x['Range Min'] else 0, axis=1).sum()
    range_max_sum = merged_df.apply(lambda x: x['Range Max'] - x['Base Pay'] if x['Base Pay'] > x['Range Max'] else 0, axis=1).sum() * -1
    avg_base_pay_range_mid = (merged_df['Base Pay'] / merged_df['Range Mid']).mean()
    median_base_pay_range_mid = (merged_df['Base Pay'] / merged_df['Range Mid']).median()
    avg_pay_gap_range = ((merged_df['Base Pay'] - merged_df['Range Min']) / (merged_df['Range Max'] - merged_df['Range Min'])).mean()
    min_pay_gap_range = ((merged_df['Base Pay'] - merged_df['Range Min']) / (merged_df['Range Max'] - merged_df['Range Min'])).min()
    grade_count = pay_range_final['Grade'].nunique()
    job_count = user_loaded_data['Job'].nunique()
    avg_compa_ratio = merged_df['Compa-Ratio'].mean()
    med_compa_ratio = merged_df['Compa-Ratio'].median()
    avg_range_pen = merged_df['Range Penetration'].mean()
    med_range_pen = merged_df['Range Penetration'].median()
    max_range_pen = merged_df['Range Penetration'].max()
    min_range_pen = merged_df['Range Penetration'].min()
    max_compa_ratio = merged_df['Compa-Ratio'].max()
    min_compa_ratio = merged_df['Compa-Ratio'].min()
    green_circled = len(merged_df) - count_above_range_max - count_below_range_min
    avg_male_pay = merged_df.loc[merged_df['Gender'] == 'Male', 'Base Pay'].mean()
    med_male_pay = merged_df.loc[merged_df['Gender'] == 'Male', 'Base Pay'].median()
    avg_female_pay = merged_df.loc[merged_df['Gender'] == 'Female', 'Base Pay'].mean()
    med_female_pay = merged_df.loc[merged_df['Gender'] == 'Female', 'Base Pay'].median()
    avg_pay_gap = 1-(avg_female_pay / avg_male_pay)
    med_pay_gap = 1 - (med_female_pay / med_male_pay)
    avg_pay_gap_dollar = (avg_male_pay - avg_female_pay)
    med_pay_gap_dollar = (med_male_pay - med_female_pay) 
    within_range_pct = green_circled / len(merged_df)
    outliers_pct = 1 - within_range_pct
    below_min_pct = count_below_range_min / len(merged_df)
    above_max_pct = count_above_range_max / len(merged_df)
    outliers = len(merged_df) - green_circled
    paygap_payroll_pct = pay_gap_sum / merged_df['Base Pay'].sum()
    percentile_10 = merged_df['Base Pay'].quantile(0.10)
    percentile_25 = merged_df['Base Pay'].quantile(0.25)
    percentile_75 = merged_df['Base Pay'].quantile(0.75)
    percentile_90 = merged_df['Base Pay'].quantile(0.90)
    p90_p10 = percentile_90 / percentile_10

    # Identify rows where Base Pay is below Range Min
    # pay_gap_records = merged_df[merged_df['Base Pay'] < merged_df['Range Min']]

    # Group by 'Grade' and count the number of pay gap cases for each grade
    # pay_gap_count_by_grade = pay_gap_records.groupby('Grade').size()

    # Identify the grade with the maximum pay gap count
    # grade_with_max_gap = pay_gap_count_by_grade.idxmax()
    # pay_gap_max_grade = pay_gap_count_by_grade.max()
    # grade_with_min_gap = pay_gap_count_by_grade.idxmin()
    # pay_gap_min_grade = pay_gap_count_by_grade.min()

    # Identify cases where Base Pay is below the Range Min (pay below the range)
    pay_below_range = merged_df[merged_df['Base Pay'] < merged_df['Range Min']]

# Group by 'Grade' and count the number of such cases for each grade
    pay_below_range_count_by_grade = pay_below_range.groupby('Grade').size()

# Identify the grade with the highest number of pay gap cases (Base Pay < Range Min)
    pay_gap_max_grade = pay_below_range_count_by_grade.idxmax()
    pay_gap_max_count = pay_below_range_count_by_grade.max()

# Identify the grade with the lowest number of pay gap cases
    pay_gap_min_grade = pay_below_range_count_by_grade.idxmin()
    pay_gap_min_count = pay_below_range_count_by_grade.min()



    # Calculate average midpoint differential directly from pay_range_final
    if 'Mid Point Differential' in pay_range_final.columns:
        pay_range_final['Mid Point Differential'] = (
            pay_range_final['Mid Point Differential']
            .astype(str).str.rstrip('%').astype(float) / 100
        )
        avg_midpoint_differential = pay_range_final['Mid Point Differential'].mean()
    else:
        avg_midpoint_differential = None

    # Calculate percentage of employees below Range Min
    total_employees = len(user_loaded_data)
    percent_below_range_min = (count_below_range_min / total_employees) * 100

    # Create a dictionary to store the raw results
    results = {
        "count_below_range_min": count_below_range_min,
        "count_above_range_max": count_above_range_max,
        "pay_gap_sum": pay_gap_sum,
        "avg_base_pay_range_mid": avg_base_pay_range_mid,
        "median_base_pay_range_mid": median_base_pay_range_mid,
        "avg_pay_gap_range": avg_pay_gap_range,
        "min_pay_gap_range": min_pay_gap_range,
        "grade_count": grade_count,
        "job_count": job_count,
        "avg_midpoint_differential": avg_midpoint_differential,
        "percent_below_range_min": percent_below_range_min,
        "avg_compa_ratio": avg_compa_ratio,
        "med_compa_ratio": med_compa_ratio,
        "avg_range_pen": avg_range_pen,
        "med_range_pen": med_range_pen,
        "avg_base_pay": user_loaded_data['Base Pay'].mean(),
        "med_base_pay": user_loaded_data['Base Pay'].median(),
        "employee_count": total_employees,
        "range_max_sum": range_max_sum,
        "green_circled": green_circled,
        "min_range_pen": min_range_pen,
        "max_range_pen": max_range_pen,
        "min_compa_ratio": min_compa_ratio,
        "max_compa_ratio": max_compa_ratio,
        "avg_pay_gap": avg_pay_gap,
        "med_pay_gap": med_pay_gap,
        "avg_female_pay": avg_female_pay,
        "avg_male_pay": avg_male_pay,
        "med_female_pay": med_female_pay,
        "med_male_pay": med_male_pay,
        "within_range_pct": within_range_pct,
        "outliers": outliers,
        "below_min_pct": below_min_pct,
        "above_max_pct": above_max_pct,
        "outliers_pct": outliers_pct,
        "paygap_payroll_pct": paygap_payroll_pct,
        "percentile_90": percentile_90,
        "percentile_75": percentile_75,
        "percentile_25": percentile_25,
        "percentile_10": percentile_10,
        "p90_p10": p90_p10,
        "med_pay_gap_dollar": med_pay_gap_dollar,
        "avg_pay_gap_dollar": avg_pay_gap_dollar,
        "pay_gap_min_grade": pay_gap_min_grade,
        "pay_gap_max_grade": pay_gap_max_grade

    }

    # results["highest_pay_gap_grade"] = highest_pay_gap_grade
    # results["highest_pay_gap_value"] = highest_pay_gap_value
    # results["lowest_pay_gap_grade"] = lowest_pay_gap_grade
    # results["lowest_pay_gap_value"] = lowest_pay_gap_value

    return results
