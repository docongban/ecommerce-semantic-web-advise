from rdflib import Graph, Namespace
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(BASE_DIR, "Data")

ontology_file_path = os.path.join(data_folder, "ontology.ttl")
data_file_path = os.path.join(data_folder, "data.ttl")
inferred_file_path = os.path.join(data_folder, "inferred.ttl")

if not os.path.exists(ontology_file_path):
    print(f"Lỗi: Không tìm thấy file ontology tại {ontology_file_path}")
    exit()
if not os.path.exists(data_file_path):
    print(f"Lỗi: Không tìm thấy file data tại {data_file_path}")
    exit()

g = Graph()

print("Đang nạp ontology...")
g.parse(ontology_file_path, format="turtle")

print("Đang nạp dữ liệu...")
g.parse(data_file_path, format="turtle")

EX = Namespace("http://example.org/ontology#")
DATA = Namespace("http://example.org/data/")
g.bind("ex", EX)
g.bind("data", DATA)

# === Các luật suy diễn bằng SPARQL CONSTRUCT ===
rules = [
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:PremiumProduct .
    }
    WHERE {
        ?s a ex:Product_info ;
           ex:price ?price ;
           ex:average_rating ?rating .
        FILTER(xsd:integer(?price) > 10000000 && xsd:float(?rating) > 4.5)
    }
    """,
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:BudgetProduct .
    }
    WHERE {
        ?s a ex:Product_info ;
           ex:price ?price .
        FILTER(xsd:integer(?price) < 2000000)
    }
    """,
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:RecommendedProduct .
    }
    WHERE {
        ?s a ex:BudgetProduct ;
           ex:average_rating ?rating .
        FILTER(xsd:float(?rating) >= 4.0)
    }
    """,
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:WellRatedProduct .
    }
    WHERE {
        ?s a ex:Product_info ;
           ex:average_rating ?r .
        FILTER(xsd:float(?r) >= 4.5)
    }
    """,
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:MidRangeProduct .
    }
    WHERE {
        ?s a ex:Product_info ;
           ex:price ?p .
        FILTER(xsd:integer(?p) >= 4000000 && xsd:integer(?p) <= 7000000)
    }
    """
]

print("Đang thực hiện suy diễn logic bằng SPARQL CONSTRUCT...")
for i, rule in enumerate(rules):
    inferred = g.query(rule)
    for triple in inferred:
        g.add(triple)
    print(f"  - Luật {i+1} đã được áp dụng.")

g.serialize(destination=inferred_file_path, format="turtle")
print(f"\nĐã ghi graph suy diễn vào file: {inferred_file_path}")

rule_descriptions = {
    "PremiumProduct": "Giá > 10 triệu và Rating > 4.5",
    "BudgetProduct": "Giá < 2 triệu",
    "RecommendedProduct": "Là BudgetProduct và Rating >= 4.0",
    "WellRatedProduct": "Số average_rating >= 4.5",
    "MidRangeProduct": "Price từ 4 triệu đến 7 triệu"
}

def print_inferred_products(class_name):
    query_template = f"""
    PREFIX ex: <http://example.org/ontology#>
    SELECT ?product_info ?finalName
    WHERE {{
        ?product_info a ex:{class_name} .

        # Lấy tên trực tiếp nếu có
        OPTIONAL {{ ?product_info ex:name ?name . }}

        # Nếu không có tên, lấy từ product liên kết qua product_id
        OPTIONAL {{
            ?product_info ex:product_id ?product .
            ?product ex:name ?altName .
        }}

        BIND(COALESCE(?name, ?altName) AS ?finalName)
    }}
    """
    results = g.query(query_template)
    rows = list(results)

    print(f"\n[{class_name}] - {rule_descriptions[class_name]}")
    print(f"  → Tổng số: {len(rows)} sản phẩm")
    if not rows:
        print("  (Không có sản phẩm thỏa mãn)")
    else:
        for row in rows:
            name_display = f'"{row.finalName}"' if row.finalName else "(Không có tên)"
            print(f"  - {row.product_info} | Tên: {name_display}")


print("\n=== KẾT QUẢ SUY DIỄN ===")
for cls in rule_descriptions.keys():
    print_inferred_products(cls)

print("\nHoàn thành.")
