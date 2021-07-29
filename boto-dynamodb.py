import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys
from smart_open import smart_open
from boto3.dynamodb.conditions import Key

def query_tasks(job_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('Tasks')
    response = table.query(
        KeyConditionExpression=Key('job_id').eq(job_id)
    )
    return response['Items']

Dynamoclient = boto3.client('dynamodb')

parser = argparse.ArgumentParser()
parser.add_argument('--job-id', action='store', dest='job_id', default=False)
parser.add_argument('--debug', action='store_true', dest='debug', default=False)

args = parser.parse_args()
# print('args', args)

# Set up Debug Logging
if args.debug:
    LOGGER.setLevel(logging.DEBUG)

error = False

if not args.job_id:
    print('Please ! specify job_id')
    error = True

if error:
    print('python boto-dynamodb.py --job-id=job_id')

if args.job_id:

    # stream lines from an S3 object
    for line in smart_open('s3://job-bucket001/jobs.txt', 'rb'):
        print(line.decode('utf8'))
        print(type(line.decode('utf8')))

        for job_id in line.decode('utf8').split(':'):

            if job_id == args.job_id:
                print('Querying dynamodb ...')
                job = query_tasks(int(args.job_id))
                print(job)
                f = open("job_id" + args.job_id + ".txt", "w")
                f.write("job_id: " + str(job[0]['job_id']))
                f.write("start_date: " + job[0]['start_date'])
                f.write("end_date: " + job[0]['end_date'])
                # f.write("job_duration: " + str(job[0]['job_duration']))
                f.write("job: " + str(job[0]['job']))
                f.close()






# if __name__ == '__main__':
#     query_year = 1985
#     print(f"Movies from {query_year}")
#     movies = query_movies(query_year)
#     for movie in movies:
#         print(movie['year'], ":", movie['title'])
