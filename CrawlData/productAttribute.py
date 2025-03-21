from ultils.callApi import *
from ultils.mysql import *

# Lấy thông tin category từ API Cellphones
def getCategoryInfo(category):
    url = "https://api.cellphones.com.vn/graphql-url/graphql/query"
    payload = {
        "query": f"""query URL_INFO {{
            url_info(request_path: "/mobile/{category}.html") {{
                id
                category_id
                request_path
                target_path
                h1_title
                meta_title
                meta_keywords
                meta_description
                canonical
            }}
        }}""",
        "variables": {}
    }

    response = callApiCellphones(url, payload)
    return response.get("data").get("url_info")

# Lấy thông tin tất cả sản phẩm theo category từ API Cellphones
def getAllProductByCategory(categoryId):
    url = "https://api.cellphones.com.vn/v2/graphql/query"
    payload = {
        "query": f"""query GetProductsByCateId {{
            products(
                filter: {{
                    static: {{
                        categories: ["{categoryId}"],
                        province_id: 24,
                        stock: {{
                            from: 0
                        }},
                    }},
                }},
                page: 1,
                size: 1000,
                sort: [{{view: desc}}],
            ) {{
                general {{
                    product_id
                    name
                    attributes
                    sku
                    review{{
                        total_count
                        average_rating
                    }}
                }}
                filterable {{
                    price
                    special_price
                }}
            }}
        }}""",
        "variables": {}
    }
    
    response = callApiCellphones(url, payload)
    return response.get("data").get("products")

# Lưu dữ liệu sản phẩm, product_info Cellphones vào MySQL
def saveDataProductToMySQL(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        categoryInfo = getCategoryInfo(category)
        categoryId = categoryInfo.get("category_id")
        categoryItem = {
            "original_category_id": categoryId,
            "name": categoryInfo.get("h1_title"),
            "sku": category,
        }
        print(f"---INSERT_CATEGORY_{category}---", categoryItem)
        category_id = insertToMysql("category", categoryItem, cursor)

        products = getAllProductByCategory(categoryId)
        if products:
            productList = []
            for product in products:
                attributes = product.get("general").get("attributes", {})
                productList.append({
                    "category_id": category_id,
                    "name": product.get("general").get("name"),
                    "sku": product.get("general").get("sku"),
                    "display_size": attributes.get("display_size"),
                    "display_resolution": attributes.get("display_resolution"),
                    "display_type": attributes.get("mobile_type_of_display"),
                    "display_rate": attributes.get("mobile_tan_so_quet"),
                    "camera_primary": attributes.get("camera_primary"),
                    "camera_secondary": attributes.get("camera_secondary"),
                    "camera_feature": attributes.get("mobile_tinh_nang_camera"),
                    "operating_system": attributes.get("operating_system"),
                    "operating_system_version": attributes.get("os_version"),
                    "memory_internal": attributes.get("memory_internal"),
                    "memory_card_slot": attributes.get("memory_card_slot"),
                    "memory_filter": attributes.get("mobile_ram_filter"),
                    "storage": attributes.get("storage"),
                    "storage_filter": attributes.get("mobile_storage_filter"),
                    "chipset": attributes.get("chipset"),
                    "nfc": attributes.get("mobile_nfc"),
                    "sim": attributes.get("sim"),
                    "internet": attributes.get("loai_mang"),
                    "battery": attributes.get("battery"),
                    "charg_type": attributes.get("mobile_cong_sac"),
                    "charg": attributes.get("mobile_cong_nghe_sac"),
                    "weight": attributes.get("product_weight"),
                    "special_feature": attributes.get("mobile_tinh_nang_dac_biet"),
                })
                print(f"---INSERT_PRODUCT_{product.get('general').get('product_id')}---", product.get("general").get("name"))
            productIds = insertAllToMysql("product", productList, cursor)

            productInfoList = []
            for index, product in enumerate(products):
                productInfoList.append({
                    "product_id": productIds[index],
                    "original_product_id": product.get("general").get("product_id"),
                    "ecom": "CELLPHONES",
                    "price": product.get("filterable").get("price"),
                    "special_price": product.get("filterable").get("special_price"),
                    "total_rating": product.get("general").get("review").get("total_count"),
                    "average_rating": product.get("general").get("review").get("average_rating"),
                })
                print(f"---INSERT_PRODUCT_INFO_{product.get('general').get('product_id')}---", product.get("general").get("name"))
            insertAllToMysql("product_info", productInfoList, cursor)

            conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi xảy ra, đã rollback dữ liệu: {e}")
    finally:
        cursor.close()
        conn.close()

# saveDataProductToMySQL("samsung")