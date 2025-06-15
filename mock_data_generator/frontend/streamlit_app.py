# import pandas as pd
# import requests
# import streamlit as st
# import io
# from typing import Optional, List, Dict

# # Configure page
# st.set_page_config(
#     page_title="Mock Data Generator",
#     page_icon="🎲",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # API Base URL
# API_BASE_URL = "http://localhost:8000"

# # Cache API responses to reduce lag
# @st.cache_data(ttl=300)  # Cache for 5 minutes
# def load_topics():
#     """Load available topics from API"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/topics", timeout=2)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return []
#     except:
#         return []

# @st.cache_data(ttl=300)  # Cache for 5 minutes
# def load_formats():
#     """Load supported formats from API"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/formats", timeout=2)
#         if response.status_code == 200:
#             return response.json()["formats"]
#         else:
#             return ["JSON", "CSV", "XML", "YAML"]
#     except:
#         return ["JSON", "CSV", "XML", "YAML"]

# @st.cache_data(ttl=60)  # Cache API health check for 1 minute
# def check_api_health():
#     """Check if API is available"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/", timeout=2)
#         return response.status_code == 200
#     except:
#         return False

# class MockDataGeneratorApp:
#     def __init__(self):
#         # Load data only once
#         if 'topics_loaded' not in st.session_state:
#             st.session_state.topics = load_topics()
#             st.session_state.formats = load_formats()
#             st.session_state.topics_loaded = True
        
#         self.topics = st.session_state.topics
#         self.formats = st.session_state.formats
    
#     def generate_data(self, topic: str, format_type: str, num_records: int, custom_fields: list = None, seed: int = None):
#         """Generate data via API"""
#         payload = {
#             "topic": topic,
#             "format": format_type,
#             "num_records": num_records,
#             "custom_fields": custom_fields,
#             "seed": seed
#         }
        
#         try:
#             response = requests.post(f"{API_BASE_URL}/generate", json=payload, timeout=10)
#             if response.status_code == 200:
#                 return response.json()
#             else:
#                 st.error(f"Error: {response.text}")
#                 return None
#         except Exception as e:
#             st.error(f"Connection error: {str(e)}")
#             return None
    
#     def download_data(self, topic: str, format_type: str, num_records: int, custom_fields: list = None, seed: int = None):
#         """Download data via API"""
#         payload = {
#             "topic": topic,
#             "format": format_type,
#             "num_records": num_records,
#             "custom_fields": custom_fields,
#             "seed": seed
#         }
        
#         try:
#             response = requests.post(f"{API_BASE_URL}/download", json=payload, timeout=10)
#             if response.status_code == 200:
#                 return response.content, response.headers.get("Content-Disposition", "")
#             else:
#                 return None, None
#         except Exception as e:
#             st.error(f"Download error: {str(e)}")
#             return None, None
    
#     def render_sidebar(self):
#         """Render sidebar with options"""
#         st.sidebar.header("🎲 Mock Data Generator")
#         st.sidebar.markdown("---")
        
#         # Topic selection
#         st.sidebar.subheader("📋 Select Topic")
        
#         # Add custom topic option
#         topic_options = [topic["name"] for topic in self.topics] + ["custom"]
        
#         selected_topic = st.sidebar.selectbox(
#             "Choose a topic:",
#             options=topic_options,
#             format_func=lambda x: "Custom Topic" if x == "custom" else x.title().replace("_", " "),
#             key="topic_select"
#         )
        
#         # Show topic description (only when topic changes)
#         if selected_topic != "custom":
#             topic_info = next((t for t in self.topics if t["name"] == selected_topic), None)
#             if topic_info:
#                 st.sidebar.info(f"**Description:** {topic_info['description']}")
#                 with st.sidebar.expander("📝 Available Fields"):
#                     for field in topic_info['fields']:
#                         st.write(f"• {field}")
        
