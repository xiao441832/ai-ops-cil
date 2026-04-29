# @ai 详细部署文档

## 目录

- [环境要求](#环境要求)
- [安装方式](#安装方式)
- [Shell Alias 配置](#shell-alias-配置)
- [API 配置详解](#api-配置详解)
- [跨平台部署](#跨平台部署)
- [常见问题排查](#常见问题排查)

---

## 环境要求

| 依赖 | 版本要求 |
|------|---------|
| Python | >= 3.10 |
| pip | 最新版 |
| Git | 可选，用于开发者安装 |

核心依赖（pip 自动安装）：

- `prompt_toolkit >= 3.0` — 交互式终端预填
- `httpx[http2] >= 0.27` — 异步 HTTP 客户端
- `tomli >= 2.0` — TOML 解析（Python < 3.11）
- `tomli_w >= 1.0` — TOML 写入

---

## 安装方式

### 方式一：从源码安装（开发者）

```bash
git clone <repo-url> ai-ops-ali
cd ai-ops-ali
pip install -e .
```

### 方式二：从源码安装（带开发工具）

```bash
pip install -e ".[dev]"
```

额外安装：`pytest`, `pytest-asyncio`, `ruff`

### 方式三：pip 直接安装（未来发布到 PyPI 后）

```bash
pip install ai-ops
```

### 验证安装

```bash
ai-ops --help 2>&1 || echo "安装成功，用法: ai-ops <需求描述>"
```

安装成功后，以下可执行文件已生成：

- Linux/macOS: `~/.local/bin/ai-ops`、`~/.local/bin/@ai`
- Windows: `%APPDATA%\Python\Python3X\Scripts\ai-ops.exe`、`%APPDATA%\Python\Python3X\Scripts\@ai.exe`

---

## Shell Alias 配置

### 为什么需要 Alias？

`@ai` 中的 `@` 符号在部分 Shell 中有特殊含义：
- **Bash**：`@` 可能在某些上下文中被特殊解释
- **Zsh**：默认支持 `@` 作为命令名，但 alias 更稳定
- **Fish**：`@` 需要转义

通过 alias，将 `@ai` 映射到 `ai-ops`（pip 注册的合法命令名），确保在所有 Shell 中一致体验。

### Bash 配置

编辑 `~/.bashrc`：

```bash
# 交互式终端运维助手
alias @ai='ai-ops'
```

立即生效：

```bash
source ~/.bashrc
```

验证：

```bash
type @ai
# 输出: @ai is aliased to 'ai-ops'

@ai 查看当前时间
```

### Zsh 配置

编辑 `~/.zshrc`：

```bash
# 交互式终端运维助手
alias @ai='ai-ops'
```

立即生效：

```bash
source ~/.zshrc
```

验证：

```bash
which @ai
# 输出: @ai: aliased to ai-ops

@ai 查看当前时间
```

### Fish 配置

编辑 `~/.config/fish/config.fish`：

```fish
# 交互式终端运维助手
alias @ai='ai-ops'
```

或使用 Fish 的 abbr（缩写展开）：

```fish
abbr -a @ai ai-ops
```

立即生效：

```bash
source ~/.config/fish/config.fish
```

### Windows 配置

Windows 上 `@ai.exe` 由 pip 直接生成，**无需 alias**。

如果 `@ai` 无法识别，需要确保 Scripts 目录在 PATH 中：

```powershell
# 查看当前 Scripts 路径
python -c "import os, sys; print(os.path.join(os.path.dirname(sys.executable), 'Scripts'))"

# 或查看用户级 Scripts 路径
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```

将输出的路径添加到系统 PATH：

1. 打开「设置」→「系统」→「关于」→「高级系统设置」→「环境变量」
2. 在用户变量的 `Path` 中添加上述路径
3. 重启终端

也可在 PowerShell Profile 中设置 alias：

```powershell
# 编辑 Profile
notepad $PROFILE

# 添加以下内容
function Invoke-AiOps { ai-ops @Args }
Set-Alias -Name '@ai' -Value Invoke-AiOps
```

### 远程服务器配置（SSH）

在远程服务器上同样需要配置 alias。登录后：

```bash
echo "alias @ai='ai-ops'" >> ~/.bashrc
source ~/.bashrc
```

如果使用非交互式 SSH 执行命令（如 `ssh server '@ai check disk'`），需要确保 `.bashrc` 在非交互模式下也加载 alias：

```bash
# 在 ~/.bashrc 顶部添加（如果不存在）
if [[ $- != *i* ]] ; then
    source ~/.bashrc 2>/dev/null
fi
```

或直接在命令中使用完整命令名：

```bash
ssh server 'ai-ops check disk'
```

---

## API 配置详解

### 配置文件位置

```
~/.aiops/config.toml
```

首次运行 `@ai` 会自动创建此文件。

### 最小配置

只需填写 `api_key`：

```toml
[llm]
api_key = "sk-your-openai-key"
```

其余使用默认值。

### 使用 OpenAI 官方 API

```toml
[llm]
base_url = "https://api.openai.com/v1"
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
model = "gpt-4o"
temperature = 0.0
max_tokens = 256
timeout_seconds = 30
```

### 使用国内中转服务

```toml
[llm]
base_url = "https://api.aiproxy.io/v1"    # 替换为你的中转地址
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
model = "gpt-4o"
temperature = 0.0
max_tokens = 256
timeout_seconds = 30
```

常见的国内中转只需修改 `base_url`，API 格式完全兼容 OpenAI。

### 使用 Azure OpenAI

```toml
[llm]
base_url = "https://your-resource.openai.azure.com/openai/deployments/your-deployment"
api_key = "your-azure-api-key"
model = "gpt-4o"
temperature = 0.0
max_tokens = 256
timeout_seconds = 30
```

### 使用本地模型（Ollama / LMStudio）

```toml
[llm]
base_url = "http://localhost:11434/v1"    # Ollama 默认端口
api_key = "ollama"                         # Ollama 不需要真实 key，随便填
model = "qwen2.5-coder:7b"                # 本地模型名
temperature = 0.0
max_tokens = 256
timeout_seconds = 60                       # 本地模型可能较慢，增大超时
```

### 自定义安全规则

在配置文件中添加自定义拦截正则：

```toml
[safety]
comment_mode = true
extra_deny_patterns = [
    "company-internal-tool\\s+--destroy",
    "kubectl\\s+delete\\s+namespace\\s+prod",
    "terraform\\s+destroy",
]
```

每条规则是一个 Python 正则表达式，匹配到的命令将被转为注释拦截。

---

## 跨平台部署

### Linux

```bash
# 安装
pip install -e .

# 配置 alias
echo "alias @ai='ai-ops'" >> ~/.bashrc
source ~/.bashrc

# 配置 API Key
@ai init  # 触发配置文件创建
vim ~/.aiops/config.toml

# 验证
@ai 查看系统内存使用
```

### macOS

```bash
# 安装（推荐使用 Homebrew Python）
brew install python@3.12
pip install -e .

# 配置 alias
echo "alias @ai='ai-ops'" >> ~/.zshrc
source ~/.zshrc

# 配置 API Key
@ai init
vim ~/.aiops/config.toml

# 验证
@ai 查看系统内存使用
```

### Windows

```powershell
# 安装
pip install -e .

# 确保 Scripts 目录在 PATH（上面已说明）
# 无需 alias，@ai.exe 直接可用

# 配置 API Key
@ai init
notepad %USERPROFILE%\.aiops\config.toml

# 验证
@ai 查看系统内存使用
```

### Docker 部署（可选）

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

# 配置 alias
RUN echo 'alias @ai="ai-ops"' >> /etc/bash.bashrc

ENTRYPOINT ["ai-ops"]
```

使用：

```bash
docker build -t ai-ops .

# 交互式使用
docker run -it --rm ai-ops "查看磁盘使用"

# 挂载配置文件
docker run -it --rm \
    -v ~/.aiops:/root/.aiops \
    ai-ops "查看磁盘使用"
```

---

## 常见问题排查

### Q: 输入 `@ai` 提示 command not found

**原因**：alias 未配置，或 pip Scripts 目录不在 PATH 中。

**解决**：

1. 确认 `ai-ops` 是否可用：`which ai-ops` 或 `where ai-ops`
2. 如果 `ai-ops` 可用，添加 alias：`echo "alias @ai='ai-ops'" >> ~/.bashrc && source ~/.bashrc`
3. 如果 `ai-ops` 也不可用，检查 PATH 是否包含 pip Scripts 目录

### Q: 提示「请在 ~/.aiops/config.toml 中设置 llm.api_key」

**原因**：首次使用，未配置 API Key。

**解决**：

```bash
vim ~/.aiops/config.toml
# 将 api_key = "" 改为 api_key = "sk-your-key"
```

### Q: 提示「无法连接到 LLM 服务」

**原因**：网络不通或 `base_url` 配置错误。

**解决**：

1. 检查网络：`curl https://api.openai.com/v1/models`
2. 如果在国内，使用中转服务修改 `base_url`
3. 如果在公司内网，检查代理设置

### Q: 提示「API 密钥无效」

**原因**：`api_key` 填写错误或已过期。

**解决**：

1. 确认 Key 格式正确（通常以 `sk-` 开头）
2. 如果使用中转，确认 Key 适用于对应的 `base_url`
3. 检查 Key 是否有余额

### Q: 命令执行后没有颜色输出

**原因**：部分命令（如 `ls --color=auto`）会检测是否在 TTY 中运行。

**解决**：这取决于具体命令。可以尝试在需求中明确指定颜色参数，如 `@ai 用彩色输出当前目录文件列表`。

### Q: Python 版本不是 3.10+

**解决**：

```bash
# 使用 pyenv（Linux/macOS）
pyenv install 3.12
pyenv global 3.12

# 或使用 conda
conda create -n ai-ops python=3.12
conda activate ai-ops
```

### Q: pip install 报错 tomli 相关

**原因**：Python 3.11+ 内置 `tomllib`，不需要 `tomli`。这是自动处理的，无需干预。如果遇到问题：

```bash
pip install --upgrade pip
pip install -e .
```

### Q: 如何更换模型？

编辑 `~/.aiops/config.toml`：

```toml
[llm]
model = "gpt-4o-mini"    # 更快更便宜
# model = "gpt-4o"       # 更强
# model = "qwen2.5-coder:7b"  # 本地模型
```

保存后立即生效，无需重启。
