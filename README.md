# User Segmentation & Analytics Tool

## Overview

This is a Streamlit-based web application for user segmentation and analytics, designed for ecommerce businesses. The application provides data visualization capabilities through interactive dashboards, allowing users to analyze customer behavior, segment users, and perform pivot analysis on generated user data.

## System Architecture

The application follows a modular architecture with three main components:

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Visualization**: Plotly (Express and Graph Objects) for interactive charts and dashboards
- **Layout**: Wide layout with expandable sidebar for controls
- **Styling**: Custom CSS embedded in the main application

### Backend Architecture
- **Data Generation**: Faker library for creating realistic synthetic ecommerce data
- **Data Processing**: Pandas and NumPy for data manipulation and analysis
- **Analytics Engine**: Custom PivotEngine class for segmentation and bucketing operations

### Data Layer
- **Storage**: In-memory data processing (no persistent database)
- **Data Generation**: On-demand synthetic data creation with configurable parameters
- **Format**: Pandas DataFrames for all data operations

## Key Components

### 1. Main Application (app.py)
- Streamlit web interface with custom styling
- Dashboard layout with metrics and visualizations
- Integration with data generation and pivot analysis modules
- User interaction controls for filtering and segmentation

### 2. Data Generator (data_generator.py)
- Generates realistic ecommerce user data with 20-30 properties
- Uses Faker library for realistic names, emails, and addresses
- Creates behavioral data including purchase history, engagement metrics, and customer lifetime value
- Implements seeded random generation for reproducible datasets

### 3. Pivot Engine (pivot_engine.py)
- Handles user segmentation and bucketing operations
- Provides flexible dimension analysis with configurable bucket definitions
- Supports multiple bucketing strategies (e.g., age groups, recency segments)
- Enables pivot table generation for multi-dimensional analysis

## Data Flow

1. **Data Generation**: DataGenerator creates synthetic user data with realistic ecommerce properties
2. **Data Processing**: Raw data is processed and enriched with calculated metrics
3. **Segmentation**: PivotEngine applies bucketing logic to create user segments
4. **Visualization**: Plotly generates interactive charts and dashboards
5. **User Interaction**: Streamlit interface allows real-time filtering and analysis

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualization library
- **faker**: Synthetic data generation

### Data Processing
- **datetime**: Date and time handling
- **json**: JSON data processing
- **random**: Random number generation for data synthesis

## Deployment Strategy

The application is designed for:
- **Local Development**: Direct execution via `streamlit run app.py`
- **Cloud Deployment**: Compatible with Streamlit Cloud, Heroku, or similar platforms
- **Container Deployment**: Can be containerized using Docker
- **Replit Deployment**: Optimized for Replit's Python environment

### Key Considerations
- No persistent database required (uses in-memory processing)
- Lightweight architecture suitable for demo and development environments
- Synthetic data generation eliminates need for external data sources
- Self-contained application with minimal external dependencies

## Changelog

- July 08, 2025: Initial setup with basic pivot table functionality
- July 08, 2025: Enhanced interactive analytics experience with:
  - More intuitive dimension selection with data type info
  - Custom bucketing capabilities for all dimensions
  - Advanced filtering for complex analysis (age>25 AND LTV<30)
  - Signup date bucketing by year/month/quarter/week
  - Additional metrics (AOV, Total Orders)
  - Visual improvements to pivot table configuration

## User Preferences

Preferred communication style: Simple, everyday language.