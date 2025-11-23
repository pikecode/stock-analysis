#!/bin/bash
# =================================
# Stock Analysis - 系统依赖安装
# =================================
# 支持: Ubuntu 20.04/22.04, Debian 11/12, CentOS 7/8
# 用法: sudo ./install-deps.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 root 权限运行: sudo $0${NC}"
    exit 1
fi

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Stock Analysis - 系统依赖安装           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo -e "${RED}无法检测操作系统${NC}"
    exit 1
fi

echo -e "${YELLOW}检测到系统: $OS $VERSION${NC}"
echo ""

# =================================
# Install based on OS
# =================================

install_ubuntu_debian() {
    echo -e "${YELLOW}[1/6] 更新软件包列表...${NC}"
    apt-get update

    echo -e "${YELLOW}[2/6] 安装基础依赖...${NC}"
    apt-get install -y \
        curl \
        wget \
        git \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        supervisor \
        nginx

    echo -e "${YELLOW}[3/6] 安装 Python 3.11...${NC}"
    if ! command -v python3.11 &> /dev/null; then
        apt-get install -y software-properties-common
        add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
        apt-get update
        apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
    fi
    echo -e "  ✓ Python $(python3.11 --version)"

    echo -e "${YELLOW}[4/6] 安装 Node.js 20.x...${NC}"
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
    fi
    echo -e "  ✓ Node.js $(node --version)"

    echo -e "${YELLOW}[5/6] 安装 PostgreSQL 15...${NC}"
    if ! command -v psql &> /dev/null; then
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
        wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
        apt-get update
        apt-get install -y postgresql-15
    fi
    systemctl enable postgresql
    systemctl start postgresql
    echo -e "  ✓ PostgreSQL $(psql --version | head -1)"

    echo -e "${YELLOW}[6/6] 安装 Redis...${NC}"
    if ! command -v redis-server &> /dev/null; then
        apt-get install -y redis-server
    fi
    systemctl enable redis-server
    systemctl start redis-server
    echo -e "  ✓ Redis $(redis-server --version | head -1)"
}

install_centos() {
    echo -e "${YELLOW}[1/6] 安装 EPEL 仓库...${NC}"
    yum install -y epel-release

    echo -e "${YELLOW}[2/6] 安装基础依赖...${NC}"
    yum install -y \
        curl \
        wget \
        git \
        gcc \
        gcc-c++ \
        make \
        postgresql-devel \
        libffi-devel \
        openssl-devel \
        supervisor \
        nginx

    echo -e "${YELLOW}[3/6] 安装 Python 3.11...${NC}"
    if ! command -v python3.11 &> /dev/null; then
        yum install -y python3.11 python3.11-devel python3-pip
    fi

    echo -e "${YELLOW}[4/6] 安装 Node.js 20.x...${NC}"
    if ! command -v node &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
        yum install -y nodejs
    fi

    echo -e "${YELLOW}[5/6] 安装 PostgreSQL 15...${NC}"
    if ! command -v psql &> /dev/null; then
        yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-${VERSION%%.*}-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        yum install -y postgresql15-server postgresql15
        /usr/pgsql-15/bin/postgresql-15-setup initdb
    fi
    systemctl enable postgresql-15
    systemctl start postgresql-15

    echo -e "${YELLOW}[6/6] 安装 Redis...${NC}"
    if ! command -v redis-server &> /dev/null; then
        yum install -y redis
    fi
    systemctl enable redis
    systemctl start redis
}

# Run installation
case $OS in
    ubuntu|debian)
        install_ubuntu_debian
        ;;
    centos|rhel|rocky|almalinux)
        install_centos
        ;;
    *)
        echo -e "${RED}不支持的操作系统: $OS${NC}"
        echo "支持的系统: Ubuntu, Debian, CentOS, RHEL, Rocky, AlmaLinux"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  系统依赖安装完成！${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo "已安装:"
echo "  - Python 3.11"
echo "  - Node.js 20.x"
echo "  - PostgreSQL 15"
echo "  - Redis"
echo "  - Nginx"
echo "  - Supervisor"
echo ""
echo -e "${YELLOW}下一步: 运行部署脚本 ./deploy.sh${NC}"
