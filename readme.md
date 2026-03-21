# Dress Select 智能穿搭系统 - 核心数据库

本环境包含了 Dress Select 系统所需的所有表结构、服装属性标签以及多模态特征向量（CLIP + DINOv2 ATF Super Vectors）。

## 🛠️ 前置要求
请确保您的电脑上已经安装了以下环境：
- [Docker](https://www.docker.com/products/docker-desktop)
- Docker Compose (通常随 Docker Desktop 一同安装)

## 🚀 快速启动指南

1. **打开终端 (Terminal / 命令提示符)**
   进入到当前包含 `docker_compose.yml` 的文件夹目录。

2. **一键启动数据库**
   在终端中运行以下命令：
   ```bash
   docker_compose up -d