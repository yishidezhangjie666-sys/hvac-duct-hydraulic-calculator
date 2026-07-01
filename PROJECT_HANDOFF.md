# 建环工程计算工具箱项目交接说明

## 1. 项目一句话说明

建环工程计算工具箱是一个基于 Python + Streamlit 的建筑环境与能源应用工程在线计算工具箱，覆盖通风风管、空调水系统、空调末端、冷热源设备和风机 / 水泵选型校核，支持在线计算、简化校核和 CSV / Excel / Word 导出。

## 2. 当前版本状态

- 当前稳定版本：v0.2.1
- v0.2.0：已发布并归档
- v0.2.1：已发布并归档
- main：已完成展示优化、作品集文档、FAQ、截图刷新和版本一致性修复
- 当前测试：44 passed
- 当前线上地址：https://hvac-mep-calc-toolbox.streamlit.app/

## 3. 当前模块

1. 通风风管水力计算
2. 空调水系统水力计算
3. 空调末端设备初步选型
4. 冷热源设备初步选型
5. 风机 / 水泵选型校核

## 4. 主要技术栈

- Python
- Streamlit
- pandas
- openpyxl
- python-docx
- pytest
- GitHub Actions
- Streamlit Community Cloud

## 5. 主要目录和文件

- `app.py`：Streamlit 入口和侧边栏模块入口
- `modules/`：各计算模块页面和计算逻辑
- `utils/`：导出、Word 报告、校核说明等工具
- `tests/`：计算、导出、文档链接、版本边界测试
- `docs/`：用户指南、展示说明、FAQ、Roadmap、发布后检查
- `screenshots/`：README 和展示文档使用的截图
- `RELEASE_NOTES_v0.2.0.md` / `RELEASE_NOTES_v0.2.1.md`：历史发布说明
- `CHANGELOG.md`：版本变更记录
- `AGENTS.md`：项目维护规则

## 6. 已完成的重要工作

- 五个模块功能闭环
- CSV / Excel / Word 导出
- Word 计算说明书基础结构
- 示例数据和校核说明
- pytest 测试
- GitHub Actions
- Streamlit Cloud 部署
- v0.2.0 Release
- v0.2.1 Release
- 发布后归档
- README 展示优化
- `docs/PROJECT_SHOWCASE.md`
- `docs/PORTFOLIO_PITCH.md`
- `docs/FAQ.md`
- v0.2.1 截图刷新
- `app.py` 版本展示修复为 v0.2.1

## 7. 维护禁区

后续维护时禁止随意修改：

- 核心计算公式
- 校核阈值
- 单位换算
- CSV / Excel / Word 导出字段和顺序
- 已发布 tag
- 已发布 Release
- GitHub Actions
- `requirements.txt`

除非有明确测试、文档说明和版本计划。

## 8. 推荐的后续方向

优先考虑：

- README 截图和展示细节微调
- 示例数据扩充
- Word 导出可读性细节优化
- 用户指南补充常见输入案例
- 小范围修复线上展示问题

不建议马上做：

- 大型新计算模块
- 厂家设备库
- AI 自动生成计算书
- 正式工程设计软件包装
- 商业化功能
- 用户登录和数据库系统

## 9. 每次修改前必须做的检查

```powershell
.venv\Scripts\python.exe -m compileall app.py modules utils
.venv\Scripts\python.exe -m pytest tests
git diff --check
.\scripts\check_project.ps1
```

## 10. 给下一个 AI / Codex 的提醒

这是一个已经发布并归档到 v0.2.1 的稳定项目。后续任务应以维护、展示优化和小修为主，不要主动重构、不要主动改公式、不要主动新增大功能、不要主动发新版本。所有修改必须先确认范围，再跑全量测试，再提交。
