from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3, os
from datetime import date, datetime, timedelta

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "healthcare_spm.db")
app = Flask(__name__)
app.secret_key = "healthcare-spm-local-demo-key"

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS project (
      id INTEGER PRIMARY KEY, name TEXT NOT NULL, objectives TEXT, stakeholders TEXT,
      scope_in TEXT, scope_out TEXT, budget REAL NOT NULL, deadline TEXT NOT NULL,
      status TEXT DEFAULT 'In Progress', quality_plan TEXT, closure_notes TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS requirements (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT, priority TEXT DEFAULT 'Medium',
      status TEXT DEFAULT 'Proposed', source TEXT DEFAULT 'Hospital Management'
    );
    CREATE TABLE IF NOT EXISTS changes (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, justification TEXT, cost_impact REAL DEFAULT 0,
      weeks_impact INTEGER DEFAULT 0, status TEXT DEFAULT 'Pending'
    );
    CREATE TABLE IF NOT EXISTS wbs (
      id INTEGER PRIMARY KEY, code TEXT NOT NULL, title TEXT NOT NULL, parent_code TEXT DEFAULT '',
      deliverable TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, owner TEXT, start_date TEXT NOT NULL,
      duration INTEGER NOT NULL, dependency_id INTEGER, planned_cost REAL DEFAULT 0,
      actual_cost REAL DEFAULT 0, percent_complete INTEGER DEFAULT 0, status TEXT DEFAULT 'Not Started',
      milestone INTEGER DEFAULT 0, FOREIGN KEY(dependency_id) REFERENCES tasks(id)
    );
    CREATE TABLE IF NOT EXISTS defects (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT, severity TEXT DEFAULT 'Medium',
      assigned_to TEXT, status TEXT DEFAULT 'Open', found_date TEXT
    );
    CREATE TABLE IF NOT EXISTS checklist (
      id INTEGER PRIMARY KEY, deliverable TEXT NOT NULL, check_item TEXT NOT NULL,
      result TEXT DEFAULT 'Not Checked', notes TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS risks (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, likelihood INTEGER NOT NULL,
      impact INTEGER NOT NULL, response TEXT, status TEXT DEFAULT 'Open'
    );
    """)
    if not con.execute("SELECT id FROM project LIMIT 1").fetchone():
        con.execute("""INSERT INTO project (name, objectives, stakeholders, scope_in, scope_out, budget, deadline, status, quality_plan)
        VALUES (?,?,?,?,?,?,?,?,?)""", (
          "Smart Healthcare Project Management System",
          "Deliver an integrated system for appointments, laboratory reports, doctor schedules, online consultations and hospital billing.",
          "Five hospitals, hospital management, doctors, patients, laboratory staff, billing staff, project team.",
          "Web-based appointment scheduling, patient records, lab reports, doctor schedules, online consultations, billing and project monitoring.",
          "AI preliminary diagnosis and mobile application are proposed changes and are excluded until approved.",
          5000000, "2027-02-19", "In Progress",
          "QA testing, requirement reviews, integration testing, defect tracking and acceptance checks."
        ))
        reqs = [
          ("Patient appointment scheduling","Book, update and cancel appointments","High","Approved"),
          ("Patient record management","Store and retrieve patient records securely","High","Approved"),
          ("Laboratory reports","Upload and view laboratory reports","High","Approved"),
          ("Doctor schedules","Maintain doctor availability","Medium","Approved"),
          ("Online consultations","Support remote consultations","Medium","Approved"),
          ("Hospital billing","Generate bills and track payments","High","Approved"),
          ("AI preliminary diagnosis module","AI-assisted preliminary diagnosis","High","Proposed"),
          ("Mobile application","Mobile app for patients and staff","Medium","Proposed")
        ]
        con.executemany("INSERT INTO requirements(title,description,priority,status) VALUES(?,?,?,?)", reqs)
        changes = [
          ("AI-based preliminary diagnosis module","Requested by hospital management",500000,2,"Pending"),
          ("Mobile application","Requested by hospital management",300000,1,"Pending")
        ]
        con.executemany("INSERT INTO changes(title,justification,cost_impact,weeks_impact,status) VALUES(?,?,?,?,?)", changes)
        wbs = [
          ("1","Project Management","","Charter, plan and monitoring"),
          ("1.1","Initiation","1","Project charter and stakeholder register"),
          ("1.2","Planning","1","Scope, schedule, cost and quality plan"),
          ("2","Healthcare Modules","","Integrated hospital system"),
          ("2.1","Appointments","2","Appointment scheduling"),
          ("2.2","Patient Records","2","Patient record management"),
          ("2.3","Laboratory Reports","2","Lab report module"),
          ("2.4","Doctor Schedules","2","Doctor availability"),
          ("2.5","Online Consultation","2","Remote consultation"),
          ("2.6","Billing","2","Billing and payment records"),
          ("3","Testing & Deployment","","Validated release"),
          ("3.1","Integration and QA","3","Tested integrated system")
        ]
        con.executemany("INSERT INTO wbs(code,title,parent_code,deliverable) VALUES(?,?,?,?)", wbs)
        today = date.today()
        task_data = [
          ("Requirements & charter","Project Manager",0,5,None,250000,250000,100,"Completed",1),
          ("Database design","Database Developer",5,10,1,450000,470000,100,"Completed",0),
          ("Backend modules","Backend Developer 1",15,25,2,1200000,800000,65,"In Progress",0),
          ("Frontend interface","Frontend Developer 1",15,25,2,900000,650000,60,"In Progress",0),
          ("Integration testing","QA Engineer",40,12,3,600000,180000,20,"In Progress",0),
          ("User acceptance & deployment","Project Manager",52,8,5,350000,0,0,"Not Started",1),
        ]
        for title, owner, offset, duration, dep, pcost, acost, pct, status, mile in task_data:
            start = today + timedelta(days=offset)
            con.execute("""INSERT INTO tasks(title,owner,start_date,duration,dependency_id,planned_cost,actual_cost,percent_complete,status,milestone)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",(title,owner,start.isoformat(),duration,dep,pcost,acost,pct,status,mile))
        con.executemany("INSERT INTO defects(title,description,severity,assigned_to,status,found_date) VALUES(?,?,?,?,?,?)", [
          ("Appointment scheduling conflict","Overlapping appointments can be booked for one doctor.","Critical","Backend Developer 1","Open",today.isoformat()),
          ("Patient record retrieval error","Some patient records fail to load after update.","Critical","Backend Developer 2","In Progress",today.isoformat()),
          ("Billing total rounding","Rounding mismatch in one invoice case.","Medium","Backend Developer 1","Open",today.isoformat())
        ])
        con.executemany("INSERT INTO checklist(deliverable,check_item,result,notes) VALUES(?,?,?,?)", [
          ("Appointments","Prevent double-booking of doctor time slots","Not Checked",""),
          ("Patient Records","Verify record creation, update and retrieval","Not Checked",""),
          ("Laboratory Reports","Confirm report upload and authorized access","Not Checked",""),
          ("Billing","Reconcile invoice totals and payment status","Not Checked",""),
          ("Integrated System","Run regression and user acceptance tests","Not Checked","")
        ])
        con.executemany("INSERT INTO risks(title,likelihood,impact,response,status) VALUES(?,?,?,?,?)", [
          ("Critical defects delay release",4,5,"Prioritize fixes; retest appointment and patient-record workflows.","Open"),
          ("Scope expansion increases cost",4,4,"Approve changes only after impact review and budget authorization.","Open"),
          ("Dependency delays integration testing",3,4,"Track predecessors daily and reserve time for regression testing.","Open")
        ])
    con.commit()
    con.close()

def get_project():
    con=db(); row=con.execute("SELECT * FROM project LIMIT 1").fetchone(); con.close(); return row

def all_rows(sql, args=()):
    con=db(); rows=con.execute(sql,args).fetchall(); con.close(); return rows

def one(sql,args=()):
    con=db(); row=con.execute(sql,args).fetchone(); con.close(); return row

def run(sql,args=()):
    con=db(); cur=con.execute(sql,args); con.commit(); con.close(); return cur.lastrowid

def task_end(t):
    return (datetime.strptime(t["start_date"], "%Y-%m-%d").date() + timedelta(days=int(t["duration"])-1)).isoformat()

def schedule_rows():
    tasks=all_rows("""SELECT t.*, d.title AS dependency_title FROM tasks t LEFT JOIN tasks d ON t.dependency_id=d.id ORDER BY t.start_date,t.id""")
    out=[]
    for t in tasks:
        end=task_end(t)
        dep_late=False
        if t["dependency_id"]:
            dep=one("SELECT * FROM tasks WHERE id=?",(t["dependency_id"],))
            if dep:
                dep_end=datetime.strptime(task_end(dep),"%Y-%m-%d").date()
                start=datetime.strptime(t["start_date"],"%Y-%m-%d").date()
                dep_late = start <= dep_end
        out.append(dict(t, end_date=end, delayed=(t["status"] not in ("Completed",) and datetime.strptime(end,"%Y-%m-%d").date()<date.today()), dependency_late=dep_late))
    return out

def evm_data():
    p=get_project()
    tasks=all_rows("SELECT * FROM tasks")
    total_days=max(1,(datetime.strptime(p["deadline"],"%Y-%m-%d").date()-date.today()).days)
    # Demonstration status date: use elapsed time from earliest task start to today.
    pv=ev=ac=0.0
    for t in tasks:
        start=datetime.strptime(t["start_date"],"%Y-%m-%d").date()
        elapsed=max(0,(date.today()-start).days)
        fraction=min(1,elapsed/max(1,int(t["duration"])))
        pv += float(t["planned_cost"])*fraction
        ev += float(t["planned_cost"])*int(t["percent_complete"])/100
        ac += float(t["actual_cost"])
    cpi=ev/ac if ac else 0
    spi=ev/pv if pv else 0
    return {"pv":pv,"ev":ev,"ac":ac,"cpi":cpi,"spi":spi,"budget":p["budget"],
            "forecast":ac+(p["budget"]-ev) if ev else ac}

BASE = """
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Healthcare SPM</title>
<style>
:root{--navy:#14213d;--blue:#2563eb;--teal:#0f766e;--bg:#f3f6fb;--ink:#1f2937;--muted:#64748b;--line:#e2e8f0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--ink)}
header{background:linear-gradient(115deg,#14213d,#1d4ed8);color:#fff;padding:24px 30px}
header h1{margin:0;font-size:24px}header p{margin:6px 0 0;color:#dbeafe;font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2}
nav a{color:#334155;text-decoration:none;padding:9px 12px;border-radius:9px;font-size:13px;font-weight:600}nav a:hover,nav a.active{background:#dbeafe;color:#1d4ed8}
main{max-width:1250px;margin:24px auto;padding:0 20px}.page-title{display:flex;justify-content:space-between;align-items:end;gap:10px;margin-bottom:18px}
h2{font-size:22px;margin:0 0 5px}h3{font-size:15px;margin:0 0 14px}.muted{color:var(--muted);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}.grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.card{background:#fff;border:1px solid var(--line);border-radius:15px;padding:18px;box-shadow:0 5px 18px #0f172a08;margin-bottom:16px}
.metric{font-size:26px;font-weight:750;margin:8px 0}.metric-label{font-size:12px;color:var(--muted);font-weight:650;text-transform:uppercase;letter-spacing:.05em}
form .fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}label{font-size:12px;font-weight:700;color:#475569;display:block;margin-bottom:5px}
input,select,textarea{width:100%;padding:10px 11px;border:1px solid #cbd5e1;border-radius:8px;background:#fff;color:#0f172a;font:inherit;font-size:13px}
textarea{min-height:75px;resize:vertical}.full{grid-column:1/-1}.btn{display:inline-block;border:0;border-radius:8px;background:var(--blue);color:white;padding:10px 14px;font-weight:700;font-size:13px;cursor:pointer;text-decoration:none;margin-top:12px}.btn.secondary{background:#e2e8f0;color:#334155}.btn.green{background:var(--teal)}
table{width:100%;border-collapse:collapse;font-size:13px}th{text-align:left;color:#64748b;background:#f8fafc;font-size:11px;text-transform:uppercase;letter-spacing:.04em}td,th{padding:11px 10px;border-bottom:1px solid var(--line);vertical-align:top}tr:last-child td{border-bottom:0}.table-wrap{overflow-x:auto}
.badge{display:inline-block;border-radius:999px;padding:4px 8px;font-size:11px;font-weight:750;background:#e2e8f0;color:#334155}.badge.red{background:#fee2e2;color:#991b1b}.badge.amber{background:#fef3c7;color:#92400e}.badge.green{background:#d1fae5;color:#065f46}.badge.blue{background:#dbeafe;color:#1d4ed8}
.alert{padding:12px 14px;border-radius:10px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;margin-bottom:12px;font-size:13px}.success{background:#ecfdf5;border-color:#a7f3d0;color:#065f46}
.bar{height:10px;background:#e2e8f0;border-radius:99px;overflow:hidden;min-width:100px}.bar span{display:block;height:100%;background:linear-gradient(90deg,#2563eb,#14b8a6)}
.timeline{display:grid;gap:10px}.timeline-row{display:grid;grid-template-columns:180px 1fr;gap:12px;align-items:center;font-size:12px}.track{height:25px;background:repeating-linear-gradient(90deg,#f1f5f9 0,#f1f5f9 calc(10% - 1px),#dbe3ee calc(10% - 1px),#dbe3ee 10%);border-radius:5px;position:relative}.taskbar{height:17px;position:absolute;top:4px;left:0;border-radius:4px;background:#2563eb;color:white;font-size:10px;line-height:17px;text-align:center;white-space:nowrap;overflow:hidden}.taskbar.late{background:#dc2626}.small{font-size:12px}.footer{padding:22px;text-align:center;color:#94a3b8;font-size:12px}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.grid.two{grid-template-columns:1fr}.timeline-row{grid-template-columns:130px 1fr}}
@media(max-width:550px){header{padding:20px}.grid{grid-template-columns:1fr 1fr}form .fields{grid-template-columns:1fr}.full{grid-column:auto}main{padding:0 12px}nav{padding:8px}}
</style></head><body>
<header><h1>✚ Smart Healthcare SPM</h1><p>Project planning • Scope control • Schedule • Cost & quality monitoring</p></header>
<nav>
<a href="/">Dashboard</a><a href="/project">Project Charter</a><a href="/requirements">Requirements & Changes</a><a href="/wbs">WBS</a><a href="/schedule">Schedule & Resources</a><a href="/cost">Cost & EVM</a><a href="/quality">Quality & Risks</a><a href="/reports">Reports</a>
</nav><main>
{% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}<div class="alert success">{{m}}</div>{% endfor %}{% endif %}{% endwith %}
{{ content|safe }}
</main><div class="footer">Smart Healthcare Project Management System · CSE-494 · Local demo application</div></body></html>
"""

def page(title, subtitle, body, **context):
    inner = render_template_string(body, **context)
    return render_template_string(BASE, content=f'<div class="page-title"><div><h2>{title}</h2><div class="muted">{subtitle}</div></div></div>{inner}')

@app.route("/")
def dashboard():
    p=get_project(); tasks=schedule_rows(); ev=evm_data()
    req_count=one("SELECT COUNT(*) n FROM requirements WHERE status='Approved'")["n"]
    pending=one("SELECT COUNT(*) n FROM changes WHERE status='Pending'")["n"]
    critical=one("SELECT COUNT(*) n FROM defects WHERE severity='Critical' AND status!='Resolved'")["n"]
    delayed=sum(1 for t in tasks if t["delayed"])
    progress=round(sum(t["percent_complete"] for t in tasks)/max(1,len(tasks)))
    alerts=[]
    if ev["cpi"] and ev["cpi"]<0.9: alerts.append("Cost warning: CPI is below 0.90.")
    if ev["spi"] and ev["spi"]<0.9: alerts.append("Schedule warning: SPI is below 0.90.")
    if critical: alerts.append(f"{critical} unresolved critical defect(s) require attention.")
    if pending: alerts.append(f"{pending} change request(s) are pending approval; they are excluded from approved scope.")
    body="""
    {% for a in alerts %}<div class="alert">{{a}}</div>{% endfor %}
    <div class="grid">
      <div class="card"><div class="metric-label">Approved budget</div><div class="metric">PKR {{'{:,.0f}'.format(p.budget)}}</div><div class="muted">Original approved baseline</div></div>
      <div class="card"><div class="metric-label">Task progress</div><div class="metric">{{progress}}%</div><div class="bar"><span style="width:{{progress}}%"></span></div></div>
      <div class="card"><div class="metric-label">Pending changes</div><div class="metric">{{pending}}</div><div class="muted">Not included in scope</div></div>
      <div class="card"><div class="metric-label">Critical defects</div><div class="metric">{{critical}}</div><div class="muted">Unresolved</div></div>
    </div>
    <div class="grid two">
      <section class="card"><h3>Project snapshot</h3><p><b>{{p.name}}</b></p><p class="muted">{{p.objectives}}</p>
      <p><b>Deadline:</b> {{p.deadline}} &nbsp; <b>Status:</b> <span class="badge blue">{{p.status}}</span></p>
      <p><b>Approved requirements:</b> {{req_count}} &nbsp; <b>Delayed activities:</b> {{delayed}}</p>
      <a class="btn" href="/project">Manage project</a></section>
      <section class="card"><h3>Earned Value indicators</h3>
      <table><tr><td>Planned Value (PV)</td><td><b>PKR {{'{:,.0f}'.format(evm.pv)}}</b></td></tr>
      <tr><td>Earned Value (EV)</td><td><b>PKR {{'{:,.0f}'.format(evm.ev)}}</b></td></tr>
      <tr><td>Actual Cost (AC)</td><td><b>PKR {{'{:,.0f}'.format(evm.ac)}}</b></td></tr>
      <tr><td>CPI</td><td><span class="badge {{'red' if evm.cpi and evm.cpi<0.9 else 'green'}}">{{'{:.2f}'.format(evm.cpi)}}</span></td></tr>
      <tr><td>SPI</td><td><span class="badge {{'red' if evm.spi and evm.spi<0.9 else 'green'}}">{{'{:.2f}'.format(evm.spi)}}</span></td></tr></table>
      <a class="btn secondary" href="/cost">View cost analysis</a></section>
    </div>
    <section class="card"><h3>Next attention items</h3><div class="table-wrap"><table><tr><th>Item</th><th>Owner / impact</th><th>Status</th></tr>
    {% for d in defects %}<tr><td>{{d.title}}</td><td>{{d.assigned_to}}</td><td><span class="badge {{'red' if d.severity=='Critical' else 'amber'}}">{{d.severity}} · {{d.status}}</span></td></tr>{% endfor %}
    {% if not defects %}<tr><td colspan="3">No unresolved defects.</td></tr>{% endif %}</table></div></section>
    """
    defects=all_rows("SELECT * FROM defects WHERE status!='Resolved' ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 ELSE 3 END LIMIT 5")
    return page("Project Dashboard","A live summary of the case-study project and its current controls.",body,p=p,progress=progress,pending=pending,critical=critical,delayed=delayed,req_count=req_count,evm=ev,alerts=alerts,defects=defects)

@app.route("/project", methods=["GET","POST"])
def project():
    if request.method=="POST":
        try:
            budget=float(request.form["budget"])
            if budget<=0: raise ValueError("Budget must be greater than zero.")
            deadline=request.form["deadline"]
            datetime.strptime(deadline,"%Y-%m-%d")
            run("""UPDATE project SET name=?,objectives=?,stakeholders=?,scope_in=?,scope_out=?,budget=?,deadline=?,status=?,quality_plan=?,closure_notes=? WHERE id=1""",
                (request.form["name"].strip(),request.form["objectives"].strip(),request.form["stakeholders"].strip(),request.form["scope_in"].strip(),request.form["scope_out"].strip(),budget,deadline,request.form["status"],request.form["quality_plan"].strip(),request.form["closure_notes"].strip()))
            flash("Project charter and management plan saved.")
            return redirect(url_for("project"))
        except (ValueError,KeyError) as e:
            flash("Invalid input: "+str(e))
    p=get_project()
    body="""
    <form method="post" class="card"><h3>Project charter & management plan</h3><div class="fields">
    <div class="full"><label>Project name</label><input name="name" required value="{{p.name}}"></div>
    <div class="full"><label>Objectives</label><textarea name="objectives" required>{{p.objectives}}</textarea></div>
    <div class="full"><label>Stakeholders</label><textarea name="stakeholders" required>{{p.stakeholders}}</textarea></div>
    <div><label>In-scope boundaries</label><textarea name="scope_in" required>{{p.scope_in}}</textarea></div>
    <div><label>Out-of-scope boundaries</label><textarea name="scope_out" required>{{p.scope_out}}</textarea></div>
    <div><label>Approved budget (PKR)</label><input type="number" min="1" step="1000" name="budget" required value="{{p.budget}}"></div>
    <div><label>Approved deadline</label><input type="date" name="deadline" required value="{{p.deadline}}"></div>
    <div><label>Project status</label><select name="status">{% for s in ['Not Started','In Progress','On Hold','Completed','Closed'] %}<option {{'selected' if p.status==s else ''}}>{{s}}</option>{% endfor %}</select></div>
    <div><label>Quality management plan</label><textarea name="quality_plan">{{p.quality_plan}}</textarea></div>
    <div class="full"><label>Closure record / notes</label><textarea name="closure_notes">{{p.closure_notes}}</textarea></div></div><button class="btn">Save charter and plan</button></form>
    <div class="card"><h3>Baseline reminder</h3><p class="muted">Original approved budget: PKR 5,000,000. The requested AI diagnosis module and mobile application remain outside approved scope until their change requests are approved.</p></div>
    """
    return page("Initiation & Integration","Manage charter, stakeholders, scope baseline, schedule deadline, quality plan and closure record.",body,p=p)

@app.route("/requirements", methods=["GET","POST"])
def requirements():
    if request.method=="POST":
        action=request.form.get("action")
        try:
            if action=="req":
                title=request.form["title"].strip()
                if not title: raise ValueError("Requirement title is required.")
                status=request.form["status"]
                if status not in ("Proposed","Under Review","Approved","Rejected"): raise ValueError("Invalid requirement status.")
                run("INSERT INTO requirements(title,description,priority,status,source) VALUES(?,?,?,?,?)",(title,request.form.get("description","").strip(),request.form["priority"],status,request.form.get("source","").strip()))
                flash("Requirement saved. Only Approved requirements are treated as approved scope.")
            elif action=="req_update":
                rid=int(request.form["id"]); status=request.form["status"]
                run("UPDATE requirements SET title=?,description=?,priority=?,status=? WHERE id=?",(request.form["title"].strip(),request.form["description"].strip(),request.form["priority"],status,rid))
                flash("Requirement updated.")
            elif action=="change":
                title=request.form["change_title"].strip()
                cost=float(request.form["cost_impact"]); weeks=int(request.form["weeks_impact"])
                if not title or cost<0 or weeks<0: raise ValueError("Enter a title and non-negative impacts.")
                run("INSERT INTO changes(title,justification,cost_impact,weeks_impact,status) VALUES(?,?,?,?, 'Pending')",(title,request.form["justification"].strip(),cost,weeks))
                flash("Change request submitted as Pending.")
            elif action=="change_status":
                cid=int(request.form["id"]); status=request.form["status"]
                cr=one("SELECT * FROM changes WHERE id=?",(cid,))
                if not cr: raise ValueError("Change request not found.")
                run("UPDATE changes SET status=? WHERE id=?",(status,cid))
                if status=="Approved":
                    # Approved change expands the baseline, creates approved requirement if absent,
                    # adds impact to project budget/deadline, and records it in the scope boundary.
                    p=get_project()
                    new_deadline=(datetime.strptime(p["deadline"],"%Y-%m-%d").date()+timedelta(weeks=int(cr["weeks_impact"]))).isoformat()
                    run("UPDATE project SET budget=?,deadline=?,scope_in=? WHERE id=1",
                        (float(p["budget"])+float(cr["cost_impact"]),new_deadline,p["scope_in"]+"; Approved change: "+cr["title"]))
                    if not one("SELECT id FROM requirements WHERE title=?",(cr["title"],)):
                        run("INSERT INTO requirements(title,description,priority,status,source) VALUES(?,?,?,'Approved','Approved change request')",
                            (cr["title"],cr["justification"],"High"))
                    else:
                        run("UPDATE requirements SET status='Approved' WHERE title=?",(cr["title"],))
                    flash("Change approved: requirement added to approved scope and project budget/deadline baseline updated.")
                else:
                    flash("Change request status updated. Only approved changes affect the baseline.")
        except (ValueError,KeyError) as e:
            flash("Invalid input: "+str(e))
        return redirect(url_for("requirements"))
    reqs=all_rows("SELECT * FROM requirements ORDER BY CASE status WHEN 'Proposed' THEN 1 WHEN 'Under Review' THEN 2 WHEN 'Approved' THEN 3 ELSE 4 END,id")
    changes=all_rows("SELECT * FROM changes ORDER BY id DESC")
    body="""
    <div class="grid two"><form method="post" class="card"><h3>Add requirement</h3><input type="hidden" name="action" value="req">
    <label>Requirement title</label><input name="title" required>
    <label style="margin-top:10px">Description</label><textarea name="description"></textarea>
    <div class="fields"><div><label>Priority</label><select name="priority"><option>High</option><option selected>Medium</option><option>Low</option></select></div>
    <div><label>Status</label><select name="status"><option>Proposed</option><option>Under Review</option><option>Approved</option><option>Rejected</option></select></div></div>
    <label style="margin-top:10px">Source / stakeholder</label><input name="source" value="Hospital Management"><button class="btn">Save requirement</button></form>
    <form method="post" class="card"><h3>Submit change request</h3><input type="hidden" name="action" value="change">
    <label>Change title</label><input name="change_title" required placeholder="e.g. Mobile application">
    <label style="margin-top:10px">Justification</label><textarea name="justification" required></textarea>
    <div class="fields"><div><label>Cost impact (PKR)</label><input type="number" min="0" step="1000" name="cost_impact" required value="0"></div>
    <div><label>Schedule impact (weeks)</label><input type="number" min="0" name="weeks_impact" required value="0"></div></div>
    <button class="btn">Submit for approval</button></form></div>
    <section class="card"><h3>Requirements register</h3><p class="muted">Only requirements with Approved status form part of the approved scope.</p><div class="table-wrap"><table><tr><th>Requirement</th><th>Priority</th><th>Status</th><th>Update status</th></tr>
    {% for r in reqs %}<tr><td><b>{{r.title}}</b><div class="muted">{{r.description}}</div></td><td>{{r.priority}}</td><td><span class="badge {{'green' if r.status=='Approved' else 'amber' if r.status in ['Proposed','Under Review'] else ''}}">{{r.status}}</span></td>
    <td><form method="post"><input type="hidden" name="action" value="req_update"><input type="hidden" name="id" value="{{r.id}}"><input type="hidden" name="title" value="{{r.title}}"><input type="hidden" name="description" value="{{r.description or ''}}"><input type="hidden" name="priority" value="{{r.priority}}"><select name="status">{% for s in ['Proposed','Under Review','Approved','Rejected'] %}<option {{'selected' if r.status==s else ''}}>{{s}}</option>{% endfor %}</select><button class="btn secondary">Update</button></form></td></tr>{% endfor %}
    </table></div></section>
    <section class="card"><h3>Change request register</h3><div class="table-wrap"><table><tr><th>Change</th><th>Cost impact</th><th>Schedule impact</th><th>Status / action</th></tr>
    {% for c in changes %}<tr><td><b>{{c.title}}</b><div class="muted">{{c.justification}}</div></td><td>PKR {{'{:,.0f}'.format(c.cost_impact)}}</td><td>{{c.weeks_impact}} week(s)</td><td><form method="post"><input type="hidden" name="action" value="change_status"><input type="hidden" name="id" value="{{c.id}}"><select name="status">{% for s in ['Pending','Approved','Rejected'] %}<option {{'selected' if c.status==s else ''}}>{{s}}</option>{% endfor %}</select><button class="btn secondary">Apply</button></form><span class="badge {{'green' if c.status=='Approved' else 'amber' if c.status=='Pending' else ''}}">{{c.status}}</span></td></tr>{% endfor %}
    </table></div></section>
    """
    return page("Scope & Change Control","Prioritize and approve requirements; review change impacts before they alter the baseline.",body,reqs=reqs,changes=changes)

@app.route("/wbs", methods=["GET","POST"])
def wbs():
    if request.method=="POST":
        try:
            code=request.form["code"].strip(); title=request.form["title"].strip()
            if not code or not title: raise ValueError("WBS code and title are required.")
            run("INSERT INTO wbs(code,title,parent_code,deliverable) VALUES(?,?,?,?)",(code,title,request.form["parent_code"].strip(),request.form["deliverable"].strip()))
            flash("WBS work package added.")
        except (ValueError,KeyError) as e: flash("Invalid input: "+str(e))
        return redirect(url_for("wbs"))
    rows=all_rows("SELECT * FROM wbs ORDER BY code")
    body="""
    <div class="grid two"><section class="card"><h3>Hierarchical WBS</h3><div class="table-wrap"><table><tr><th>WBS</th><th>Deliverable / work package</th><th>Parent</th></tr>
    {% for r in rows %}<tr><td><b>{{r.code}}</b></td><td>{{'　' if '.' in r.code else ''}}{{r.title}}<div class="muted">{{r.deliverable}}</div></td><td>{{r.parent_code or '—'}}</td></tr>{% endfor %}</table></div></section>
    <form method="post" class="card"><h3>Add WBS item</h3><label>WBS code</label><input name="code" required placeholder="e.g. 2.7"><label style="margin-top:10px">Title</label><input name="title" required><label style="margin-top:10px">Parent code</label><input name="parent_code" placeholder="e.g. 2"><label style="margin-top:10px">Deliverable / work package</label><textarea name="deliverable"></textarea><button class="btn">Add WBS item</button></form></div>
    """
    return page("Scope Breakdown Structure","A hierarchical view of deliverables and work packages.",body,rows=rows)

@app.route("/schedule", methods=["GET","POST"])
def schedule():
    if request.method=="POST":
        try:
            title=request.form["title"].strip(); owner=request.form["owner"].strip()
            start=request.form["start_date"]; datetime.strptime(start,"%Y-%m-%d")
            duration=int(request.form["duration"]); cost=float(request.form["planned_cost"]); dep=request.form.get("dependency_id") or None
            pct=int(request.form["percent_complete"])
            if not title or duration<1 or cost<0 or not 0<=pct<=100: raise ValueError("Check title, duration, costs and completion percentage.")
            if dep and not one("SELECT id FROM tasks WHERE id=?",(int(dep),)): raise ValueError("Dependency task does not exist.")
            status="Completed" if pct==100 else "In Progress" if pct>0 else "Not Started"
            run("INSERT INTO tasks(title,owner,start_date,duration,dependency_id,planned_cost,actual_cost,percent_complete,status,milestone) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (title,owner,start,duration,int(dep) if dep else None,cost,float(request.form["actual_cost"]),pct,status,1 if request.form.get("milestone") else 0))
            flash("Activity added to schedule.")
        except (ValueError,KeyError) as e: flash("Invalid input: "+str(e))
        return redirect(url_for("schedule"))
    tasks=schedule_rows(); raw=all_rows("SELECT id,title FROM tasks ORDER BY id")
    today=date.today()
    minstart=min([datetime.strptime(t["start_date"],"%Y-%m-%d").date() for t in tasks],default=today)
    maxend=max([datetime.strptime(t["end_date"],"%Y-%m-%d").date() for t in tasks],default=today+timedelta(days=1))
    span=max(1,(maxend-minstart).days+1)
    chart=[]
    for t in tasks:
        st=datetime.strptime(t["start_date"],"%Y-%m-%d").date()
        offset=max(0,(st-minstart).days)
        left=offset/span*100; width=max(2,int(t["duration"])/span*100)
        chart.append(dict(t,left=min(98,left),width=min(100-left,width)))
    body="""
    <form method="post" class="card"><h3>Add activity / resource assignment</h3><div class="fields">
    <div><label>Activity name</label><input name="title" required></div><div><label>Assigned team member / role</label><input name="owner" required placeholder="e.g. QA Engineer"></div>
    <div><label>Start date</label><input type="date" name="start_date" required value="{{today}}"></div><div><label>Duration (days)</label><input type="number" min="1" name="duration" required value="5"></div>
    <div><label>Dependency (predecessor)</label><select name="dependency_id"><option value="">No dependency</option>{% for t in raw %}<option value="{{t.id}}">{{t.id}} — {{t.title}}</option>{% endfor %}</select></div>
    <div><label>Planned cost (PKR)</label><input type="number" min="0" step="1000" name="planned_cost" value="0"></div>
    <div><label>Actual cost (PKR)</label><input type="number" min="0" step="1000" name="actual_cost" value="0"></div><div><label>Completion (%)</label><input type="number" min="0" max="100" name="percent_complete" value="0"></div>
    <div class="full"><label><input style="width:auto" type="checkbox" name="milestone" value="1"> Mark as milestone</label></div></div><button class="btn">Add activity</button></form>
    <section class="card"><h3>Gantt-style project timeline</h3><p class="muted">Timeline bars use the activity start date and duration. Red indicates an activity whose planned end date has passed while it is not complete.</p>
    <div class="timeline">{% for t in chart %}<div class="timeline-row"><div><b>{{t.title}}</b><div class="muted">{{t.start_date}} → {{t.end_date}}</div></div><div class="track"><div class="taskbar {{'late' if t.delayed else ''}}" style="left:{{t.left}}%;width:{{t.width}}%">{{t.percent_complete}}%</div></div></div>{% endfor %}</div></section>
    <section class="card"><h3>Activity register</h3><div class="table-wrap"><table><tr><th>Activity / owner</th><th>Dates</th><th>Dependency</th><th>Progress</th><th>Costs</th><th>Status</th></tr>
    {% for t in tasks %}<tr><td><b>{{t.title}}</b><div class="muted">{{t.owner}} {% if t.milestone %} · ★ Milestone{% endif %}</div></td><td>{{t.start_date}}<br>to {{t.end_date}}</td><td>{{t.dependency_title or '—'}}{% if t.dependency_late %}<div class="badge amber">Check dependency</div>{% endif %}</td><td><div class="bar"><span style="width:{{t.percent_complete}}%"></span></div>{{t.percent_complete}}%</td><td>Plan {{'{:,.0f}'.format(t.planned_cost)}}<br>Actual {{'{:,.0f}'.format(t.actual_cost)}}</td><td><span class="badge {{'red' if t.delayed else 'green' if t.status=='Completed' else 'blue'}}">{{'Delayed' if t.delayed else t.status}}</span></td></tr>{% endfor %}</table></div></section>
    """
    return page("Schedule & Resources","Create activities, assign owners, set dependencies, and inspect schedule delays.",body,tasks=tasks,raw=raw,chart=chart,today=today.isoformat())

@app.route("/cost", methods=["GET","POST"])
def cost():
    if request.method=="POST":
        try:
            tid=int(request.form["task_id"]); actual=float(request.form["actual_cost"]); pct=int(request.form["percent_complete"])
            if actual<0 or not 0<=pct<=100: raise ValueError("Actual cost must be non-negative and completion must be 0–100.")
            run("UPDATE tasks SET actual_cost=?,percent_complete=?,status=? WHERE id=?",(actual,pct,"Completed" if pct==100 else "In Progress" if pct>0 else "Not Started",tid))
            flash("Actual expenditure and completion updated; EVM recalculated.")
        except (ValueError,KeyError) as e: flash("Invalid input: "+str(e))
        return redirect(url_for("cost"))
    e=evm_data(); tasks=all_rows("SELECT * FROM tasks ORDER BY id")
    plan=sum(t["planned_cost"] for t in tasks); actual=sum(t["actual_cost"] for t in tasks)
    over=actual>get_project()["budget"]
    body="""
    {% if over %}<div class="alert">Budget overrun: actual expenditure exceeds the current approved project budget.</div>{% endif %}
    {% if evm.cpi and evm.cpi<0.9 %}<div class="alert">Cost warning: CPI is below 0.90; the project is spending inefficiently.</div>{% endif %}
    {% if evm.spi and evm.spi<0.9 %}<div class="alert">Schedule warning: SPI is below 0.90; earned work is behind planned work.</div>{% endif %}
    <div class="grid">
    {% for label,val in [('Planned Value (PV)',evm.pv),('Earned Value (EV)',evm.ev),('Actual Cost (AC)',evm.ac)] %}<div class="card"><div class="metric-label">{{label}}</div><div class="metric">PKR {{'{:,.0f}'.format(val)}}</div></div>{% endfor %}
    <div class="card"><div class="metric-label">Approved budget</div><div class="metric">PKR {{'{:,.0f}'.format(evm.budget)}}</div></div></div>
    <div class="grid two"><div class="card"><h3>Performance indices</h3><table><tr><td>Cost Performance Index (CPI = EV / AC)</td><td><span class="badge {{'red' if evm.cpi and evm.cpi<0.9 else 'green'}}">{{'{:.2f}'.format(evm.cpi)}}</span></td></tr>
    <tr><td>Schedule Performance Index (SPI = EV / PV)</td><td><span class="badge {{'red' if evm.spi and evm.spi<0.9 else 'green'}}">{{'{:.2f}'.format(evm.spi)}}</span></td></tr>
    <tr><td>Total planned activity costs</td><td>PKR {{'{:,.0f}'.format(plan)}}</td></tr><tr><td>Total actual expenditure</td><td>PKR {{'{:,.0f}'.format(actual)}}</td></tr></table><p class="muted">CPI/SPI above 1.00 generally indicates better-than-baseline performance; below 1.00 indicates cost or schedule inefficiency.</p></div>
    <form method="post" class="card"><h3>Update activity cost and progress</h3><label>Activity</label><select name="task_id">{% for t in tasks %}<option value="{{t.id}}">{{t.title}}</option>{% endfor %}</select>
    <label style="margin-top:10px">Actual expenditure (PKR)</label><input type="number" name="actual_cost" min="0" step="1000" required>
    <label style="margin-top:10px">Percent complete</label><input type="number" name="percent_complete" min="0" max="100" required><button class="btn">Update EVM data</button></form></div>
    """
    return page("Cost Management & EVM","Track activity cost, actual expenditure and earned value indicators.",body,evm=e,tasks=tasks,plan=plan,actual=actual,over=over)

@app.route("/quality", methods=["GET","POST"])
def quality():
    if request.method=="POST":
        action=request.form.get("action")
        try:
            if action=="defect":
                title=request.form["title"].strip()
                if not title: raise ValueError("Defect title is required.")
                run("INSERT INTO defects(title,description,severity,assigned_to,status,found_date) VALUES(?,?,?,?,?,?)",
                    (title,request.form["description"].strip(),request.form["severity"],request.form["assigned_to"].strip(),request.form["status"],date.today().isoformat()))
                flash("Defect recorded.")
            elif action=="defect_status":
                run("UPDATE defects SET status=? WHERE id=?",(request.form["status"],int(request.form["id"])))
                flash("Defect status updated.")
            elif action=="check":
                run("INSERT INTO checklist(deliverable,check_item,result,notes) VALUES(?,?,?,?)",(request.form["deliverable"].strip(),request.form["check_item"].strip(),request.form["result"],request.form["notes"].strip()))
                flash("Quality checklist item added.")
            elif action=="check_update":
                run("UPDATE checklist SET result=?,notes=? WHERE id=?",(request.form["result"],request.form["notes"].strip(),int(request.form["id"])))
                flash("Inspection result saved.")
            elif action=="risk":
                title=request.form["risk_title"].strip(); l=int(request.form["likelihood"]); i=int(request.form["impact"])
                if not title or not 1<=l<=5 or not 1<=i<=5: raise ValueError("Risk likelihood and impact must be between 1 and 5.")
                run("INSERT INTO risks(title,likelihood,impact,response,status) VALUES(?,?,?,?,?)",(title,l,i,request.form["response"].strip(),request.form["risk_status"]))
                flash("Risk added to prioritization matrix.")
            elif action=="risk_status":
                run("UPDATE risks SET status=? WHERE id=?",(request.form["status"],int(request.form["id"])))
                flash("Risk status updated.")
        except (ValueError,KeyError) as e: flash("Invalid input: "+str(e))
        return redirect(url_for("quality"))
    defects=all_rows("SELECT * FROM defects ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,id")
    checks=all_rows("SELECT * FROM checklist ORDER BY id")
    risks=all_rows("SELECT * FROM risks ORDER BY (likelihood*impact) DESC")
    body="""
    <div class="grid two"><form method="post" class="card"><h3>Log a defect</h3><input type="hidden" name="action" value="defect"><label>Defect title</label><input name="title" required>
    <label style="margin-top:10px">Description</label><textarea name="description"></textarea><div class="fields"><div><label>Severity</label><select name="severity"><option>Critical</option><option>High</option><option selected>Medium</option><option>Low</option></select></div>
    <div><label>Assigned to</label><input name="assigned_to" required></div><div><label>Status</label><select name="status"><option>Open</option><option>In Progress</option><option>Resolved</option></select></div></div><button class="btn">Record defect</button></form>
    <form method="post" class="card"><h3>Add quality checklist item</h3><input type="hidden" name="action" value="check"><label>Deliverable</label><input name="deliverable" required><label style="margin-top:10px">Inspection / test item</label><textarea name="check_item" required></textarea>
    <label style="margin-top:10px">Result</label><select name="result"><option>Not Checked</option><option>Pass</option><option>Fail</option><option>Needs Retest</option></select><label style="margin-top:10px">Notes</label><input name="notes"><button class="btn">Add checklist item</button></form></div>
    <section class="card"><h3>Defect register</h3><div class="table-wrap"><table><tr><th>Defect</th><th>Severity</th><th>Assigned to</th><th>Status / update</th></tr>{% for d in defects %}<tr><td><b>{{d.title}}</b><div class="muted">{{d.description}}</div></td><td><span class="badge {{'red' if d.severity=='Critical' else 'amber'}}">{{d.severity}}</span></td><td>{{d.assigned_to}}</td><td><form method="post"><input type="hidden" name="action" value="defect_status"><input type="hidden" name="id" value="{{d.id}}"><select name="status">{% for s in ['Open','In Progress','Resolved'] %}<option {{'selected' if d.status==s else ''}}>{{s}}</option>{% endfor %}</select><button class="btn secondary">Save</button></form></td></tr>{% endfor %}</table></div></section>
    <section class="card"><h3>Quality checklist & inspection results</h3><div class="table-wrap"><table><tr><th>Deliverable</th><th>Check item</th><th>Result</th><th>Notes / update</th></tr>{% for c in checks %}<tr><td>{{c.deliverable}}</td><td>{{c.check_item}}</td><td><span class="badge {{'green' if c.result=='Pass' else 'red' if c.result=='Fail' else 'amber'}}">{{c.result}}</span></td><td><form method="post"><input type="hidden" name="action" value="check_update"><input type="hidden" name="id" value="{{c.id}}"><select name="result">{% for s in ['Not Checked','Pass','Fail','Needs Retest'] %}<option {{'selected' if c.result==s else ''}}>{{s}}</option>{% endfor %}</select><input name="notes" value="{{c.notes or ''}}" placeholder="Inspection notes"><button class="btn secondary">Save</button></form></td></tr>{% endfor %}</table></div></section>
    <div class="grid two"><form method="post" class="card"><h3>Add risk / issue</h3><input type="hidden" name="action" value="risk"><label>Risk title</label><input name="risk_title" required><div class="fields">
    <div><label>Likelihood (1–5)</label><input type="number" name="likelihood" min="1" max="5" value="3" required></div><div><label>Impact (1–5)</label><input type="number" name="impact" min="1" max="5" value="3" required></div></div>
    <label style="margin-top:10px">Preventive / corrective response (PDPC)</label><textarea name="response" required placeholder="Action to prevent or correct the problem"></textarea><label style="margin-top:10px">Status</label><select name="risk_status"><option>Open</option><option>Monitoring</option><option>Closed</option></select><button class="btn">Add risk</button></form>
    <section class="card"><h3>Risk prioritization matrix & response view</h3><p class="muted">Risk score = likelihood × impact (maximum 25).</p><div class="table-wrap"><table><tr><th>Risk / issue</th><th>L×I</th><th>Priority</th><th>PDPC response</th><th>Status</th></tr>
    {% for r in risks %}<tr><td><b>{{r.title}}</b></td><td>{{r.likelihood}} × {{r.impact}} = <b>{{r.likelihood*r.impact}}</b></td><td><span class="badge {{'red' if r.likelihood*r.impact>=16 else 'amber' if r.likelihood*r.impact>=9 else 'green'}}">{{'High' if r.likelihood*r.impact>=16 else 'Medium' if r.likelihood*r.impact>=9 else 'Low'}}</span></td><td>{{r.response}}</td><td><form method="post"><input type="hidden" name="action" value="risk_status"><input type="hidden" name="id" value="{{r.id}}"><select name="status">{% for s in ['Open','Monitoring','Closed'] %}<option {{'selected' if r.status==s else ''}}>{{s}}</option>{% endfor %}</select><button class="btn secondary">Save</button></form></td></tr>{% endfor %}</table></div></section></div>
    """
    return page("Quality & Risk Control","Track defects, inspection results, risk priorities and preventive/corrective actions.",body,defects=defects,checks=checks,risks=risks)

@app.route("/reports")
def reports():
    p=get_project(); e=evm_data(); tasks=schedule_rows()
    pending=all_rows("SELECT * FROM changes WHERE status='Pending'")
    delayed=[t for t in tasks if t["delayed"]]
    critical=all_rows("SELECT * FROM defects WHERE severity='Critical' AND status!='Resolved'")
    approved=all_rows("SELECT * FROM requirements WHERE status='Approved'")
    body="""
    <section class="card"><h3>Project monitoring report</h3><p><b>{{p.name}}</b></p><p class="muted">Generated: {{today}} · Project status: {{p.status}}</p>
    <div class="grid"><div><div class="metric-label">Approved budget</div><b>PKR {{'{:,.0f}'.format(p.budget)}}</b></div><div><div class="metric-label">Deadline</div><b>{{p.deadline}}</b></div><div><div class="metric-label">Approved scope</div><b>{{approved|length}} requirements</b></div><div><div class="metric-label">PV / EV / AC</div><b>{{'{:,.0f}'.format(e.pv)}} / {{'{:,.0f}'.format(e.ev)}} / {{'{:,.0f}'.format(e.ac)}}</b></div></div></section>
    <div class="grid two"><section class="card"><h3>Pending change requests ({{pending|length}})</h3>{% if pending %}<table><tr><th>Change</th><th>Cost</th><th>Time</th></tr>{% for c in pending %}<tr><td>{{c.title}}</td><td>PKR {{'{:,.0f}'.format(c.cost_impact)}}</td><td>{{c.weeks_impact}} week(s)</td></tr>{% endfor %}</table>{% else %}<p class="muted">No pending change requests.</p>{% endif %}</section>
    <section class="card"><h3>Delayed activities ({{delayed|length}})</h3>{% if delayed %}<table><tr><th>Activity</th><th>Planned end</th><th>Owner</th></tr>{% for t in delayed %}<tr><td>{{t.title}}</td><td>{{t.end_date}}</td><td>{{t.owner}}</td></tr>{% endfor %}</table>{% else %}<p class="muted">No activities are currently past their planned end date.</p>{% endif %}</section>
    <section class="card"><h3>Unresolved critical defects ({{critical|length}})</h3>{% if critical %}<table><tr><th>Defect</th><th>Assigned to</th><th>Status</th></tr>{% for d in critical %}<tr><td>{{d.title}}</td><td>{{d.assigned_to}}</td><td>{{d.status}}</td></tr>{% endfor %}</table>{% else %}<p class="muted">No unresolved critical defects.</p>{% endif %}</section>
    <section class="card"><h3>Approved scope</h3><ul>{% for r in approved %}<li>{{r.title}} <span class="badge green">{{r.priority}}</span></li>{% endfor %}</ul><p class="muted">Pending or rejected requirements are excluded from this list.</p></section></div>
    <button class="btn" onclick="window.print()">Print / Save report as PDF</button>
    """
    return page("Reports & Validation","A consolidated report of progress, change control, schedule, cost and critical quality issues.",body,p=p,e=e,today=date.today().isoformat(),pending=pending,delayed=delayed,critical=critical,approved=approved)

@app.errorhandler(404)
def not_found(e):
    return page("Page not found","The requested page is not available.",'<div class="card">Use the navigation menu to open a module.</div>'),404

@app.errorhandler(500)
def server_error(e):
    return page("Application error","A request could not be completed.",'<div class="alert">Please verify the entered values and restart the local application if the issue continues.</div>'),500

init_db()
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
