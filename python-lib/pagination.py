from utils import extract_data_with_json_path


class Pagination(object):

    def __init__(self):
        self.next_page_key = None
        self.next_token_key = None
        self.skip_key = None
        self.limit_key = None
        self.total_key = None
        self.next_page_url = None
        self.next_page_token = None
        self.remaining_records = None
        self.records_to_skip = None
        self.pagination_style = ""
        self.counting_key = None
        self.counter = None
        self.is_data_single_dict = None
        self.is_last_page = None
        self.error_flag = None

    def configure_paging(self, config=None, skip_key=None, limit_key=None, total_key=None, next_page_key=None, next_token_key=None):
        config = {} if config is None else config
        self.next_page_key = config.get("next_page_key", next_page_key)
        self.next_token_key = config.get("next_token_key", next_token_key)
        self.skip_key = config.get("skip_key", skip_key)
        self.limit_key = config.get("limit_key", limit_key)
        self.total_key = config.get("total_key", total_key)

    def reset_paging(self, counting_key=None, url=None):
        self.remaining_records = 0
        self.records_to_skip = 0
        self.counting_key = counting_key
        self.counter = 0
        self.next_page_url = url
        self.is_data_single_dict = False
        self.is_last_page = False
        self.error_flag = False

    def set_counting_key(self, counting_key):
        self.counting_key = counting_key

    def update_next_page(self, data):
        if isinstance(data, list):
            batch_size = len(data)
            self.records_to_skip = self.records_to_skip + batch_size
            return
        self.is_last_page = data.get('isLastPage', False)
        if self.counting_key:
            if isinstance(self.counting_key, list):
                counting_key = self.extract_counting_key(data)
            else:
                counting_key = self.counting_key
            if counting_key is not None:
                batch_size = len(extract_data_with_json_path(data, counting_key))
            else:
                self.is_last_page = True
                batch_size = 1
        else:
            self.is_data_single_dict = True
            return
        self.update_page_parameters(data, batch_size)

    def update_page_parameters(self, data, batch_size):
        if self.next_page_key:
            self.next_page_url = self.get_from_path(data, self.next_page_key)
        if self.next_token_key:
            self.next_page_token = self.get_from_path(data, self.next_token_key)
        if self.skip_key:
            self.skip = data.get(self.skip_key)
        if self.limit_key:
            self.limit = data.get(self.limit_key)
        if self.total_key:
            self.total = data.get(self.total_key)
        self.records_to_skip = self.records_to_skip + batch_size
        if self.total:
            self.remaining_records = self.total - self.records_to_skip

    def extract_counting_key(self, data):
        counting_key = None
        for key in self.counting_key:
            if key in data:
                counting_key = key
        return counting_key

    def get_from_path(self, dictionary, path):
        if isinstance(path, list):
            endpoint = dictionary
            for key in path:
                endpoint = endpoint.get(key)
                if endpoint is None:
                    return None
            return endpoint
        else:
            return dictionary.get(path)

    def is_next_page(self):
        if self.is_last_page:
            return False
        if self.is_data_single_dict or self.error_flag:
            return False
        if self.next_token_key and self.next_page_token:
            return True
        elif self.next_token_key and not self.next_page_token:
            return False
        if self.next_page_key:
            ret = (self.next_page_url is not None) and (self.next_page_url != "")
        else:
            ret = self.counter < self.remaining_records
        return ret

    def get_params(self):
        ret = {}
        if self.skip_key and (self.records_to_skip > 0):
            ret.update({self.skip_key: self.records_to_skip})
        if self.next_page_token:
            ret.update({self.next_token_key[-1:][0]: self.next_page_token})
        return ret

    def get_next_page_url(self):
        return self.next_page_url

    def set_error_flag(self, flag=True):
        self.error_flag = flag
