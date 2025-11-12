import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Advanced URL Hitter", layout="wide")
st.title("🚀 Advanced Frequency and Duration Based URL Hitter")

gh --version# Sidebar for input
with st.sidebar:
    st.header("⚙️ Configuration")
    frequency = st.number_input("Enter frequency (hits per second):", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
    duration = st.number_input("Enter duration (seconds):", min_value=1.0, max_value=3600.0, value=10.0, step=1.0)
    url = st.text_input("Enter URL to hit:")
    timeout = st.number_input("Request timeout (seconds):", min_value=1.0, max_value=60.0, value=5.0, step=0.5)

# Main content area
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Frequency", f"{frequency} hits/sec")
with col2:
    st.metric("Duration", f"{duration} sec")
with col3:
    st.metric("Total Expected Hits", f"~{int(frequency * duration)}")

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
        st.subheader("📊 Final Results")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Hits", hits)
            
        with col2:
            st.metric("Successful", successful_hits, delta=f"✅")
        with col3:
            st.metric("Failed", failed_hits, delta=f"❌")
        with col4:
            success_rate = (successful_hits / hits * 100) if hits > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        if successful_hits > 0:
            avg_response_time = total_response_time / successful_hits
            avg_size = sum(response_sizes) / len(response_sizes)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Response Time", f"{avg_response_time*1000:.2f}ms")
            with col2:
                st.metric("Max Response Time", f"{max([rt*1000 for rt in [interval for interval in response_sizes]])/len(response_sizes)*1000:.2f}ms" if response_sizes else "N/A")
            with col3:
                st.metric("Avg Response Size", f"{avg_size:.0f} bytes")
        
        st.divider()
        st.subheader("📝 Detailed Hit Log")
        st.dataframe(hit_details, use_container_width=True)
        
        st.success(f"✅ Finished hitting URL {hits} times in {duration} seconds!")
