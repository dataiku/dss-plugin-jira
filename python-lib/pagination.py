class Pagination(object):

    def __init__(self, config=None, skip_key=None, limit_key=None, total_key=None, next_page_key=None):
        self.next_page_key = None
        self.skip_key = None
        self.limit_key = None
        self.total_key = None
        self.next_page_url = None
        self.remaining_records = None
        self.records_to_skip = None
        self.pagination_style = ""
        self.counting_key = None
        self.counter = None

    def configure_paging(self, config=None, skip_key=None, limit_key=None, total_key=None, next_page_key=None, url=None):
        config = {} if config is None else config
        self.next_page_key = config.get("next_page_key", next_page_key)
        self.skip_key = config.get("skip_key", skip_key)
        self.limit_key = config.get("limit_key", limit_key)
        self.total_key = config.get("total_key", total_key)

    def reset_paging(self, counting_key=None, url=None):
        self.remaining_records = 0
        self.records_to_skip = 0
        self.counting_key = counting_key
        self.counter = 0
        self.next_page_url = url

    def set_counting_key(self, counting_key):
        self.counting_key = counting_key

    def update_next_page(self, data):
        if isinstance(data, list):
            batch_size = len(data)
            self.records_to_skip = self.records_to_skip + batch_size
            return
        elif self.counting_key:
            batch_size = len(data.get(self.counting_key))
        else:
            batch_size = None
        if self.next_page_key:
            self.next_page_url = self.get_from_path(data, self.next_page_key)
        if self.skip_key:
            self.skip = data.get(self.skip_key)
        if self.limit_key:
            self.limit = data.get(self.limit_key)
        if self.total_key:
            self.total = data.get(self.total_key)
        self.records_to_skip = self.records_to_skip + batch_size
        if self.total:
            self.remaining_records = self.total - self.records_to_skip

    def get_from_path(self, dictionary, path):
        if isinstance(path, list):
            edge = dictionary
            for key in path:
                edge = edge.get(key)
                if edge is None:
                    return None
            return edge
        else:
            return dictionary.get(path)

    def is_next_page(self):
        if self.next_page_key:
            ret = (self.next_page_url is not None) and (self.next_page_url != "")
        else:
            ret = self.counter < self.remaining_records
        return ret

    def get_params(self):
        ret = {}
        if self.skip_key and (self.records_to_skip > 0):
            ret.update({self.skip_key: self.records_to_skip})
        return ret

    def get_next_page_url(self):
        return self.next_page_url