#         # Custom fields for custom topic
#         custom_fields = None
#         if selected_topic == "custom":
#             st.sidebar.subheader("🛠️ Custom Fields")
#             custom_fields_input = st.sidebar.text_area(
#                 "Enter field names (one per line):",
#                 value="name\nemail\nage\ncategory\ndate\nstatus\ndescription",
#                 height=150,
#                 key="custom_fields_input"
#             )
#             custom_fields = [field.strip() for field in custom_fields_input.split('\n') if field.strip()]
            
#             if custom_fields:
#                 st.sidebar.success(f"✅ {len(custom_fields)} custom fields defined")
        
#         st.sidebar.markdown("---")
        
#         # Format selection
#         st.sidebar.subheader("📁 Select Format")
#         selected_format = st.sidebar.selectbox(
#             "Choose output format:",
#             options=self.formats,
#             key="format_select"
#         )
        
#         # Number of records
#         st.sidebar.subheader("🔢 Records")
#         num_records = st.sidebar.slider(
#             "Number of records:",
#             min_value=1,
#             max_value=1000,
#             value=100,
#             step=10,
#             key="num_records_slider"
#         )
        
#         # Advanced options
#         with st.sidebar.expander("⚙️ Advanced Options"):
#             seed = st.number_input(
#                 "Seed (for reproducible data):",
#                 min_value=0,
#                 max_value=99999,
#                 value=42,
#                 help="Use the same seed to generate identical data",
#                 key="seed_input"
#             )
            
#             use_seed = st.checkbox("Use seed", value=False, key="use_seed_checkbox")
        
#         return selected_topic, selected_format, num_records, custom_fields, seed if use_seed else None
    
#     def render_data_preview(self, data_result, format_type):
#         """Render data preview efficiently"""
#         # Data preview
#         st.subheader("📊 Data Preview")
        
#         # Show preview based on format
#         if format_type in ["JSON", "YAML", "TOML", "XML"]:
#             st.code(data_result["data"], language=format_type.lower())
        
#         elif format_type in ["CSV", "TSV"]:
#             # Parse CSV for table display
#             try:
#                 csv_data = pd.read_csv(io.StringIO(data_result["data"]))
#                 st.dataframe(csv_data, use_container_width=True, height=400)
                
#                 # Show raw CSV in expandable section
#                 with st.expander("View Raw CSV"):
#                     st.code(data_result["data"], language="csv")
                    
#                 # Data statistics
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.subheader("📈 Data Statistics")
#                     st.write(f"**Rows:** {len(csv_data)}")
#                     st.write(f"**Columns:** {len(csv_data.columns)}")
#                     st.write(f"**Size:** {len(data_result['data'])} characters")
                
#                 with col2:
#                     st.subheader("🏷️ Column Names")
#                     for col in csv_data.columns:
#                         st.write(f"• {col}")
#             except Exception as e:
#                 st.error(f"Error parsing CSV: {str(e)}")
#                 st.code(data_result["data"], language="csv")
        
#         else:
#             # For other formats, show as code
#             st.code(data_result["data"], language="text")
    
#     def render_main_content(self, topic, format_type, num_records, custom_fields, seed):
#         """Render main content area"""
#         st.title("🎲 Mock Data Generator")
#         st.markdown("Generate realistic fake data in multiple formats for testing and development purposes.")
        
#         # Configuration summary
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.metric("Topic", topic.title().replace("_", " ") if topic != "custom" else "Custom")
#         with col2:
#             st.metric("Format", format_type)
#         with col3:
#             st.metric("Records", num_records)
#         with col4:
#             if custom_fields:
#                 st.metric("Custom Fields", len(custom_fields))
#             else:
#                 st.metric("Seed", seed if seed else "Random")
        
#         st.markdown("---")
        
#         # Generate button
#         col1, col2, col3 = st.columns([2, 1, 1])
        
#         with col1:
#             if st.button("🚀 Generate Data", type="primary", use_container_width=True, key="generate_button"):
#                 with st.spinner("Generating mock data..."):
#                     result = self.generate_data(topic, format_type, num_records, custom_fields, seed)
                    
#                     if result and result.get("success"):
#                         st.session_state.generated_data = result
#                         st.session_state.current_config = {
#                             'topic': topic,
#                             'format_type': format_type,
#                             'num_records': num_records,
#                             'custom_fields': custom_fields,
#                             'seed': seed
#                         }
#                         st.success("✅ Data generated successfully!")
#                         st.rerun()
#                     else:
#                         st.error("❌ Failed to generate data")
        
