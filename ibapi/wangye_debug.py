# import streamlit as st
# import time
#
# 'Starting a long computation...'
#
# # Add a placeholder
# latest_iteration = st.empty()
# bar = st.progress(0)
#
# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

with st.empty():
    while 1:

        arr = np.random.normal(1, 1, size=100)
        fig, ax = plt.subplots()
        ax.hist(arr, bins=20)
        time.sleep(0.5)
        st.pyplot(fig, clear_figure=True)