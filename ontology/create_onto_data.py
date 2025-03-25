import mysql.connector
from rdflib import Graph, URIRef, Literal, Namespace, OWL, XSD
from rdflib.namespace import RDF, RDFS

config = {
    'user': 'root',
    'password': '123456',
    'host': '127.0.0.1',
    'database': 'websemantic'
}

# Lấy thông tin data
def get_data(query):
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()

# Lấy thông tin cột
def get_table_columns(table_name):
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()

# Truy vấn
categories = get_data("SELECT * FROM category")
products = get_data("SELECT * FROM product")
product_infos = get_data("SELECT * FROM product_info")
product_reviews = get_data("SELECT * FROM product_review")

if categories and products and product_infos and product_reviews:
    print("Dữ liệu đã được truy xuất thành công.")
else:
    print("Có lỗi xảy ra khi truy xuất dữ liệu.")

# Tạo Graph
g = Graph()
namespace = "http://example.org/data/"
ontology_uri = "http://example.org/ontology/" # URI cho ontology
ex = Namespace(ontology_uri)  # Namespace cho ontology
SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
SWRLB = Namespace("http://www.w3.org/2003/11/swrlb#")
g.bind("ex", ex)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("owl", OWL)
g.bind("xsd", XSD)
g.bind("swrl", SWRL)
g.bind("swrlb", SWRLB)

# Thêm các triples mô tả ontology
g.add((URIRef(ontology_uri), RDF.type, OWL.Ontology))
# Thêm dữ liệu từ bảng category
if categories:
    for category in categories:
        category_uri = URIRef(namespace + "category/" + str(category[0]))
        g.add((category_uri, RDF.type, ex.Category))
        g.add((category_uri, ex.id_category, Literal(category[0])))
        if category[1] is not None:
            g.add((category_uri, ex.original_category_id, Literal(category[1])))
        if category[2] is not None:
            g.add((category_uri, ex.name_category, Literal(category[2])))
        if category[3] is not None:
            g.add((category_uri, ex.sku_category, Literal(category[3])))

# Thêm dữ liệu từ bảng product
if products:
    for product in products:
        product_uri = URIRef(namespace + "product/" + str(product[0]))
        g.add((product_uri, RDF.type, ex.Product))
        g.add((product_uri, ex.id_product, Literal(product[0])))
        if product[1] is not None:
            category_uri = URIRef(namespace + "category/" + str(product[1]))
            g.add((product_uri, ex.has_category, category_uri))
        if product[2] is not None:
            g.add((product_uri, ex.name_product, Literal(product[2])))
        if product[3] is not None:
            g.add((product_uri, ex.sku_product, Literal(product[3])))
        if product[4] is not None:
            g.add((product_uri, ex.display_size, Literal(product[4])))
        if product[5] is not None:
            g.add((product_uri, ex.display_resolution, Literal(product[5])))
        if product[6] is not None:
            g.add((product_uri, ex.display_type, Literal(product[6])))
        if product[7] is not None:
            g.add((product_uri, ex.display_rate, Literal(product[7])))
        if product[8] is not None:
            g.add((product_uri, ex.camera_primary, Literal(product[8])))
        if product[9] is not None:
            g.add((product_uri, ex.camera_secondary, Literal(product[9])))
        if product[10] is not None:
            g.add((product_uri, ex.camera_feature, Literal(product[10])))
        if product[11] is not None:
            g.add((product_uri, ex.operating_system, Literal(product[11])))
        if product[12] is not None:
            g.add((product_uri, ex.operating_system_version, Literal(product[12])))
        if product[13] is not None:
            g.add((product_uri, ex.memory_internal, Literal(product[13])))
        if product[14] is not None:
            g.add((product_uri, ex.memory_card_slot, Literal(product[14])))
        if product[15] is not None:
            g.add((product_uri, ex.memory_filter, Literal(product[15])))
        if product[16] is not None:
            g.add((product_uri, ex.storage, Literal(product[16])))
        if product[17] is not None:
            g.add((product_uri, ex.storage_filter, Literal(product[17])))
        if product[18] is not None:
            g.add((product_uri, ex.chipset, Literal(product[18])))
        if product[19] is not None:
            g.add((product_uri, ex.nfc, Literal(product[19])))
        if product[20] is not None:
            g.add((product_uri, ex.sim, Literal(product[20])))
        if product[21] is not None:
            g.add((product_uri, ex.internet, Literal(product[21])))
        if product[22] is not None:
            g.add((product_uri, ex.battery, Literal(product[22])))
        if product[23] is not None:
            g.add((product_uri, ex.charg_type, Literal(product[23])))
        if product[24] is not None:
            g.add((product_uri, ex.charg, Literal(product[24])))
        if product[25] is not None:
            g.add((product_uri, ex.weight, Literal(product[25])))
        if product[26] is not None:
            g.add((product_uri, ex.special_feature, Literal(product[26])))

