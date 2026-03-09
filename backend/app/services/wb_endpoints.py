WB_ENDPOINTS = {
    "wb_adverts": ("GET", "https://advert-api.wildberries.ru/api/advert/v2/adverts"),
    "wb_fullstats": ("GET", "https://advert-api.wildberries.ru/adv/v3/fullstats"),
    "wb_stop": ("GET", "https://advert-api.wildberries.ru/adv/v0/stop"),
    "wb_normquery_stats": ("POST", "https://advert-api.wildberries.ru/adv/v0/normquery/stats"),
    "wb_normquery_get_minus": ("POST", "https://advert-api.wildberries.ru/adv/v0/normquery/get-minus"),
    "wb_orders": ("GET", "https://statistics-api.wildberries.ru/api/v1/supplier/orders"),
    "wb_search_report_product_search_texts": (
        "POST",
        "https://seller-analytics-api.wildberries.ru/api/v2/search-report/product/search-texts",
    ),
}
