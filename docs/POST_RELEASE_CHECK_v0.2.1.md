# v0.2.1 发布后检查记录

## 基本信息

- 版本：v0.2.1
- 发布日期：2026-06-30
- Git tag：v0.2.1
- GitHub Release：已发布
- 在线地址：https://hvac-mep-calc-toolbox.streamlit.app/

## 发布状态

- [x] README 当前稳定版本已更新为 v0.2.1
- [x] CHANGELOG 已新增 v0.2.1
- [x] RELEASE_NOTES_v0.2.1.md 已新增
- [x] v0.2.1 tag 已推送
- [x] GitHub Release 已发布
- [x] GitHub Release 显示为最新版本
- [x] 线上页面可访问
- [x] 线上可见五个模块
- [x] 线上显示当前稳定版本 v0.2.1
- [x] 风机 / 水泵结果表不直接显示 None、NaN 或 <NA>
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
