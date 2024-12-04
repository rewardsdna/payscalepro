import pandas as pd

def calculate_pay_metrics(pay_range_file, user_data_file):

    # Load the CSV files with error handling
    try:
        pay_range_final = pd.read_csv(pay_range_file)
        user_loaded_data = pd.read_csv(user_data_file)
    except Exception as e:
        raise ValueError(f"Error loading CSV files: {e}")

    # Calculate metrics
    try:
        grade_count = pay_range_final['Grade'].nunique()
        job_count = user_loaded_data['Job'].nunique()

        # Handle potential percentage strings in Mid Point Differential
        if pay_range_final['Mid Point Differential'].dtype == 'object':
            pay_range_final['Mid Point Differential'] = (
                pay_range_final['Mid Point Differential'].str.rstrip('%').astype(float) / 100
            )
        avg_midpoint_differential = pay_range_final['Mid Point Differential'].mean()
        avg_range_overlap = pay_range_final['Range Overlap'].mean()
        avg_range_spread = pay_range_final['Range Spread'].mean()

        # Format percentages as strings
        avg_midpoint_differential = f"{avg_midpoint_differential:.1f}%"
        avg_range_overlap = f"{avg_range_overlap:.1f}%"
        avg_range_spread = f"{avg_range_spread:.1f}%"
    except Exception as e:
        raise ValueError(f"Error calculating metrics: {e}")

    # Store the results in a dictionary
    results = {
        "grade_count": grade_count,
        "job_count": job_count,
        "avg_midpoint_differential": avg_midpoint_differential,
        "avg_range_spread": avg_range_spread,
        "avg_range_overlap": avg_range_overlap

    }

    return results
