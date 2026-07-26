import trimesh

mesh = trimesh.load("models/heart/heart.stl", force="mesh")

print("Number of vertices:", len(mesh.vertices))
print("Bounding box min:", mesh.bounds[0])
print("Bounding box max:", mesh.bounds[1])
print("Center:", mesh.centroid)