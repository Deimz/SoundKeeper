# SoundKeeper

[English](README.en.md) · **简体中文**

通过定期播放低振幅噪声，帮助音频设备保持唤醒的 Windows 托盘工具。

本版本基于 **[Deimz/SoundKeeper](https://github.com/Deimz/SoundKeeper)**，增加了设置保存、多语言菜单和自动采样率选择。感谢原作者 Deimz 及上游贡献者的开发和维护。这些修改已通过 [上游 PR #1](https://github.com/Deimz/SoundKeeper/pull/1) 提交。

[本分支发布版本](https://github.com/Jazzwind/SoundKeeper/releases) · [上游项目](https://github.com/Deimz/SoundKeeper) · [反馈问题](https://github.com/Jazzwind/SoundKeeper/issues)

## 项目用途

一些回音壁、蓝牙音箱和耳机会在长时间没有音频时进入待机。SoundKeeper 通过默认音频输出设备定期播放低振幅白噪声，尝试重置设备的待机计时。

是否有效、是否能听到声音取决于设备、系统音量和参数，没有适用于所有设备的固定待机时间或保活设置。蓝牙仍显示已连接也不一定代表设备没有待机。

## 相比上游新增什么

下表以本 Fork 起点的 [上游提交 `7c1fde4`](https://github.com/Deimz/SoundKeeper/tree/7c1fde480cac87edae8d88cc1ba674d4e1868585) 为对照，不表示上游后续版本一定没有这些改进。

| 项目 | 上游基准版本 | 本 Fork |
| --- | --- | --- |
| 界面语言 | 没有语言选择或系统语言匹配机制 | 跟随 Windows 界面语言，或选择英文、简体中文、法语、俄语、西班牙语、阿拉伯语 |
| 时间设置 | 修改 Python 源码中的常量 | 五种等待预设、三种播放时长预设、恢复时间默认值，以及 JSON 自定义数值 |
| 偏好保存 | 没有独立偏好文件 | 自动保存并恢复当前用户的 `config.json` |
| 高级配置 | 修改 `soundkeeper.py` 中的四个常量 | 集中放置源码默认值，支持带校验的 JSON 覆盖时间、振幅、采样率和语言 |
| 采样率 | 使用源码中的固定值 | 检查设备默认采样率，必要时尝试 44100/48000 Hz，也可检查并使用手动指定值 |
| 播放失败 | 静默忽略异常 | 橙色托盘图标、错误状态文字，每 5 秒重试 |
| 高 DPI 菜单 | 没有显式 DPI 初始化或打包 DPI 声明 | PMv2 清单、源码早期初始化，以及旧系统回退 |
| 使用说明 | 英文 README | 默认英文、可切换中文的首页，以及独立中英文说明 |

低音量定期播放、Windows 原生托盘菜单、启用与暂停、开机启动和单实例保护来自原始项目，并不是本 Fork 新增的功能。默认播放 1 秒、播放后等待 55 秒、振幅 0.0001 保持原值；实际设备兼容性仍需验证。

## 功能

- 从托盘启用或暂停保活，退出程序。
- 选择等待时长、播放时长，并恢复时间默认值。
- 开机启动：在当前用户登录 Windows 后启动。
- 自动跟随系统界面语言，或手动选择六种语言。
- 将偏好保存到当前用户的 JSON 文件，下次启动继续使用。
- 自动检查采样率，也支持通过源码和 JSON 指定固定采样率。
- 单实例保护；播放失败时显示橙色图标并重试。
- 不增加独立设置窗口或新的 GUI 框架。

## 下载与运行

### 使用便携程序

打包好的 Windows 程序不需要另外安装 Python。

1. 打开本 Fork 的 [Releases 页面](https://github.com/Jazzwind/SoundKeeper/releases)。
2. 如果已有发布版本，下载附件中的 exe 或便携 ZIP。
3. ZIP 需先解压，将程序放在固定目录，再运行 `SoundKeeper.exe`。
4. 在系统托盘找到绿色图标，右键调整设置或启用开机启动。

如果页面尚无 Release，可以按照下文从源码构建。GitHub 自动生成的 **Source code** 压缩包是源码，不是已经编译的程序。上游发布的旧版 exe 不一定包含本 Fork 新增的菜单和翻译。

更新时先从托盘退出旧版，再运行新版。替换 exe 会保留 `%APPDATA%\SoundKeeper\config.json` 中的偏好。

### 从源码运行

需要 Windows 和 Python 3.9 或以上；依赖版本也需要支持所选 Python 版本。开发分支当前为 `tray-settings-and-localization`。

```powershell
git clone --branch tray-settings-and-localization https://github.com/Jazzwind/SoundKeeper.git
cd SoundKeeper

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe soundkeeper.py
```

这里显式使用虚拟环境的 Python，不需要先运行激活脚本。在 VS Code 中，也应为此项目选择 `.venv\Scripts\python.exe`。

## 托盘菜单

| 菜单项 | 功能 |
| --- | --- |
| 启用音频保活 | 勾选为启用，取消为暂停；重新启用时立即播放 |
| 开机启动 | 注册或取消当前用户的 Windows 登录启动项 |
| 设置 | 选择等待时长、播放时长，或恢复时间默认值 |
| 语言 | 跟随系统或手动选择语言 |
| 退出 | 停止保活并退出程序 |

绿色表示启用，灰色表示暂停。橙色图标及音频状态文字表示播放失败，程序会每隔 5 秒重新检查并尝试恢复。绿色只表示没有报告播放错误，不保证目标设备一定不会待机。

## 配置

### 菜单预设

| 设置 | 选项 | 原始默认值 |
| --- | --- | --- |
| 等待时长 | 30 秒、55 秒、4 分 55 秒、9 分 55 秒、14 分 55 秒 | 55 秒 |
| 播放时长 | 0.01 秒、0.1 秒、1 秒 | 1 秒 |
| 语言 | 跟随系统、英文、简体中文、法语、俄语、西班牙语、阿拉伯语 | 跟随系统 |

等待从**本次播放结束后**开始计算。默认播放 1 秒、等待 55 秒，两次播放开始之间约为 56 秒。等待期间修改音频设置，会按所选等待时长重新计时；正在播放的一段声音正常结束。

等待时长应小于设备的待机超时。很短的声音不一定足以让所有设备保持唤醒。建议先验证默认 1 秒有效，再逐步测试 0.1 秒、0.01 秒。

### 源码默认值

高级用户可以在运行源码或构建 exe 前，修改 `settings.py` 顶部集中放置的默认配置：

```python
DEFAULT_SAMPLE_RATE = "auto"  # 自动选择；也可写设备支持的整数，例如 48000
DEFAULT_DURATION = 1.0
DEFAULT_INTERVAL = 55
DEFAULT_AMPLITUDE = 0.0001
DEFAULT_LANGUAGE = "auto"
```

首次运行没有 JSON 时，使用这些默认值创建配置文件。已有 JSON 中的有效字段优先，包括更新 exe 之后；缺失或无效的字段才使用相应的源码默认值。修改默认值不能覆盖用户已有的有效偏好。

### JSON 高级设置

文件位置：`%APPDATA%\SoundKeeper\config.json`。**先退出程序，再修改并保存，重新启动后生效。**

```json
{
  "wait_seconds": 55,
  "duration_seconds": 1.0,
  "amplitude": 0.0001,
  "sample_rate": "auto",
  "language": "auto"
}
```

JSON 中的时长不限于菜单预设，例如等待 45 秒、播放 0.5 秒也可以。非预设时长会在菜单中显示为已勾选的只读项目，选择预设后切换到预设值。修改菜单不会重置振幅和采样率，也没有手动输入窗口。

| 字段 | 接受的值 |
| --- | --- |
| `wait_seconds` | 0.1 至 86400 秒的数值 |
| `duration_seconds` | 0.001 至 10 秒的数值 |
| `amplitude` | 0 至 1 的数值，较大值可能产生可听见的声音 |
| `sample_rate` | 字符串 `"auto"`，或 8000 至 192000 Hz 范围内、设备支持的整数 |
| `language` | 下表列出的语言代码字符串 |

这些范围用于限制无效参数和过大的音频内存分配，不保证任意参数组合都有效。源码默认值也应遵守这些范围。无效字段回退到源码默认值；旧文件中的 `version` 被忽略，下次保存时不再写入。

固定使用 48000 Hz、法语菜单时，对应字段写为：

```json
{
  "sample_rate": 48000,
  "language": "fr"
}
```

这是部分字段的示例，可以保留原文件中的其他字段。固定采样率是**不带引号的整数**：写 `48000`，不要写 `"48000"` 或 `48000.0`。自动模式写为带引号的 `"auto"`。源码中的等效写法是 `DEFAULT_SAMPLE_RATE = 48000`、`DEFAULT_LANGUAGE = "fr"`。

JSON 不支持注释，不要添加 `#` 或 `//`。配置使用原子替换保存；写入失败会提示，当前会话的设置仍然生效。

“恢复默认设置”只将两个时长恢复为这个 exe 打包时的源码默认值，保留语言、振幅、采样率选择和开机启动状态。每次启动默认启用保活。

### 自动与固定采样率

`sample_rate` 为 `"auto"` 时，程序先检查默认输出设备的默认采样率能否用于双声道 `float32` 音频；不支持则尝试 44100、48000 Hz，并跳过重复值。生成音频和播放音频使用同一个采样率。

检查结果会缓存，设备报告信息变化或播放失败后失效。JSON 只保存用户选择的 `"auto"` 或固定数值，不保存检测结果。手动指定的有效整数若不被设备支持，会报告音频错误，不会悄悄换成另一个采样率。

检测不修改 Windows 音频设置，也不能判断设备是否真的被保活。部分驱动在连接或断开设备后需要重启程序才能刷新设备列表。

### 语言

| 值 | 含义 |
| --- | --- |
| `"auto"` | 跟随系统，没有匹配语言时使用英文 |
| `"en"` | 英文 |
| `"zh-Hans"` | 简体中文 |
| `"fr"` | 法语 |
| `"ru"` | 俄语 |
| `"es"` | 西班牙语 |
| `"ar"` | 阿拉伯语 |

自动模式按 Windows 首选界面语言顺序匹配，不使用地区的数字或日期格式。中文地区变体目前都显示简体中文。手动选择会立即更新菜单并保存，语言名称使用各自语言显示。源码和 JSON 中的语言代码都必须带引号。

## 构建便携 exe

先完成上面的虚拟环境和依赖安装，再运行：

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller SoundKeeper.spec
```

生成文件为 `dist\SoundKeeper.exe`。构建前退出正在使用该文件的程序。也可以不用 spec，执行等效的单文件打包：

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --manifest=SoundKeeper.manifest --icon=icon.ico --name SoundKeeper soundkeeper.py
```

本地已验证的构建约 28.18 MiB，不同 Python 和依赖版本的产物可能不同。单文件程序运行时还需要临时磁盘空间解压运行库；其运行内存并不等于下载大小。开机启动由 Windows Run 注册表项管理，不写入 JSON。

## 故障排查

### 高 DPI 菜单

打包程序通过清单声明 Per-Monitor V2 DPI 感知，并提供旧版 Windows 回退。源码运行时，在任何托盘窗口或消息框创建前初始化 DPI，保留宿主已经设置的 DPI 模式。上述两种构建命令使用同一份清单。

菜单继续使用 pystray 的 Win32 原生后端和 Windows 绘制的文字，不自定义字号，也不增加 GUI 依赖。清单保留普通用户权限、Windows 兼容性、Common Controls v6 和长路径支持。DPI 初始化失败不会阻止保活程序启动。

测试包应在目标缩放下实测；不能只凭清单保证混合 DPI 多显示器行为。本次改动不改变音频参数或已保存的偏好。

- **设备仍然待机**：确认保活已勾选；缩短等待时长；尝试默认 1 秒播放时长。先测不运行程序时的正常待机时间，再做开关对照。
- **图标变橙色**：确认输出设备可用、固定采样率受支持。重新连接设备后仍未恢复时，尝试退出并重启。
- **提示程序已在运行**：先找到旧版托盘图标并退出，单实例限制会阻止新实例启动。
- **看不到图标**：检查 Windows 托盘隐藏区域和任务栏设置；检查进程是否异常退出。
- **修改源码默认值没有效果**：已有 JSON 中的有效字段优先。先退出程序，再修改 JSON 中的对应字段，或移走配置以重新使用全部默认值。

## 开发检查与文档维护

安装依赖后，在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/SyncReadme.py --check
```

回归测试使用临时配置和模拟的音频、注册表操作，不会播放声音或修改真实开机启动项。实际蓝牙长期保活效果、其他驱动兼容性和阿拉伯语视觉排版仍需实机验证。

GitHub 首页默认展开英文。点击顶部“简体中文”在当前页面显示中文并收起英文，点击 English 切回；这不影响应用界面的语言。较旧浏览器可以通过语言标题旁的三角箭头手动展开或收起。

维护时编辑 `README.en.md` 与 `README.zh-CN.md`，再执行：

```powershell
.\.venv\Scripts\python.exe scripts/SyncReadme.py
```

`README.md` 由上述脚本生成。两份独立文档也可以随便携发布包提供，修改文档不需要重新打包 exe。

## 系统要求

- Windows 10 / 11，64 位。
- 可用的音频输出设备；蓝牙回音壁、音箱、耳机等均需按实际设备验证。
- 使用打包程序无需另装 Python；从源码运行需安装 Python 和依赖。
- 下载体积和运行内存随 Python、依赖和音频驱动版本变化。

## 贡献、许可与致谢

欢迎在 [本 Fork](https://github.com/Jazzwind/SoundKeeper) 反馈问题，或参与 [上游项目](https://github.com/Deimz/SoundKeeper) 的讨论与贡献。

项目采用 [MIT 许可](LICENSE)。原始项目来自 Deimz，原图标由上游注明使用 Gemini 生成；托盘使用 [pystray](https://github.com/moses-palmer/pystray)，音频输出使用 [sounddevice](https://python-sounddevice.readthedocs.io/)，图像和数组分别使用 Pillow 与 NumPy。
