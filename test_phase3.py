from ingestion import fetch_all
from processing import run_pipeline

articles = fetch_all()
cleaned  = run_pipeline(articles)

print('Title  :', cleaned[0]['title_clean'])
print('Source :', cleaned[0]['source'])
print('Score  :', cleaned[0]['quality_score'])
print('Domain :', cleaned[0]['domain_hint'])