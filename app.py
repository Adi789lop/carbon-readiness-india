import streamlit as st

st.set_page_config(
    page_title='Carbon Readiness & Supplier Sustainability Tool',
    page_icon='🌱',
    layout='wide'
)

st.title('🌱 Carbon Price Readiness & Supplier Sustainability Tool')
st.subheader('For Indian Auto Component Manufacturers')
st.markdown('---')
col1, col2, col3 = st.columns(3)
col1.info('**Step 1**: Complete Supplier Input form with your facility data')
col2.info('**Step 2**: View your Scope 1&2 emissions, CPRI score, and MAC curve')
col3.info('**Step 3**: Buyers compare all suppliers in the dashboard')
st.markdown('---')
st.caption('Data sources: CEA, IPCC 2006, MNRE 2024')
