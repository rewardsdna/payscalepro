import pandas as pd

def recalculate_min_max_from_mid(grades_data, current_grade_index):
    """
    Recalculates Range Min and Range Max from the given Range Mid and Range Spread.
    """
    mid_point = grades_data.loc[current_grade_index, 'Range Mid']
    spread = grades_data.loc[current_grade_index, 'Range Spread'] / 100  # Convert to decimal

    # Calculate Range Min and Range Max
    new_min = mid_point - (mid_point * spread / 2)
    new_max = new_min * (1 + spread)

    return new_min, new_max

def recalculate_mid_point_diff(current_grade_mid, previous_grade_mid):
    """
    Recalculates Mid Point Differential between the current and previous grade.
    """
    return previous_grade_mid / current_grade_mid if current_grade_mid != 0 else None

def recalculate_range_overlap(current_grade_min, current_grade_max, next_grade_min):
    """
    Recalculates Range Overlap between the current and next grade.
    """
    numerator = current_grade_max - next_grade_min
    denominator = current_grade_max - current_grade_min
    return (numerator / denominator) * 100 if denominator != 0 else None

def update_range_mid(grades_data, grade_to_update, new_range_mid):
    """
    Updates Range Mid for a specific grade, recalculates Range Min/Max,
    adjusts Mid Point Differential for the next grade, and refreshes Range Overlap
    only for the lower and upper grades if they exist.
    """
    # Ensure data is sorted by grade in descending order
    grades_data = grades_data.sort_values('Grade', ascending=False).reset_index(drop=True)

    # Find the index of the grade to update
    current_grade_index = grades_data[grades_data['Grade'] == grade_to_update].index[0]

    # Update Range Mid
    grades_data.loc[current_grade_index, 'Range Mid'] = new_range_mid

    # Recalculate Range Min and Range Max
    new_min, new_max = recalculate_min_max_from_mid(grades_data, current_grade_index)
    grades_data.loc[current_grade_index, ['Range Min', 'Range Max']] = [new_min, new_max]

    # Update Mid Point Differential for the next grade (if it exists)
    if current_grade_index + 1 < len(grades_data):
        next_grade_mid = grades_data.loc[current_grade_index + 1, 'Range Mid']
        mid_point_diff = recalculate_mid_point_diff(grades_data.loc[current_grade_index, 'Range Mid'], next_grade_mid)
        grades_data.loc[current_grade_index + 1, 'Mid Point Differential'] = mid_point_diff

    # Refresh Range Overlap for the current grade and its neighbors
    if current_grade_index - 1 >= 0:  # Upper grade exists
        upper_min = grades_data.loc[current_grade_index - 1, 'Range Min']
        current_min = grades_data.loc[current_grade_index, 'Range Min']
        current_max = grades_data.loc[current_grade_index, 'Range Max']

        grades_data.loc[current_grade_index, 'Range Overlap'] = recalculate_range_overlap(
            current_min, current_max, upper_min
        )

    # Current grade overlap
    if current_grade_index + 1 < len(grades_data):  # Lower grade exists
        lower_max = grades_data.loc[current_grade_index + 1, 'Range Max']
        lower_min = grades_data.loc[current_grade_index + 1, 'Range Min']
        current_min = grades_data.loc[current_grade_index, 'Range Min']
        current_max = grades_data.loc[current_grade_index, 'Range Max']

        grades_data.loc[current_grade_index + 1, 'Range Overlap'] = recalculate_range_overlap(
            lower_min, lower_max, current_min
        )

    return grades_data


def update_range_spread(grades_data, grade_to_update, new_range_spread):
    """
    Updates Range Spread for a specific grade and recalculates Range Min and Range Max.
    Refreshes Range Overlap for the lower and upper grades if they exist.
    """
    # Ensure data is sorted by grade in descending order
    grades_data = grades_data.sort_values('Grade', ascending=False).reset_index(drop=True)

    # Find the index of the grade to update
    current_grade_index = grades_data[grades_data['Grade'] == grade_to_update].index[0]

    # Update Range Spread
    grades_data.loc[current_grade_index, 'Range Spread'] = new_range_spread

    # Recalculate Range Min and Range Max
    new_min, new_max = recalculate_min_max_from_mid(grades_data, current_grade_index)
    grades_data.loc[current_grade_index, ['Range Min', 'Range Max']] = [new_min, new_max]

    # Refresh Range Overlap for the current grade and its neighbors
    if current_grade_index - 1 >= 0:  # Upper grade exists
        upper_min = grades_data.loc[current_grade_index - 1, 'Range Min']
        current_min = grades_data.loc[current_grade_index, 'Range Min']
        current_max = grades_data.loc[current_grade_index, 'Range Max']

        grades_data.loc[current_grade_index, 'Range Overlap'] = recalculate_range_overlap(
            current_min, current_max, upper_min
        )

    # Current grade overlap
    if current_grade_index + 1 < len(grades_data):  # Lower grade exists
        lower_max = grades_data.loc[current_grade_index + 1, 'Range Max']
        lower_min = grades_data.loc[current_grade_index + 1, 'Range Min']
        current_min = grades_data.loc[current_grade_index, 'Range Min']
        current_max = grades_data.loc[current_grade_index, 'Range Max']

        grades_data.loc[current_grade_index + 1, 'Range Overlap'] = recalculate_range_overlap(
            lower_min, lower_max, current_min
        )

    return grades_data