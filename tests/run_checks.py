import subprocess
import sys


def run(name, cmd):
    print("==== {} ====".format(name))
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    run("数据库连接检查", "python tests\\test_db_connection.py")
    run("前后端交互检查", "python tests\\test_front_backend_flow.py")
    print("全部检查通过")
