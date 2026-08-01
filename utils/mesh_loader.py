import trimesh
import numpy as np
import streamlit as st


@st.cache_resource
def load_heart_mesh(path: str = "models/heart/heart.stl"):
    """
    Loads the real anatomical heart mesh once and caches it,
    so it doesn't reload from disk on every Streamlit rerun.
    """
    mesh = trimesh.load(path, force="mesh")

    vertices = mesh.vertices
    faces = mesh.faces

    return {
        "x": vertices[:, 0].tolist(),
        "y": vertices[:, 1].tolist(),
        "z": vertices[:, 2].tolist(),
        "i": faces[:, 0].tolist(),
        "j": faces[:, 1].tolist(),
        "k": faces[:, 2].tolist(),
    }

@st.cache_resource
def load_brain_mesh(path: str = "models/brain/brain.stl"):
    mesh = trimesh.load(path, force="mesh")

    vertices = mesh.vertices - mesh.vertices.mean(axis=0)
    scale = np.abs(vertices).max()
    vertices = vertices / scale

    faces = mesh.faces

    return {
        "x": vertices[:, 0].tolist(),
        "y": vertices[:, 1].tolist(),
        "z": vertices[:, 2].tolist(),
        "i": faces[:, 0].tolist(),
        "j": faces[:, 1].tolist(),
        "k": faces[:, 2].tolist(),
    }

@st.cache_resource
def load_lungs_mesh(path: str = "models/lungs/lungs_simplified.stl"):
    mesh = trimesh.load(path, force="mesh")

    vertices = mesh.vertices - mesh.vertices.mean(axis=0)
    scale = np.abs(vertices).max()
    vertices = vertices / scale

    faces = mesh.faces

    return {
        "x": vertices[:, 0].tolist(),
        "y": vertices[:, 1].tolist(),
        "z": vertices[:, 2].tolist(),
        "i": faces[:, 0].tolist(),
        "j": faces[:, 1].tolist(),
        "k": faces[:, 2].tolist(),
    }