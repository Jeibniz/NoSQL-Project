""" AUTHOR: Jonathan Persgården (jpersgarden@gmail.com) """

from ..big_query_client import BigQueryClient

def test_run_query():
    """
    We know that the dataset contains the id cronp21
    This tests will check that the run_query method can fetch that id from the dataset
    """
    dataFetcher = BigQueryClient()
    queryRows = dataFetcher.run_query('SELECT id FROM `fh-bigquery.reddit_comments.2015_05` '
                                      'WHERE id = "cronp21" '
                                      'LIMIT 1')
    for row in queryRows:
        resultId = row.id
    assert resultId == 'cronp21'