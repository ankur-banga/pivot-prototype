import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from data_generator import DataGenerator
from pivot_engine import PivotEngine

# Page configuration
st.set_page_config(
    page_title="User Segmentation & Analytics Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        color: #667EEA;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #764BA2;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667EEA;
    }
    .success-text {
        color: #48BB78;
        font-weight: 600;
    }
    .segment-table {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }
    .stSelectbox > div > div > div {
        background-color: white;
        border: 1px solid #E2E8F0;
    }
    .stDataFrame {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_generator' not in st.session_state:
    st.session_state.data_generator = DataGenerator()
    st.session_state.pivot_engine = PivotEngine()
    
if 'user_data' not in st.session_state:
    st.session_state.user_data = st.session_state.data_generator.generate_user_data()

# Main header
st.markdown('<h1 class="main-header">User Segmentation & Analytics Tool</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #1A202C; font-size: 1.1rem;">Analyze customer data through interactive pivot tables and dynamic bucketing for retention marketing</p>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.markdown('<h2 class="sub-header">Configuration</h2>', unsafe_allow_html=True)

# Data refresh button
if st.sidebar.button("🔄 Generate New Data", type="primary"):
    st.session_state.user_data = st.session_state.data_generator.generate_user_data()
    st.rerun()

# Audience selection
st.sidebar.markdown("### Audience Selection")
audiences = st.session_state.data_generator.get_audience_definitions()
selected_audience = st.sidebar.selectbox(
    "Primary Audience",
    options=list(audiences.keys()),
    index=0,
    key="primary_audience"
)

# Comparison audience
comparison_enabled = st.sidebar.checkbox("Enable Audience Comparison")
selected_comparison = None
if comparison_enabled:
    selected_comparison = st.sidebar.selectbox(
        "Comparison Audience",
        options=list(audiences.keys()),
        index=1,
        key="comparison_audience"
    )

# Time period selection
st.sidebar.markdown("### Time Period")
time_period = st.sidebar.selectbox(
    "Analysis Period",
    options=["L30D", "L7D", "L90D", "All Time"],
    index=0
)

# Available dimensions
all_dimensions = st.session_state.pivot_engine.get_available_dimensions()
metrics = ["Count", "Total Revenue", "Avg LTV", "Retention Rate", "Avg AOV", "Total Orders"]

# Audience Filters in sidebar - compact version
st.sidebar.markdown("### 🎯 Audience Filters")

# Number of filters
num_filters = st.sidebar.number_input("# Filters", min_value=0, max_value=5, value=1, key="num_filters")

# Store filter conditions
filter_conditions = []
for i in range(num_filters):
    with st.sidebar.container():
        st.markdown(f"**Filter {i+1}**")
        
        # Compact 3-column layout for filter controls
        filter_col = st.selectbox(
            "Column",
            options=all_dimensions,
            index=0,
            key=f"filter_col_{i}",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 2])
        with col1:
            filter_op = st.selectbox(
                "Op",
                options=[">", "<", ">=", "<=", "==", "!="],
                index=0,
                key=f"filter_op_{i}",
                label_visibility="collapsed"
            )
        with col2:
            filter_val = st.text_input(
                "Value",
                placeholder="Value...",
                key=f"filter_val_{i}",
                label_visibility="collapsed"
            )
        
        if filter_val:
            filter_conditions.append((filter_col, filter_op, filter_val))

# Get filtered data
filtered_data = st.session_state.data_generator.filter_by_audience(
    st.session_state.user_data, 
    selected_audience
)

# Apply additional filters from sidebar
for filter_col, filter_op, filter_val in filter_conditions:
    try:
        if filter_op == ">":
            filtered_data = filtered_data[filtered_data[filter_col] > float(filter_val)]
        elif filter_op == "<":
            filtered_data = filtered_data[filtered_data[filter_col] < float(filter_val)]
        elif filter_op == ">=":
            filtered_data = filtered_data[filtered_data[filter_col] >= float(filter_val)]
        elif filter_op == "<=":
            filtered_data = filtered_data[filtered_data[filter_col] <= float(filter_val)]
        elif filter_op == "==":
            if filtered_data[filter_col].dtype == 'object':
                filtered_data = filtered_data[filtered_data[filter_col] == filter_val]
            else:
                filtered_data = filtered_data[filtered_data[filter_col] == float(filter_val)]
        elif filter_op == "!=":
            if filtered_data[filter_col].dtype == 'object':
                filtered_data = filtered_data[filtered_data[filter_col] != filter_val]
            else:
                filtered_data = filtered_data[filtered_data[filter_col] != float(filter_val)]
    except Exception as e:
        st.warning(f"Invalid filter value: {filter_val} for {filter_col}")

# Show filtered audience size prominently
st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 20px 0;">
    <h3 style="color: #667EEA; margin: 0;">Filtered Audience Size</h3>
    <h2 style="color: #1A202C; margin: 5px 0 0 0;">{len(filtered_data):,} users</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Pivot table section
st.markdown('<h2 class="sub-header">Interactive Pivot Analysis</h2>', unsafe_allow_html=True)

# Metrics Selection (compact, above table)
metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    metric = st.selectbox(
        "Primary Metric",
        options=metrics,
        index=0,
        key="metric_select",
        help="This metric will be calculated for each cell in the pivot table"
    )

with metric_col2:
    secondary_metric = st.selectbox(
        "Secondary Metric (optional)",
        options=["None"] + metrics,
        index=0,
        key="secondary_metric_select",
        help="This metric will be shown in brackets alongside the primary metric"
    )

# Y-Axis Selection (above table area)
y_col1, y_col2 = st.columns([3, 2])

with y_col1:
    y_axis = st.selectbox(
        "📈 Columns (Y-Axis)",
        options=all_dimensions,
        index=1,
        key="y_axis_select",
        help="This dimension will appear as columns in your pivot table"
    )

with y_col2:
    y_bucket_type = st.selectbox(
        f"Y-Axis Bucketing",
        options=st.session_state.pivot_engine.get_bucket_options(y_axis),
        key=f"y_bucket_{y_axis}"
    )
    
    if y_bucket_type == 'Custom Buckets':
        y_custom_ranges = st.text_input(
            f"Custom ranges",
            placeholder="e.g., 0,25,50,75,100",
            key=f"y_custom_{y_axis}"
        )
    else:
        y_custom_ranges = None

# Create table unit with X-axis controls aligned to table start
table_col1, table_col2 = st.columns([1, 4])

with table_col1:
    # X-axis controls aligned with table start
    x_axis = st.selectbox(
        "📊 Rows (X-Axis)",
        options=all_dimensions,
        index=0,
        key="x_axis_select",
        help="This dimension will appear as rows in your pivot table"
    )
    
    x_bucket_type = st.selectbox(
        f"X-Axis Bucketing",
        options=st.session_state.pivot_engine.get_bucket_options(x_axis),
        key=f"x_bucket_{x_axis}"
    )
    
    if x_bucket_type == 'Custom Buckets':
        x_custom_ranges = st.text_input(
            f"Custom ranges",
            placeholder="e.g., 0,25,50,75,100",
            key=f"x_custom_{x_axis}"
        )
    else:
        x_custom_ranges = None

with table_col2:
    
    # Generate pivot table with secondary metrics support
    pivot_data = st.session_state.pivot_engine.create_pivot_table(
        filtered_data, x_axis, y_axis, metric, x_bucket_type, y_bucket_type, x_custom_ranges, y_custom_ranges
    )
    
    # Store original pivot data for calculations
    original_pivot_data = pivot_data.copy()
    
    # Handle secondary metrics
    if secondary_metric != "None":
        secondary_pivot_data = st.session_state.pivot_engine.create_pivot_table(
            filtered_data, x_axis, y_axis, secondary_metric, x_bucket_type, y_bucket_type, x_custom_ranges, y_custom_ranges
        )
    else:
        secondary_pivot_data = None
    
    # Default display format (will be controlled by selector below)
    display_format = st.session_state.get("display_format", "values")
    
    # Calculate display data based on format
    if display_format == "values":
        display_data = pivot_data.copy()
    elif display_format == "% of rows":
        display_data = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100
        display_data = display_data.round(1)
    elif display_format == "% of columns":
        display_data = pivot_data.div(pivot_data.sum(axis=0), axis=1) * 100
        display_data = display_data.round(1)
    elif display_format == "% of total":
        total_sum = pivot_data.sum().sum()
        display_data = (pivot_data / total_sum) * 100
        display_data = display_data.round(1)
    
    # For now, skip totals to avoid Arrow serialization issues
    # Will add back once the basic layout is working
    display_data = display_data.astype(float)  # Ensure numeric type
    
    # Handle secondary metrics display
    if secondary_metric != "None":
        # Apply same formatting to secondary data
        if display_format == "values":
            secondary_display_data = secondary_pivot_data.copy()
        elif display_format == "% of rows":
            secondary_display_data = secondary_pivot_data.div(secondary_pivot_data.sum(axis=1), axis=0) * 100
            secondary_display_data = secondary_display_data.round(1)
        elif display_format == "% of columns":
            secondary_display_data = secondary_pivot_data.div(secondary_pivot_data.sum(axis=0), axis=1) * 100
            secondary_display_data = secondary_display_data.round(1)
        elif display_format == "% of total":
            secondary_total_sum = secondary_pivot_data.sum().sum()
            secondary_display_data = (secondary_pivot_data / secondary_total_sum) * 100
            secondary_display_data = secondary_display_data.round(1)
        
        # For now, skip totals to avoid Arrow serialization issues
        secondary_display_data = secondary_display_data.astype(float)
        
        # Combine primary and secondary metrics
        combined_data = display_data.copy().astype(str)
        for idx in combined_data.index:
            for col in combined_data.columns:
                primary_val = display_data.loc[idx, col]
                secondary_val = secondary_display_data.loc[idx, col]
                if display_format == "values":
                    combined_data.loc[idx, col] = f"{primary_val} ({secondary_val})"
                else:
                    combined_data.loc[idx, col] = f"{primary_val}% ({secondary_val}%)"
        
        display_data = combined_data
    
    # Display pivot table
    st.dataframe(
        display_data,
        use_container_width=True,
        height=400
    )
    
    # Add minimal display format selector below table on the right
    _, format_col = st.columns([3, 1])
    with format_col:
        st.selectbox(
            "Show:",
            options=["values", "% of rows", "% of columns", "% of total"],
            index=0,
            key="display_format"
        )

# Visualization (only for primary metric)
if secondary_metric == "None":
    st.markdown("### Heatmap Visualization")
    fig = px.imshow(
        pivot_data.values,
        labels=dict(x=y_axis.replace('_', ' ').title(), y=x_axis.replace('_', ' ').title(), color=metric),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale="Blues",
        title=f"{metric} by {x_axis.replace('_', ' ').title()} and {y_axis.replace('_', ' ').title()}"
    )
    fig.update_layout(
        title_font_color="#667EEA",
        title_font_size=16,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Heatmap visualization is not available when using secondary metrics. The table above shows both primary and secondary metrics.")

# Comparison section
if comparison_enabled and selected_comparison:
    st.markdown("---")
    st.markdown('<h2 class="sub-header">Audience Comparison</h2>', unsafe_allow_html=True)
    
    # Get comparison data
    comparison_data = st.session_state.data_generator.filter_by_audience(
        st.session_state.user_data, 
        selected_comparison
    )
    
    # Create comparison pivot table
    comparison_pivot = st.session_state.pivot_engine.create_pivot_table(
        comparison_data, x_axis, y_axis, metric, x_bucket_type, y_bucket_type, x_custom_ranges, y_custom_ranges
    )
    
    # Display comparison
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        st.markdown(f"#### {selected_audience}")
        st.dataframe(pivot_data, use_container_width=True)
    
    with comp_col2:
        st.markdown(f"#### {selected_comparison}")
        st.dataframe(comparison_pivot, use_container_width=True)
    
    # Difference heatmap
    st.markdown("#### Difference Analysis")
    if pivot_data.shape == comparison_pivot.shape:
        diff_data = pivot_data - comparison_pivot
        fig_diff = px.imshow(
            diff_data.values,
            labels=dict(x=y_axis.replace('_', ' ').title(), y=x_axis.replace('_', ' ').title(), color=f"{metric} Difference"),
            x=diff_data.columns,
            y=diff_data.index,
            color_continuous_scale="RdBu",
            title=f"Difference in {metric} ({selected_audience} - {selected_comparison})"
        )
        fig_diff.update_layout(
            title_font_color="#667EEA",
            title_font_size=16,
            height=400
        )
        st.plotly_chart(fig_diff, use_container_width=True)
    else:
        st.info("Pivot tables have different dimensions. Cannot calculate difference.")

# Export functionality
st.markdown("---")
st.markdown('<h2 class="sub-header">Export Data</h2>', unsafe_allow_html=True)

export_col1, export_col2 = st.columns(2)

with export_col1:
    if st.button("📊 Export Pivot Table as CSV"):
        csv = pivot_data.to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"pivot_table_{selected_audience}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with export_col2:
    if st.button("📈 Export Raw Data as CSV"):
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download Raw Data",
            data=csv,
            file_name=f"user_data_{selected_audience}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #764BA2; font-size: 0.9rem;">User Segmentation & Analytics Tool - Built for Retention Marketing</p>',
    unsafe_allow_html=True
)
