from .base import TEST_HOST


class TestPaginator:

    def __init__(self, base_url: str, *, instance_count: int, page_size: int):
        self.base_url = base_url
        self.page_size = page_size
        self.underfull_page_size = instance_count % page_size
        self.page_count = (
            instance_count // page_size 
            + (self.underfull_page_size > 0)
        )

    @property
    def last_page_size(self):
        return (
            self.page_size 
            if self.underfull_page_size == 0
            else self.underfull_page_size
        )

    def first_item_number(self, page):
        return (page - 1)*self.page_size + 1

    def actual_page_size(self, page):
        return (
            self.page_size 
            if page != self.page_count 
            else self.last_page_size
        )

    def previous_page_link(self, page, request_params):
        if page <= 1:
            return None

        link = TEST_HOST + self.base_url        
        params = []
        if 'limit' in request_params:
            params.append(f'limit={request_params["limit"]}')

        prev_page = page - 1
        if prev_page > 1:
            params.append(f'page={prev_page}')

        param_str = '&'.join(params)
        return f'{link}?{param_str}' if param_str else link

    def next_page_link(self, page, request_params):
        if page >= self.page_count:
            return None

        link = TEST_HOST + self.base_url        
        params = []
        if 'limit' in request_params:
            params.append(f'limit={request_params["limit"]}')

        next_page = page + 1
        params.append(f'page={next_page}')
        param_str = '&'.join(params)
        return f'{link}?{param_str}'
