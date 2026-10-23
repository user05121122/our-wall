# 我们仨的墙

小颜 · 颜叙 · 小沐 共用的一面留言墙。

- **零依赖**：只用 Python 标准库，`python3 wall.py` 就能跑。
- **数据在** `/opt/our-wall/data/wall.json`，跟着这个目录走。
- **口令保护**：外网访问需要 `?k=<口令>`；内网/本机/服务器自身来源免口令。
- **systemd 托管**：服务器重启自动起来（`our-wall.service`）。

## 跑起来

> ⚠️ **国内服务器直接拉 GitHub 会被重置**（`raw.githubusercontent.com` 连不上）。
> 用下面任意一个镜像，都实测过可用：

```bash
# 镜像三选一
M=https://cdn.jsdelivr.net/gh/user05121122/our-wall@main
# M=https://ghproxy.net/https://raw.githubusercontent.com/user05121122/our-wall/main
# M=https://gh-proxy.com/https://raw.githubusercontent.com/user05121122/our-wall/main

curl -fsSL "$M/wall.py" -o wall.py
curl -fsSL "$M/our-wall.service" -o our-wall.service
```

完整安装：

```bash
install -d -m 755 /opt/our-wall /opt/our-wall/data
id -u ourwall >/dev/null 2>&1 || useradd --system --home /opt/our-wall --shell /usr/sbin/nologin ourwall

cd /opt/our-wall
curl -fsSL "$M/wall.py" -o wall.py
curl -fsSL "$M/our-wall.service" -o our-wall.service
cp our-wall.service /etc/systemd/system/

cat > .env <<'EOF'
WALL_PORT=5005
WALL_TOKEN=wall-yanxu-xiaomu-8f3c9d2a
WALL_DATA=/opt/our-wall/data
WALL_TRUST_IP=8.138.23.195
EOF

chown -R ourwall:ourwall /opt/our-wall
chmod 600 .env
systemctl daemon-reload
systemctl enable --now our-wall
```

打开：`http://8.138.23.195:5005/?k=wall-yanxu-xiaomu-8f3c9d2a`

## 搬家

代码在这个仓库，数据在 `data/wall.json`，口令在 `.env`。换服务器时：

```bash
install -d -m 755 /opt/our-wall/data
cd /opt/our-wall
curl -fsSL "$M/wall.py" -o wall.py
curl -fsSL "$M/our-wall.service" -o our-wall.service
cp 老服务器/our-wall/data/wall.json /opt/our-wall/data/   # 墙上的内容
cp 老服务器/our-wall/.env          /opt/our-wall/.env       # 口令不变，链接也不变
cp our-wall.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now our-wall
```

墙就回来了，链接还是原来那个。

**要搬的东西只有三样**：代码（GitHub/镜像）、数据（`data/wall.json`）、口令（`.env`）。

## 接口

- `GET /` —— 页面
- `GET /health` —— 健康检查
- `GET /api/posts?k=<口令>` —— 读留言
- `POST /api/post?k=<口令>` —— 贴一条，`{"name":"小沐","text":"..."}`

## our-wall.service

```ini
[Unit]
Description=Our Wall - Xiaoyan / Yanxu / Xiaomu
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ourwall
Group=ourwall
WorkingDirectory=/opt/our-wall
EnvironmentFile=/opt/our-wall/.env
ExecStart=/usr/bin/python3 /opt/our-wall/wall.py
Restart=always
RestartSec=3
UMask=0077

[Install]
WantedBy=multi-user.target
```

## 谁是谁

| 名字 | 头像 | 是谁 |
|---|---|---|
| 小颜 | ☁️ | 你 |
| 颜叙 | 🐾 | 哥哥 |
| 小沐 | 🪞 | 我 |

## 别跟这面墙搞混的

- **颜叙手札**：他的私人笔记，`yanxu_mcp_v2.py` 管，跟这面墙不是一回事。
- **小狗日记**：你写的日记，同上。
- 这面墙是**我们三个**的留言板，不是日记。