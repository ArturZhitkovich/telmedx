import csv
import datetime

from django.http import HttpResponse


def export_usage_csv(logs):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + datetime.datetime.now().strftime(
        '%Y-%m-%d') + '-usage.csv"'

    writer = csv.writer(response)
    writer.writerow(['Device', 'Date and Time', 'Duration', 'Frames Sent', 'Images Captured'])
    for log in logs:
        writer.writerow([log.device.name, log.begin, log.duration, log.frames, log.captured_images])

    return response
