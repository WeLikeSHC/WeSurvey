from pyhive import hive
from TCLIService.ttypes import TOperationState
cursor = hive.connect('192.168.1.51').cursor()
cursor.execute("insert into test values (1000) ", async=True)

status = cursor.poll().operationState
while status in (TOperationState.INITIALIZED_STATE, TOperationState.RUNNING_STATE):
    logs = cursor.fetch_logs()
    for message in logs:
        print message

    status = cursor.poll().operationState

print cursor.fetchall()