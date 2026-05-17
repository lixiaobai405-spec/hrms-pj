-- ============================================================
-- HRMS 数据库初始化脚本
-- 建表 + 索引 + 存储过程 + 示例数据（seed）
-- 仅在 Docker volume 首次创建时执行
-- ============================================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ----------------------------
-- 1. 部门表 department
-- ----------------------------
CREATE TABLE IF NOT EXISTS department (
    dept_id         BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '部门编号',
    dept_name       VARCHAR(50)     NOT NULL                 COMMENT '部门名称',
    parent_dept_id  BIGINT          DEFAULT NULL             COMMENT '上级部门编号',
    is_deleted      TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除标记（0正常/1删除）',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (dept_id),
    UNIQUE KEY uk_dept_name (dept_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- ----------------------------
-- 2. 岗位表 position
-- ----------------------------
CREATE TABLE IF NOT EXISTS `position` (
    pos_id          BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '岗位编号',
    pos_name        VARCHAR(50)     NOT NULL                 COMMENT '岗位名称',
    level_no        INT             NOT NULL DEFAULT 1      COMMENT '岗位等级',
    is_deleted      TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除标记（0正常/1删除）',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (pos_id),
    UNIQUE KEY uk_pos_name (pos_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- ----------------------------
-- 3. 员工表 employee
-- ----------------------------
CREATE TABLE IF NOT EXISTS employee (
    emp_id          BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '员工编号',
    emp_no          VARCHAR(20)     NOT NULL                 COMMENT '工号',
    emp_name        VARCHAR(50)     NOT NULL                 COMMENT '姓名',
    gender          TINYINT         DEFAULT NULL             COMMENT '性别（1男/2女）',
    phone           VARCHAR(20)     DEFAULT NULL             COMMENT '手机号',
    email           VARCHAR(100)    DEFAULT NULL             COMMENT '邮箱',
    dept_id         BIGINT          NOT NULL                 COMMENT '部门编号',
    pos_id          BIGINT          NOT NULL                 COMMENT '岗位编号',
    hire_date       DATE            NOT NULL                 COMMENT '入职日期',
    status          TINYINT         NOT NULL DEFAULT 1      COMMENT '员工状态（1在职/2离职/3试用）',
    is_deleted      TINYINT         NOT NULL DEFAULT 0      COMMENT '逻辑删除标记（0正常/1删除）',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (emp_id),
    UNIQUE KEY uk_emp_no (emp_no),
    UNIQUE KEY uk_phone (phone),
    UNIQUE KEY uk_email (email),
    KEY idx_employee_dept_status (dept_id, status),
    KEY idx_employee_name (emp_name),
    CONSTRAINT fk_employee_dept FOREIGN KEY (dept_id) REFERENCES department (dept_id),
    CONSTRAINT fk_employee_pos  FOREIGN KEY (pos_id)  REFERENCES `position` (pos_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工表';

-- ----------------------------
-- 4. 薪资记录表 salary_record
-- ----------------------------
CREATE TABLE IF NOT EXISTS salary_record (
    salary_id       BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '薪资记录编号',
    emp_id          BIGINT          NOT NULL                 COMMENT '员工编号',
    salary_month    CHAR(7)         NOT NULL                 COMMENT '薪资月份（YYYY-MM）',
    base_salary     DECIMAL(10,2)   NOT NULL DEFAULT 0     COMMENT '基本工资',
    bonus           DECIMAL(10,2)   NOT NULL DEFAULT 0     COMMENT '奖金',
    allowance       DECIMAL(10,2)   NOT NULL DEFAULT 0     COMMENT '补贴',
    deduction       DECIMAL(10,2)   NOT NULL DEFAULT 0     COMMENT '扣款',
    net_salary      DECIMAL(10,2)   GENERATED ALWAYS AS (base_salary + bonus + allowance - deduction) STORED COMMENT '实发工资',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (salary_id),
    UNIQUE KEY uk_salary_emp_month (emp_id, salary_month),
    KEY idx_salary_month (salary_month),
    CONSTRAINT fk_salary_emp FOREIGN KEY (emp_id) REFERENCES employee (emp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='薪资记录表';

-- ----------------------------
-- 5. 考勤记录表 attendance_record
-- ----------------------------
CREATE TABLE IF NOT EXISTS attendance_record (
    att_id          BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '考勤记录编号',
    emp_id          BIGINT          NOT NULL                 COMMENT '员工编号',
    att_date        DATE            NOT NULL                 COMMENT '考勤日期',
    check_in        TIME            DEFAULT NULL             COMMENT '上班时间',
    check_out       TIME            DEFAULT NULL             COMMENT '下班时间',
    att_status      TINYINT         NOT NULL DEFAULT 1      COMMENT '考勤状态（1正常/2迟到/3早退/4缺勤）',
    remark          VARCHAR(200)    DEFAULT NULL             COMMENT '备注',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (att_id),
    UNIQUE KEY uk_att_emp_date (emp_id, att_date),
    KEY idx_att_date (att_date),
    CONSTRAINT fk_att_emp FOREIGN KEY (emp_id) REFERENCES employee (emp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考勤记录表';

-- ----------------------------
-- 6. 自定义存储过程（部门月度薪资统计）
-- ----------------------------
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_dept_salary_total $$
CREATE PROCEDURE sp_dept_salary_total(IN p_month CHAR(7))
BEGIN
    SELECT d.dept_name, SUM(s.net_salary) AS total_salary
    FROM salary_record s
    JOIN employee e ON e.emp_id = s.emp_id
    JOIN department d ON d.dept_id = e.dept_id
    WHERE s.salary_month = p_month
    GROUP BY d.dept_id, d.dept_name
    ORDER BY total_salary DESC;
END $$

DELIMITER ;

-- ----------------------------
-- 7. 示例数据（seed）
-- ----------------------------
-- 部门
INSERT INTO department (dept_name, parent_dept_id) VALUES
('总经办', NULL),
('技术部', NULL),
('产品部', NULL),
('市场部', NULL),
('人力资源部', NULL);

-- 岗位
INSERT INTO `position` (pos_name, level_no) VALUES
('总经理',       5),
('部门经理',     4),
('高级工程师',   3),
('工程师',       2),
('助理',         1),
('实习生',       1);

-- 员工
INSERT INTO employee (emp_no, emp_name, gender, phone, email, dept_id, pos_id, hire_date, status) VALUES
('E1001', '张三',   1, '13800001001', 'zhangsan@hrms.com',   1, 1, '2020-01-15', 1),
('E1002', '李四',   1, '13800001002', 'lisi@hrms.com',       2, 2, '2020-06-01', 1),
('E1003', '王五',   2, '13800001003', 'wangwu@hrms.com',     2, 3, '2021-03-10', 1),
('E1004', '赵六',   1, '13800001004', 'zhaoliu@hrms.com',    3, 2, '2019-09-01', 1),
('E1005', '孙七',   2, '13800001005', 'sunqi@hrms.com',      4, 4, '2022-07-20', 1),
('E1006', '周八',   1, '13800001006', 'zhouba@hrms.com',     5, 2, '2021-01-05', 1),
('E1007', '吴九',   2, '13800001007', 'wujiu@hrms.com',      3, 5, '2023-02-14', 1),
('E1008', '郑十',   1, '13800001008', 'zhengshi@hrms.com',   2, 6, '2024-06-01', 3),
('E1009', '冯十一', 2, '13800001009', 'fengshiyi@hrms.com',  4, 4, '2023-08-15', 1),
('E1010', '陈十二', 1, '13800001010', 'chenshier@hrms.com',  5, 3, '2022-11-20', 1);

-- 薪资记录（2024-06 月份）
INSERT INTO salary_record (emp_id, salary_month, base_salary, bonus, allowance, deduction) VALUES
(1,  '2024-06', 20000.00, 5000.00, 1000.00, 500.00),
(2,  '2024-06', 15000.00, 3000.00, 800.00,  300.00),
(3,  '2024-06', 12000.00, 2000.00, 600.00,  200.00),
(4,  '2024-06', 16000.00, 4000.00, 900.00,  400.00),
(5,  '2024-06', 8000.00,  1000.00, 500.00,  100.00),
(6,  '2024-06', 14000.00, 2500.00, 700.00,  350.00),
(7,  '2024-06', 6000.00,  500.00,  400.00,  50.00),
(8,  '2024-06', 5000.00,  300.00,  300.00,  0.00),
(9,  '2024-06', 9000.00,  1500.00, 500.00,  150.00),
(10, '2024-06', 13000.00, 2000.00, 600.00,  250.00);

-- 考勤记录（最近一周示例）
INSERT INTO attendance_record (emp_id, att_date, check_in, check_out, att_status, remark) VALUES
(1,  '2024-06-10', '08:55:00', '18:05:00', 1, NULL),
(1,  '2024-06-11', '09:10:00', '18:00:00', 2, '交通拥堵'),
(1,  '2024-06-12', '08:50:00', '18:02:00', 1, NULL),
(2,  '2024-06-10', '08:45:00', '17:55:00', 1, NULL),
(2,  '2024-06-11', '08:58:00', '18:10:00', 1, NULL),
(3,  '2024-06-10', '09:05:00', '18:00:00', 2, NULL),
(3,  '2024-06-11', '08:30:00', '17:45:00', 1, NULL),
(4,  '2024-06-10', NULL,       NULL,       4, '请假'),
(4,  '2024-06-11', '08:50:00', '18:00:00', 1, NULL),
(5,  '2024-06-10', '09:15:00', '17:30:00', 3, '早退'),
(7,  '2024-06-10', '09:20:00', '18:00:00', 2, NULL),
(8,  '2024-06-10', '09:10:00', '18:05:00', 2, NULL),
(9,  '2024-06-10', '08:55:00', '18:00:00', 1, NULL),
(10, '2024-06-10', '09:05:00', '17:50:00', 2, NULL);
