# 智能招聘系统前端需求文档 (Web Client)

## 1. 项目概述
本项目旨在构建一个基于 AI 的智能招聘系统前端，配合后端 FastAPI 服务，实现简历自动解析、岗位自动分析以及简历与岗位的智能匹配。
核心亮点在于支持**批量简历流式处理**，提供实时的匹配进度反馈。

## 2. 技术栈要求
- **框架**: Vue 3.x (Composition API) + TypeScript
- **构建工具**: Vite
- **UI 组件库**: Element Plus 或 Ant Design Vue (推荐 Element Plus，适合中后台)
- **CSS 框架**: TailwindCSS (可选，用于原子化样式)
- **网络请求**: Axios 或 Fetch API (需支持流式响应处理)
- **状态管理**: Pinia

## 3. 功能模块设计

### 3.1 岗位管理 (Job Management)
负责管理招聘岗位信息，支持 AI 辅助解析 JD。

**功能点**:
1.  **岗位列表**:
    -   展示已发布的岗位 (ID, 标题, 部门, 经验要求, 技能要求)。
    -   操作: 查看详情, 发起招聘(跳转至简历上传)。
2.  **创建/编辑岗位**:
    -   **AI 解析模式**: 提供一个大文本框，输入原始 JD 文本，调用 `/api/v1/job/parse` 自动填充表单。
    -   **表单模式**: 手动填写标题、部门、技能要求、经验年限等。
    -   提交保存至 `/api/v1/jobs`。

### 3.2 简历匹配工作台 (Matching Workbench) —— **核心功能**
核心业务场景，支持针对特定岗位批量上传简历并实时查看分析结果。

**功能点**:
1.  **岗位选择**: 下拉选择当前要匹配的岗位 (Job ID)。
2.  **批量上传区**:
    -   支持拖拽上传多个 PDF 文件。
    -   调用 `/api/v1/application/batch-submit` 接口。
3.  **实时结果列表 (Streaming UI)**:
    -   **技术难点**: 必须支持处理 **NDJSON (Newline Delimited JSON)** 流式响应。
    -   **交互要求**:
        -   上传开始后，表格应立即出现，并显示"处理中"状态。
        -   后端每处理完一份简历，前端表格应立即自动追加一行新数据，而不是等待所有请求结束。
        -   **展示字段**:
            -   候选人姓名 (Resume Name)
            -   匹配度 (Score) - 使用进度条或颜色标识 (高/中/低)。
            -   匹配分析 (Summary) - 展示简短评价。
            -   状态 (成功/失败) - 展示解析是否报错。
        -   **操作**: 查看详情 (弹窗展示完整简历信息和匹配报告)。

### 3.3 候选人库 (Candidate Pool)
查看历史所有已归档的候选人信息。

**功能点**:
1.  **列表展示**: 分页展示所有候选人。
2.  **筛选**: 按岗位、按匹配分数筛选。

## 4. 接口对接说明 (API Integration)

| 模块 | 动作 | 接口地址 | 请求方式 | 关键参数 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **岗位** | 解析 JD | `/api/v1/job/parse` | POST | `{text: string}` | AI 辅助填单 |
| **岗位** | 创建岗位 | `/api/v1/jobs` | POST | JSON | 保存结构化数据 |
| **匹配** | **批量投递** | `/api/v1/application/batch-submit` | POST | `FormData` | **流式响应** <br> `files`: multiple files <br> `job_id`: int |

### 4.1 流式响应处理规范 (Streaming Handling)
前端需实现类似以下的流式读取逻辑 (Fetch API 示例):

```typescript
const response = await fetch('/api/v1/application/batch-submit', {
  method: 'POST',
  body: formData
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value, { stream: true });
  // 处理 NDJSON: 按换行符分割，解析每个 JSON 对象
  const lines = chunk.split('\n').filter(line => line.trim() !== '');
  for (const line of lines) {
    try {
      const result = JSON.parse(line);
      // TODO: 将 result 追加到 Vue 的响应式列表数据中
      candidates.value.push(result.data);
    } catch (e) {
      console.error('JSON Parse Error', e);
    }
  }
}
```

## 5. 页面原型示意

### 5.1 岗位发布页
```
[ 智能解析 JD 文本框 ] [ 解析按钮 ]
----------------------------------
职位名称: [       ]  部门: [       ]
核心技能: [ Vue3, TS ] (Tag 输入)
...
[ 提交创建 ]
```

### 5.2 批量匹配页 (Streaming)
```
当前岗位: [ 高级 Python 工程师 v ]

[      拖拽上传 PDF 区域      ]
[      (支持多文件上传)       ]

实时匹配结果:
| 状态 | 姓名   | 匹配度 | 核心评价           | 操作 |
|:----:|:------|:------|:-------------------|:----|
| ✅   | 张三   | 85分  | 技术栈匹配，经验足 | [详情] |
| ✅   | 李四   | 40分  | 缺乏相关项目经验   | [详情] |
| 🔄   | 王五.pdf | -   | 分析中...          | -    |
```

## 6. 开发计划建议
1.  **Phase 1**: 搭建项目框架，实现 Job 的 CRUD。
2.  **Phase 2**: 实现 `fetch` 流式读取工具函数，完成批量上传核心功能。
3.  **Phase 3**: 完善 UI 细节，增加图表展示匹配分布。
