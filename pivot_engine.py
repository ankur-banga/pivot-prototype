import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PivotEngine:
    def __init__(self):
        self.bucket_definitions = {
            'age': {
                'Young/Old': lambda x: pd.cut(x, bins=[0, 35, 100], labels=['Young (18-35)', 'Mature (35+)']),
                'Three Groups': lambda x: pd.cut(x, bins=[0, 25, 45, 100], labels=['18-25', '26-45', '46+']),
                'Fine Grained': lambda x: pd.cut(x, bins=[0, 20, 25, 35, 50, 100], labels=['18-20', '21-25', '26-35', '36-50', '50+'])
            },
            'days_since_signup': {
                'New/Established': lambda x: pd.cut(x, bins=[0, 90, 10000], labels=['New (0-90 days)', 'Established (90+ days)']),
                'Quarterly': lambda x: pd.cut(x, bins=[0, 90, 180, 365, 10000], labels=['0-3 months', '3-6 months', '6-12 months', '1+ years']),
                'Monthly': lambda x: pd.cut(x, bins=[0, 30, 60, 90, 180, 365, 10000], labels=['0-1 month', '1-2 months', '2-3 months', '3-6 months', '6-12 months', '1+ years'])
            },
            'days_since_last_purchase': {
                'Recent/Lapsed': lambda x: pd.cut(x, bins=[0, 30, 10000], labels=['Recent (0-30 days)', 'Lapsed (30+ days)']),
                'Recency Groups': lambda x: pd.cut(x, bins=[0, 7, 30, 90, 10000], labels=['0-7 days', '8-30 days', '31-90 days', '90+ days']),
                'Weekly': lambda x: pd.cut(x, bins=[0, 7, 14, 21, 30, 60, 90, 10000], labels=['0-1 week', '1-2 weeks', '2-3 weeks', '3-4 weeks', '1-2 months', '2-3 months', '3+ months'])
            },
            'signup_date': {
                'By Year': lambda x: pd.to_datetime(x).dt.year.astype(str),
                'By Month': lambda x: pd.to_datetime(x).dt.to_period('M').astype(str),
                'By Quarter': lambda x: pd.to_datetime(x).dt.to_period('Q').astype(str),
                'By Week': lambda x: pd.to_datetime(x).dt.to_period('W').astype(str)
            },
            'total_revenue': {
                'Low/Medium/High': lambda x: pd.cut(x, bins=[0, 100, 500, float('inf')], labels=['Low (<$100)', 'Medium ($100-500)', 'High ($500+)']),
                'Quartiles': lambda x: pd.qcut(x, q=4, labels=['Q1 (Bottom 25%)', 'Q2', 'Q3', 'Q4 (Top 25%)']),
                'Detailed': lambda x: pd.cut(x, bins=[0, 50, 100, 250, 500, 1000, float('inf')], labels=['<$50', '$50-100', '$100-250', '$250-500', '$500-1000', '$1000+'])
            },
            'ltv': {
                'Low/Medium/High': lambda x: pd.cut(x, bins=[0, 200, 1000, float('inf')], labels=['Low (<$200)', 'Medium ($200-1000)', 'High ($1000+)']),
                'Quartiles': lambda x: pd.qcut(x, q=4, labels=['Q1 (Bottom 25%)', 'Q2', 'Q3', 'Q4 (Top 25%)']),
                'Detailed': lambda x: pd.cut(x, bins=[0, 100, 250, 500, 1000, 2000, float('inf')], labels=['<$100', '$100-250', '$250-500', '$500-1000', '$1000-2000', '$2000+'])
            },
            'total_orders': {
                'Low/Medium/High': lambda x: pd.cut(x, bins=[0, 2, 10, float('inf')], labels=['Low (0-2)', 'Medium (3-10)', 'High (10+)']),
                'Detailed': lambda x: pd.cut(x, bins=[0, 1, 3, 5, 10, 20, float('inf')], labels=['0-1', '2-3', '4-5', '6-10', '11-20', '20+'])
            }
        }
    
    def get_available_dimensions(self):
        """Get list of available dimensions for pivot analysis"""
        return [
            'age',
            'gender',
            'country',
            'device_type',
            'acquisition_channel',
            'loyalty_tier',
            'product_category_preference',
            'price_sensitivity',
            'days_since_signup',
            'days_since_last_purchase',
            'signup_date',
            'signup_timestamp',
            'total_orders',
            'total_revenue',
            'ltv',
            'average_order_value',
            'email_subscriber',
            'seasonal_shopper',
            'payment_method',
            'shipping_preference',
            'churn_risk_score',
            'nps_score',
            'is_retained',
            'is_churned'
        ]
    
    def get_bucket_options(self, dimension):
        """Get bucketing options for a given dimension"""
        if dimension in self.bucket_definitions:
            return ['No Bucketing'] + list(self.bucket_definitions[dimension].keys()) + ['Custom Buckets']
        return ['No Bucketing', 'Custom Buckets']
    
    def create_custom_buckets(self, series, bucket_ranges, bucket_labels=None):
        """Create custom buckets from user-defined ranges"""
        try:
            # Handle numeric buckets
            if pd.api.types.is_numeric_dtype(series):
                if bucket_labels and len(bucket_labels) == len(bucket_ranges) - 1:
                    return pd.cut(series, bins=bucket_ranges, labels=bucket_labels)
                else:
                    return pd.cut(series, bins=bucket_ranges)
            # Handle categorical buckets
            else:
                # For categorical data, create groups based on provided mapping
                if isinstance(bucket_ranges, dict):
                    return series.map(bucket_ranges)
                else:
                    return series
        except Exception as e:
            return series  # Return original if bucketing fails
    
    def apply_bucketing(self, series, dimension, bucket_type, custom_ranges=None):
        """Apply bucketing to a series"""
        if bucket_type == 'No Bucketing' or bucket_type is None:
            return series
        
        if bucket_type == 'Custom Buckets' and custom_ranges:
            return self._apply_custom_bucketing(series, custom_ranges)
        
        if dimension in self.bucket_definitions and bucket_type in self.bucket_definitions[dimension]:
            return self.bucket_definitions[dimension][bucket_type](series)
        
        # Handle special cases for numeric dimensions
        if dimension == 'churn_risk_score':
            if bucket_type == 'Risk Levels':
                return pd.cut(series, bins=[0, 0.3, 0.7, 1.0], labels=['Low Risk', 'Medium Risk', 'High Risk'])
        
        elif dimension == 'nps_score':
            if bucket_type == 'NPS Categories':
                return pd.cut(series, bins=[0, 6, 8, 10], labels=['Detractors (0-6)', 'Passives (7-8)', 'Promoters (9-10)'])
        
        return series
    
    def _apply_custom_bucketing(self, series, custom_ranges):
        """Apply custom bucketing based on user input"""
        try:
            # Parse custom ranges
            if ',' in custom_ranges:
                ranges = [x.strip() for x in custom_ranges.split(',')]
                
                # Check if numeric ranges
                try:
                    numeric_ranges = [float(x) for x in ranges]
                    if len(numeric_ranges) >= 2:
                        return pd.cut(series, bins=numeric_ranges, include_lowest=True)
                except ValueError:
                    # Handle categorical ranges
                    if len(ranges) > 1:
                        # Create equal-sized bins with custom labels
                        return pd.qcut(series, q=len(ranges), labels=ranges, duplicates='drop')
            
            return series
        except Exception:
            return series
    
    def create_pivot_table(self, df, x_axis, y_axis, metric, x_bucket_type=None, y_bucket_type=None, x_custom_ranges=None, y_custom_ranges=None):
        """Create pivot table with dynamic bucketing"""
        # Create a copy to avoid modifying original data
        pivot_df = df.copy()
        
        # Apply bucketing
        x_data = self.apply_bucketing(pivot_df[x_axis], x_axis, x_bucket_type, x_custom_ranges)
        y_data = self.apply_bucketing(pivot_df[y_axis], y_axis, y_bucket_type, y_custom_ranges)
        
        # Create pivot table based on metric (without margins to avoid mixed types)
        if metric == "Count":
            pivot_table = pd.crosstab(x_data, y_data)
        
        elif metric == "Total Revenue":
            pivot_table = pd.crosstab(
                x_data, y_data, 
                values=pivot_df['total_revenue'], 
                aggfunc='sum'
            ).round(2)
        
        elif metric == "Avg LTV":
            pivot_table = pd.crosstab(
                x_data, y_data, 
                values=pivot_df['ltv'], 
                aggfunc='mean'
            ).round(2)
        
        elif metric == "Retention Rate":
            pivot_table = pd.crosstab(
                x_data, y_data, 
                values=pivot_df['is_retained'], 
                aggfunc='mean'
            ).round(3) * 100  # Convert to percentage
        
        elif metric == "Avg AOV":
            pivot_table = pd.crosstab(
                x_data, y_data, 
                values=pivot_df['average_order_value'], 
                aggfunc='mean'
            ).round(2)
        
        elif metric == "Total Orders":
            pivot_table = pd.crosstab(
                x_data, y_data, 
                values=pivot_df['total_orders'], 
                aggfunc='sum'
            )
        
        # Fill NaN values with 0
        pivot_table = pivot_table.fillna(0)
        
        return pivot_table
    
    def calculate_segment_insights(self, df, segment_col, metric_col):
        """Calculate insights for a specific segment"""
        insights = {}
        
        # Group by segment
        grouped = df.groupby(segment_col)
        
        insights['segment_sizes'] = grouped.size()
        insights['metric_means'] = grouped[metric_col].mean()
        insights['metric_medians'] = grouped[metric_col].median()
        insights['metric_stds'] = grouped[metric_col].std()
        
        # Calculate percentiles
        insights['percentile_25'] = grouped[metric_col].quantile(0.25)
        insights['percentile_75'] = grouped[metric_col].quantile(0.75)
        
        return insights
    
    def compare_segments(self, df1, df2, x_axis, y_axis, metric, x_bucket_type=None, y_bucket_type=None):
        """Compare two segments and return difference analysis"""
        pivot1 = self.create_pivot_table(df1, x_axis, y_axis, metric, x_bucket_type, y_bucket_type)
        pivot2 = self.create_pivot_table(df2, x_axis, y_axis, metric, x_bucket_type, y_bucket_type)
        
        # Align indices and columns
        all_index = pivot1.index.union(pivot2.index)
        all_columns = pivot1.columns.union(pivot2.columns)
        
        pivot1 = pivot1.reindex(index=all_index, columns=all_columns, fill_value=0)
        pivot2 = pivot2.reindex(index=all_index, columns=all_columns, fill_value=0)
        
        # Calculate differences
        difference = pivot1 - pivot2
        percentage_diff = ((pivot1 - pivot2) / pivot2 * 100).replace([np.inf, -np.inf], 0)
        
        return {
            'absolute_difference': difference,
            'percentage_difference': percentage_diff,
            'pivot1': pivot1,
            'pivot2': pivot2
        }
    
    def get_time_based_metrics(self, df, date_column, metric_column, time_periods):
        """Calculate metrics for different time periods"""
        results = {}
        
        for period_name, days in time_periods.items():
            cutoff_date = datetime.now() - timedelta(days=days)
            period_df = df[df[date_column] >= cutoff_date]
            
            results[period_name] = {
                'count': len(period_df),
                'metric_mean': period_df[metric_column].mean(),
                'metric_sum': period_df[metric_column].sum(),
                'metric_median': period_df[metric_column].median()
            }
        
        return results
