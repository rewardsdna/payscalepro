import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os



def avg_gender_pay_chart(user_loaded_data, pay_range_final):
    """
    Creates a Plotly figure showing the gender distribution across pay quartiles.

    Parameters:
    user_loaded_data (pd.DataFrame or str): DataFrame or CSV file path containing user data with 'Base Pay', 'Gender', and 'Grade' columns.
    pay_range_final (pd.DataFrame or str): DataFrame or CSV file path containing pay range data to merge on 'Grade'.

    Returns:
    fig (plotly.graph_objects.Figure): Plotly Figure object containing the subplots.
    """


    # If inputs are file paths (strings), read the CSV files
    if isinstance(user_loaded_data, str):
        if not os.path.exists(user_loaded_data):
            raise FileNotFoundError(f"The file {user_loaded_data} does not exist.")
        user_loaded_data = pd.read_csv(user_loaded_data)

    if isinstance(pay_range_final, str):
        if not os.path.exists(pay_range_final):
            raise FileNotFoundError(f"The file {pay_range_final} does not exist.")
        pay_range_final = pd.read_csv(pay_range_final)

    # Check for the required columns in the user data
    required_columns = ['Base Pay', 'Gender', 'Grade']
    missing_cols = [col for col in required_columns if col not in user_loaded_data.columns]
    if missing_cols:
        raise ValueError(f"Missing columns from user data: {', '.join(missing_cols)}")

    # Merge the dataframes on 'Grade'
    merged_df = pd.merge(user_loaded_data, pay_range_final, on='Grade', how='left')

    # Standardize 'Gender' labels (e.g., 'male' -> 'Male')
    merged_df['Gender'] = merged_df['Gender'].str.title()

    # Drop rows with missing 'Base Pay' or 'Gender'
    merged_df = merged_df.dropna(subset=['Base Pay', 'Gender'])

    # Ensure 'Base Pay' is numeric
    merged_df['Base Pay'] = pd.to_numeric(merged_df['Base Pay'], errors='coerce')
    merged_df = merged_df.dropna(subset=['Base Pay'])

    # Calculate quartiles based on 'Base Pay' across all data
    merged_df['Quartiles'] = pd.qcut(merged_df['Base Pay'].rank(method='first'), 4, labels=False)

    # Count the number of each gender in each quartile
    gender_counts = merged_df.groupby(['Quartiles', 'Gender']).size().unstack(fill_value=0)

    # Define custom colors mapping for genders
    color_mapping = {'Female': '#ff7f0e', 'Male': '#1f77b4'}

    labels = gender_counts.columns.tolist()
    # Ensure colors match the labels
    colors = [color_mapping.get(label, '#d3d3d3') for label in labels]  # default color is light gray

    # Create figure with 1 row and 4 columns
    fig = make_subplots(
        rows=1, cols=4,
        specs=[[{'type': 'domain'}]*4],
        subplot_titles=('Q1', 'Q2', 'Q3', 'Q4')
    )

    # Create donut charts for each quartile
    for i in range(4):
        row = 1
        col = i + 1
        # Get the values for this quartile, default to zeros if quartile is missing
        values = gender_counts.loc[i] if i in gender_counts.index else pd.Series([0]*len(labels), index=labels)
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker_colors=colors,
                name=f'Quartile {i+1}'
            ),
            row=row,
            col=col
        )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        template='simple_white',
        title_text='Gender Distribution across Pay Quartiles',
        title_x=0.5,
        showlegend=True  # Set to True to display the legend
    )

    return fig



def gender_ratio_chart(user_loaded_data):
    """
    Creates a donut chart showing the ratio of Male to Female counts.

    Parameters:
    user_loaded_data (pd.DataFrame): DataFrame containing user data with a 'Gender' column.

    Returns:
    fig (plotly.graph_objects.Figure): Plotly Figure object for the donut chart.
    """
    
    # Standardize 'Gender' labels
    user_loaded_data['Gender'] = user_loaded_data['Gender'].str.title()

    # Count the number of Females and Males
    gender_counts = user_loaded_data['Gender'].value_counts()

    # Define custom colors for genders
    color_mapping = {'Female': '#ff7f0e', 'Male': '#1f77b4'}
    labels = gender_counts.index.tolist()
    values = gender_counts.values.tolist()
    colors = [color_mapping.get(label, '#d3d3d3') for label in labels]

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='percent+label'
    )])

    fig.update_layout(
        template='simple_white',
        title_text='Gender Ratio',
        title_x=0.5,
        showlegend=True
    )

    return fig
    



