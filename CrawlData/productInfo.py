import urllib.parse

from ultils.callApi import *
from ultils.mysql import *

# Lấy tất cả sản phẩm theo category từ MySQL
def getAllProductByCategoryFromMysql(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        sql = f"""
            SELECT p.* FROM product p
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

# Lấy tất cả product_info theo category từ MySQL
def getAllProductInfoByCategoryFromMysql(category, ecom):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        sql = f"""
            SELECT pi.*, p.sku FROM product p
            JOIN product_info pi ON p.id = pi.product_id
            JOIN category c ON c.id = p.category_id
            WHERE c.sku = '{category}' AND pi.ecom = '{ecom}'
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

# Lấy thông tin tổng quan sản phẩm từ API FPT
def getProductPreviewFromPathFpt(path):
    url = f"https://papi.fptshop.com.vn/gw/v1/public/bff-before-order/product?slug={urllib.parse.quote(path)}"
    response = callApiFpt("get", url, {})
    if response:
        return response.get("data").get("upc")
    return

# Lấy thông tin sản phẩm từ API FPT
def getProductInfoByProductIdFpt(productId):
    url = "https://papi.fptshop.com.vn/gw/v1/public/fulltext-search-service/product-by-upcs"
    payload = {
        "upcs": [productId]
    }
    response = callApiFpt("post", url, payload)
    if response:
        return response[0]
    return

# Lấy tổng hợp đánh giá sản phẩm từ API FPT
def getProductReviewOverviewByProductIdFpt(productId):
    url = f"https://papi.fptshop.com.vn/gw/v1/public/bff-before-order/comment/get-summary-rating-score?contentId={productId}"
    response = callApiFpt("get", url, {})
    if response:
        return response.get("data")
    return

# Lưu dữ liệu product_info Cellphones vào MySQL
def saveProductInfoCellphonesToMySQL(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        productInfos = getAllProductInfoByCategoryFromMysql(category, "CELLPHONES")
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

# Lưu dữ liệu product_info FPT vào MySQL
def saveProductInfoFptToMySQL(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        productInfos = getAllProductInfoByCategoryFromMysql(category, "FPT")
        productInfoList = []
        if productInfos:
            for productInfo in productInfos:
                productInfoNew = getProductInfoByProductIdFpt(productInfo[2])
                productReview = getProductReviewOverviewByProductIdFpt(productInfo[2])
                productInfoList.append({
                    "id": productInfo[0],
                    "product_id": productInfo[1],
                    "original_product_id": productInfo[2],
                    "ecom": productInfo[3],
                    "price": productInfoNew.get("originalPrice"),
                    "special_price": productInfoNew.get("currentPrice"),
                    "total_rating": productReview.get("totalRating"),
                    "average_rating": productReview.get("averageScore"),
                })
                print(f"---UPDATE_PRODUCT_INFO_{productInfo[2]}---", productInfoNew.get("name"))
        else:
            products = getAllProductByCategoryFromMysql(category)
            if products:
                for product in products:
                    sku = product[3]
                    path = sku
                    if sku.startswith("dien-thoai-"): path = sku.split("dien-thoai-")[1]
                    productPreview = getProductPreviewFromPathFpt(f"dien-thoai/{path}")
                    if productPreview:
                        productInfo = getProductInfoByProductIdFpt(productPreview.get("code"))
                        productReview = getProductReviewOverviewByProductIdFpt(productPreview.get("code"))
                        productInfoList.append({
                            "product_id": product[0],
                            "original_product_id": productInfo.get("code"),
                            "ecom": "FPT",
                            "price": productInfo.get("originalPrice"),
                            "special_price": productInfo.get("currentPrice"),
                            "total_rating": productReview.get("totalRating"),
                            "average_rating": productReview.get("averageScore"),
                        })
                        print(f"---INSERT_PRODUCT_INFO_{productInfo.get('code')}---", product[2])          
                    
        if productInfoList:
            insertAllToMysql("product_info", productInfoList, cursor)
            conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi xảy ra, đã rollback dữ liệu: {e}")
    finally:
        cursor.close()
        conn.close()

# saveProductInfoCellphonesToMySQL("samsung")
# saveProductInfoFptToMySQL("samsung")