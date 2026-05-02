"""
Testa o repository de subjects.
Roda com: python -m scripts.test_subjects
"""

from src.repositories import subjects
from src.db import close_pool


def main() -> None:
    print("=== Testando repository de subjects ===\n")

    # 1. Cria duas matérias de categorias diferentes
    print("1. Criando matérias...")
    calc = subjects.get_or_create("Cálculo I", category="faculdade")
    print(f"   Criada: {calc}")

    react = subjects.get_or_create("React", category="pessoal")
    print(f"   Criada: {react}")

    # 2. Tenta criar a mesma de novo (deve retornar a existente, sem erro)
    print("\n2. Chamando get_or_create de novo (deve retornar existente)...")
    calc_again = subjects.get_or_create("Cálculo I")
    assert calc_again["id"] == calc["id"], "Deveria ter o mesmo id!"
    print(f"   OK, mesmo id: {calc_again['id']}")

    # 3. Busca por id
    print("\n3. Buscando por id...")
    found = subjects.get_by_id(calc["id"])
    print(f"   {found}")

    # 4. Busca por id que não existe
    print("\n4. Buscando id inexistente...")
    not_found = subjects.get_by_id(999999)
    print(f"   Resultado: {not_found}")  # deve ser None

    # 5. Lista todas
    print("\n5. Listando todas:")
    for s in subjects.list_all():
        print(f"   - [{s['category']}] {s['name']} (id={s['id']})")

    # 6. Lista só pessoais
    print("\n6. Listando apenas 'pessoal':")
    for s in subjects.list_all(category="pessoal"):
        print(f"   - {s['name']}")

    close_pool()
    print("\n✅ Todos os testes passaram!")


if __name__ == "__main__":
    main()