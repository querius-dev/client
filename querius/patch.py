from google.cloud.bigquery import QueryJob, Client

from querius.client import QueriusClient


def patch_bq_client_with_querius_client(bq_client: Client, qs_client: QueriusClient) -> Client:
    """
    Take an instance of a BigQuery client and wrap the query and result methods with methods that call the Querius API.
    """
    orig_query_method = bq_client.query

    def query(query_str: str, *query_args, **query_kwargs) -> QueryJob:
        project, request_id = qs_client.route(query_str)
        query_kwargs['project'] = project
        qj = orig_query_method(query_str, *query_args, **query_kwargs)

        orig_result_method = qj.result

        def post_log_to_querius_and_get_result(*result_args, **result_kwargs):
            qj.result = orig_result_method
            result = qj.result(*result_args, **result_kwargs)
            qs_client.log_query_stats(qj, request_id)
            return result

        qj.result = post_log_to_querius_and_get_result
        return qj

    bq_client.query = query
    return bq_client
