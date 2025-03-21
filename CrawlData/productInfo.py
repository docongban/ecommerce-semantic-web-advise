from ultils.callApi import *
from ultils.mysql import *

# Lấy tất cả product_info theo category từ MySQL
def getAllProductInfoByCategoryFromMysql(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        sql = f"""
            SELECT pi.* FROM product p
            JOIN product_info pi ON p.id = pi.product_id
            JOIN category c ON c.id = p.category_id
            WHERE c.sku = '{category}'
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"❌ Lỗi khi select từ MySQL: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Lấy thông tin tất cả sản phẩm theo productId từ API Cellphones
def getProductInfoByProductId(productId):
    url = "https://api.cellphones.com.vn/v2/graphql/query"
    payload = {
        "query": f"""query getProductDataDetail {{
            product(
                id: {productId},
                provinceId: 24,
            ) {{
                general {{
                    name
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
    return response.get("data").get("product")

# Lưu dữ liệu product_info Cellphones vào MySQL
def saveProductInfoCellphonesToMySQL(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        productInfos = getAllProductInfoByCategoryFromMysql(category)
        productInfoList = []
        if productInfos:
            for productInfo in productInfos:
                product = getProductInfoByProductId(productInfo[2])
                productInfoList.append({
                    "id": productInfo[0],
                    "product_id": productInfo[1],
                    "original_product_id": productInfo[2],
                    "ecom": productInfo[3],
                    "price": product.get("filterable").get("price"),
                    "special_price": product.get("filterable").get("special_price"),
                    "total_rating": product.get("general").get("review").get("total_count"),
                    "average_rating": product.get("general").get("review").get("average_rating"),
                })
                print(f"---UPDATE_PRODUCT_INFO_{productInfo[2]}---", product.get("general").get("name"))
            if productInfoList:
                insertAllToMysql("product_info", productInfoList, cursor)
                conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi xảy ra, đã rollback dữ liệu: {e}")
    finally:
        cursor.close()
        conn.close()

saveProductInfoCellphonesToMySQL("samsung")