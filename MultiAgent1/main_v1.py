from ontology import *

def analyze_question_type(question):
    if any(keyword in question.lower() for keyword in ["tất cả", "danh sách", "liệt kê", "những"]):
        result = "list"
    else:
        result = "detail"
    
    return result

def analyze_question_product(question):
    keyword_category = ["apple", "iphone", "samsung", "oppo", "xiaomi", "vivo", "realme", "nokia",
                        "galaxy", "pro", "plus", "128gb", "256gb", "512gb", "1tb", "note", "max", 
                        "redmi", "find", "reno", "flip", "fold", "mini"]

    words = question.lower().split()
    first_index = float('inf')
    last_index = -1
    for i, word in enumerate(words):
        if word in keyword_category:
            first_index = min(first_index, i)
            last_index = max(last_index, i)
    
    if first_index == float('inf'):
        return []
    result = words[first_index:last_index + 1]
    
    return result

def analyze_question_attribute(question):
    attribute_keywords = {
        "name": ["tên", "tên điện thoại", "tên máy"],
        "display_size": ["kích thước màn hình"],
        "display_resolution": ["độ phân giải màn hình", "độ phân giải"],
        "display_type": ["công nghệ màn hình"],
        "display_rate": ["tần số quét màn hình","tần số quét"],
        "camera_primary": ["camera chính", "camera sau"],
        "camera_secondary": ["camera trước", "camera selfie"],
        "camera_feature": ["tính năng camera", "tính năng chụp ảnh"],
        "operating_system": ["hệ điều hành"],
        "operating_system_version": ["phiên bản hệ điều hành"],
        "memory_internal": ["ram", "bộ nhớ đệm"],
        "memory_card_slot": ["thẻ nhớ", "thẻ nhớ ngoài", "thẻ nhớ mở rộng", "khe cắm thẻ nhớ", "khe cắm thẻ nhớ ngoài"],
        "memory_filter": ["phiên bản ram"],
        "storage": ["bộ nhớ trong", "dung lượng", "bộ nhớ"],
        "storage_filter": ["phiên bản bộ nhớ trong", "phiên bản dung lượng", "phiên bản bộ nhớ"],
        "chipset": ["chipset", "vi xử lý", "chip"],
        "nfc": ["công nghệ nfc", "nfc"],
        "sim": ["thẻ sim", "sim"],
        "internet": ["internet", "mạng"],
        "battery": ["pin", "dung lượng pin"],
        "charging_type": ["cổng sạc"],
        "charg": ["công nghệ sạc"],
        "weight": ["trọng lượng", "cân nặng", "nặng"],
        "special_feature": ["tính năng đặc biệt", "tính năng nổi trội", "tính năng mới"],
        "ecom": ["loại sàn", "shop", "cửa hàng", "nơi bán", "mua tại", "mua ở", "bán ở", "bán tại"],
        "price": ["giá gốc", "giá chưa khuyến mãi"],
        "special_price": ["giá khuyến mãi", "giá sale", "giá ưu đãi", "giá hiện tại", "giá hiện tại"],
        "total_rating": ["tổng số lượng đánh giá", "tổng đánh giá", "số lượt đánh giá", "tổng số lượt đánh giá"],
        "average_rating": ["điểm trung bình", "đánh giá trung bình", "sao trung bình", "điểm đánh giá trung bình"],
        "content": ["nội dung đánh giá", "đánh giá chi tiết", "cảm nhận"],
        "rate": ["đánh giá", "điểm đánh giá", "điểm", "sao"],
    }
    
    question_lower = question.lower()
    result = []
    for attr, keywords in attribute_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            if attr in ["name", "display_size", "display_resolution", "display_type", "display_rate", 
                        "camera_primary", "camera_secondary", "camera_feature", "operating_system", 
                        "operating_system_version", "memory_internal", "memory_card_slot", "memory_filter",
                        "storage", "storage_filter", "chipset", "nfc", "sim", "internet", "battery",
                        "charging_type", "charg", "weight", "special_feature"]:
                category = "Product"
            elif attr in ["ecom", "price", "special_price", "total_rating", "average_rating"]:
                category = "Product_info"
            else:
                category = "Product_review"
            return [category, attr]
    return []

def generate_sparql(type, product, attribute):
    if type == "detail":
        filter_product_conditions = " && ".join(
            f'CONTAINS(LCASE(STR(?name)), "{p}")' for p in product if p
        )
        filter_attribute_conditions = f' && CONTAINS(LCASE(STR(?{attribute[0]})), "{attribute[1]}")'
        query = f"""
            PREFIX ex: <http://example.org/ontology#>

            SELECT ?name ?{attribute[1]} 
            WHERE {{
            ?product a ex:Product ;
                    ex:name ?name ;
                    {attribute[0] == "Product" and f'ex:{attribute[1]} ?{attribute[1]};' or ''}
                    ex:id ?id .
        """
        if attribute[0] == "Product_review":
            query += f"""
                ?product_review a ex:Product_review ;
                                ex:product_id ?id ;
                                ex:ecom ?ecom ;
                                ex:price ?price .
            """
        elif attribute[0] == "Product_info":
            query += f"""
                ?product_info a ex:Product_info ;
                            ex:product_id ?id ;
                            ex:ecom ?ecom ;
                            ex:{attribute[1]} ?{attribute[1]} .
            """
        query += f"""
            FILTER({filter_product_conditions} )
            }}
            LIMIT 1
        """
    else:
        query = """
                SELECT ?product
                WHERE {
                    ?product a ex:Product .
                }
                """
    return query

def main():
    print("📥 Hỏi về điện thoại ... (gõ 'exit' để thoát)")
    # while True:
    question = "tổng đánh giá iphone 15 pro max"
    # if question.lower() == "exit":
    #     break

    type = analyze_question_type(question)
    product = analyze_question_product(question)
    if(not product):
        print("❌ Không tìm thấy sản phẩm trong câu hỏi.")
        return
    attribute = analyze_question_attribute(question)
    
    if(not attribute):
        print("❌ Không tìm thấy thuộc tính trong câu hỏi.")
        return

    sparql = generate_sparql(type, product, attribute)
    print("\n📄 SPARQL được tạo là:\n", sparql)

    graph = load_graph()

    results = execute_sparql(graph, sparql)
    # answer = synthesize_answer(question, results)

    print("💬 Trả lời:", results[0])
    # print("-" * 50)

if __name__ == "__main__":
    main()
