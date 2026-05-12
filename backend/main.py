from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import SessionLocal

app = FastAPI(title="HRMS API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    v = db.execute(text("SELECT 1")).scalar()
    return {"ok": True, "db": v}

@app.get("/employees")
def list_employees(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT emp_id, emp_no, emp_name, dept_id, pos_id, hire_date, status
        FROM employee
        WHERE is_deleted=0
        ORDER BY emp_id DESC
        LIMIT 100
    """)).mappings().all()
    return list(rows)
from pydantic import BaseModel
from datetime import date
from typing import Optional

class EmployeeCreate(BaseModel):
    emp_no: str
    emp_name: str
    gender: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    dept_id: int
    pos_id: int
    hire_date: date
    status: int = 1

class EmployeeUpdate(BaseModel):
    emp_name: Optional[str] = None
    gender: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    dept_id: Optional[int] = None
    pos_id: Optional[int] = None
    hire_date: Optional[date] = None
    status: Optional[int] = None

@app.post("/employees")
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    db.execute(
        text("""
            INSERT INTO employee(emp_no, emp_name, gender, phone, email, dept_id, pos_id, hire_date, status, is_deleted)
            VALUES (:emp_no, :emp_name, :gender, :phone, :email, :dept_id, :pos_id, :hire_date, :status, 0)
        """),
        payload.model_dump(),
    )
    db.commit()
    return {"ok": True}

@app.put("/employees/{emp_id}")
def update_employee(emp_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"ok": True, "updated": 0}

    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["emp_id"] = emp_id

    result = db.execute(
        text(f"""
            UPDATE employee
            SET {set_clause}
            WHERE emp_id = :emp_id AND is_deleted = 0
        """),
        data,
    )
    db.commit()
    return {"ok": True, "updated": result.rowcount}

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            UPDATE employee
            SET is_deleted = 1
            WHERE emp_id = :emp_id AND is_deleted = 0
        """),
        {"emp_id": emp_id},
    )
    db.commit()
    return {"ok": True, "deleted": result.rowcount}
@app.get("/stats/dept-employee-count")
def stat_dept_employee_count(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT d.dept_name, COUNT(*) AS emp_count
        FROM employee e
        JOIN department d ON d.dept_id = e.dept_id
        WHERE e.is_deleted=0 AND e.status=1
        GROUP BY d.dept_id, d.dept_name
        ORDER BY emp_count DESC
    """)).mappings().all()
    return list(rows)

@app.get("/stats/dept-salary-total")
def stat_dept_salary_total(month: str, db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT d.dept_name, SUM(s.net_salary) AS total_salary
        FROM salary_record s
        JOIN employee e ON e.emp_id = s.emp_id
        JOIN department d ON d.dept_id = e.dept_id
        WHERE s.salary_month = :month
        GROUP BY d.dept_id, d.dept_name
        ORDER BY total_salary DESC
    """), {"month": month}).mappings().all()
    return list(rows)

@app.get("/stats/late-top")
def stat_late_top(month: str, db: Session = Depends(get_db)):
    # month: YYYY-MM
    start = f"{month}-01"
    # 简化处理：用当月+1月的01号作为上界（适合演示；正式可用日期库计算）
    y, m = month.split("-")
    y = int(y); m = int(m)
    if m == 12:
        end = f"{y+1}-01-01"
    else:
        end = f"{y}-{m+1:02d}-01"

    rows = db.execute(text("""
        SELECT e.emp_name, COUNT(*) AS late_times
        FROM attendance_record a
        JOIN employee e ON e.emp_id = a.emp_id
        WHERE a.att_status=2 AND a.att_date >= :start AND a.att_date < :end
        GROUP BY e.emp_id, e.emp_name
        ORDER BY late_times DESC
        LIMIT 10
    """), {"start": start, "end": end}).mappings().all()
    return list(rows)
class DepartmentCreate(BaseModel):
    dept_name: str
    parent_dept_id: Optional[int] = None

class DepartmentUpdate(BaseModel):
    dept_name: Optional[str] = None
    parent_dept_id: Optional[int] = None

@app.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT dept_id, dept_name, parent_dept_id, is_deleted
        FROM department
        WHERE is_deleted=0
        ORDER BY dept_id DESC
        LIMIT 200
    """)).mappings().all()
    return list(rows)

@app.post("/departments")
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO department(dept_name, parent_dept_id, is_deleted)
        VALUES (:dept_name, :parent_dept_id, 0)
    """), payload.model_dump())
    db.commit()
    return {"ok": True}

@app.put("/departments/{dept_id}")
def update_department(dept_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"ok": True, "updated": 0}
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["dept_id"] = dept_id
    result = db.execute(text(f"""
        UPDATE department
        SET {set_clause}
        WHERE dept_id=:dept_id AND is_deleted=0
    """), data)
    db.commit()
    return {"ok": True, "updated": result.rowcount}

@app.delete("/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE department
        SET is_deleted=1
        WHERE dept_id=:dept_id AND is_deleted=0
    """), {"dept_id": dept_id})
    db.commit()
    return {"ok": True, "deleted": result.rowcount}
class PositionCreate(BaseModel):
    pos_name: str
    level_no: int = 1

class PositionUpdate(BaseModel):
    pos_name: Optional[str] = None
    level_no: Optional[int] = None

@app.get("/positions")
def list_positions(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT pos_id, pos_name, level_no, is_deleted
        FROM `position`
        WHERE is_deleted=0
        ORDER BY pos_id DESC
        LIMIT 200
    """)).mappings().all()
    return list(rows)

