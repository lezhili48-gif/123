# LitReviewAgent 小白使用指南（一步一步点）

> 你只需要按顺序做，不懂命令行也可以照着复制。

## 0) 先准备好

你需要：
- 一台已安装 **Python 3.11+**、**Node.js 18+**、**npm** 的电脑。
- 可访问 WoS / Scopus 的校园网或 VPN。
- （可选）OpenAI API Key。

---

## 1) 第一次启动（只做一次）

### 1.1 打开终端
- Windows：按 `Win` 键，搜索 `PowerShell`，打开。
- macOS：打开“终端”。

### 1.2 进入项目目录
把下面命令里的路径替换成你的项目路径：

```bash
cd /workspace/123
```

### 1.3 复制配置文件

```bash
cp .env.example .env
```

### 1.4 安装依赖

```bash
npm install
cd apps/desktop && npm install && cd ../..
cd services/backend && python -m pip install -e .[test] && cd ../..
python -m playwright install chromium
```

---

## 2) 每次使用都这么做

### 2.1 打开终端，进入项目目录

```bash
cd /workspace/123
```

### 2.2 启动应用

```bash
make dev
```

你会看到：
- 后端服务在 `http://127.0.0.1:8000`
- 桌面窗口（Electron）自动弹出

> 不要关闭这个终端窗口，关了程序就停了。

---

## 3) 在桌面 UI 里“点什么”

## 3.1 Dashboard（项目页）
1. 点击顶部 `dashboard`。
2. 在表单里填写：
   - `name`：项目名（例如 `biochar-review`）
   - `query`：检索式
   - `source`：选 `WoS` 或 `Scopus`
   - `year`：例如 `2020-2024`
3. 点击 `create`。
4. 在下方列表勾选你刚创建的项目（单选圆点）。
5. 点击 `Start Run`。

## 3.2 Console（运行控制台）
1. 点击顶部 `console`。
2. 看 `status` 字段：
   - `RUNNING`：自动运行中
   - `NEED_TAKEOVER`：需要你人工接管（登录/验证码/条款）
   - `COMPLETED`：完成
   - `FAILED`：失败
3. 如果出现 `NEED_TAKEOVER`：
   - 在弹出的受控浏览器里手动完成登录/验证码/条款；
   - 回到桌面 UI，点击 `继续(approve takeover)`；
   - 自动化继续运行。

## 3.3 Papers / Evidence
- 点击 `papers`：看导入文献和数量。
- 点击 `evidence`：看抽取的证据条目。

## 3.4 Drafts（生成 Word 草稿）
1. 点击 `drafts`。
2. 点击 `Generate Word Draft`。
3. 页面会出现生成记录（含文件路径）。

## 3.5 Settings
- 点击 `settings` 查看说明。
- 真正的配置在项目根目录 `.env` 文件里改。

---

## 4) 结果文件在哪

都在 `data/` 目录：
- `data/screenshots/`：每一步截图（排错最重要）
- `data/exports/`：导出题录文件
- `data/drafts/`：Word 草稿 `.docx`
- `data/audit/`：审计日志（含导出文件 hash）

---

## 5) 最常见问题

### Q1. 桌面窗口没弹出
- 先确认终端里没有报错；
- 再试一次 `make dev`。

### Q2. 一直 `NEED_TAKEOVER`
- 说明站点需要你人工操作（登录/验证码/同意条款）；
- 完成后记得点 `继续(approve takeover)`。

### Q3. 失败了怎么排查
- 先看 `console` 里的 `message`；
- 再看 `data/screenshots/` 最后一张图，通常能定位问题。

### Q4. 不想保留登录状态（清 Cookie）
删除目录后重启：

```bash
rm -rf services/backend/playwright-profile
```

