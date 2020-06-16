import logging
from dataiku.connector import Connector
from jira_client import JiraClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='jira plugin %(levelname)s - %(message)s')


class JiraConnector(Connector):

    def __init__(self, config, plugin_config):
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class

        logging.info("JiraConnector init")
        self.access_type = self.config.get("access_type", "token_access")
        self.connection_details = self.config.get(self.access_type)
        self.edge_name = self.config.get("edge_name", "")
        self.item_value = self.config.get("item_value", "")
        self.data = self.config.get("data", None)
        self.queue_id = self.config.get("queue_id", None)
        self.expand = self.config.get("expand", [])
        self.client = JiraClient(self.connection_details)

    def get_read_schema(self):
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                      partition_id=None, records_limit=-1):
        logger.info("JiraConnector:generate_rows")
        self.client.start_session(self.edge_name)
        data = self.client.get_edge(self.edge_name, self.item_value, self.data, queue_id=self.queue_id, expand=self.expand)
        while len(data) > 0:
            counter = 0
            for result in data:
                if counter == records_limit:
                    break
                else:
                    counter = counter + 1
                yield (self.client.format(result))
            if self.client.has_next_page():
                data = self.client.get_next_page()
            else:
                break

    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                   partition_id=None):
        """
        Returns a writer object to write in the dataset (or in a partition).

        The dataset_schema given here will match the the rows given to the writer below.

        Note: the writer is responsible for clearing the partition, if relevant.
        """
        raise Exception("Unimplemented")

    def get_partitioning(self):
        """
        Return the partitioning schema that the connector defines.
        """
        raise Exception("Unimplemented")

    def list_partitions(self, partitioning):
        """Return the list of partitions for the partitioning scheme
        passed as parameter"""
        return []

    def partition_exists(self, partitioning, partition_id):
        """Return whether the partition passed as parameter exists

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")

    def get_records_count(self, partitioning=None, partition_id=None):
        """
        Returns the count of records for the dataset (or a partition).

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")
