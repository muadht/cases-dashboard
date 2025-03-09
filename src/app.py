import streamlit as st
import pandas as pd
import plotly.express as px
import json
import translations
from arabic_support_custom import arabic_support_custom

# Set page to wide mode
st.set_page_config(layout="wide")

# Enable Arabic text support for all components
arabic_support_custom()

# Load data from CSV file
@st.cache_data
def get_data():
    df = pd.read_csv("data/cases.csv")  # Replace with actual CSV file path
    df["filing_date_dt"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["year"] = df["filing_date_dt"].dt.year
    return df

df = get_data()

# Column name mappings (English to Arabic)
column_map = translations.column_map

# Add company name and logo in a clean header layout
header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

with header_col2:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; ">
            <h2 style="margin-right: 20px; font-family: 'Noto Kufi Arabic', sans-serif; font-optical-sizing: auto; color: #686D76;
  font-weight: 400;">مجلة المحكمة العليا</h2>
            <img src="https://img.icons8.com/color/96/law.png" width="60" style="transform: scaleX(-1);">
        </div>
    """, unsafe_allow_html=True)

with st.expander("☰ تصفية القضايا", expanded=True):
    
    # Use more columns for a more compact layout, with the last column for the filter button
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    
    with col1:
        case_type_filter = st.selectbox("⚖️ نوع القضية:", ["الكل"] + list(df["case_type"].dropna().unique()))
    
    with col2:
        court_filter = st.selectbox("المحكمة:", ["الكل"] + list(df["court_name"].dropna().unique()))
    
    with col3:
        court_level_filter = st.selectbox("مستوى المحكمة:", ["الكل"] + list(df["court_level"].dropna().unique()))
    
    with col4:
        judgment_outcome_filter = st.selectbox("نتيجة الحكم:", ["الكل"] + list(df["judgment_outcome"].dropna().unique()))
    
    with col5:
        appeal_outcome_filter = st.selectbox("نتيجة الاستئناف:", ["الكل"] + list(df["appeal_outcome"].dropna().unique()))
    
    with col6:
        date_range = st.date_input("نطاق التاريخ:", [])
    
    

# Create tabs with icons
tab1, tab2 = st.tabs([
    "⚖️ قائمة القضايا",  # Add icon for cases list tab
    "📊 التحليلات والرسوم البيانية"  # Add icon for analytics tab
])

with tab1:

    # Apply filters to data
    filtered_df = df.copy()
    
    # Apply case type filter
    if case_type_filter != "الكل":
        filtered_df = filtered_df[filtered_df["case_type"] == case_type_filter]
    
    # Apply court filter
    if court_filter != "الكل":
        filtered_df = filtered_df[filtered_df["court_name"] == court_filter]
    
    # Apply appeal outcome filter
    if appeal_outcome_filter != "الكل":
        filtered_df = filtered_df[filtered_df["appeal_outcome"] == appeal_outcome_filter]
    
    # Apply court level filter
    if court_level_filter != "الكل":
        filtered_df = filtered_df[filtered_df["court_level"] == court_level_filter]
    
    # Apply judgment outcome filter
    if judgment_outcome_filter != "الكل":
        filtered_df = filtered_df[filtered_df["judgment_outcome"] == judgment_outcome_filter]
    
    # Apply date range filter if dates are selected
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df["filing_date_dt"] >= pd.Timestamp(start_date)) & 
                                  (filtered_df["filing_date_dt"] <= pd.Timestamp(end_date))]

    # Create a copy of filtered dataframe for table display
    filtered_df_for_table = filtered_df.copy()

    st.write("")
    # Create a 30/70 layout with table on left, details on right
    table_col, details_col = st.columns([1, 1])
    
    # Table section (on the left)
    with table_col:
        # Prepare table with only two columns for selection
        minimal_df_for_table = filtered_df_for_table[["judgment_outcome", "court_level", "case_type", "case_id"]].copy()
        
        # Convert judgment_outcome to visual indicators
        def add_outcome_indicator(outcome):
            if 'رفض' in str(outcome).lower():
                return '🔴 ' + str(outcome)
            elif 'قبول' in str(outcome).lower() or 'نقض' in str(outcome).lower():
                return '🟢 ' + str(outcome)
            else:
                return '⚪ ' + str(outcome)
        
        minimal_df_for_table['judgment_outcome'] = minimal_df_for_table['judgment_outcome'].apply(add_outcome_indicator)
        # Display the interactive dataframe
        # Add custom CSS for RTL table styling
        # with st.container(height=350):
        st.dataframe(
            minimal_df_for_table.rename(columns=column_map),
            on_select="rerun",
            selection_mode="single-row",
            key="cases_table",
            use_container_width=True,
            height= 300,
            column_config={
            column_map["case_id"]: st.column_config.TextColumn(
                "رقم القضية",
                help="رقم تعريفي للقضية",
                width="medium",
                pinned=True
                
            ),
            column_map["judgment_outcome"]: st.column_config.TextColumn(
                "نتيجة الحكم",
                help="النتيجة النهائية للقضية",
                width="medium",
                max_chars=10
            )
            },
            hide_index=True,
        )
        
        # Add quick stats below the table
        
        # Create metrics in a single row
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.metric("إجمالي القضايا", f"{len(filtered_df_for_table):,}")
        
        # Calculate accepted and rejected cases
        if len(filtered_df_for_table) > 0 and 'judgment_outcome' in filtered_df_for_table.columns:
            # Convert to string to avoid NaN issues
            judgment_str = filtered_df_for_table['judgment_outcome'].astype(str)
            
            # Count accepted cases (containing 'قبول' or 'نقض')
            accepted_cases = judgment_str.str.contains('قبول|نقض', case=False, na=False).sum()
            with m2:
                st.metric("القضايا المقبولة", f"{accepted_cases:,}")
                if accepted_cases > 0:
                    st.caption(f"{accepted_cases/len(filtered_df_for_table)*100:.1f}% من الإجمالي")
            
            # Count rejected cases (containing 'رفض')
            rejected_cases = judgment_str.str.contains('رفض', case=False, na=False).sum()
            with m3:
                st.metric("القضايا المرفوضة", f"{rejected_cases:,}")
                if rejected_cases > 0:
                    st.caption(f"{rejected_cases/len(filtered_df_for_table)*100:.1f}% من الإجمالي")
        else:
            with m2:
                st.metric("القضايا المقبولة", "0")
            with m3:
                st.metric("القضايا المرفوضة", "0")
    
    # Case details section (on the right)
    with details_col:
        # Apply a light background color to the details column
        # Check if a case is selected
        if ("cases_table" in st.session_state and 
            "selection" in st.session_state.cases_table and 
            "rows" in st.session_state.cases_table["selection"] and 
            st.session_state.cases_table["selection"]["rows"]):
            
            # Get selected row and case details
            selected_index = st.session_state.cases_table["selection"]["rows"][0]
            selected_case_id = filtered_df_for_table.iloc[selected_index]["case_id"]
            case_details = df[df["case_id"] == selected_case_id].iloc[0]
            
            # Display case header
            # Use Streamlit's native info component for the case header
            st.info(f"تفاصيل القضية: {selected_case_id}")
            
            # Display details in organized groups
            basic_col, dates_col, outcome_col = st.columns(3)
                        
            with basic_col:
                st.write("**معلومات أساسية**")
                st.write(f"**رقم القضية:** {case_details['case_id']}")
                st.write(f"**نوع القضية:** {case_details['case_type']}")
                st.write(f"**المحكمة:** {case_details['court_name']}")
                st.write(f"**الموقع:** {case_details['court_location']}")
            
            with dates_col:
                st.write("**التواريخ**")
                st.write(f"**تاريخ التقديم:** {case_details['filing_date']}")
                st.write(f"**تاريخ الجلسة:** {case_details['session_date_gregorian']}")
                st.write(f"**تاريخ الحكم:** {case_details['judgment_date']}")
            
            with outcome_col:
                st.write("**النتائج**")
                st.write(f"**نتيجة الحكم:** {case_details['judgment_outcome']}")
                st.write(f"**نتيجة الاستئناف:** {case_details['appeal_outcome']}")
            
            # Detail sections in tabs
            st.write("")  # Add spacing
            st.write("")  # Add spacing

            with st.expander("مزيد", expanded=False, ):
                detailed_tabs = st.tabs(["الوقائع", "الأسباب", "المراجع القانونية"])
                
                with detailed_tabs[0]:
                    with st.container(height=200, border=False):
                        st.write("")  # Add spacing
                        st.markdown(f"{case_details['sections_facts']}")
                
                with detailed_tabs[1]:
                    with st.container(height=200, border=False):
                        st.write("")
                        st.markdown(f"{case_details['sections_reasons']}")
                
                with detailed_tabs[2]:
                    with st.container(height=200, border=False):
                        st.write("")
                        # Parse and display legal references in a nicer format
                        if pd.notna(case_details['legal_references']):
                            try:
                                # Check if it's a string and needs parsing
                                if isinstance(case_details['legal_references'], str):
                                    legal_refs = json.loads(case_details['legal_references'])
                                else:
                                    legal_refs = case_details['legal_references']
                                
                                for ref in legal_refs:
                                    st.markdown(f"• {ref}")
                            except (json.JSONDecodeError, TypeError):
                                # If parsing fails, display as is
                                st.markdown(f"{case_details['legal_references']}")
                        else:
                            st.markdown("*لا توجد مراجع قانونية*")
        else:
            # Clear selection message
            with st.container(height=350):
                st.markdown("""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%;">
                        <img src="https://img.icons8.com/color/96/000000/documents--v1.png" style="width: 64px; height: 64px; opacity: 0.7;">
                        <h3 style="color: #666;"> اختر قضية من الجدول</h3>
                        <p style="color: #888;">انقر على أي صف في الجدول لعرض التفاصيل الكاملة للقضية</p>
                    </div>
                """, unsafe_allow_html=True)
                
# Analytics tab content
with tab2:    
    
    # First group of charts
    col1, col2 = st.columns(2)
    with col1:
        # Improved case distribution by year chart
        yearly_fig = px.box(
            df, 
            x="year", 
            title="توزيع القضايا عبر السنوات",
            labels={"year": "السنة", "value": "العدد"}
        )
        yearly_fig.update_layout(height=300)
        st.plotly_chart(yearly_fig, use_container_width=True)
        st.caption("توضيح: يظهر هذا الرسم البياني توزيع القضايا عبر السنوات")

    with col2:
        # Improved case type distribution chart
        case_type_counts = df['case_type'].value_counts()
        case_type_fig = px.pie(
            names=case_type_counts.index, 
            values=case_type_counts.values, 
            hole=0.3, 
            title="توزيع أنواع القضايا"
        )
        case_type_fig.update_layout(height=300)
        st.plotly_chart(case_type_fig, use_container_width=True)
        st.caption("توضيح: يوضح هذا الرسم الدائري توزيع أنواع القضايا")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Second group of charts
    st.subheader("نتائج وتوزيعات زمنية")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        # Improved judgment outcomes distribution chart
        judgment_counts = df['judgment_outcome'].value_counts().sort_values()
        judgment_fig = px.bar(
            x=judgment_counts.values, 
            y=judgment_counts.index, 
            orientation='h', 
            title="توزيع نتائج الأحكام",
            labels={"x": "العدد", "y": "نتيجة الحكم"}
        )
        judgment_fig.update_layout(height=300)
        st.plotly_chart(judgment_fig, use_container_width=True)
        st.caption("توضيح: يظهر هذا الرسم البياني توزيع نتائج الأحكام")

    with col4:
        # Improved cases over time chart
        cases_per_year = df['year'].value_counts().sort_index()
        trend_fig = px.line(
            x=cases_per_year.index, 
            y=cases_per_year.values, 
            title="عدد القضايا بمرور السنوات",
            labels={"x": "السنة", "y": "عدد القضايا"}
        )
        trend_fig.update_layout(height=300)
        trend_fig.update_traces(mode="lines+markers")
        st.plotly_chart(trend_fig, use_container_width=True)
        st.caption("توضيح: يوضح هذا الرسم الخطي عدد القضايا بمرور السنوات")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analytics explanations section
    with st.expander("معلومات تحليلية إضافية"):
        st.markdown("""
        ### ملخص التحليلات:
        
        هذه التحليلات تساعد في فهم اتجاهات القضايا وتوزيعها عبر الزمن ونتائجها المختلفة.
        يمكن استخدام هذه المعلومات لتحسين فهم النظام القضائي وتوزيع القضايا.
        """)