from productAttribute import *
from productInfo import *
from productReview import *

# Đồng độ thông tin điện thoại (Dùng của Cellphones)
def productAttributeSynchronize(type):
    saveDataProductToMySQL(type)

# Đồng bộ giá và tổng quan đánh giá
def productInfoSynchronize(type):
    saveProductInfoFptToMySQL(type)

# Đồng bộ lại giá và tổng quan đánh giá
def productInfoAgainSynchronize(type):
    saveProductInfoCellphonesToMySQL(type)
    saveProductInfoFptToMySQL(type)

# Đồng bộ đánh giá
def productReviewSynchronize(type):
    saveDataReviewCellphonesToMySQL(type)
    saveDataReviewFptToMySQL(type)

# Đồng bộ tất cả
def productSynchronize(type):
    productAttributeSynchronize(type)
    productInfoSynchronize(type)
    productReviewSynchronize(type)

# Đồng bộ lại giá và đánh giá
def productAgainSynchronize(type):
    productInfoAgainSynchronize(type)
    productReviewSynchronize(type)

productSynchronize("vivo")
# productAgainSynchronize("apple")