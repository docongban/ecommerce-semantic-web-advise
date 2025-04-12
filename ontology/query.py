from rdflib import Graph, Namespace
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Tạo graph RDF
g = Graph()

# Nạp file ontology và data
g.parse(os.path.join(BASE_DIR, "ontology.ttl"), format="turtle")
g.parse(os.path.join(BASE_DIR, "data.ttl"), format="turtle")

# Định nghĩa namespace
EX = Namespace("http://example.org/ontology#")

# Viết SPARQL query
query = """
PREFIX ex: <http://example.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?productInfo ?price ?rating
WHERE {
    ?productInfo a ex:ProductInfo ;
                 ex:price ?price ;
                 ex:average_rating ?rating .
    FILTER (?price > 5000000 && ?rating > 4.5)
}
"""

# Thực thi truy vấn
results = g.query(query)

# In kết quả
for row in results:
    print(f"ProductInfo: {row.productInfo}, Price: {row.price}, Rating: {row.rating}")