#         # Display generated data
#         if hasattr(st.session_state, 'generated_data') and st.session_state.generated_data:
#             data_result = st.session_state.generated_data
            
#             # Action buttons
#             with col2:
#                 # Copy button (just shows the data in a code block)
#                 if st.button("📋 Show Raw", use_container_width=True, key="copy_button"):
#                     st.session_state.show_raw = not st.session_state.get('show_raw', False)
            
#             with col3:
#                 # Download button
#                 if st.button("⬇️ Download", use_container_width=True, key="download_button"):
#                     with st.spinner("Preparing download..."):
#                         config = st.session_state.get('current_config', {})
#                         content, headers = self.download_data(
#                             config.get('topic', topic),
#                             config.get('format_type', format_type),
#                             config.get('num_records', num_records),
#                             config.get('custom_fields', custom_fields),
#                             config.get('seed', seed)
#                         )
                        
#                         if content:
#                             filename = data_result.get("filename", f"data.{format_type.lower()}")
                            
#                             st.download_button(
#                                 label=f"💾 Download {filename}",
#                                 data=content,
#                                 file_name=filename,
#                                 mime=data_result.get("content_type", "application/octet-stream"),
#                                 use_container_width=True,
#                                 key="download_file_button"
#                             )
            
#             st.markdown("---")
            
#             # Show raw data if requested
#             if st.session_state.get('show_raw', False):
#                 st.subheader("📄 Raw Data")
#                 st.code(data_result["data"], language=format_type.lower())
#                 st.markdown("---")
            
#             # Render data preview
#             self.render_data_preview(data_result, format_type)
    
#     def run(self):
#         """Main app runner"""
#         # Check API connection (cached)
#         if not check_api_health():
#             st.error("❌ Backend API is not running!")
#             st.info("To start the backend:")
#             st.code("cd mock-data-generator\npython run.py")
            
#             # Add a refresh button
#             if st.button("🔄 Retry Connection"):
#                 st.cache_data.clear()
#                 st.rerun()
#             return
        
#         # Render sidebar
#         topic, format_type, num_records, custom_fields, seed = self.render_sidebar()
        
#         # Render main content
#         self.render_main_content(topic, format_type, num_records, custom_fields, seed)
        
#         # Footer
#         st.markdown("---")
#         st.markdown(
#             """
#             <div style='text-align: center; color: #666;'>
#                 <p>🎲 Mock Data Generator | Built with FastAPI & Streamlit</p>
#                 <p>Generate realistic fake data for testing and development</p>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

# # Initialize session state
# if 'generated_data' not in st.session_state:
#     st.session_state.generated_data = None
# if 'current_config' not in st.session_state:
#     st.session_state.current_config = {}
# if 'show_raw' not in st.session_state:
#     st.session_state.show_raw = False

# # Run the app
# if __name__ == "__main__":
#     app = MockDataGeneratorApp()
#     app.run()

import pandas as pd
import requests
import streamlit as st
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Optional, List, Dict

