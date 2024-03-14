import boto3
import json

def lambda_handler(event, context):
    sf = boto3.client('stepfunctions', region_name = 'us-east-1')
    
    input_dict = {'Comment': 'Initiating Step Function from Lambda'}
    
    #TODO Replace <STATE_MACHINE ARN> with your state machine ARN
    list_exec_response = sf.list_executions(
        stateMachineArn='<STATE_MACHINE_ARN>',
        statusFilter='RUNNING',
    )
    
    #TODO Replace <STATE_MACHINE ARN> with your state machine ARN
    if len(list_exec_response['executions']) <= 0:
        response = sf.start_execution(
            stateMachineArn = '<STATE_MACHINE_ARN>',
            input = json.dumps(input_dict))

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully Initiated State Machine from Lambda!')
        }
    
    return {
            'statusCode': 200,
            'body': json.dumps('State Machine already Running!')
        }
