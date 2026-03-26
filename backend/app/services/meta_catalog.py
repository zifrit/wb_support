from backend.app.schemas.meta import EndpointMeta, FieldMeta


def get_endpoint_catalog() -> list[EndpointMeta]:
    return [
        EndpointMeta(
            id="wb_adverts",
            title="Информация о кампании (статус РК)",
            method="POST",
            path="/wb/adverts",
            requiresUsername=True,
            query=[
                FieldMeta(name="shop_id", type="int", required=True, description="ID магазина"),
                FieldMeta(name="ids", type="string", required=False, description="CSV id кампаний: 123,456"),
                FieldMeta(name="statuses", type="string", required=False, description="CSV статусов: 9,11"),
                FieldMeta(name="payment_type", type="string", required=False, description="cpm | cpc"),
            ],
        ),
        EndpointMeta(
            id="wb_fullstats",
            title="Статистика кампаний",
            method="POST",
            path="/wb/fullstats",
            requiresUsername=True,
            query=[
                FieldMeta(name="shop_id", type="int", required=True, description="ID магазина"),
                FieldMeta(name="ids", type="string", required=True, description="CSV advert ids"),
                FieldMeta(name="beginDate", type="string", required=True, description="YYYY-MM-DD"),
                FieldMeta(name="endDate", type="string", required=True, description="YYYY-MM-DD"),
            ],
        ),
        EndpointMeta(
            id="wb_normquery_stats",
            title="Статистика поисковых кластеров",
            method="POST",
            path="/wb/normquery/stats",
            requiresUsername=True,
            query=[FieldMeta(name="shop_id", type="int", required=True, description="ID магазина")],
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_normquery_get_minus",
            title="Список минус-фраз кампаний",
            method="POST",
            path="/wb/normquery/get-minus",
            requiresUsername=True,
            query=[FieldMeta(name="shop_id", type="int", required=True, description="ID магазина")],
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_orders",
            title="Заказы",
            method="POST",
            path="/wb/orders",
            requiresUsername=True,
            query=[
                FieldMeta(name="shop_id", type="int", required=True, description="ID магазина"),
                FieldMeta(name="dateFrom", type="string", required=True, description="YYYY-MM-DD"),
                FieldMeta(name="flag", type="int", required=False, description="Default 0"),
            ],
        ),
        EndpointMeta(
            id="wb_search_report_product_search_texts",
            title="Поисковые запросы по товару",
            method="POST",
            path="/wb/search-report/product/search-texts",
            requiresUsername=True,
            query=[FieldMeta(name="shop_id", type="int", required=True, description="ID магазина")],
            body={"type": "object"},
        ),
    ]
