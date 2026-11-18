import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(name, test_file):
    print("==== {} ====".format(name))
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tests" / test_file)],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    run("数据库连接检查", "test_db_connection.py")
    run("后端启动行为检查", "test_backend_startup.py")
    run("认证与配置检查", "test_auth_service.py")
    run("批改分数一致性检查", "test_grade_service.py")
    run("安全配置检查", "test_config_security.py")
    run("前后端交互检查", "test_front_backend_flow.py")
    print("全部检查通过")
