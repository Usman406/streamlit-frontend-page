import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Advanced URL Hitter", layout="wide")

# Custom CSS Styling - Pakistan Background with Colors Layout
st.markdown("""
<style>
    /* Body background - Hunza Valley Background Image */
    html, body {
        background: linear-gradient(rgba(206, 17, 38, 0.4), rgba(31, 71, 136, 0.4)), 
                    url('https://images.pexels.com/photos/1619317/pexels-photo-1619317.jpeg?auto=compress&cs=tinysrgb&w=1600') center/cover fixed !important;
        margin: 0;
        padding: 0;
    }
    
    /* Main app container */
    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    /* Main content area with semi-transparent white background */
    .main {
        background: rgba(255, 255, 255, 0.92) !important;
        border-radius: 15px;
    }
    
    /* Top Red Header - Pakistan Flag Color */
    header {
        background: linear-gradient(to right, #CE1126 0%, #CE1126 50%, #FFFFFF 50%, #FFFFFF 100%) !important;
        padding: 25px;
        border-bottom: 5px solid #CE1126;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        border-radius: 10px 10px 0 0;
    }
    
    /* Bottom Yellow Footer */
    footer {
        background: linear-gradient(to right, #CE1126 0%, #CE1126 50%, #FFFFFF 50%, #FFFFFF 100%) !important;
        color: #000000;
        padding: 20px;
        border-top: 5px solid #CE1126;
        font-weight: bold;
        border-radius: 0 0 10px 10px;
    }
    
    /* Title styling */
    h1 {
        color: #FFFFFF;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.8);
        background: linear-gradient(135deg, #CE1126 0%, #1F4788 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 240, 240, 0.98) 100%) !important;
        border-right: 5px solid #00ff00;
        box-shadow: 2px 0 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] h2 {
        color: #CE1126;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Custom colored boxes */
    .metric-box {
        border-left: 5px solid #00ff00;
        padding: 15px;
        border-radius: 5px;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* Content box styling */
    div[data-testid="stMarkdownContainer"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Button styling */
    button {
        background: linear-gradient(135deg, #CE1126 0%, #1F4788 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Advanced Frequency and Duration Based URL Hitter")

# Add Pakistan theme subtitle
st.markdown("""
<div style='text-align: center; background: rgba(206, 17, 38, 0.8); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <h3 style='color: #FFFFFF; margin: 0;'>🇵🇰 Pakistan Theme Edition 🇵🇰</h3>
    <p style='color: #FFD700; margin: 5px 0 0 0;'>Made with ❤️ in Pakistan</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for input
with st.sidebar:
    st.header("⚙️ Configuration")
    frequency = st.number_input("Enter frequency (hits per second):", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
    duration = st.number_input("Enter duration (seconds):", min_value=1.0, max_value=3600.0, value=10.0, step=1.0)
    url = st.text_input("Enter URL to hit:")
    timeout = st.number_input("Request timeout (seconds):", min_value=1.0, max_value=60.0, value=5.0, step=0.5)

# Main content area
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style='background-color: #90EE90; padding: 15px; border-radius: 10px; text-align: center;'>
        <h4 style='color: #000000;'>⚡ Frequency</h4>
        <h3 style='color: #006400;'>{} hits/sec</h3>
    </div>
    """.format(frequency), unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style='background-color: #FFD700; padding: 15px; border-radius: 10px; text-align: center;'>
        <h4 style='color: #000000;'>⏱️ Duration</h4>
        <h3 style='color: #FF8C00;'>{} sec</h3>
    </div>
    """.format(duration), unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style='background-color: #FF6347; padding: 15px; border-radius: 10px; text-align: center;'>
        <h4 style='color: #FFFFFF;'>🎯 Expected Hits</h4>
        <h3 style='color: #FFFFFF;'>~{}</h3>
    </div>
    """.format(int(frequency * duration)), unsafe_allow_html=True)

if st.button("🎯 Start Hitting URL", key="start_button"):
    if not url:
        st.error("❌ Please enter a URL!")
    else:
        start_time = time.time()
        interval = 1.0 / frequency  
        hits = 0
        successful_hits = 0
        failed_hits = 0
        total_response_time = 0
        response_sizes = []
        hit_details = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        results_placeholder = st.empty()
        details_placeholder = st.empty()
        
        st.info(f"🔄 Starting to hit URL: `{url}`")
        
        while (time.time() - start_time) < duration:
            try:
                request_start = time.time()
                response = requests.get(url, timeout=timeout)
                response_time = time.time() - request_start
                
                hits += 1
                successful_hits += 1
                total_response_time += response_time
                response_size = len(response.content)
                response_sizes.append(response_size)
                
                # Status code color coding
                if response.status_code == 200:
                    status_emoji = "✅"
                    status_color = "green"
                elif 300 <= response.status_code < 400:
                    status_emoji = "🔀"
                    status_color = "blue"
                elif 400 <= response.status_code < 500:
                    status_emoji = "⚠️"
                    status_color = "orange"
                else:
                    status_emoji = "❌"
                    status_color = "red"
                
                hit_details.append({
                    "Hit": hits,
                    "Time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "Status": f"{status_emoji} {response.status_code}",
                    "Response Time": f"{response_time*1000:.2f}ms",
                    "Size": f"{response_size} bytes"
                })
                
            except requests.exceptions.Timeout:
                hits += 1
                failed_hits += 1
                hit_details.append({
                    "Hit": hits,
                    "Time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "Status": "⏱️ Timeout",
                    "Response Time": f">{timeout*1000:.0f}ms",
                    "Size": "N/A"
                })
            except requests.exceptions.RequestException as e:
                hits += 1
                failed_hits += 1
                hit_details.append({
                    "Hit": hits,
                    "Time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "Status": "❌ Error",
                    "Response Time": "N/A",
                    "Size": "N/A"
                })
            
            # Update progress bar
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            progress_bar.progress(progress)
            
            # Update status
            status_placeholder.info(f"⏱️ {elapsed:.1f}s / {duration}s | Hits: {hits} | Success: {successful_hits} | Failed: {failed_hits}")
            
            # Update results
            if successful_hits > 0:
                avg_response_time = total_response_time / successful_hits
                results_placeholder.success(
                    f"✅ Avg Response Time: {avg_response_time*1000:.2f}ms | "
                    f"Avg Size: {sum(response_sizes)/len(response_sizes):.0f} bytes"
                )
            
            time.sleep(interval)
        
        # Final results
        st.divider()
        st.markdown("""
        <h2 style='text-align: center; color: #ff0000; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            📊 Final Results
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #00ff00;'>
                <p style='color: #555;'>Total Hits</p>
                <h2 style='color: #00ff00; margin: 0;'>{}</h2>
            </div>
            """.format(hits), unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #4CAF50;'>
                <p style='color: #555;'>✅ Successful</p>
                <h2 style='color: #4CAF50; margin: 0;'>{}</h2>
            </div>
            """.format(successful_hits), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style='background-color: #FFEBEE; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #ff0000;'>
                <p style='color: #555;'>❌ Failed</p>
                <h2 style='color: #ff0000; margin: 0;'>{}</h2>
            </div>
            """.format(failed_hits), unsafe_allow_html=True)
        with col4:
            success_rate = (successful_hits / hits * 100) if hits > 0 else 0
            st.markdown("""
            <div style='background-color: #FFF3E0; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #ffff00;'>
                <p style='color: #555;'>Success Rate</p>
                <h2 style='color: #FF8C00; margin: 0;'>{:.1f}%</h2>
            </div>
            """.format(success_rate), unsafe_allow_html=True)
        
        if successful_hits > 0:
            avg_response_time = total_response_time / successful_hits
            avg_size = sum(response_sizes) / len(response_sizes)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style='background-color: #F3E5F5; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #9C27B0;'>
                    <p style='color: #555;'>Avg Response Time</p>
                    <h3 style='color: #9C27B0; margin: 0;'>{:.2f}ms</h3>
                </div>
                """.format(avg_response_time*1000), unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style='background-color: #E0F2F1; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #009688;'>
                    <p style='color: #555;'>Avg Response Size</p>
                    <h3 style='color: #009688; margin: 0;'>{:.0f} bytes</h3>
                </div>
                """.format(avg_size), unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style='background-color: #FCE4EC; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #E91E63;'>
                    <p style='color: #555;'>Performance</p>
                    <h3 style='color: #E91E63; margin: 0;'>⚡ Good</h3>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📝 Detailed Hit Log")
        st.dataframe(hit_details, use_container_width=True)
        
        st.success(f"✅ Finished hitting URL {hits} times in {duration} seconds!")

# Bottom Yellow Footer with Pakistan Theme
st.markdown("""
<div style='background: linear-gradient(to right, #CE1126 0%, #CE1126 50%, #FFFFFF 50%, #FFFFFF 100%); padding: 20px; text-align: center; margin-top: 30px; border-top: 5px solid #CE1126; color: #000000; font-weight: bold;'>
    <h3 style='color: #CE1126;'>🎉 Advanced URL Hitter v2.0 Pakistan Edition 🇵🇰</h3>
    <p style='color: #333;'>Developed by <strong>Usman406</strong> with ❤️</p>
    <p style='color: #666; font-size: 12px;'>© 2025 - Pakistan | All Rights Reserved</p>
    <p style='color: #CE1126; font-size: 10px;'>🏔️ Hunza Valley Background | Pakistan's Beauty 🏔️</p>
</div>
""", unsafe_allow_html=True)
