import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import uuid

st.title("GyroOS Prototype")

# --- Session State ---
if "objects" not in st.session_state:
    st.session_state.objects = {}
if "relations" not in st.session_state:
    st.session_state.relations = []
if "frame" not in st.session_state:
    st.session_state.frame = {"goal": "default"}

# --- Create Object ---
st.sidebar.header("Create Object")

content = st.sidebar.text_input("Content")
obj_type = st.sidebar.selectbox("Type", ["Concept", "Task", "Memory"])

if st.sidebar.button("Add Object"):
    oid = str(uuid.uuid4())[:6]
    st.session_state.objects[oid] = {
        "content": content,
        "type": obj_type,
        "energy": 1.0
    }

# --- Create Relation ---
st.sidebar.header("Create Relation")

obj_ids = list(st.session_state.objects.keys())

if len(obj_ids) >= 2:
    src = st.sidebar.selectbox("Source", obj_ids)
    dst = st.sidebar.selectbox("Target", obj_ids)
    rel_type = st.sidebar.selectbox("Relation", ["support", "conflict"])

    if st.sidebar.button("Add Relation"):
        st.session_state.relations.append({
            "src": src,
            "dst": dst,
            "type": rel_type
        })

# --- Frame Switch ---
st.sidebar.header("Frame")

goal = st.sidebar.selectbox("Goal", ["default", "research", "implementation"])
st.session_state.frame["goal"] = goal

# --- Graph ---
G = nx.Graph()

for oid, obj in st.session_state.objects.items():
    G.add_node(oid, label=obj["content"])

for rel in st.session_state.relations:
    color = "red" if rel["type"] == "conflict" else "black"
    G.add_edge(rel["src"], rel["dst"], color=color)

# --- Draw ---
fig, ax = plt.subplots()
pos = nx.spring_layout(G)

edges = G.edges()
colors = [G[u][v]["color"] for u,v in edges]

nx.draw(G, pos, with_labels=True, edge_color=colors, ax=ax)

st.pyplot(fig)

# --- Info Panel ---
st.subheader("Objects")
st.json(st.session_state.objects)

st.subheader("Frame")
st.json(st.session_state.frame)