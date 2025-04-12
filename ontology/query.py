from rdflib import Graph, Namespace
import os

# Đường dẫn tuyệt đối đến thư mục chứa file hiện tại
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn đến folder Data
data_folder = os.path.join(BASE_DIR, "Data")

# Đường dẫn đến file ontology và data
ontology_file_path = os.path.join(data_folder, "ontology.ttl")
data_file_path = os.path.join(data_folder, "data.ttl")
inferred_file_path = os.path.join(data_folder, "inferred.ttl")

# Kiểm tra sự tồn tại của file
if not os.path.exists(ontology_file_path):
    print(f"Lỗi: Không tìm thấy file ontology tại {ontology_file_path}")
    exit()
if not os.path.exists(data_file_path):
    print(f"Lỗi: Không tìm thấy file data tại {data_file_path}")
    exit()

# Tạo graph và load dữ liệu
g = Graph()

print("Đang nạp ontology...")
g.parse(ontology_file_path, format="turtle")

print("Đang nạp dữ liệu...")
g.parse(data_file_path, format="turtle")

# Định nghĩa prefix
EX = Namespace("http://example.org/ontology#")
g.bind("ex", EX)

# === Các luật suy diễn bằng SPARQL CONSTRUCT ===
rules = [
    # Luật 1: PremiumProduct
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
    # Luật 2: BudgetProduct
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
    # Luật 3: RecommendedProduct
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
    # Luật 4: PopularProduct
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:PopularProduct .
    }
    WHERE {
        ?s ex:number_of_reviews ?n .
        FILTER(xsd:integer(?n) > 1000)
    }
    """,
    # Luật 5: UntrustworthyProduct
    """
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a ex:UntrustworthyProduct .
    }
    WHERE {
        ?s ex:average_rating ?r ;
           ex:number_of_reviews ?n .
        FILTER(xsd:float(?r) < 3.0 && xsd:integer(?n) > 500)
    }
    """
]

print("Đang thực hiện suy diễn logic bằng SPARQL CONSTRUCT...")
for i, rule in enumerate(rules):
    inferred = g.query(rule)
    for triple in inferred:
        g.add(triple)
    print(f"  - Luật {i+1} đã được áp dụng.")

# Ghi graph sau suy diễn ra file
g.serialize(destination=inferred_file_path, format="turtle")
print(f"\nĐã ghi graph suy diễn vào file: {inferred_file_path}")

# === In kết quả của từng luật đã áp dụng ===
rule_descriptions = {
    "PremiumProduct": "Giá > 10 triệu và Rating > 4.5",
    "BudgetProduct": "Giá < 2 triệu",
    "RecommendedProduct": "Là BudgetProduct và Rating >= 4.0",
    "PopularProduct": "Số review > 1000",
    "UntrustworthyProduct": "Rating < 3.0 và review > 500"
}

def print_inferred_products(class_name):
    query_template = f"""
    PREFIX ex: <http://example.org/ontology#>
    SELECT ?product
    WHERE {{
        ?product a ex:{class_name} .
    }}
    """
    results = g.query(query_template)
    count = 0
    print(f"\n[{class_name}] - {rule_descriptions[class_name]}")
    for row in results:
        print(f"  - {row.product}")
        count += 1
    if count == 0:
        print("  (Không có sản phẩm thỏa mãn)")

# In tất cả loại sản phẩm suy diễn
print("\n=== KẾT QUẢ SUY DIỄN ===")
for cls in rule_descriptions.keys():
    print_inferred_products(cls)

print("\nHoàn thành.")
