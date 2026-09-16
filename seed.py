from db import initialize
from domain.services import seed_demo


if __name__ == "__main__":
    initialize()
    seed_demo()
    print("Banco HRMS inicializado com dados de demonstração.")
