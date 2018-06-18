class PiPUpgrader:
    def __init__(self, file: str):
        self.__file = file

    def upgradePackages(self):
        import subprocess
        with open(self.__file, 'r') as f:
            requirements = f.read().splitlines()
        for requirement in requirements:
            subprocess.run(("pip install -U " + requirement).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
