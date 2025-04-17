import mysql.connector
import os
from rdflib import Graph, URIRef, Literal, Namespace, OWL, XSD, BNode
from rdflib.namespace import RDF, RDFS

# Cấu hình kết nối CSDL
config = {
    'user': 'root',
    'password': '123456',
    'host': '127.0.0.1',
    'database': 'websemantic'
}

tables = ["category", "product", "product_info", "product_review"]
os.makedirs("Data", exist_ok=True)

# Hàm lấy dữ liệu từ DB
def get_data(query):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()

# Lấy thông tin cột của bảng
def get_table_columns(table_name):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()

# Lấy foreign key
def get_foreign_keys():
    query = """
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
    """
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query, (config["database"],))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if conn:
            conn.close()

# Lấy dữ liệu
data_map = {table: get_data(f"SELECT * FROM {table}") for table in tables}

# Ontology
g_onto = Graph()
ex = Namespace("http://example.org/ontology#")
g_onto.bind("ex", ex)
g_onto.bind("rdf", RDF)
g_onto.bind("rdfs", RDFS)
g_onto.bind("owl", OWL)
g_onto.bind("xsd", XSD)

# Tạo lớp
for table in tables:
    class_uri = URIRef(ex[table.capitalize()])
    g_onto.add((class_uri, RDF.type, OWL.Class))
    g_onto.add((class_uri, RDFS.label, Literal(table.capitalize())))

# ✅ Ràng buộc: Category và Product không giao nhau
g_onto.add((ex.Category, OWL.disjointWith, ex.Product))

# ✅ Ràng buộc nâng cao: Product_info phải có giá cụ thể (giả sử = 0 để dùng OWL.hasValue)
restriction = BNode()
g_onto.add((restriction, RDF.type, OWL.Restriction))
g_onto.add((restriction, OWL.onProperty, ex.price))
g_onto.add((restriction, OWL.hasValue, Literal(0, datatype=XSD.integer)))
g_onto.add((ex.Product_info, OWL.equivalentClass, restriction))

# Lấy khóa ngoại
foreign_keys = get_foreign_keys()
foreign_key_map = {(fk[0], fk[1]): (fk[2], fk[3]) for fk in foreign_keys}

# Tạo properties
for table in tables:
    class_uri = URIRef(ex[table.capitalize()])
    columns = get_table_columns(table)
    for column in columns:
        col_name, col_type = column[0], column[1]
        property_uri = URIRef(ex[col_name])

        # Foreign key → ObjectProperty
        if (table, col_name) in foreign_key_map:
            target_table = foreign_key_map[(table, col_name)][0]
            g_onto.add((property_uri, RDF.type, OWL.ObjectProperty))
            g_onto.add((property_uri, RDFS.domain, class_uri))
            g_onto.add((property_uri, RDFS.range, URIRef(ex[target_table.capitalize()])))

            # ✅ FunctionalProperty cho category_id
            if col_name == "category_id":
                g_onto.add((property_uri, RDF.type, OWL.FunctionalProperty))

        else:
            # DatatypeProperty
            g_onto.add((property_uri, RDF.type, OWL.DatatypeProperty))
            g_onto.add((property_uri, RDFS.domain, class_uri))

            # ✅ FunctionalProperty cho các thuộc tính cụ thể
            if col_name in ["price", "average_rating", "name", "rate"]:
                g_onto.add((property_uri, RDF.type, OWL.FunctionalProperty))

            # Gán kiểu dữ liệu
            if col_name in ["price", "discount_price", "monthly_price"]:
                xsd_type = XSD.integer
            elif col_name in ["stock", "rate", "total_rating"]:
                xsd_type = XSD.integer
            elif col_name in ["average_rating"]:
                xsd_type = XSD.float
            else:
                xsd_type = XSD.string

            g_onto.add((property_uri, RDFS.range, xsd_type))

        g_onto.add((property_uri, RDFS.label, Literal(col_name)))

# Lưu ontology
onto_path = os.path.join("Data", "ontology.ttl")
g_onto.serialize(onto_path, format="turtle")
print(f"✔ Ontology đã lưu vào {onto_path}")

# RDF Data
g_data = Graph()
data_ns = Namespace("http://example.org/data/")
g_data.bind("ex", ex)
g_data.bind("data", data_ns)

def create_uri(table, id_value):
    return URIRef(data_ns + f"{table}/{id_value}")

for table, rows in data_map.items():
    columns = get_table_columns(table)
    for row in rows:
        subject = create_uri(table, row[0])
        g_data.add((subject, RDF.type, ex[table.capitalize()]))

        for idx, column in enumerate(columns):
            col_name = column[0]
            value = row[idx]
            if value is None:
                continue
            predicate = URIRef(ex[col_name])

            # Foreign key → URI
            if (table, col_name) in foreign_key_map:
                ref_table = foreign_key_map[(table, col_name)][0]
                obj_uri = create_uri(ref_table, value)
                g_data.add((subject, predicate, obj_uri))
            else:
                # Literal
                if col_name in ["price", "discount_price", "monthly_price"]:
                    lit = Literal(value, datatype=XSD.integer)
                elif col_name in ["stock", "rate", "total_rating"]:
                    lit = Literal(value, datatype=XSD.integer)
                elif col_name == "average_rating":
                    lit = Literal(value, datatype=XSD.float)
                else:
                    lit = Literal(str(value), datatype=XSD.string)
                g_data.add((subject, predicate, lit))

        # Gán ex:name cho product_info từ product
        if table == "product_info":
            product_id = row[1]
            product_data = next((r for r in data_map["product"] if r[0] == product_id), None)
            if product_data:
                product_name = product_data[2]  # Giả sử cột name là cột thứ 3
                g_data.add((subject, ex.name, Literal(product_name, datatype=XSD.string)))
                print(f"[INFO] Gán tên '{product_name}' cho {subject}")
            else:
                g_data.add((subject, ex.name, Literal(f"Unknown Product {row[0]}", datatype=XSD.string)))

# Lưu RDF
data_path = os.path.join("Data", "data.ttl")
g_data.serialize(data_path, format="turtle")
print(f"✔ RDF data đã lưu vào {data_path}")
