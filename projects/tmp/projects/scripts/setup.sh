# 初始化目录
if [ "$COZE_PROJECT_ENV" = "DEV" ]; then
  if [ ! -d "${COZE_WORKSPACE_PATH}/assets" ]; then
    mkdir -p "${COZE_WORKSPACE_PATH}/assets"
  fi
fi

# 安装Python三方包依赖
pip install -r requirements.txt

pip install -U "coze-coding-dev-sdk>=0.5.0,<1.0"
pip install -U "coze-coding-utils>=0.1.11,<1.0"

# 安装系统依赖
