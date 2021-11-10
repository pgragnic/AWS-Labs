import json
import boto3
import cfnresponse
import threading

def copyIndex(sourceBucket, destBucket, apiGatewayUrl, ob):
    s3 = boto3.client('s3')
    modify_extensions = ['js', 'html', 'css', 'txt']
    extension_type = {
        'js': 'application/javascript',
        'html': 'text/html',
        'css': 'text/css',
        'txt': 'text/plain'
    }

    if ob.split('.')[-1] in modify_extensions:
        file = s3.get_object(Bucket=sourceBucket, Key=ob)['Body'].read().decode('utf-8')
        file = file.replace('APGATEWAY', apiGatewayUrl).encode('utf-8')

        s3.put_object(
            Body = file,
            Bucket = destBucket,
            Key = ob.split('/')[-1],
            ContentType = extension_type[ob.split('.')[-1]]
        )

    else:
        print(f'Source Bucket: {sourceBucket}\nDestination Bucket: {destBucket}\nCopy Source: {sourceBucket}/{ob}')
        s3.copy_object(
            Bucket = destBucket,
            Key = ob.split('/')[-1],
            CopySource = f'{sourceBucket}/{ob}'
        )

def clean_bucket(bucket):
    s3 = boto3.client('s3')
    keys = []
    for k in s3.list_objects_v2(Bucket = bucket)['Contents']:
        if 'Key' in k.keys():
            keys.append(k['Key'])

    for key in keys:
        s3.delete_objects(Bucket=bucket, Delete={'Objects': [{'Key': key}]})

def timeout(event, context):
    print('Timing out, sending failure response to CFN')
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)

def handler(event, context):
    print(f'Received event: {json.dumps(event)}')
    timer = threading.Timer((context.get_remaining_time_in_millis() / 1000.00) - 0.5, timeout, args=[event, context])
    timer.start()

    status = cfnresponse.SUCCESS
    try:
        sourceBucket = event['ResourceProperties']['SourceBucket']
        destBucket = event['ResourceProperties']['DestBucket']
        apiGatewayUrl = event['ResourceProperties']['APIGatewayURL']
        Objects = event['ResourceProperties']['Objects']
        if event['RequestType'] == 'Delete':
            clean_bucket(destBucket)
        else:
            for ob in Objects:
                copyIndex(sourceBucket, destBucket, apiGatewayUrl, ob)

    except Exception as e:
        print(e)
        status = cfnresponse.FAILED
    finally:
        timer.cancel()
        cfnresponse.send(event, context, status, {}, None)
