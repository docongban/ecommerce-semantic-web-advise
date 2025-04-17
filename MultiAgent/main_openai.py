# main_llm.py
import os
import openai
import rdflib
from rdflib import Graph

# --- Khởi tạo API Key ---
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-fm61aSE74f32oM5gu5g4w9Nl7lc999v8448Ctx2ZHa0b7RoQ"  # Thay bằng key thật

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

# --- Agent: Generate SPARQL bằng LLM ---
def generate_sparql_with_llm(question: str) -> str:
    system_prompt = """
Bạn là một trợ lý RDF chuyên sinh truy vấn SPARQL.
Ontology sử dụng namespace <http://example.org/ontology#>
Dưới đây là các ví dụ:

Ví dụ 1:
Câu hỏi: ID của danh mục có tên Xiaomi là gì?
SPARQL:
PREFIX ex: <http://example.org/ontology#>
SELECT ?id WHERE {
  ?s a ex:Category ;
     ex:name ?name ;
     ex:id ?id .
  FILTER CONTAINS(LCASE(STR(?name)), "xiaomi")
}

Chỉ trả về SPARQL truy vấn, không có chú thích, không có giải thích.
Hãy viết SPARQL cho câu hỏi sau:
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # hoặc "gpt-3.5-turbo"
        messages=messages,
        temperature=0
    )

    # Trích xuất truy vấn SPARQL
    content = response["choices"][0]["message"]["content"]
    sparql_code = content.strip()
    return sparql_code

# --- Agent: Execute SPARQL ---
def execute_sparql(graph: Graph, sparql: str):
    try:
        results = graph.query(sparql)
        return [str(row[0]) for row in results]
    except Exception as e:
        return [f"Lỗi khi thực thi SPARQL: {e}"]

# --- Agent: Tạo câu trả lời tự nhiên ---
def synthesize_answer(question: str, results: list[str]) -> str:
    if not results:
        return "Không tìm thấy thông tin phù hợp."
    if len(results) == 1:
        return f"Kết quả: {results[0]}"
    return "Kết quả:\n" + "\n".join(results)

# --- Main ---
def main():
    print("📥 Hỏi bất kỳ câu hỏi về sản phẩm, danh mục,... (gõ 'exit' để thoát)")
    while True:
        question = input("❓ Câu hỏi: ")
        if question.lower() == "exit":
            break

        sparql = generate_sparql_with_llm(question)
        print("\n📄 SPARQL sinh bởi GPT:\n", sparql)

        results = execute_sparql(graph, sparql)
        answer = synthesize_answer(question, results)

        print("💬 Trả lời:", answer)
        print("-" * 50)

if __name__ == "__main__":
    main()
