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
        "storage": ["bộ nhớ trong", "bộ nhớ", "dung lượng bộ nhớ trong"],
        "storage_filter": ["phiên bản bộ nhớ trong", "phiên bản dung lượng", "phiên bản bộ nhớ"],
        "chipset": ["chipset", "vi xử lý", "chip"],
        "nfc": ["công nghệ nfc", "nfc"],
        "sim": ["thẻ sim", "sim"],
        "internet": ["internet", "mạng"],
        "battery": ["pin", "dung lượng pin"],
        "charging_type": ["cổng sạc"],
        "charg": ["công nghệ sạc"],
        "weight": ["trọng lượng", "cân nặng", "nặng"],
        "special_feature": ["tính năng đặc biệt", "tính năng nổi trội", "tính năng mới", "tính năng nổi bật"],
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
            result.append((category, attr))
    return result

def analyze_question_condition(question):
    condition_keywords = {
        "shop": ["mua tại", "mua ở", "bán tại", "bán ở", "cửa hàng", "shop", "mua", "tại", "ở"],
        "price_from": ["giá từ", "giá thấp nhất", "giá tối thiểu", "giá bắt đầu từ", "giá khởi điểm từ", "giá lớn hơn"],
        "price_to": ["giá đến", "giá cao nhất", "giá tối đa", "giá nhỏ hơn", "giá kết thúc", "giá dưới", "giá ít hơn"],
        "total_rating_from": ["tổng đánh giá từ", "tổng đánh giá tối thiểu", "tổng đánh giá bắt đầu từ"],
        "total_rating_to": ["tổng đánh giá đến", "tổng đánh giá tối đa", "tổng đánh giá kết thúc"],
        "average_rating_from": ["điểm đánh giá từ", "điểm đánh giá tối thiểu", "điểm đánh giá bắt đầu từ"],
        "average_rating_to": ["điểm đánh giá đến", "điểm đánh giá tối đa", "điểm đánh giá kết thúc"],
    }
    
    question_lower = question.lower()
    result = []
    
    # Tách câu hỏi thành danh sách các từ
    words = question_lower.split()
    
    for cond, keywords in condition_keywords.items():
        for keyword in keywords:
            # Kiểm tra xem từ khóa có trong câu hỏi không
            if keyword in question_lower:
                # Tìm vị trí của từ khóa trong danh sách từ
                for i in range(len(words) - len(keyword.split())):
                    # Kiểm tra xem cụm từ tại vị trí i có khớp với từ khóa không
                    if " ".join(words[i:i + len(keyword.split())]) == keyword:
                        # Lấy từ ngay sau từ khóa (nếu tồn tại)
                        next_word_index = i + len(keyword.split())
                        if next_word_index < len(words):
                            next_word = words[next_word_index]
                            # Xác định category
                            if cond in ["shop"]:
                                category = "ecom"
                            elif cond in ["price_from", "price_to"]:
                                category = "special_price"
                            elif cond in ["total_rating_from", "total_rating_to"]:
                                category = "total_rating"
                            elif cond in ["average_rating_from", "average_rating_to"]:
                                category = "average_rating"
                            # Thêm tuple (category, operator, next_word) vào kết quả
                            result.append((category, cond, next_word))
                            break
    return result

def generate_sparql(type, product, attributes, conditions):
    if type == "detail":
        select_clause = "?name " + " ".join(f"?{attr[1]}" for attr in attributes) + " ".join(f"?{cond[0]}" for cond in conditions)
        query = f"""
            PREFIX ex: <http://example.org/ontology#>

            SELECT {select_clause}
            WHERE {{
            ?product a ex:Product ;
                    ex:name ?name ;
        """
        # Group attributes by category
        product_attrs = [attr for category, attr in attributes if category == "Product"]
        product_info_attrs = [attr for category, attr in attributes if category == "Product_info"]
        product_review_attrs = [attr for category, attr in attributes if category == "Product_review"]

        # Handle Product attributes
        if product_attrs:
            query += "\n".join(f"ex:{attr} ?{attr} ;" for attr in product_attrs)
        query += "\n ex:id ?id ."

        # Handle Product_info attributes
        if product_info_attrs:
            query += f"""
                ?product_info a ex:Product_info ;
                            ex:product_id ?id ;
            """
            if conditions:
                product_cond = [cond[0] for cond in conditions]
                query += "\n".join(f"ex:{attr} ?{attr} ;" for attr in product_cond)[:-1] + " ."
            query += "\n".join(f"ex:{attr} ?{attr} ;" for attr in product_info_attrs)[:-1] + " ."
        else:
            query += f"""
                ?product_info a ex:Product_info ;
                            ex:product_id ?id ;
            """
            if conditions:
                product_cond = [cond[0] for cond in conditions]
                query += "\n".join(f"ex:{attr} ?{attr} ;" for attr in product_cond)[:-1] + " ."
            

        # Handle Product_review attributes
        if product_review_attrs:
            query += f"""
            {{
                SELECT ?content ?rate
                    WHERE {{
                        ?product_review a ex:Product_review ;
                        ex:product_id ?id ;
                        ex:rate ?rate ;
                        ex:content ?content .
                    }}
                    LIMIT 5
            }}
            """

        filter_product_conditions = " && ".join(
            f'CONTAINS(LCASE(STR(?name)), "{p}")' for p in product if p
        )
        logic_parts = [
            f'xsd:float(?{cond[0]}) >= {cond[2]}' if "from" in cond[1] else
            f'xsd:float(?{cond[0]}) <= {cond[2]}' if "to" in cond[1] else
            f'CONTAINS(LCASE(STR(?{cond[0]})), "{cond[2]}")'
            for cond in conditions if cond
        ]
        filter_logic_conditions = f'&& {" && ".join(logic_parts)}' if logic_parts else ''


        query += f"""
            FILTER({filter_product_conditions} {filter_logic_conditions} )
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
    # question = "tính năng nổi bật của samsung galaxy s25 ultra là gì"
    # question = "tổng đánh giá và giá khuyến mãi iphone 15 pro max"
    # question = "tìm giá khuyến mãi iphone 15 pro max tại fpt"
    # question = "tìm iphone có giá lớn hơn 10000000 và giá nhỏ hơn 20000000"
    while True:
        question = input("❓ Câu hỏi: ")
        if question.lower() == "exit":
            break

        type = analyze_question_type(question)
        product = analyze_question_product(question)
        if not product:
            print("❌ Không tìm thấy sản phẩm trong câu hỏi.")
            return
        attributes = analyze_question_attribute(question)
        
        # if not attributes:
        #     print("❌ Không tìm thấy thuộc tính trong câu hỏi.")
        #     return
        
        conditions = analyze_question_condition(question)

        sparql = generate_sparql(type, product, attributes, conditions)
        print("\n📄 SPARQL được tạo là:\n", sparql)

        graph = load_graph()
        results = execute_sparql(graph, sparql)

        print("💬 Trả lời:", results)

if __name__ == "__main__":
    main()