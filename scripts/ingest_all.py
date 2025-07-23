import logging
from datetime import datetime
from scripts.ingest_xlsx import ingest_excel_data
from scripts.ingest_pdf import ingest_pdf_data
from scripts.calc_metrics import calculate_metrics
from scripts.questions_engine import generate_questions
from scripts.update_ranking import update_ranking

LOG_FILE = "output/logs/ingestion_run.log"
QUESTIONS_CSV = "output/checklists/questions_and_observations.csv"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log(msg):
    logging.info(msg)
    print(msg)

def run_pipeline():
    log("==== Ingestion Started ====")
    try:
        # Step 1: Ingest XLSX and PDF
        log("Ingesting Excel files...")
        ingest_excel_data("data/")
        log("Ingesting PDF files...")
        ingest_pdf_data("data/")

        # Step 2: Calculate derived metrics
        log("Calculating metrics...")
        calculate_metrics()

        # Step 3: Generate checklist questions
        log("Generating questions and checklist...")
        generate_questions(output_csv=QUESTIONS_CSV)

        # Step 4: Update scoring/weights
        log("Updating rankings...")
        update_ranking()

        log("==== Ingestion Complete ====")
    except Exception as e:
        logging.exception("Fatal error in pipeline")
        raise

if __name__ == "__main__":
    run_pipeline()