def avg_base_pay_gap_chart(user_loaded_data):
    """
    Creates a donut chart showing the average female base pay and the pay gap.

    Parameters:
    user_loaded_data (pd.DataFrame): DataFrame containing user data with 'Base Pay' and 'Gender' columns.

    Returns:
    fig (plotly.graph_objects.Figure): Plotly Figure object for the donut chart.
    """
    import pandas as pd
    import plotly.graph_objects as go

    # Standardize 'Gender' labels
    user_loaded_data['Gender'] = user_loaded_data['Gender'].str.title()

    # Ensure 'Base Pay' is numeric
    user_loaded_data['Base Pay'] = pd.to_numeric(user_loaded_data['Base Pay'], errors='coerce')
    # Drop rows with missing 'Base Pay' or 'Gender'
    user_loaded_data = user_loaded_data.dropna(subset=['Base Pay', 'Gender'])

    # Calculate the average base pay for males and females
    average_base_pay = user_loaded_data.groupby('Gender')['Base Pay'].mean()

    average_female_base_pay = average_base_pay.get('Female', 0)
    average_male_base_pay = average_base_pay.get('Male', 0)

    # Calculate the pay gap
    pay_gap = average_male_base_pay - average_female_base_pay

    # Ensure pay_gap is not negative
    pay_gap = max(0, pay_gap)

    # Prepare labels and values
    labels = ["Average Female Base Pay", "Pay Gap"]
    values = [average_female_base_pay, pay_gap]

    # Define custom colors
    colors = ['#ff7f0e', '#d3d3d3']  # Orange for female pay, gray for pay gap

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='percent+label',
        textposition='inside'
    )])

    # Customize the chart
    fig.update_layout(
        template='simple_white',
        title_text="Average Base Pay Gap",
        title_x=0.5  # Center the title
    )

    return fig




def med_base_pay_gap_chart(user_loaded_data):
    """
    Creates a donut chart showing the median female base pay and the pay gap.

    Parameters:
    user_loaded_data (pd.DataFrame): DataFrame containing user data with 'Base Pay' and 'Gender' columns.

    Returns:
    fig (plotly.graph_objects.Figure): Plotly Figure object for the donut chart.
    """
    
    # Standardize 'Gender' labels
    user_loaded_data['Gender'] = user_loaded_data['Gender'].str.title()

    # Ensure 'Base Pay' is numeric
    user_loaded_data['Base Pay'] = pd.to_numeric(user_loaded_data['Base Pay'], errors='coerce')
    # Drop rows with missing 'Base Pay' or 'Gender'
    user_loaded_data = user_loaded_data.dropna(subset=['Base Pay', 'Gender'])

    # Calculate the median base pay for males and females
    median_base_pay = user_loaded_data.groupby('Gender')['Base Pay'].median()

    median_female_base_pay = median_base_pay.get('Female', 0)
    median_male_base_pay = median_base_pay.get('Male', 0)

    # Calculate the pay gap
    pay_gap = median_male_base_pay - median_female_base_pay

    # Ensure pay_gap is not negative
    pay_gap = max(0, pay_gap)

    # Prepare labels and values
    labels = ["Median Female Base Pay", "Pay Gap"]
    values = [median_female_base_pay, pay_gap]

    # Define custom colors
    colors = ['#ff7f0e', '#d3d3d3']  # Orange for female pay, gray for pay gap

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='percent+label',
        textposition='inside'
    )])

    # Customize the chart
    fig.update_layout(
        template='simple_white',
        title_text="Median Base Pay Gap",
        title_x=0.5  # Center the title
    )

    return fig




def gender_grade_count_chart(user_loaded_data):
    """
    Creates a stacked bar chart showing the count of Male and Female employees in each Grade.

    Parameters:
    user_loaded_data (pd.DataFrame): DataFrame containing user data with 'Gender' and 'Grade' columns.

    Returns:
    fig (plotly.graph_objects.Figure): Plotly Figure object for the bar chart.
    """

    # Ensure 'Gender' and 'Grade' columns are present
    required_columns = ['Gender', 'Grade']
    missing_cols = [col for col in required_columns if col not in user_loaded_data.columns]
    if missing_cols:
        raise ValueError(f"Missing columns from user data: {', '.join(missing_cols)}")

    # Standardize 'Gender' labels
    user_loaded_data['Gender'] = user_loaded_data['Gender'].str.title()

    # Count Male and Female in each Grade
    grade_gender_counts = user_loaded_data.groupby(['Grade', 'Gender']).size().unstack(fill_value=0)

    # Sort grades if they are not sorted
    grade_gender_counts = grade_gender_counts.sort_index()

    # Define custom colors for genders
    color_mapping = {'Female': '#ff7f0e', 'Male': '#1f77b4'}
    genders = grade_gender_counts.columns.tolist()
    colors = [color_mapping.get(gender, '#d3d3d3') for gender in genders]

    # Create the bar chart
    fig = go.Figure()

    for gender, color in zip(genders, colors):
        fig.add_trace(go.Bar(
            x=grade_gender_counts.index,
            y=grade_gender_counts[gender],
            name=gender,
            marker_color=color
        ))

    fig.update_layout(
        template='simple_white',
        title="Count of Male and Female in Each Grade",
        xaxis_title="Grade",
        yaxis_title="Count",
        barmode='stack',  # Stack the bars
        title_x=0.5,      # Center the title
        legend_title_text='Gender'
    )

    return fig    