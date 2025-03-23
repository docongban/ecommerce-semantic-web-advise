from ultils.callApi import *
from ultils.mysql import *

# Lấy tất cả sản phẩm theo category từ MySQL
def getAllProductByCategoryFromMysql(category, ecom):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        sql = f"""
            SELECT pi.original_product_id, p.* FROM product p
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

# Lấy đánh giá mới nhất từ MySQL
def getLastReviewFromMysql(productId, ecom):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        sql = f"""
            SELECT * FROM product_review
            WHERE product_id = {productId} AND ecom = '{ecom}'
            ORDER BY original_review_id DESC
            LIMIT 1
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"❌ Lỗi khi select từ MySQL: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Lấy đánh giá trên Cellphones
def getReviewByProductIdCellphones(productId, page):
    url = "https://api.cellphones.com.vn/graphql-customer/graphql/query"
    payload = {
        "query": f"""query {{
            reviews(
                filter: {{
                    product_id: {productId},
                }},
                page: {page},
            ) {{
                matches {{
                    id
                    content
                    rating_id
                }}
                total
            }}
        }}""",
        "variables": {}
    }
    
    response = callApiCellphones(url, payload)
    return response.get("data").get("reviews").get("matches")

# Lấy đánh giá trên Fpt
def getReviewByProductIdFpt(productId, page):
    url = "https://papi.fptshop.com.vn/gw/v1/public/bff-before-order/comment/list"
    payload = {
        "content": {
            "id": productId,
            "type": "PRODUCT"
        },
        "state": [
            "ACTIVE"
        ],
        "score": [
            "4","5","3","2","1"
        ],
        "skipCount": 10 * page,
        "maxResultCount": 10,
        "sortMethod": 1
    }
    response = callApiFpt("post", url, payload)
    if response:
        return response.get("data").get("items")
    return

# Lưu dữ liệu đánh giá Cellphones vào MySQL
def saveDataReviewCellphonesToMySQL(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        products = getAllProductByCategoryFromMysql(category, "CELLPHONES")
        if products:
            reviewList = []
            for product in products:
                originalProductId = product[0]
                productId = product[1]
                lastReview = getLastReviewFromMysql(productId, "CELLPHONES")
                if lastReview:
                    lastReviewId = lastReview[0]
                else:
                    lastReviewId = 0
                for page in range(1, 10):
                    reviews = getReviewByProductIdCellphones(originalProductId, page)
                    if reviews:
                        for review in reviews:
                            if review.get("id") > lastReviewId:
                                print(f"---INSERT_REVIEW_{productId}_{page}--",review)
                                reviewList.append({
                                    "product_id": productId,
                                    "original_product_id": originalProductId,
                                    "original_review_id": review.get("id"),
                                    "ecom": "CELLPHONES",
                                    "content": review.get("content"),
                                    "rate": review.get("rating_id"),
                                })
                    else:
                        break
            if reviewList:
                insertAllToMysql("product_review", reviewList, cursor)
                conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi xảy ra, đã rollback dữ liệu: {e}")
    finally:
        cursor.close()
        conn.close()

# Lưu dữ liệu đánh giá Fpt vào MySQL
def saveDataReviewFptToMySQL(category):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        products = getAllProductByCategoryFromMysql(category, "FPT")
        if products:
            reviewList = []
            for product in products:
                originalProductId = product[0]
                productId = product[1]
                lastReview = getLastReviewFromMysql(productId, "FPT")
                if lastReview:
                    lastReviewId = lastReview[0]
                else:
                    lastReviewId = 0
                for page in range(0, 1000):
                    reviews = getReviewByProductIdFpt(originalProductId, page)
                    if reviews:
                        for review in reviews:
                            if review.get("id") > lastReviewId:
                                print(f"---INSERT_REVIEW_{productId}_{page}--",review)
                                reviewList.append({
                                    "product_id": productId,
                                    "original_product_id": originalProductId,
                                    "original_review_id": review.get("id"),
                                    "ecom": "FPT",
                                    "content": review.get("content"),
                                    "rate": review.get("score"),
                                })
                    else:
                        break
            if reviewList:
                insertAllToMysql("product_review", reviewList, cursor)
                conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi xảy ra, đã rollback dữ liệu: {e}")
    finally:
        cursor.close()
        conn.close()

# saveDataReviewCellphonesToMySQL("samsung")
# saveDataReviewFptToMySQL("samsung")