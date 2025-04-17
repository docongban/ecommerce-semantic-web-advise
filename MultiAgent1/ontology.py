import os
from rdflib import Graph

# Đường dẫn đến folder Data
data_folder = os.path.join(os.getcwd(), "Data")
# Đường dẫn đến file ontology và data
ontology_file_path = os.path.join(data_folder, "ontology.ttl")
data_file_path = os.path.join(data_folder, "data.ttl")
# Kiểm tra sự tồn tại của file
if not os.path.exists(ontology_file_path):
    print(f"Lỗi: Không tìm thấy file ontology tại {ontology_file_path}")
    exit()
if not os.path.exists(data_file_path):
    print(f"Lỗi: Không tìm thấy file data tại {data_file_path}")
    exit()

# ----------------------
# Step 1: Load ontology + data
# ----------------------
def load_graph():
    g = Graph()
    g.parse(ontology_file_path, format="ttl")
    g.parse(data_file_path, format="ttl")
    return g

def execute_sparql(graph: Graph, sparql: str):
    try:
        results = graph.query(sparql)
        return [tuple(str(col) for col in row) for row in results]
    except Exception as e:
        # return [f"Lỗi khi thực thi SPARQL: {e}"]
        return [f"❌ Không tìm thấy sản phẩm trong câu hỏi."]