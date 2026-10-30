# Test cases — Smart Healthcare SPM System

| ID | Test | Steps / input | Expected result |
|---|---|---|---|
| TC-01 | Start application | Run `py app.py`; open localhost:5000 | Dashboard loads and sample data is seeded |
| TC-02 | Update charter | Change project status or quality plan and save | Saved values remain after refresh |
| TC-03 | Proposed requirement control | Add a requirement with status Proposed | It appears as Proposed and is not shown under approved scope in reports |
| TC-04 | Approve change request | Set AI diagnosis change to Approved | Its cost and weeks are added to the baseline, and matching requirement becomes Approved |
| TC-05 | Reject change request | Set a pending request to Rejected | Budget and deadline remain unchanged |
| TC-06 | Add WBS package | Add code 2.7, title and deliverable | Item appears in the WBS list |
| TC-07 | Add activity validation | Try duration 0 or completion above 100 | Input is rejected with a validation message |
| TC-08 | Add schedule task | Add task with valid dates, duration, owner and cost | Activity appears in task register and timeline |
| TC-09 | Update actual cost/progress | Change a task's actual cost and completion | PV, EV, AC, CPI and SPI recalculate |
| TC-10 | Defect tracking | Add a Critical defect, then update to Resolved | Defect is stored and no longer counted as unresolved critical |
| TC-11 | Quality inspection | Set checklist result to Fail and save notes | Result and notes persist |
| TC-12 | Risk scoring | Add likelihood 4 and impact 5 | Score is 20 and priority is High |
| TC-13 | Dashboard warnings | Leave critical defects unresolved or set cost/progress data below threshold | Dashboard shows appropriate warning |
| TC-14 | Consolidated report | Open Reports and use Print / Save as PDF | Report lists pending changes, delayed activities, critical defects and EVM |
