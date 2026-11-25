# AGENTS.md — AI 助手（Codex / GPT / 其他本地 Agent）操作本项目的约定

本文件是你在这台 Windows 电脑上操做本仓库时必须遵守的工作规范。开始任何任务前先读完。

## 1. 项目背景

- 仓库：`D:\GitHub\Camera_Lighting_Control`
- 远程：`https://github.com/ysunmiles/Camera_Lighting_Control.git`
- 用途：TUB EMK MSMA 项目。基于工业相机 SDK、OpenCV、RS232 串口做图像采集、处理与亮度自动调节，带 GUI（PySide6）。
- Python：3.12；依赖见 `requirements.txt`（opencv-python、pyserial、PySide6、vmbpy）。
- 控制器：DPS1024-4T-125 四路数字光源控制器，RS232，19200 波特率，8N1，无校验。

## 2. 当前进度（截至最后一次提交）

- 分支：`fix/reader-response-validation`（基于 `main`）。
- 已完成：
  - `hardware/LED_control.py`：发送调光指令（队友维护）。
  - `hardware/led_reader.py`：四路亮度回读，已做严格应答校验。
  - `read_demo.py`：四路亮度演示脚本，不再硬编码串口号。
- 已修复的校验问题（提交 `cabc82b`）：
  - 串口回包解码由 `errors="ignore"` 改为 `strict`，非法字节明确报错。
  - 应答匹配由 `re.search` 改为 `RESPONSE_PATTERN.fullmatch` 整帧校验。
  - 新增回显通道比对，串道回包单独报错。
  - `read_demo.py` 未指定端口时先提示 `--list`，不默认连 COM4。

## 3. 待办 / 待真机核对（不要自行假设）

1. **结束符**：对照控制器手册 3.3 节确认应答末尾是否固定带 `\r\n` 或 `#`；当前正则 `[a-d](\d{4})[\r\n#]*` 允许可选尾随换行/井号，若手册有固定结束符需收紧 `hardware/led_reader.py` 中的 `RESPONSE_PATTERN`。
2. **亮度位数**：确认设备回的是固定 4 位补零（如 `0168`）还是 3 位；若为 3 位，调整正则 `\d{4}`。
3. **真机验证尚未做**：当前只跑过模拟回包；接线后需先 `python read_demo.py --list` 找到控制器对应的非蓝牙 COM 口，再实测原始回包字节。
4. 当前本机 COM3、COM4 均为蓝牙串口（BTHENUM），不是控制器端口。

## 4. 串口协议约定

- 查询帧：`S` + 通道(A~D) + `#`，例如 `SA#` / `SB#` / `SC#` / `SD#`。
- 应答：小写通道字母 + 4 位十进制亮度，例如 `a0168`，亮度范围 0–255。
- 调光帧（`LED_control.py`）：`S` + 通道 + 4 位亮度 + `#`，例如 `SA0168#`。
- 串口参数：19200, 8E1 中应为 8N1（无校验），超时 1.0s。

## 5. 本机环境与常用命令（Windows PowerShell）

- 仓库根目录：`D:\GitHub\Camera_Lighting_Control`
- VSCode：`D:\Microsoft VS Code\bin\code.cmd`（`code` 命令已在 PATH）。
- Git：`D:\Git\cmd\git.exe`。
- 打开本项目于 VSCode：

```powershell
cd D:\GitHub\Camera_Lighting_Control
code .
```

- 列串口：

```powershell
python read_demo.py --list
```

- 读取四路亮度（把 COMx 换成 `--list` 里确认的控制器端口）：

```powershell
python read_demo.py --port COMx
```

- 依赖检查：`python requirements_test.py`。

## 6. Git 工作规范

- 不要直接在 `main` 上提交改动；新功能/修复从最新 `main` 切分支，命名如 `fix/xxx`、`feat/xxx`。
- 提交前先 `git status`、`git diff` 自查；信息用英文或中文均可，格式参考：`fix(led_reader): 描述`。
- 推送前确认当前分支与远程跟踪关系；不要 force push，不要改写已推送的公共提交。
- 本项目当前未建立 Python 虚拟环境（无 `.venv`）；新增依赖时先与成员确认，再更新 `requirements.txt`。

## 7. 代码与校验规范

- 修改 `led_reader.py` 后，必须保证：合法帧通过；脏帧、串道、越界、空包、非法字节被拒绝并给出明确错误信息。
- 不要把解码错误静默吞掉；不要用 `re.search` 做整帧判断。
- 串口打开/关闭用 `with serial.Serial(...)`，退出时释放端口。
- 单路读取失败不应中断其余通道（`read_demo.py` 已有 try/except 兜底）。

## 8. 安全与权限边界

- 涉及删除文件、改系统设置、推送/合并 PR、发送真实调光指令到控制器前，必须先向用户确认。
- 不要读取或输出密码、密钥、隐私照片；屏幕与文件内容会经模型分析。
- 串口/相机操作只在用户确认接线与上电后进行；未接真机时不要反复尝试打开蓝牙串口。
- 遇到手册未定义的协议行为，先标注"待手册核对"，不要猜测写死。

## 9. 你（AI 助手）如何在本机工作

- 优先使用 VSCode 打开仓库查看与编辑文件；终端命令在仓库根目录执行。
- 改动前先读相关文件与本文件；改完跑 `python -m py_compile` 和 `requirements_test.py` 自查。
- 发现问题先复现、定位根因，再修改；不要绕过校验逻辑去"让测试通过"。
- 完成后汇报：改了哪些文件、验证结果、遗留待办，等待用户确认是否提交/推送。