# Configure page
st.set_page_config(
    page_title="Mock Data Generator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000"

# Cache API responses to reduce lag
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_topics():
    """Load available topics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/topics", timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_formats():
    """Load supported formats from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/formats", timeout=2)
        if response.status_code == 200:
            return response.json()["formats"]
        else:
            return ["JSON", "CSV", "XML", "YAML"]
    except:
        return ["JSON", "CSV", "XML", "YAML"]

@st.cache_data(ttl=60)  # Cache API health check for 1 minute
def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

class MockDataGeneratorApp:
    def __init__(self):
        # Load data only once
        if 'topics_loaded' not in st.session_state:
            st.session_state.topics = load_topics()
            st.session_state.formats = load_formats()
            st.session_state.topics_loaded = True
        
        self.topics = st.session_state.topics
        self.formats = st.session_state.formats
    
    def generate_data(self, topic: str, format_type: str, num_records: int, custom_fields: list = None, seed: int = None):
        """Generate data via API"""
        payload = {
            "topic": topic,
            "format": format_type,
            "num_records": num_records,
            "custom_fields": custom_fields,
            "seed": seed
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/generate", json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def download_data(self, topic: str, format_type: str, num_records: int, custom_fields: list = None, seed: int = None):
        """Download data via API"""
        payload = {
            "topic": topic,
            "format": format_type,
            "num_records": num_records,
            "custom_fields": custom_fields,
            "seed": seed
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/download", json=payload, timeout=10)
            if response.status_code == 200:
                return response.content, response.headers.get("Content-Disposition", "")
            else:
                return None, None
        except Exception as e:
            st.error(f"Download error: {str(e)}")
            return None, None
    
    def create_data_visualizations(self, df: pd.DataFrame):
        """Create interactive visualizations for data analysis"""
        
        # Create tabs for different visualization types
        viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(["📊 Column Analysis", "📈 Data Distribution", "🔍 Data Quality", "📋 Summary"])
        
        with viz_tab1:
            # Column type analysis
            col1, col2 = st.columns(2)
            
            with col1:
                # Column types pie chart
                column_types = df.dtypes.value_counts()
                type_mapping = {
                    'object': 'Text/Categorical',
                    'int64': 'Integer',
                    'float64': 'Decimal',
                    'bool': 'Boolean',
                    'datetime64[ns]': 'Date/Time'
                }
                
                # Map data types to more readable names
                readable_types = [type_mapping.get(str(dtype), str(dtype)) for dtype in column_types.index]
                
                fig_types = px.pie(
                    values=column_types.values,
                    names=readable_types,
                    title="📊 Column Data Types Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_types.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_types, use_container_width=True)
            
            with col2:
                # Column count bar chart
                fig_columns = go.Figure(data=[
                    go.Bar(
                        x=['Total Columns', 'Numeric Columns', 'Text Columns', 'Missing Values'],
                        y=[
                            len(df.columns),
                            len(df.select_dtypes(include=[np.number]).columns),
                            len(df.select_dtypes(include=['object']).columns),
                            df.isnull().sum().sum()
                        ],
                        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
                        text=[
                            len(df.columns),
                            len(df.select_dtypes(include=[np.number]).columns),
                            len(df.select_dtypes(include=['object']).columns),
                            df.isnull().sum().sum()
                        ],
                        textposition='auto'
                    )
                ])
                fig_columns.update_layout(
                    title="📈 Data Structure Overview",
                    xaxis_title="Category",
                    yaxis_title="Count",
                    showlegend=False
                )
                st.plotly_chart(fig_columns, use_container_width=True)
        
        with viz_tab2:
            # Data distribution analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                st.subheader("🔢 Numeric Columns Distribution")
                
                # Select column for distribution
                selected_numeric = st.selectbox(
                    "Select numeric column for distribution analysis:",
                    numeric_cols,
                    key="numeric_dist_select"
                )
                
                if selected_numeric:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Histogram
                        fig_hist = px.histogram(
                            df, 
                            x=selected_numeric,
                            title=f"📊 Distribution of {selected_numeric}",
                            nbins=30,
                            color_discrete_sequence=['#FF6B6B']
                        )
                        fig_hist.update_layout(showlegend=False)
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with col2:
                        # Box plot
                        fig_box = px.box(
                            df,
                            y=selected_numeric,
                            title=f"📦 Box Plot of {selected_numeric}",
                            color_discrete_sequence=['#4ECDC4']
                        )
                        st.plotly_chart(fig_box, use_container_width=True)
            
            if len(categorical_cols) > 0:
                st.subheader("📝 Categorical Columns Distribution")
                
                # Select column for categorical analysis
                selected_categorical = st.selectbox(
                    "Select categorical column for analysis:",
                    categorical_cols,
                    key="categorical_dist_select"
                )
                
                if selected_categorical:
                    # Value counts
                    value_counts = df[selected_categorical].value_counts().head(15)  # Top 15 values
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Bar chart
                        fig_bar = px.bar(
                            x=value_counts.index,
                            y=value_counts.values,
                            title=f"📊 Top Values in {selected_categorical}",
                            color=value_counts.values,
                            color_continuous_scale='viridis'
                        )
                        fig_bar.update_layout(
                            xaxis_title=selected_categorical,
                            yaxis_title="Count",
                            showlegend=False
                        )
                        fig_bar.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # Pie chart for top categories
                        fig_pie = px.pie(
                            values=value_counts.values,
                            names=value_counts.index,
                            title=f"🥧 Distribution of {selected_categorical}",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pie, use_container_width=True)
        
        with viz_tab3:
            # Data quality metrics
            st.subheader("🔍 Data Quality Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Missing values heatmap
                missing_data = df.isnull().sum()
                if missing_data.sum() > 0:
                    fig_missing = px.bar(
                        x=missing_data.index,
                        y=missing_data.values,
                        title="❌ Missing Values by Column",
                        color=missing_data.values,
                        color_continuous_scale='Reds'
                    )
                    fig_missing.update_layout(
                        xaxis_title="Columns",
                        yaxis_title="Missing Count",
                        showlegend=False
                    )
                    fig_missing.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_missing, use_container_width=True)
                else:
                    st.success("✅ No missing values found!")
                    # Create a placeholder chart
                    fig_no_missing = go.Figure(data=[
                        go.Bar(x=df.columns[:5], y=[0]*min(5, len(df.columns)), marker_color='lightgreen')
                    ])
                    fig_no_missing.update_layout(
                        title="✅ Data Completeness",
                        xaxis_title="Sample Columns",
                        yaxis_title="Missing Count"
                    )
                    st.plotly_chart(fig_no_missing, use_container_width=True)
            
            with col2:
                # Duplicate analysis
                duplicate_count = df.duplicated().sum()
                unique_count = len(df) - duplicate_count
                
                fig_duplicates = px.pie(
                    values=[unique_count, duplicate_count],
                    names=['Unique Records', 'Duplicate Records'],
                    title="🔄 Record Uniqueness",
                    color_discrete_sequence=['#90EE90', '#FFB6C1']
                )
                fig_duplicates.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_duplicates, use_container_width=True)
        
        with viz_tab4:
            # Summary statistics
            st.subheader("📋 Dataset Summary")
            
            # Create summary metrics
            total_records = len(df)
            total_columns = len(df.columns)
            numeric_columns = len(df.select_dtypes(include=[np.number]).columns)
            categorical_columns = len(df.select_dtypes(include=['object']).columns)
            missing_values = df.isnull().sum().sum()
            duplicate_records = df.duplicated().sum()
            
            # Create a summary visualization
            fig_summary = make_subplots(
                rows=2, cols=2,
                subplot_titles=('📊 Dataset Size', '📈 Column Types', '❌ Data Issues', '💾 Memory Usage'),
                specs=[[{"type": "indicator"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "indicator"}]]
            )
            
            # Dataset size indicator
            fig_summary.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=total_records,
                    title={'text': "Total Records"},
                    gauge={'axis': {'range': [None, total_records * 1.2]},
                           'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, total_records * 0.5], 'color': "lightgray"},
                                   {'range': [total_records * 0.5, total_records], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': total_records}}
                ),
                row=1, col=1
            )
            
            # Column types bar chart
            fig_summary.add_trace(
                go.Bar(x=['Numeric', 'Categorical'], 
                      y=[numeric_columns, categorical_columns],
                      marker_color=['#FF6B6B', '#4ECDC4'],
                      name="Column Types"),
                row=1, col=2
            )
            
            # Data issues
            fig_summary.add_trace(
                go.Bar(x=['Missing Values', 'Duplicates'], 
                      y=[missing_values, duplicate_records],
                      marker_color=['#FFA07A', '#FFB6C1'],
                      name="Data Issues"),
                row=2, col=1
            )
            
            # Memory usage indicator
            memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
            fig_summary.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=memory_usage,
                    title={'text': "Memory (MB)"},
                    number={'suffix': " MB"},
                    delta={'reference': 1, 'relative': True}
                ),
                row=2, col=2
            )
            
            fig_summary.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_summary, use_container_width=True)
            
            # Additional summary table
            st.subheader("📊 Quick Stats")
            summary_data = {
                'Metric': ['Total Records', 'Total Columns', 'Numeric Columns', 'Text Columns', 
                          'Missing Values', 'Duplicate Records', 'Memory Usage (KB)'],
                'Value': [total_records, total_columns, numeric_columns, categorical_columns,
                         missing_values, duplicate_records, f"{df.memory_usage(deep=True).sum() / 1024:.2f}"],
                'Percentage': ['100%', '100%', f'{(numeric_columns/total_columns)*100:.1f}%', 
                              f'{(categorical_columns/total_columns)*100:.1f}%',
                              f'{(missing_values/(total_records*total_columns))*100:.2f}%' if total_records > 0 else '0%',
                              f'{(duplicate_records/total_records)*100:.2f}%' if total_records > 0 else '0%',
                              '-']
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    def render_sidebar(self):
        """Render sidebar with options"""
        st.sidebar.header("🎲 Mock Data Generator")
        st.sidebar.markdown("---")
        
        # Topic selection
        st.sidebar.subheader("📋 Select Topic")
        
        # Add custom topic option
        topic_options = [topic["name"] for topic in self.topics] + ["custom"]
        
        selected_topic = st.sidebar.selectbox(
            "Choose a topic:",
            options=topic_options,
            format_func=lambda x: "Custom Topic" if x == "custom" else x.title().replace("_", " "),
            key="topic_select"
        )
        
        # Show topic description (only when topic changes)
        if selected_topic != "custom":
            topic_info = next((t for t in self.topics if t["name"] == selected_topic), None)
            if topic_info:
                st.sidebar.info(f"**Description:** {topic_info['description']}")
                with st.sidebar.expander("📝 Available Fields"):
                    for field in topic_info['fields']:
                        st.write(f"• {field}")
        
        # Custom fields for custom topic
        custom_fields = None
        if selected_topic == "custom":
            st.sidebar.subheader("🛠️ Custom Fields")
            custom_fields_input = st.sidebar.text_area(
                "Enter field names (one per line):",
                value="name\nemail\nage\ncategory\ndate\nstatus\ndescription",
                height=150,
                key="custom_fields_input"
            )
            custom_fields = [field.strip() for field in custom_fields_input.split('\n') if field.strip()]
            
            if custom_fields:
                st.sidebar.success(f"✅ {len(custom_fields)} custom fields defined")
        
        st.sidebar.markdown("---")
        
        # Format selection
        st.sidebar.subheader("📁 Select Format")
        selected_format = st.sidebar.selectbox(
            "Choose output format:",
            options=self.formats,
            key="format_select"
        )
        
        # Number of records
        st.sidebar.subheader("🔢 Records")
        num_records = st.sidebar.slider(
            "Number of records:",
            min_value=1,
            max_value=1000,
            value=100,
            step=10,
            key="num_records_slider"
        )
        
        # Advanced options
        with st.sidebar.expander("⚙️ Advanced Options"):
            seed = st.number_input(
                "Seed (for reproducible data):",
                min_value=0,
                max_value=99999,
                value=42,
                help="Use the same seed to generate identical data",
                key="seed_input"
            )
            
            use_seed = st.checkbox("Use seed", value=False, key="use_seed_checkbox")
        
        return selected_topic, selected_format, num_records, custom_fields, seed if use_seed else None
    
    def render_data_preview(self, data_result, format_type):
        """Render data preview with enhanced graphical statistics"""
        # Data preview
        st.subheader("📊 Data Preview")
        
        # Show preview based on format
        if format_type in ["JSON", "YAML", "TOML", "XML"]:
            st.code(data_result["data"], language=format_type.lower())
        
        elif format_type in ["CSV", "TSV"]:
            # Parse CSV for table display
            try:
                csv_data = pd.read_csv(io.StringIO(data_result["data"]))
                st.dataframe(csv_data, use_container_width=True, height=400)
                
                # Show raw CSV in expandable section
                with st.expander("View Raw CSV"):
                    st.code(data_result["data"], language="csv")
                
                # Enhanced graphical data statistics
                st.markdown("---")
                st.subheader("📈 Data Analytics Dashboard")
                
                # Create the visualizations
                self.create_data_visualizations(csv_data)
                
            except Exception as e:
                st.error(f"Error parsing CSV: {str(e)}")
                st.code(data_result["data"], language="csv")
        
        else:
            # For other formats, show as code
            st.code(data_result["data"], language="text")
    
    def render_main_content(self, topic, format_type, num_records, custom_fields, seed):
        """Render main content area"""
        st.title("🎲 Mock Data Generator")
        st.markdown("Generate realistic fake data in multiple formats for testing and development purposes.")
        
        # Configuration summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Topic", topic.title().replace("_", " ") if topic != "custom" else "Custom")
        with col2:
            st.metric("Format", format_type)
        with col3:
            st.metric("Records", num_records)
        with col4:
            if custom_fields:
                st.metric("Custom Fields", len(custom_fields))
            else:
                st.metric("Seed", seed if seed else "Random")
        
        st.markdown("---")
        
        # Generate button
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🚀 Generate Data", type="primary", use_container_width=True, key="generate_button"):
                with st.spinner("Generating mock data..."):
                    result = self.generate_data(topic, format_type, num_records, custom_fields, seed)
                    
                    if result and result.get("success"):
                        st.session_state.generated_data = result
                        st.session_state.current_config = {
                            'topic': topic,
                            'format_type': format_type,
                            'num_records': num_records,
                            'custom_fields': custom_fields,
                            'seed': seed
                        }
                        st.success("✅ Data generated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate data")
        
        # Display generated data
        if hasattr(st.session_state, 'generated_data') and st.session_state.generated_data:
            data_result = st.session_state.generated_data
            
            # Action buttons
            with col2:
                # Copy button (just shows the data in a code block)
                if st.button("📋 Show Raw", use_container_width=True, key="copy_button"):
                    st.session_state.show_raw = not st.session_state.get('show_raw', False)
            
            with col3:
                # Download button
                if st.button("⬇️ Download", use_container_width=True, key="download_button"):
                    with st.spinner("Preparing download..."):
                        config = st.session_state.get('current_config', {})
                        content, headers = self.download_data(
                            config.get('topic', topic),
                            config.get('format_type', format_type),
                            config.get('num_records', num_records),
                            config.get('custom_fields', custom_fields),
                            config.get('seed', seed)
                        )
                        
                        if content:
                            filename = data_result.get("filename", f"data.{format_type.lower()}")
                            
                            st.download_button(
                                label=f"💾 Download {filename}",
                                data=content,
                                file_name=filename,
                                mime=data_result.get("content_type", "application/octet-stream"),
                                use_container_width=True,
                                key="download_file_button"
                            )
            
            st.markdown("---")
            
            # Show raw data if requested
            if st.session_state.get('show_raw', False):
                st.subheader("📄 Raw Data")
                st.code(data_result["data"], language=format_type.lower())
                st.markdown("---")
            
            # Render data preview
            self.render_data_preview(data_result, format_type)
    
    def run(self):
        """Main app runner"""
        # Check API connection (cached)
        if not check_api_health():
            st.error("❌ Backend API is not running!")
            st.info("To start the backend:")
            st.code("cd mock-data-generator\npython run.py")
            
            # Add a refresh button
            if st.button("🔄 Retry Connection"):
                st.cache_data.clear()
                st.rerun()
            return
        
        # Render sidebar
        topic, format_type, num_records, custom_fields, seed = self.render_sidebar()
        
        # Render main content
        self.render_main_content(topic, format_type, num_records, custom_fields, seed)
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666;'>
                <p>🎲 Mock Data Generator | Built with FastAPI & Streamlit</p>
                <p>Generate realistic fake data for testing and development</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Initialize session state
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'current_config' not in st.session_state:
    st.session_state.current_config = {}
if 'show_raw' not in st.session_state:
    st.session_state.show_raw = False

# Run the app
if __name__ == "__main__":
    app = MockDataGeneratorApp()
    app.run()