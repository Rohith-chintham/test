import streamlit as st
import subprocess
import re
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# ---------- Get Connected Devices ----------
def get_connected_devices():
    try:
        output = subprocess.check_output("arp -a", shell=True).decode()
        devices = []
        for line in output.splitlines():
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9\-]+)", line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                devices.append((ip, mac))
        return devices
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# ---------- Create Network Graph ----------
def create_network_graph(devices, host_ip="192.168.1.1"):
    G = nx.Graph()
    G.add_node("Host", label="Hotspot", color="red")

    for idx, (ip, mac) in enumerate(devices):
        node_id = f"Device {idx+1}\n{ip}"
        G.add_node(node_id, label=node_id, color="green")
        G.add_edge("Host", node_id)

    return G

# ---------- Display Network with Pyvis ----------
def display_network(G):
    net = Network(height="400px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    net.repulsion(node_distance=150, central_gravity=0.3)

    net.save_graph("network_graph.html")
    HtmlFile = open("network_graph.html", "r", encoding="utf-8")
    source_code = HtmlFile.read()
    components.html(source_code, height=450, width=800)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="WiFi Network Map", layout="centered")
st.title("🌐 Live WiFi Network Map")

if st.button("🔄 Refresh Device List"):
    with st.spinner("Scanning network..."):
        devices = get_connected_devices()
    st.success(f"Found {len(devices)} device(s) connected.")

    if devices:
        G = create_network_graph(devices)
        st.subheader("📊 Connected Devices Map")
        display_network(G)

        st.subheader("📋 Device List")
        for idx, (ip, mac) in enumerate(devices, start=1):
            st.write(f"**{idx}. IP:** {ip} | **MAC:** {mac}")
    else:
        st.info("No devices found.")
else:
    st.info("Click the button above to scan your hotspot network.")

