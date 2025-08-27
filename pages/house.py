# Libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os
import utils.web_scrap as webscrap
from datetime import datetime
import matplotlib.pyplot as plt
import utils.navigation as navigation

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

navigation.menu()

st.write("In progress")