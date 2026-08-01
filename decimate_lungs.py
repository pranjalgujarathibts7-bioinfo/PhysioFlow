import trimesh

print("Loading original mesh...")
mesh = trimesh.load("models/lungs/lungs.stl", force="mesh")
print("Original vertices:", len(mesh.vertices))
print("Original faces:", len(mesh.faces))

print("Decimating...")
simplified = mesh.simplify_quadric_decimation(face_count=30000)
print("New vertices:", len(simplified.vertices))
print("New faces:", len(simplified.faces))

simplified.export("models/lungs/lungs_simplified.stl")
print("Exported to models/lungs/lungs_simplified.stl")