import streamlit as st
import subprocess
import psutil
import socket
import speedtest
import plotly.graph_objects as go

# --------- Get WiFi SSID ----------
def get_ssid():
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        for line in output.split('\n'):
            if "SSID" in line and "BSSID" not in line:
                return line.split(":")[1].strip()
    except Exception as e:
        return f"Error: {e}"
    return "SSID not found"

# --------- Get Signal Strength ----------
def get_signal_strength():
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        for line in output.split('\n'):
            if "Signal" in line:
                return int(line.split(":")[1].replace('%', '').strip())
    except:
        return None

# --------- Get Local IP ----------
def get_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "Unknown"

# --------- Speed Test ----------
def run_speed_test():
    stt = speedtest.Speedtest()
    stt.get_best_server()
    download = round(stt.download() / 1_000_000, 2)  # Mbps
    upload = round(stt.upload() / 1_000_000, 2)      # Mbps
    ping = stt.results.ping
    return download, upload, ping

# ----------------- Streamlit UI ------------------
st.set_page_config(page_title="WiFi Analytics", layout="centered")
st.title("📡 WiFi Analytics & Report")

ssid = get_ssid()
signal = get_signal_strength()
ip = get_ip()
net_io = psutil.net_io_counters()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📶 WiFi Info")
    st.write(f"**SSID:** {ssid}")
    st.write(f"**IP Address:** {ip}")
    st.write(f"**Signal Strength:** {signal if signal else 'N/A'}%")

with col2:
    st.subheader("🔌 Interface")
    st.write(f"Bytes Sent: {net_io.bytes_sent / 1_000_000:.2f} MB")
    st.write(f"Bytes Received: {net_io.bytes_recv / 1_000_000:.2f} MB")

st.divider()

if st.button("🔄 Run Speed Test"):
    with st.spinner("Running speed test..."):
        download, upload, ping = run_speed_test()
    st.success("Speed test completed!")
    
    # Speed Report
    st.subheader("📈 Speed Test Report")
    st.write(f"**Download Speed:** {download} Mbps")
    st.write(f"**Upload Speed:** {upload} Mbps")
    st.write(f"**Ping:** {ping} ms")
    
    # Chart
    fig = go.Figure(data=[
        go.Bar(name='Download', x=['Speed'], y=[download], marker_color='green'),
        go.Bar(name='Upload', x=['Speed'], y=[upload], marker_color='blue'),
    ])
    fig.update_layout(title="WiFi Speed Comparison", yaxis_title="Mbps", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

