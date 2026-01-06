# AI 智能招聘系统 (AI Recruitment System)

基于 LLM (GLM-4.7) 的智能简历解析与人岗匹配系统。模拟真实 HR 的筛选逻辑，提供“硬性规则过滤”与“多维度评分”功能。

## 🚀 核心功能

1.  **简历解析**：
    *   支持 PDF 格式简历自动解析。
    *   结构化提取：姓名、联系方式、学历、技能栈、工作经历（含详细时间段）。
    *   **自动工龄计算**：基于工作经历起止时间（自动识别“至今”），精确计算总工龄（Float）。
2.  **人岗匹配 (AI Screening)**：
    *   **硬性风控 (Hard Filter)**：自动拦截学历不符、技能缺失、经验不足、频繁跳槽等高风险候选人。
    *   **多维度评分**：从技能 (50%)、经验 (30%)、学历 (20%) 三个维度打分。
    *   **一票否决权**：单项分数过低会强制拉低总分。
    *   **详细分析报告**：生成包含风险提示、分项评价的 JSON 报告。
3.  **批量处理**：
    *   支持多份简历批量上传与并行解析。
    *   所有匹配结果（含详细评分细节）完整持久化至数据库。

## 🛠️ 技术栈

*   **后端**: Python 3.11, FastAPI, SQLAlchemy
*   **AI/LLM**: LangChain, 智谱 GLM-4.7 (Thinking Mode Enabled/Disabled)
*   **数据库**: MySQL (推荐) / SQLite
*   **环境管理**: Conda

## 📦 快速开始

### 1. 环境准备

确保已安装 [Anaconda](https://www.anaconda.com/) 或 Miniconda。

```bash
# 1. 创建环境
conda env create -f environment.yml

# 2. 激活环境
conda activate ai-recruitment
```

### 2. 配置应用

在项目根目录创建 `.env` 文件：

```ini
# .env
OPENAI_API_KEY=your_zhipu_api_key
OPENAI_API_BASE=https://open.bigmodel.cn/api/coding/paas/v4
OPENAI_MODEL_NAME=glm-4.7

# 数据库配置 (示例为本地 MySQL)
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hr_recruitment
# 或者使用 SQLite 进行快速测试
# DATABASE_URL=sqlite:///./sql_app.db
```

### 3. 初始化数据库

确保 MySQL 服务已启动，并手动创建数据库（如果未配置自动创建）：

```sql
CREATE DATABASE hr_recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

后端服务启动时会自动创建表结构。如果需要手动执行 SQL 脚本，可参考 `scripts/init.sql`。

### 4. 启动服务

```bash
# 确保在项目根目录下
python src/main.py
```

服务将运行在: `http://localhost:8000`

### 5. API 文档

启动服务后，访问 Swagger UI 查看接口文档：
*   地址: `http://localhost:8000/docs`（注：代码中可能禁用了默认 docs，请访问自定义的 Swagger 路由或直接测试接口）

## 🧪 主要接口说明

### 1. 创建职位 (Create Job)
*   **POST** `/api/v1/jobs`
*   用于录入 JD（职位描述），系统会生成 Job ID。

### 2. 批量投递与匹配 (Batch Submit)
*   **POST** `/api/v1/application/batch-submit`
*   **参数**:
    *   `job_id`: 目标职位 ID
    *   `files`: 多个 PDF 简历文件
*   **返回**: JSON 数组，包含每份简历的解析结果、匹配分数、Hard Fail 原因及详细分析。

## 📂 项目结构

```
.
├── src/
│   ├── chain/          # LangChain 业务逻辑链
│   ├── domain/         # Pydantic 领域模型
│   ├── infra/          # 基础设施 (DB, LLM)
│   ├── models/         # SQLAlchemy 数据库模型
│   ├── prompt/         # Jinja2 提示词模板 (核心风控逻辑)
│   ├── service/        # 业务服务层
│   ├── utils/          # 工具类 (PDF解析, 日期计算)
│   ├── config.py       # 配置加载
│   └── main.py         # FastAPI 入口
├── scripts/
│   └── init.sql        # 数据库初始化脚本
├── environment.yml     # Conda 环境配置
└── README.md           # 项目说明
```