@app.post("/positions")
def create_position(payload: PositionCreate, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO `position`(pos_name, level_no, is_deleted)
        VALUES (:pos_name, :level_no, 0)
    """), payload.model_dump())
    db.commit()
    return {"ok": True}

@app.put("/positions/{pos_id}")
def update_position(pos_id: int, payload: PositionUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"ok": True, "updated": 0}
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["pos_id"] = pos_id
    result = db.execute(text(f"""
        UPDATE `position`
        SET {set_clause}
        WHERE pos_id=:pos_id AND is_deleted=0
    """), data)
    db.commit()
    return {"ok": True, "updated": result.rowcount}

@app.delete("/positions/{pos_id}")
def delete_position(pos_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("""
        UPDATE `position`
        SET is_deleted=1
        WHERE pos_id=:pos_id AND is_deleted=0
    """), {"pos_id": pos_id})
    db.commit()
    return {"ok": True, "deleted": result.rowcount}
class SalaryCreate(BaseModel):
    emp_id: int
    salary_month: str  # YYYY-MM
    base_salary: float = 0
    bonus: float = 0
    allowance: float = 0
    deduction: float = 0

class SalaryUpdate(BaseModel):
    base_salary: Optional[float] = None
    bonus: Optional[float] = None
    allowance: Optional[float] = None
    deduction: Optional[float] = None

@app.get("/salaries")
def list_salaries(month: Optional[str] = None, db: Session = Depends(get_db)):
    if month:
        rows = db.execute(text("""
            SELECT salary_id, emp_id, salary_month, base_salary, bonus, allowance, deduction, net_salary
            FROM salary_record
            WHERE salary_month=:month
            ORDER BY salary_id DESC
            LIMIT 200
        """), {"month": month}).mappings().all()
    else:
        rows = db.execute(text("""
            SELECT salary_id, emp_id, salary_month, base_salary, bonus, allowance, deduction, net_salary
            FROM salary_record
            ORDER BY salary_id DESC
            LIMIT 200
        """)).mappings().all()
    return list(rows)

@app.post("/salaries")
def create_salary(payload: SalaryCreate, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO salary_record(emp_id, salary_month, base_salary, bonus, allowance, deduction)
        VALUES (:emp_id, :salary_month, :base_salary, :bonus, :allowance, :deduction)
    """), payload.model_dump())
    db.commit()
    return {"ok": True}

@app.put("/salaries/{salary_id}")
def update_salary(salary_id: int, payload: SalaryUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"ok": True, "updated": 0}
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["salary_id"] = salary_id
    result = db.execute(text(f"""
        UPDATE salary_record
        SET {set_clause}
        WHERE salary_id=:salary_id
    """), data)
    db.commit()
    return {"ok": True, "updated": result.rowcount}

@app.delete("/salaries/{salary_id}")
def delete_salary(salary_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("""
        DELETE FROM salary_record WHERE salary_id=:salary_id
    """), {"salary_id": salary_id})
    db.commit()
    return {"ok": True, "deleted": result.rowcount}
class AttendanceCreate(BaseModel):
    emp_id: int
    att_date: date
    check_in: Optional[str] = None   # '09:00:00'
    check_out: Optional[str] = None
    att_status: int = 1
    remark: Optional[str] = None

class AttendanceUpdate(BaseModel):
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    att_status: Optional[int] = None
    remark: Optional[str] = None

@app.get("/attendance")
def list_attendance(month: Optional[str] = None, db: Session = Depends(get_db)):
    # month: YYYY-MM
    if month:
        start = f"{month}-01"
        y, m = month.split("-")
        y = int(y); m = int(m)
        end = f"{y+1}-01-01" if m == 12 else f"{y}-{m+1:02d}-01"
        rows = db.execute(text("""
            SELECT att_id, emp_id, att_date, check_in, check_out, att_status, remark
            FROM attendance_record
            WHERE att_date >= :start AND att_date < :end
            ORDER BY att_id DESC
            LIMIT 300
        """), {"start": start, "end": end}).mappings().all()
    else:
        rows = db.execute(text("""
            SELECT att_id, emp_id, att_date, check_in, check_out, att_status, remark
            FROM attendance_record
            ORDER BY att_id DESC
            LIMIT 300
        """)).mappings().all()
    return list(rows)

@app.post("/attendance")
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO attendance_record(emp_id, att_date, check_in, check_out, att_status, remark)
        VALUES (:emp_id, :att_date, :check_in, :check_out, :att_status, :remark)
    """), payload.model_dump())
    db.commit()
    return {"ok": True}

@app.put("/attendance/{att_id}")
def update_attendance(att_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"ok": True, "updated": 0}
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["att_id"] = att_id
    result = db.execute(text(f"""
        UPDATE attendance_record
        SET {set_clause}
        WHERE att_id=:att_id
    """), data)
    db.commit()
    return {"ok": True, "updated": result.rowcount}

@app.delete("/attendance/{att_id}")
def delete_attendance(att_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("""
        DELETE FROM attendance_record WHERE att_id=:att_id
    """), {"att_id": att_id})
    db.commit()
    return {"ok": True, "deleted": result.rowcount}