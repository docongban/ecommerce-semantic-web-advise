from rdflib import Graph, Namespace, URIRef
import os

# Đường dẫn tuyệt đối đến thư mục chứa file hiện tại
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn đến folder Data
data_folder = os.path.join(BASE_DIR, "Data")

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

# Tạo graph và load dữ liệu
g = Graph()

print("Đang nạp ontology...")
g.parse(ontology_file_path, format="turtle")

print("Đang nạp dữ liệu...")
g.parse(data_file_path, format="turtle")

# Định nghĩa prefix
EX = Namespace("http://example.org/ontology#")
g.bind("ex", EX)

# Truy vấn SPARQL
query = """
PREFIX ex: <http://example.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?productInfo ?price ?rating
WHERE {
    ?productInfo a ex:Product_info ;
                 ex:price ?price ;
                 ex:average_rating ?rating .
    FILTER(xsd:integer(?price) > 5000000 && xsd:float(?rating) > 4.5)
}
"""

# Thực thi truy vấn
print("Đang thực thi SPARQL...")
results = g.query(query)

# In kết quả
print("Kết quả truy vấn:")
count = 0
for row in results:
    print(f"  - ProductInfo: {row.productInfo}, Price: {row.price}, Rating: {row.rating}")
    count += 1

if count == 0:
    print("  (Không có kết quả phù hợp)")

print("Hoàn thành.")
