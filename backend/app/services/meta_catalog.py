from backend.app.schemas.meta import EndpointMeta


def get_endpoint_catalog() -> list[EndpointMeta]:
    return [
        EndpointMeta(
            id="wb_adverts",
            title="Информация о кампании (статус РК)",
            method="POST",
            path="/wb/adverts",
            requiresUsername=True,
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_fullstats",
            title="Статистика кампаний",
            method="POST",
            path="/wb/fullstats",
            requiresUsername=True,
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_stop",
            title="Завершение кампании",
            method="POST",
            path="/wb/stop",
            requiresUsername=True,
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_normquery_stats",
            title="Статистика поисковых кластеров",
            method="POST",
            path="/wb/normquery/stats",
            requiresUsername=True,
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_normquery_get_minus",
            title="Список минус-фраз кампаний",
            method="POST",
            path="/wb/normquery/get-minus",
            requiresUsername=True,
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_orders",
            title="Заказы",
            method="POST",
            path="/wb/orders",
            requiresUsername=True,
            body={"type": "object"},
        ),
        EndpointMeta(
            id="wb_search_report_product_search_texts",
            title="Поисковые запросы по товару",
            method="POST",
            path="/wb/search-report/product/search-texts",
            requiresUsername=True,
            body={"type": "object"},
        ),
    ]