# Thêm dữ liệu từ bảng product_info
if product_infos:
    for info in product_infos:
        info_uri = URIRef(namespace + "product_info/" + str(info[0]))
        g.add((info_uri, RDF.type, ex.ProductInfo))
        g.add((info_uri, ex.id_product_info, Literal(info[0])))
        product_uri = URIRef(namespace + "product/" + str(info[1]))
        g.add((info_uri, ex.has_info, product_uri))
        if info[2] is not None:
            g.add((info_uri, ex.original_product_id_info, Literal(info[2])))
        if info[3] is not None:
            g.add((info_uri, ex.ecom, Literal(info[3])))
        if info[4] is not None:
            g.add((info_uri, ex.price, Literal(info[4])))
        if info[5] is not None:
            g.add((info_uri, ex.special_price_info, Literal(info[5])))
        if info[6] is not None:
            g.add((info_uri, ex.total_rating, Literal(info[6])))
        if info[7] is not None:
            g.add((info_uri, ex.average_rating, Literal(info[7])))

# Thêm dữ liệu từ bảng product_review
if product_reviews:
    for review in product_reviews:
        review_uri = URIRef(namespace + "product_review/" + str(review[0]))
        g.add((review_uri, RDF.type, ex.ProductReview))
        g.add((review_uri, ex.id_product_review, Literal(review[0])))
        product_uri = URIRef(namespace + "product/" + str(review[1]))
        g.add((review_uri, ex.has_review, product_uri))
        if review[2] is not None:
            g.add((review_uri, ex.original_product_id, Literal(review[2])))
        if review[3] is not None:
            g.add((review_uri, ex.original_review_id, Literal(review[3])))
        if review[4] is not None:
            g.add((review_uri, ex.ecom_review, Literal(review[4])))
        if review[5] is not None:
            g.add((review_uri, ex.content, Literal(review[5])))
        if review[6] is not None:
            g.add((review_uri, ex.rate, Literal(review[6])))

# Lưu ontology vào file
# Tạo Graph
g_ontology = Graph()
ontology_uri = "http://example.org/ontology/"  # URI cho ontology
ex = Namespace(ontology_uri)  # Namespace cho ontology
g_ontology.bind("ex", ex)
g_ontology.bind("rdf", RDF)
g_ontology.bind("rdfs", RDFS)
g_ontology.bind("owl", OWL)
g_ontology.bind("xsd", XSD)

# 1. Định nghĩa các lớp (Classes) tương ứng với các bảng
tables = ["category", "product", "product_info", "product_review"]
for table_name in tables:
    class_uri = URIRef(ex[table_name.capitalize()])  # Ví dụ: ex:Category
    g_ontology.add((class_uri, RDF.type, OWL.Class))
    g_ontology.add((class_uri, RDFS.label, Literal(table_name.capitalize()))) # Thêm label cho class

# 2. Định nghĩa các thuộc tính (Properties) tương ứng với các cột
for table_name in tables:
    columns = get_table_columns(table_name)
    if columns:
        for column in columns:
            column_name = column[0]
            property_uri = URIRef(ex[column_name])  # Ví dụ: ex:id_category
            g_ontology.add((property_uri, RDF.type, OWL.ObjectProperty if column[1].startswith('int') or column[1].startswith('varchar') else OWL.DatatypeProperty)) # Xác định là ObjectProperty hay DatatypeProperty
            g_ontology.add((property_uri, RDFS.domain, URIRef(ex[table_name.capitalize()]))) # Đặt domain
            g_ontology.add((property_uri, RDFS.label, Literal(column_name))) # Thêm label cho property

# Lưu cấu trúc ontology vào file owl
g_ontology.serialize("ontology.owl", format="xml")
print("Lưu ontology vào file ontology.owl thành công")

# Lưu dữ liệu vào file turtle
g.serialize("data.ttl", format="turtle")
print("Lưu dữ liệu vào file data.ttl thành công")