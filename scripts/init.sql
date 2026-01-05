-- 初始化数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS hr_recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hr_recruitment;

-- 创建职位表 (jobs)
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '职位名称',
    department VARCHAR(255) COMMENT '部门',
    required_skills JSON COMMENT '必须技能 (JSON Array)',
    nice_to_have_skills JSON COMMENT '加分技能 (JSON Array)',
    required_experience_years INT DEFAULT 0 COMMENT '要求工作年限',
    degree_requirement VARCHAR(255) COMMENT '学历要求',
    responsibilities TEXT COMMENT '岗位职责',
    raw_text TEXT COMMENT '原始JD文本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建候选人表 (candidates)
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) COMMENT '候选人姓名',
    email VARCHAR(255) COMMENT '邮箱',
    phone VARCHAR(50) COMMENT '电话',
    summary TEXT COMMENT '个人简介',
    skills JSON COMMENT '技能列表 (JSON Array)',
    education JSON COMMENT '教育经历 (JSON Array)',
    work_experience JSON COMMENT '工作经历 (JSON Array)',
    
    -- 匹配信息
    matched_job_id INT COMMENT '关联的职位ID',
    match_score FLOAT COMMENT '匹配分数 (0-100)',
    match_analysis TEXT COMMENT '匹配分析报告',
    
    -- 文件信息
    resume_path VARCHAR(512) COMMENT '简历文件路径',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (matched_job_id) REFERENCES jobs(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
