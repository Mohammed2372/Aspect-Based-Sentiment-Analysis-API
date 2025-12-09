from celery import shared_task

import csv

from .models import FileUpload, AnalysisRecord, AspectResult
from .services import ABSAService


@shared_task
def process_bulk_file(file_id) -> None:
    try:
        # setup
        upload = FileUpload.objects.get(id=file_id)
        upload.status = "Processing"
        upload.save()

        print(f"🚀 Starting bulk processing for File {file_id}")

        # read csv
        with open(upload.csv_file.path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            raise ValueError("CSV file is empty")

        if rows and "text" in str(rows[0][0]).lower():
            print("   -> Header detected, skipping first row.")
            rows = rows[1:]

        # Save total count immediately
        count = len(rows)
        upload.total_rows = count
        upload.save()

        # process rows
        all_aspects_results = []

        for i, row in enumerate(rows):
            if not row:
                continue
            text = row[0]

            # run AI logic
            ai_result = ABSAService.analyze_sentiment(text)

            # create record
            record = AnalysisRecord(
                user=upload.user,
                original_text=text,
            )
            record.save()

            # prepare aspects
            for item in ai_result["analysis"]:
                all_aspects_results.append(
                    AspectResult(
                        record=record,
                        aspect=item["aspect"],
                        sentiment=item["sentiment"],
                        confidence=item["confidence"],
                    )
                )

            if i % 10 == 0:
                upload.processed_rows = i
                upload.save()

        # bulk save results
        AspectResult.objects.bulk_create(all_aspects_results)

        # finish
        upload.status = "Completed"
        upload.processed_rows = len(rows)
        upload.save()
        print(f"✅ Finished File {file_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        # upload.status = "Failed"
        upload.status = f"Err: {str(e)[:20]}"
        upload.save()
