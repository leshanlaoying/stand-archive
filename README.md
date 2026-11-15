# 看台档案

用 Django 构建的球迷赛后复盘档案馆。公开浏览比赛、关键时刻和复盘；注册用户可评分、写复盘、记录时刻、赞同他人观点；管理员可管理比赛和内容。

## 本地运行

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

打开 http://127.0.0.1:8000 ，管理员在 `/admin/` 添加比赛。生产环境必须设置随机 `SECRET_KEY`、`DATABASE_URL`，并使用 HTTPS。SQLite 仅用于本地开发。

## 免费部署：Render + Neon

1. 将整个项目推送到你自己的 GitHub 仓库。
2. 在 Neon 创建免费 PostgreSQL 项目，选择与 Render 地区接近的区域，复制带 `sslmode=require` 的连接串。**连接串含密码，不能提交到 GitHub。**
3. 在 Render 选择 **New > Blueprint**，连接仓库，应用 `render.yaml`。创建时将 Neon 连接串填入 `DATABASE_URL`。首次部署会自动迁移数据库并创建用户名为 `archive_admin` 的管理员；密码由 Render 随机生成，可由账号所有者在 Web Service 的 **Environment** 页面查看。首次登录后台并改成自己的密码后，可删除 Render 中的 `INITIAL_ADMIN_PASSWORD` 环境变量；后续部署不会重置管理员密码。
4. 部署成功后获得 `*.onrender.com` 公开网址。如已有自己的域名，在 Web Service 的 **Custom Domains** 中添加，并按提示设置 DNS。将域名加入 `ALLOWED_HOSTS`，将 `https://域名` 加入 `CSRF_TRUSTED_ORIGINS` 环境变量。

Render 免费网站在空闲 15 分钟后休眠，下一次访问可能等待约一分钟；Neon 免费数据库独立保存数据。`main` 分支通过 GitHub Actions 检查后自动部署。网页代码更新不会删除 PostgreSQL 数据。结构变动通过 Django migration 前向升级。重要数据仍应定期导出备份；回退网页版本并不会自动回退数据库结构。

如果希望网站不休眠，将 `render.yaml` 中的 `plan: free` 改成 `plan: 0.5c-512mb` 并在 Render 同步 Blueprint。数据库可继续用 Neon 免费套餐，无需迁移已有数据。

## 管理与后续迭代

- `/admin/`：添加比赛、修改比分、设置首页精选、管理复盘与关键时刻。
- 每个用户每场比赛可提交一份复盘，并可随时修改；所有账号均可查看公开内容。
- 关键时刻由用户共同记录，管理员可在后台处理不当内容。
- 当前版本附带三场经典比赛作为开馆内容；后续比赛和比分由管理员录入。暂不依赖第三方赛果 API 的价格、覆盖和授权。示例赛果核对自 [FIFA 2022 决赛](https://www.fifa.com/es/articles/argentina-le-gano-por-penales-a-francia-y-se-consagro-campeon-del-mundo)、[UEFA 2005 决赛](https://www.uefa.com/uefachampionsleague/news/0253-0d7b89fe7b7f-c91716d11bdf-1000--2004-05-liverpool-belief-defies-milan/) 和 [FIFA 2014 半决赛](https://inside.fifa.com/tournaments/mens/worldcup/qatar2022/news/ten-standout-world-cup-matches-from-the-past-decade)。

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | Neon PostgreSQL 连接串；本地为空时使用 SQLite |
| `SECRET_KEY` | Django 密钥，正式环境由 Render 生成 |
| `DEBUG` | 本地调试可设为 `true`，正式环境为 `false` |
| `ALLOWED_HOSTS` | 逗号分隔的自定义域名 |
| `CSRF_TRUSTED_ORIGINS` | 逗号分隔的完整 HTTPS 来源 |
| `INITIAL_ADMIN_USERNAME` / `INITIAL_ADMIN_PASSWORD` | 用户名为 `archive_admin`，初始密码由 Render 生成；首次登录并改密后可删除密码环境变量 |
