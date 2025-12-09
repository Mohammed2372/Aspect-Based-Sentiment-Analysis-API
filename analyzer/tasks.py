from celery import shared_task

import csv

from .models import AnalysisRecord, AspectResult, AnalysisSession
from .services import ABSAService


@shared_task
def process_bulk_file(session_id: int) -> None:
    try:
        # Get Session
        session = AnalysisSession.objects.get(id=session_id)
        session.status = "Processing"
        session.save()

        print(f"🚀 Starting bulk processing for session {session_id}")

        # read csv
        with open(session.csv_file.path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            raise ValueError("CSV file is empty")

        if rows and "text" in str(rows[0][0]).lower():
            print("   -> Header detected, skipping first row.")
            rows = rows[1:]

        # Save total count immediately
        count = len(rows)
        session.total_rows = count
        session.save()

        # process rows
        all_aspects_results = []

        for i, row in enumerate(rows):
            if not row:
                continue
            text = row[0]

            # run AI logic
            ai_result = ABSAService.analyze_sentiment(text)

            # create record linked to session
            record = AnalysisRecord(
                user=session.user,
                original_text=text,
                session=session,
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
                session.processed_rows = i
                session.save()

        # bulk save results
        AspectResult.objects.bulk_create(all_aspects_results)

        # finish
        session.status = "Completed"
        session.processed_rows = len(rows)
        session.save()
        print(f"✅ Finished session {session_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        # session.status = "Failed"
        session.status = f"Err: {str(e)[:20]}"
        session.save()
