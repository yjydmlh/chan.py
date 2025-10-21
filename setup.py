from setuptools import setup, find_packages

# 读取requirements文件
def read_requirements():
    with open("Script/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chan-py",
    version="1.0.0",
    author="Vespa314",
    description="缠论技术分析框架",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    include_package_data=True,
)
