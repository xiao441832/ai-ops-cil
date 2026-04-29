# @ai — 交互式终端运维助手

基于 LLM 的交互式终端运维工具。用自然语言描述需求，AI 生成 Shell 命令并预填到光标处，确认后直接执行。

## 效果演示

```
$ @ai 查询当前目录下最大的三个文件
AI 正在思考... ⠹
思考完成，请回车执行（耗时 2.3s, token: 87）
> du -sh * | sort -rh | head -3█
```

```
$ @ai 删除所有文件
AI 正在思考... ⠋
⚠ 检测到风险命令，已转为注释
思考完成，请回车执行（耗时 1.8s, token: 56）
> # 已拦截风险命令: rm -rf *█
```

## 快速开始

### 1. 安装

```bash
pip install -e .
```

安装后生成两个命令：`@ai` 和 `ai-ops`。

### 2. 设置 Shell Alias（推荐）

`@` 在部分 Shell 中是特殊字符，通过 alias 可以完美解决：

**Bash 用户** — 编辑 `~/.bashrc`：

```bash
alias @ai='ai-ops'
```

**Zsh 用户** — 编辑 `~/.zshrc`：

```bash
alias @ai='ai-ops'
```

保存后执行：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

> **原理**：`ai-ops` 是 pip 注册的合法命令名，alias 将 `@ai` 映射到它。这样在终端输入 `@ai 查询文件` 就等价于 `ai-ops 查询文件`。

> **Windows 用户**：`@ai.exe` 由 pip 直接生成，无需 alias，开箱即用。

### 3. 配置 API Key

首次运行 `@ai` 会自动在 `~/.aiops/config.toml` 创建默认配置：

```bash
@ai 任意文字  # 触发配置文件创建
```

编辑配置文件填入 API Key：

```bash
vim ~/.aiops/config.toml
```

最小配置：

```toml
[llm]
base_url = "https://api.openai.com/v1"
api_key = "sk-your-key-here"
model = "gpt-4o"
```

使用国内中转服务时，只需修改 `base_url`：

```toml
[llm]
base_url = "https://your-relay-service.com/v1"
api_key = "your-key"
model = "gpt-4o"
```

### 4. 开始使用

```bash
@ai 查看当前磁盘使用情况
@ai 找出占用 8080 端口的进程
@ai 统计当前目录下 .py 文件数量
@ai 查看最近 10 条 git 提交记录
```

## 交互方式

| 操作 | 行为 |
|------|------|
| **Enter** | 直接执行预填命令 |
| **← →** | 移动光标编辑命令后再执行 |
| **Backspace** | 删除字符 |
| **Ctrl+C** | 取消并退出 |

## 安全校验

内置 22 条正则黑名单，覆盖以下危险操作：

| 类别 | 示例拦截命令 |
|------|-------------|
| 破坏性文件操作 | `rm -rf /`, `mkfs`, `dd of=/dev/sda`, `shred` |
| 数据库毁坏 | `DROP DATABASE`, `db.dropDatabase()`, `FLUSHALL` |
| 系统关键操作 | `shutdown`, `reboot`, `systemctl stop sshd`, `iptables -F` |
| 危险网络操作 | `curl \| sh`, `nc -e /` |

**拦截行为**：危险命令不会报错退出，而是转为注释预填：

```
> # 已拦截风险命令: sudo rm -rf /opt/*
```

用户仍可手动删除 `#` 前缀执行，安全是建议性的而非强制性的。

你还可以在配置文件中添加自定义拦截规则：

```toml
[safety]
extra_deny_patterns = ["my-custom-dangerous-cmd", "internal-tool\\s+--destroy"]
```

## 完整配置参考

`~/.aiops/config.toml`：

```toml
[llm]
base_url = "https://api.openai.com/v1"   # OpenAI 兼容端点
api_key = ""                               # 必填
model = "gpt-4o"                           # 模型名
temperature = 0.0                          # 温度，0 = 确定性输出
max_tokens = 256                           # 最大输出 token
timeout_seconds = 30                       # 请求超时

[safety]
comment_mode = true                        # 拦截后转注释（true）还是英文提示
extra_deny_patterns = []                   # 自定义拦截正则列表

[display]
language = "zh-CN"                         # 影响系统提示词语言
animation_style = "spinner"                # spinner | dots | none
```

## 项目结构

```
src/ai_ops/
├── cli.py           # 入口 & 主编排
├── config.py         # 配置加载 & 首次初始化
├── llm.py            # httpx 异步 OpenAI 兼容客户端
├── safety.py         # 正则黑名单安全校验
├── prefill.py        # prompt_toolkit 预填机制
├── executor.py       # subprocess 流式执行
├── system_prompt.py  # LLM 系统提示词模板
└── utils.py          # Timer 工具
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码检查
ruff check src/
```

## License

MIT
