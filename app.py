import os
import uuid
import boto3
from src.util import ensure_deduplication, get_db_engine

def lambda_handler(event, context):

    # Ensure deduplicated message
    det = ensure_deduplication(msg=event, engine=get_db_engine(), 
        table_name = os.getenv('TABLE_NAME'), 
        queue_name = os.getenv('QUEUE_NAME'),
        schema     = os.environ['DB_SCHEMA']
    ) # end det
    if not(det): # already processed
        return {
            'status': 'failed',
            'error' : 'the event has already been processed'
        } # end
    # end if

    # Enhancement:
    # Get metadata about S3 file size to override the CPU and RAM for ECS

    # Actually call the downstream task
    task_ref_id = str(uuid.uuid4())
    ecs_client = boto3.client('ecs')
    response = ecs_client.run_task(
        cluster        = os.environ['ECS_CLUSTER'],
        taskDefinition = os.environ['ECS_TASK_DEF'],
        count          = os.getenv('ECS_TASK_COUNT', 1),
        launchType     = os.getenv('ECS_LAUNCH_TYPE', 'FARGATE'),
        overrides = {
            'containerOverrides': [
                {
                    'name': 'string',
                    'command': [
                        'string',
                    ],
                    'environment': [
                        {
                            'name': 'string',
                            'value': 'string'
                        },
                    ],
                    'environmentFiles': [
                        {
                            'value': 'string',
                            'type': 's3'
                        },
                    ],
                },
            ]
        },
        referenceId = task_ref_id,
        startedBy   = context.get('function_name', 'Lambda'),
    ) # end run_task

    return response
# end def