from distutils.core import setup


setup(
    name="smart_sauna_map",
    version="1.0",
    description="smart_sauna_map の backend",
    author="siida36",
    packages=["smart_sauna_map"],
    package_dir={
        "smart_sauna_map": "src/smart_sauna_map",
    },
    package_data={'smart_sauna_map': [
    ]},
)
