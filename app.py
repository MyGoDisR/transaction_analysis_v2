# Libraries
import streamlit as st
import pandas as pd
import numpy as np 

# This is the structure of the app,
# There will be a navigation bar in for historical spenditure by year/month/week and overall
# To do:
# 1. changing the theme of the app from dark to light
# 2. choosing different currencies - this requires downloading data from sub accounts
# 3. 

with st.sidebar:
    pages = {
        "Budget": [
            st.Page("pages/1_overview.py", title="Overview"),
            st.Page("pages/2_yearly.py", title="Yearly Dashboard"),
            st.Page("pages/3_monthly.py", title="Monthly Dashboard")
        ]
    }

pg = st.navigation(pages)
pg.run()