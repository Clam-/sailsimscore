from paginate_sqlalchemy import SqlalchemyOrmPage

def paginator(request, q, pp=50):
    query_params = request.params.mixed()
    page = int(request.params.get("page", 1))
    def url_maker(link_page):
        query_params['page'] = link_page
        return request.current_route_url(_query=query_params)
    return SqlalchemyOrmPage(q, page, items_per_page=pp,
                             url_maker=url_maker)
