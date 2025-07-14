import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

class DataGenerator:
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)  # For reproducible data
        np.random.seed(42)
        random.seed(42)
        
    def generate_user_data(self, num_users=5000):
        """Generate realistic ecommerce user data with 20-30 properties"""
        
        # Base user properties
        data = {
            'user_id': [f'user_{i:06d}' for i in range(num_users)],
            'email': [self.fake.email() for _ in range(num_users)],
            'first_name': [self.fake.first_name() for _ in range(num_users)],
            'last_name': [self.fake.last_name() for _ in range(num_users)],
        }
        
        # Demographics
        data['age'] = np.random.normal(35, 12, num_users).clip(18, 80).astype(int)
        data['gender'] = np.random.choice(['Male', 'Female', 'Other'], num_users, p=[0.45, 0.52, 0.03])
        data['country'] = np.random.choice(['US', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Spain', 'Italy'], 
                                         num_users, p=[0.4, 0.15, 0.12, 0.08, 0.08, 0.07, 0.05, 0.05])
        data['city'] = [self.fake.city() for _ in range(num_users)]
        data['state'] = [self.fake.state_abbr() for _ in range(num_users)]
        data['zip_code'] = [self.fake.zipcode() for _ in range(num_users)]
        
        # Signup and engagement data
        start_date = datetime.now() - timedelta(days=1095)  # 3 years ago
        data['signup_date'] = [start_date + timedelta(days=random.randint(0, 1095)) for _ in range(num_users)]
        data['days_since_signup'] = [(datetime.now() - signup_date).days for signup_date in data['signup_date']]
        
        # Add signup timestamp as string for display
        data['signup_timestamp'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in data['signup_date']]
        
        # Purchase behavior
        data['total_orders'] = np.random.poisson(8, num_users).clip(0, 50)
        data['total_revenue'] = np.random.lognormal(4.5, 1.2, num_users).clip(0, 10000)
        data['average_order_value'] = [rev / max(orders, 1) for rev, orders in zip(data['total_revenue'], data['total_orders'])]
        
        # Customer lifetime value
        data['ltv'] = data['total_revenue'] * np.random.uniform(1.2, 2.5, num_users)
        
        # Recency data
        data['last_purchase_date'] = [
            signup_date + timedelta(days=random.randint(0, min(365, (datetime.now() - signup_date).days)))
            for signup_date in data['signup_date']
        ]
        data['days_since_last_purchase'] = [(datetime.now() - last_purchase).days for last_purchase in data['last_purchase_date']]
        
        # Frequency metrics
        data['purchase_frequency'] = np.random.exponential(30, num_users).clip(1, 365)  # days between purchases
        data['seasonal_shopper'] = np.random.choice(['Yes', 'No'], num_users, p=[0.3, 0.7])
        
        # Channel and device data
        data['acquisition_channel'] = np.random.choice(['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Direct', 'Referral'], 
                                                     num_users, p=[0.25, 0.2, 0.15, 0.15, 0.15, 0.1])
        data['device_type'] = np.random.choice(['Desktop', 'Mobile', 'Tablet'], num_users, p=[0.4, 0.55, 0.05])
        data['preferred_os'] = np.random.choice(['iOS', 'Android', 'Windows', 'Mac'], num_users, p=[0.3, 0.35, 0.2, 0.15])
        
        # Engagement metrics
        data['email_opens_l30d'] = np.random.poisson(3, num_users).clip(0, 20)
        data['email_clicks_l30d'] = np.random.poisson(1, num_users).clip(0, 10)
        data['website_visits_l30d'] = np.random.poisson(5, num_users).clip(0, 30)
        data['app_sessions_l30d'] = np.random.poisson(2, num_users).clip(0, 15)
        
        # Behavioral segments
        data['product_category_preference'] = np.random.choice(['Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 'Beauty'], 
                                                              num_users, p=[0.2, 0.25, 0.15, 0.15, 0.1, 0.15])
        data['price_sensitivity'] = np.random.choice(['Low', 'Medium', 'High'], num_users, p=[0.3, 0.5, 0.2])
        data['loyalty_tier'] = np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], num_users, p=[0.4, 0.3, 0.2, 0.1])
        
        # Risk indicators
        data['churn_risk_score'] = np.random.beta(2, 5, num_users)  # Skewed toward lower risk
        data['is_churned'] = (np.array(data['days_since_last_purchase']) > 90) & (data['churn_risk_score'] > 0.6)
        data['is_retained'] = ~data['is_churned']
        
        # Communication preferences
        data['email_subscriber'] = np.random.choice([True, False], num_users, p=[0.8, 0.2])
        data['sms_subscriber'] = np.random.choice([True, False], num_users, p=[0.4, 0.6])
        data['push_notifications'] = np.random.choice([True, False], num_users, p=[0.6, 0.4])
        
        # Customer service
        data['support_tickets_l30d'] = np.random.poisson(0.5, num_users).clip(0, 5)
        data['nps_score'] = np.random.choice(range(0, 11), num_users, p=[0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.15, 0.15, 0.15, 0.1])
        
        # Social and referral
        data['social_media_follower'] = np.random.choice([True, False], num_users, p=[0.3, 0.7])
        data['referrals_made'] = np.random.poisson(0.8, num_users).clip(0, 10)
        
        # Payment and shipping
        data['payment_method'] = np.random.choice(['Credit Card', 'PayPal', 'Apple Pay', 'Google Pay', 'Bank Transfer'], 
                                                 num_users, p=[0.5, 0.2, 0.15, 0.1, 0.05])
        data['shipping_preference'] = np.random.choice(['Standard', 'Express', 'Overnight'], num_users, p=[0.7, 0.25, 0.05])
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Convert dates to datetime
        df['signup_date'] = pd.to_datetime(df['signup_date'])
        df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
        
        return df
    
    def get_audience_definitions(self):
        """Define various audience segments for analysis"""
        return {
            'All Users': {},
            'High Value Customers': {'ltv': ('>', 1000)},
            'Recent Signups': {'days_since_signup': ('<', 30)},
            'Churned Users': {'is_churned': ('==', True)},
            'Mobile Users': {'device_type': ('==', 'Mobile')},
            'Email Subscribers': {'email_subscriber': ('==', True)},
            'High AOV Customers': {'average_order_value': ('>', 100)},
            'Frequent Buyers': {'total_orders': ('>', 10)},
            'Gold+ Members': {'loyalty_tier': ('in', ['Gold', 'Platinum'])},
            'At-Risk Customers': {'churn_risk_score': ('>', 0.7)},
            'Social Followers': {'social_media_follower': ('==', True)},
            'High Engagement': {'website_visits_l30d': ('>', 10)},
            'Recent Purchasers': {'days_since_last_purchase': ('<', 30)},
            'High NPS': {'nps_score': ('>', 8)},
            'Fashion Lovers': {'product_category_preference': ('==', 'Fashion')},
            'Price Sensitive': {'price_sensitivity': ('==', 'High')},
            'Young Adults': {'age': ('between', 18, 35)},
            'US Customers': {'country': ('==', 'US')},
            'New Customers': {'total_orders': ('<=', 2)},
            'VIP Customers': {'loyalty_tier': ('==', 'Platinum')}
        }
    
    def filter_by_audience(self, df, audience_name):
        """Filter dataframe by audience definition"""
        audience_def = self.get_audience_definitions()[audience_name]
        
        if not audience_def:  # All Users
            return df
        
        filtered_df = df.copy()
        
        for column, (operator, value) in audience_def.items():
            if operator == '>':
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == '<':
                filtered_df = filtered_df[filtered_df[column] < value]
            elif operator == '>=':
                filtered_df = filtered_df[filtered_df[column] >= value]
            elif operator == '<=':
                filtered_df = filtered_df[filtered_df[column] <= value]
            elif operator == '==':
                filtered_df = filtered_df[filtered_df[column] == value]
            elif operator == '!=':
                filtered_df = filtered_df[filtered_df[column] != value]
            elif operator == 'in':
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            elif operator == 'between':
                filtered_df = filtered_df[
                    (filtered_df[column] >= value[0]) & 
                    (filtered_df[column] <= value[1])
                ]
        
        return filtered_df
