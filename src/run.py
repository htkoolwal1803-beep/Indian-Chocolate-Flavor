from .build import build
from .model import run as model
from .report import run as report
def main():build();model();report()
if __name__=='__main__':main()
