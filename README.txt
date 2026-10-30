# Smart Healthcare SPM System

A small, database-backed Flask application prepared for the CSE-494 Software Project Management case study. It covers only the requested modules and uses SQLite for persistent storage.

## Requirements
- Python 3.10 or newer
- Internet is not required after Flask is installed.

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted folder.
3. Open Command Prompt in this folder.
4. Run:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   py app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

On macOS/Linux, activate with `source .venv/bin/activate` and run `python app.py`.

## Included modules
1. Project charter and management plan.
2. Requirements register, change requests and approval workflow.
3. Hierarchical WBS.
4. Activity scheduling, resources, dependencies and Gantt-style timeline.
5. Planned Value, Earned Value, Actual Cost, CPI and SPI calculations.
6. Defect tracking, quality checklist, likelihood-impact risk matrix and PDPC-style responses.
7. Dashboard and consolidated report with print/save-as-PDF.

## Sample case data
The first run creates `healthcare_spm.db` and seeds it with the original PKR 5,000,000 budget, the original deadline, five-hospital stakeholders, eight sample requirements, two pending change requests totalling PKR 800,000 and three weeks, sample WBS/tasks, critical defects, checklist items and risks.

The AI diagnosis and mobile app requirements start as Proposed/Pending and are excluded from approved scope. To demonstrate change control, open **Requirements & Changes**, change one request's status to **Approved**, and apply it. The system then adds that request's cost and weeks to the project budget/deadline baseline and approves the matching requirement. Do not approve both requests if you want to demonstrate only one change at a time.

## Notes
- All records are stored in the local SQLite database.
- EVM uses task planned costs, elapsed time from activity start dates, completion percentages and recorded actual costs. It is a teaching/demo calculation, not a certified project-control tool.
- The schedule uses each activity's start date and duration; the interface flags activities past their planned end date and highlights dependency timing that should be reviewed.
- The local development server is for classroom demonstration. It is not hardened for real hospital or patient data.
- No real patient information should be entered.
