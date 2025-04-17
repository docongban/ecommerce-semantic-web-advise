from rdflib import Graph, Namespace
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
# query = """
# PREFIX ex: <http://example.org/ontology#>
# PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# SELECT ?productInfo ?price ?rating
# WHERE {
#     ?productInfo a ex:Product_info ;
#                  ex:price ?price ;
#                  ex:average_rating ?rating .
#     FILTER(xsd:integer(?price) > 5000000 && xsd:float(?rating) > 4.5)
# }
# """
query = """
PREFIX ex: <http://example.org/ontology#>

SELECT ?name ?battery
WHERE {
  ?product a ex:Product ;
           ex:name ?name ;
           ex:battery ?battery .
  FILTER(CONTAINS(LCASE(STR(?name)), "iphone 15")&&
         CONTAINS(LCASE(STR(?name)), "256gb") &&
         CONTAINS(LCASE(STR(?name)), "256gb") &&
         CONTAINS(LCASE(STR(?name)), "pro max"))
}
"""
query = """
PREFIX ex: <http://example.org/ontology#>

SELECT ?name ?price ?ecom
WHERE {
  ?product a ex:Product ;
           ex:name ?name ;
           ex:id ?id .
  ?product_info a ex:Product_info ;
                ex:product_id ?id ;
                ex:ecom ?ecom ;
                ex:price ?price .
  FILTER(CONTAINS(LCASE(STR(?name)), "iphone 15"))
}
"""

query = """
PREFIX ex: <http://example.org/ontology#>

            SELECT ?name 
            WHERE {
            ?product a ex:Product ;
                    ex:name ?name ;
        
 ex:id ?id .
                ?product_info a ex:Product_info ;
                            ex:product_id ?id ;
ex:special_price ?special_price  .
            FILTER(CONTAINS(LCASE(STR(?name)), "iphone") && xsd:float(?special_price) >= 10000000 && xsd:float(?special_price) <= 20000000 )
            }
            LIMIT 1
"""

# Thực thi truy vấn
print("Đang thực thi SPARQL...")
results = g.query(query)

# In kết quả
print("Kết quả truy vấn:")
count = 0
for row in results:
    # print(f"  - ProductInfo: {row.productInfo}, Price: {row.price}, Rating: {row.rating}")
    print(row)
    count += 1

if count == 0:
    print("  (Không có kết quả phù hợp)")

print("Hoàn thành.")
