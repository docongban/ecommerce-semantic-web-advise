from rdflib import Graph
from typing import Tuple
from transformers import pipeline
import os

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

graph = load_graph()

# ----------------------
# Step 2: Multi-Agent
# ----------------------

# === Agent 1: Intent Recognition ===
def recognize_intent(question: str) -> str:
    if "tên" in question.lower() or "name" in question.lower():
        return "ASK_NAME"
    if "id" in question.lower():
        return "ASK_ID"
    if "loại" in question.lower() or "category" in question.lower():
        return "ASK_CATEGORY"
    return "UNKNOWN"

# === Agent 2: Entity + Property Extraction ===
def extract_entities(question: str) -> Tuple[str, str]:
    # Very basic rule-based extraction
    product_keywords = ["Samsung", "iPhone", "Xiaomi"]
    for kw in product_keywords:
        if kw.lower() in question.lower():
            return ("Product", kw)
    return ("", "")

# === Agent 3: SPARQL Query Generator ===
def generate_sparql(intent: str, entity_type: str, keyword: str) -> str:
    if entity_type == "Product" and intent == "ASK_ID":
        return f"""
        PREFIX ex: <http://example.org/ontology#>
        SELECT ?id WHERE {{
            ?s a ex:Category ;
               ex:name ?name ;
               ex:id ?id .
            FILTER CONTAINS(LCASE(STR(?name)), "{keyword.lower()}")
        }}
        """
    elif entity_type == "Product" and intent == "ASK_NAME":
        return f"""
        PREFIX ex: <http://example.org/ontology#>
        SELECT ?name WHERE {{
            ?s a ex:Category ;
               ex:name ?name .
            FILTER CONTAINS(LCASE(STR(?name)), "{keyword.lower()}")
        }}
        """
    else:
        return ""

# === Agent 4: Query Execution ===
def execute_sparql(graph: Graph, query: str):
    results = graph.query(query)
    return [str(row[0]) for row in results]

# === Agent 5: Answer Synthesizer ===
def synthesize_answer(intent: str, keyword: str, results):
    if not results:
        return f"Không tìm thấy kết quả cho '{keyword}'."
    
    if intent == "ASK_NAME":
        return f"Tên danh mục chứa '{keyword}' là: {results[0]}"
    elif intent == "ASK_ID":
        return f"ID danh mục chứa '{keyword}' là: {results[0]}"
    return "Không thể tạo câu trả lời."

# === Optional: RAG Agent (placeholder) ===
def rag_fallback(question: str) -> str:
    return f"Không tìm thấy dữ liệu chính xác. Nhưng tôi có thể tìm kiếm thêm nếu bạn cung cấp thêm thông tin."

# ----------------------
# Pipeline xử lý câu hỏi
# ----------------------
def process_question(question: str):
    print(f"\n❓ Câu hỏi: {question}")
    
    intent = recognize_intent(question)
    print(f"🔍 Intent: {intent}")

    entity_type, keyword = extract_entities(question)
    print(f"🔍 Entity: {entity_type}, Keyword: {keyword}")

    sparql = generate_sparql(intent, entity_type, keyword)
    print(f"📄 SPARQL:\n{sparql.strip()}")

    if not sparql:
        return rag_fallback(question)

    results = execute_sparql(graph, sparql)
    answer = synthesize_answer(intent, keyword, results)
    return answer

# ----------------------
# Test
# ----------------------
if __name__ == "__main__":
    questions = [
        "ID của danh mục có tên Xiaomi là gì?",
        # "Tên của danh mục chứa iPhone là gì?",
        # "Iphone có những loại nào?",
    ]

    for q in questions:
        print("💬", process_question(q))
