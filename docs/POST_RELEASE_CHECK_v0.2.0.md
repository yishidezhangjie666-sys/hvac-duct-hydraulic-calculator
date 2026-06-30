# v0.2.0 发布后检查记录

## 基本信息

- 版本：v0.2.0
- 发布日期：2026-06-30
- Git tag：v0.2.0
- GitHub Release：已发布
- 在线地址：https://hvac-mep-calc-toolbox.streamlit.app/

## 发布状态

- [x] README 当前稳定版本已更新为 v0.2.0
- [x] CHANGELOG 已新增 v0.2.0
- [x] RELEASE_NOTES_v0.2.0.md 已去掉“草稿”
- [x] v0.2.0 tag 已推送
- [x] GitHub Release 已发布
- [x] 线上页面可访问
- [x] 线上可见五个模块
- [x] 本地检查通过

## 当前模块

1. 通风风管水力计算
2. 空调水系统水力计算
3. 空调末端设备初步选型
4. 冷热源设备初步选型
5. 风机 / 水泵选型校核

## 检查命令

```powershell
.venv\Scripts\python.exe -m compileall app.py modules utils
.venv\Scripts\python.exe -m pytest tests
git diff --check
.\scripts\check_project.ps1
```

## 检查结果

- compileall：通过
- pytest：35 passed
- git diff --check：通过
- check_project.ps1：通过
- GitHub Actions：Project Checks passing

## 发布边界

本版本仍采用简化工程计算口径。
计算结果仅用于学习、课程设计辅助核算、工程初步校核和个人作品集展示。
实际工程设计应结合现行规范、设计手册、设备样本、厂家曲线和工程经验复核。

## v0.2.1 建议方向

- README 文案细化和截图排版优化
- Word 导出可读性优化
- 示例数据继续补充典型工况
- 校核阈值评估，但不直接改动
- 线上体验小修
