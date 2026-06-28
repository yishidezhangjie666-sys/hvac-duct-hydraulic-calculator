# AGENTS.md — 建环工程计算工具箱项目规则

## 1. 项目定位

本项目是“建环工程计算工具箱”Web 应用，用于建筑环境与能源应用工程相关计算、公式展示、数据输入、结果导出和辅助学习。

本项目不是课程设计 Word 文档项目，禁止套用课程设计排版规则。只有在明确处理 Word 导出功能时，才允许参考课程设计格式要求。

核心目标：

* 计算结果准确
* 页面清晰好用
* 公式、变量、单位显示规范
* 导出结果稳定
* 代码可维护，不乱改
* 在线部署稳定可访问

## 2. 总体工作原则

1. 开始修改前，必须先阅读项目结构和相关文件。
2. 每次只解决当前明确问题，不要顺手重构无关模块。
3. 禁止一次性大规模改动多个模块。
4. 不确定公式、单位、变量含义时，必须先标注疑问，不得凭空改公式。
5. UI 优化不能破坏计算逻辑、导出逻辑、数据结构和接口字段。
6. 修改后必须运行检查命令，并汇报检查结果。
7. 所有修改必须可回滚，重要文件修改前先备份。
8. 优先小步修改、小步验证，不要追求一次性大改。
9. 自动化排查最多做 2 轮自查修复，避免无限循环修改。

## 3. 公式与变量显示规则

本项目涉及大量建环专业公式，必须特别注意显示规范。

禁止使用以下伪格式：

* Q_h、P_d、P_j、D_e 这类下划线伪下标
* Qh、Pd、Pj、De 这类普通文本伪下标
* Q h、P d、D e 这类主体和下标分离的错误显示
* Pᵈ、Pᵧ 这类看起来像上标的 Unicode 字符
* HTML 中未验证的 sub/sup 导致页面显示异常
* 乱码、空框、错误上标、错误下标
* 把单位写成斜体
* 私自改公式含义或计算逻辑

网页公式显示推荐规则：

1. Streamlit 页面中的公式说明表，优先使用完整 HTML table。
2. 下标使用 HTML 的 `<sub>`，上标使用 HTML 的 `<sup>`。
3. 使用 `st.markdown(html_string, unsafe_allow_html=True)` 渲染。
4. 不要用 Markdown 表格混合 `<sub>`，避免显示错位。
5. 公式表应配套局部 CSS，确保 sub/sup 在正确位置。
6. 必要时使用 `<span translate="no">...</span>` 防止浏览器翻译破坏公式或单位。
7. 单位 Pa 应写作 `<span translate="no">Pa</span>（帕）`。
8. 单位 Pa/m 应写作 `<span translate="no">Pa/m</span>（帕/米）`。
9. 不要让页面中孤立出现容易被翻译成地名的 Pa。

Word 导出公式推荐规则：

1. Word 导出中，优先使用 Word 真实下标。
2. 使用 python-docx 时，下标应通过 `run.font.subscript = True` 实现。
3. 变量本体和下标可斜体，单位必须正体。
4. 不要用 Q_h、P_d、Qh、Pd 伪装下标。
5. Unicode 下标只可作为谨慎兜底，不得用于 d、y 等容易变成上标的字符。

单位显示规则：

* Pa、kPa、MPa、m³/h、m²、m³/s、m/s、kg/m³、W、kW、℃ 必须显示正确。
* 单位必须保持正体。
* 不得把单位误写成变量。
* 不得把 Pa 翻译成“宾夕法尼亚州”。

## 4. 计算逻辑保护规则

涉及以下文件时必须谨慎：

* app.py
* modules/
* utils/
* requirements.txt
* sample_data.csv
* 导出相关代码
* Excel、Word、CSV 导出逻辑

没有用户明确要求，禁止修改：

* 计算公式
* 默认参数
* 单位换算
* 风管、水管、空调水系统、通风除尘等核心计算逻辑
* 导出字段名称和字段顺序

修改计算模块前必须说明：

1. 修改原因
2. 原公式或原逻辑
3. 新公式或新逻辑
4. 是否影响历史结果
5. 如何验证

## 5. UI 优化规则

UI 优化目标是让页面更清楚、更像正式工程工具，而不是炫技。

允许优化：

* 页面布局
* 卡片层级
* 表单对齐
* 按钮状态
* 空状态提示
* 错误提示
* 公式说明表可读性
* 移动端适配
* 结果区排版

禁止：

* 为了“高级感”加入大量动画
* 引入大型 UI 框架
* 破坏原有功能
* 隐藏必要参数
* 删除用户可理解的说明文字
* 把专业工具做成花哨展示页
* 为了美观牺牲公式、单位和计算结果的清晰度

## 6. 依赖管理规则

1. 不要随便新增依赖。
2. 新增依赖前必须说明为什么需要、是否有轻量方案、影响哪些文件、是否影响部署。
3. 不得随意升级 requirements.txt 中的依赖版本。
4. 不得删除已有依赖，除非确认未使用。
5. 不要把 Python 内置库写入 requirements.txt，例如 math、io、os、pathlib、datetime 等。

## 7. 检查命令

每次修改后，根据项目实际情况运行检查。

本项目是 Python + Streamlit 项目，优先运行：

python -m compileall app.py modules utils

或：

python -m compileall .

如需本地运行，使用：

python -m streamlit run app.py

如果项目有测试，运行：

pytest

如果某条命令不存在，需要说明“项目未配置该命令”，不能假装已运行。

## 8. Git 与部署规则

1. 修改前必须先运行 git status。
2. 提交前必须运行 git diff 检查改动范围。
3. 不要提交 `.venv/`、`__pycache__/`、`*.pyc`、临时 `docx/xlsx/csv`。
4. 不要修改 GitHub 远程地址。
5. 推送到 main 后，Streamlit Community Cloud 会自动重新部署。
6. 线上地址为：
   https://hvac-mep-calc-toolbox.streamlit.app/
7. 推送后需要检查线上页面是否更新成功。

## 9. 汇报格式

每次完成后必须汇报：

1. 修改了哪些文件
2. 解决了什么问题
3. 有没有改计算逻辑
4. 有没有改导出逻辑
5. 运行了哪些检查命令
6. 检查是否通过
7. git status 当前状态
8. 还有哪些风险或待确认项
9. 建议的提交命令

## 10. 可调用技能建议

如果当前 Codex 环境有这些 skills，可以按需使用：

* safe-powershell：涉及 PowerShell、文件备份、批量检查时优先使用
* plan：开始前先做简短计划
* debug-fixer：排查报错、页面异常、运行失败
* code-reviewer：修改后做代码审查
* ui-polish：做小范围 UI 优化
* webapp-builder：新增 Web 功能时使用
* deployment-check：部署前后检查 Streamlit 在线可用性
* git-workflow：提交前检查 git status、git diff、commit
* release-notes：阶段性整理修改记录
* readme-maker：完善 README
* spreadsheet-worker：处理 Excel
* docx-worker：处理 Word 导出
* pdf-reader：读取 PDF 资料

注意：
不要因为有 skill 就过度调用。优先完成用户当前目标。

## 11. 当前项目重点

当前项目已经完成：

* Streamlit 在线部署
* 通风风管水力计算模块
* 空调水系统水力计算模块
* CSV / Excel / Word 导出
* README 展示和在线体验链接

当前优先级：

1. 修复明显显示错误
2. 保证线上可访问
3. 保证导出功能稳定
4. 保证 README 与 GitHub 展示清晰
5. 后续再考虑新增冷热源、风机盘管、新风负荷等模块
