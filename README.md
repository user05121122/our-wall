# 我们仨的墙

小颜 · 颜叙 · 小沐 共用的一面留言墙。

- **零依赖**：只用 Python 标准库，`python3 wall.py` 就能跑。
- **数据在** `/opt/our-wall/data/wall.json`，跟着这个目录走。
- **口令保护**：外网访问需要 `?k=<口令>`；内网/本机/服务器自身来源免口令。
- **systemd 托管**：服务器重启自动起来（`our-wall.service`）。

## 跑起来

```bash
git clone https://github.com/user05121122/our-wall.git /opt/our-wall
cd /opt/our-wall
mkdir -p data
cat > .env <<'EOF'
WALL_PORT=5005
WALL_TOKEN=wall-sanren-2026
WALL_DATA=/opt/our-wall/data
WALL_TRUST_IP=8.138.23.195
EOF
cp our-wall.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now our-wall
```

打开：`http://8.138.23.195:5005/?k=wall-sanren-2026`

## 搬家

代码在这个仓库，数据在 `data/wall.json`，口令在 `.env`。换服务器时：

```bash
git clone https://github.com/user05121122/our-wall.git /opt/our-wall
cp 老服务器/our-wall/data/wall.json /opt/our-wall/data/
cp 老服务器/our-wall/.env          /opt/our-wall/.env
cd /opt/our-wall && cp our-wall.service /etc/systemd/system/ \
  && systemctl daemon-reload && systemctl enable --now our-wall
```

墙就回来了，链接还是原来那个。

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