from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.sqlite.hooks.sqlite import SqliteHook
from datetime import datetime
import pandas as pd
import io

@dag(
    dag_id='survey_results_to_s3',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def export_survey_results():

    @task
    def query_and_save_to_s3():
        # SQL query to get comprehensive survey results
        query = """
        SELECT 
            s.survey_id,
            s.title as survey_title,
            s.description as survey_description,
            r.respondent_email,
            q.question_text,
            o.option_text as selected_option,
            r.created_at as response_date
        FROM Surveys s
        JOIN Responses r ON s.survey_id = r.survey_id
        JOIN AnswerChoices ac ON r.response_id = ac.response_id
        JOIN Questions q ON ac.question_id = q.question_id
        JOIN Options o ON ac.option_id = o.option_id
        ORDER BY s.survey_id, r.respondent_email, q.question_order
        """

        # Execute query and get results
        sqlite_hook = SqliteHook(sqlite_conn_id='sqlite_default')
        df = sqlite_hook.get_pandas_df(query)

        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Upload to S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f'survey_results/survey_export_{timestamp}.csv'
        
        s3_hook.load_string(
            string_data=csv_buffer.getvalue(),
            key=s3_key,
            bucket_name='XXXXXXXXXXXXXXXX',  # Replace with your S3 bucket name
            replace=True
        )

        return f"Exported {len(df)} survey responses to s3://your-bucket-name/{s3_key}"

    query_and_save_to_s3()

dag = export_survey_results()
