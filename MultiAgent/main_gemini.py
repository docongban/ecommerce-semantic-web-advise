# main_llm.py
import os
import google.generativeai as genai
from rdflib import Graph


genai.configure(api_key="AIzaSyCgDhaKSyK2fmpZJF3MdMgx6xojXnH9_T4")
# models = genai.list_models()
# for m in models:
#     print(m.name)
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

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

def extract_sparql(response) -> str:
    try:
        # Lấy text gốc từ response
        text = response.candidates[0].content.parts[0].text.strip()

        # Nếu có code block ```sparql ... ```, ta loại bỏ
        if text.startswith("```sparql"):
            return text.replace("```sparql", "").replace("```", "").strip()
        elif text.startswith("```"):
            return text.replace("```", "").strip()
        return text  # fallback
    except Exception as e:
        print("⚠️ Lỗi khi trích SPARQL:", e)
        return ""

# --- Agent: Generate SPARQL bằng LLM ---
def generate_sparql_with_llm(question: str) -> str:
    prompt = f"""
        Đây là ontology RDF định nghĩa thông tin về sản phẩm điện tử, bao gồm các lớp như Product, Product_info, Category, và Product_review.
        
        Các thuộc tính mô tả thông tin sản phẩm gồm:
        Product: id, battery, camera_feature, camera_primary, camera_secondary, charg, charg_type, chipset, 
        display_rate, display_resolution, display_size, display_type, internet, memory_card_slot, 
        memory_filter, memory_internal, name, nfc, operating_system, operating_system_version, sim, special_feature,
        storage, storage_filter, weight
       
        Product_info: average_rating, ecom, price, product_id, special_price, total_rating
        
        Product_review: content, ecom, rate, product_id
        
        Category: name, id

        Viết SPARQL cho câu hỏi: {question}
        Chỉ trả về code SPARQL. 
        Lưu ý: Câu trả lời thì cần trả ra 1 bản ghi

        Ví dụ như này
        Câu hỏi: Tìm giá của điện thoại và kèm theo nơi bán
        PREFIX ex: <http://example.org/ontology#>

        SELECT ?name ?price ?ecom
        WHERE {{
        ?product a ex:Product ;
                ex:name ?name ;
                ex:id ?id .
        ?product_info a ex:Product_info ;
                        ex:product_id ?id ;
                        ex:ecom ?ecom ;
                        ex:price ?price .
        FILTER(CONTAINS(LCASE(STR(?name)), "iphone 15"))
        }}
        LIMIT 1
    """

    return extract_sparql(model.generate_content(prompt))

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
    # if len(results) == 1:
    #     return f"{question}: {results[0]}"
    # return "Kết quả:\n" + "\n".join(results)
    # Chuẩn bị prompt cho Gemini
    prompt = f"""
    Dựa trên câu hỏi và kết quả thô sau đây, hãy tạo một câu trả lời tự nhiên, dễ hiểu và phù hợp với ngữ cảnh bằng tiếng Việt.

    Câu hỏi: {question}
    Kết quả thô: {results[0]}

    Ví dụ:
    - Câu hỏi: "Giá của iPhone 15 là bao nhiêu tại FPT ?"
    - Kết quả thô: "iPhone 15, 20000000, FPT"
    - Câu trả lời tự nhiên: "Giá của iPhone 15 là 20.000.000 VNĐ, được bán trên FPTShop."

    Trả về chỉ câu trả lời tự nhiên.
    """

    # Gọi Gemini để tạo câu trả lời
    try:
        response = model.generate_content(prompt)
        natural_answer = response.candidates[0].content.parts[0].text.strip()
        return natural_answer
    except Exception as e:
        print(f"Lỗi khi gọi Gemini để tạo câu trả lời: {e}")
        # Fallback: trả về câu trả lời cơ bản nếu Gemini lỗi
        return f"{question}: {results[0]}"

# --- Main ---
def main():
    print("📥 Hỏi bất kỳ câu hỏi về sản phẩm, danh mục,... (gõ 'exit' để thoát)")
    while True:
        question = input("❓ Câu hỏi: ")
        if question.lower() == "exit":
            break

        sparql = generate_sparql_with_llm(question)
        # print("\n📄 SPARQL sinh bởi GPT:\n", sparql)

        results = execute_sparql(graph, sparql)
        answer = synthesize_answer(question, results)

        print("💬 Trả lời:", answer)
        print("-" * 50)

if __name__ == "__main__":
    main()
