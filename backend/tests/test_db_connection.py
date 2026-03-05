"""
Testes de integração com o banco Supabase.
Requer variáveis de ambiente reais configuradas em .env
"""
import pytest


def test_plans_seeded():
    """Verifica que os 3 planos foram inseridos pela migration."""
    from db.client import supabase
    result = supabase.table("plans").select("name").execute()
    names = {row["name"] for row in result.data}
    assert names == {"basic", "pro", "segment"}, f"Planos inesperados: {names}"


def test_core_tables_exist():
    """Verifica que todas as tabelas core existem e são consultáveis."""
    from db.client import supabase
    tables = ["plans", "tenants", "users", "whatsapp_instances",
              "agents", "contacts", "conversations", "messages"]
    for table in tables:
        result = supabase.table(table).select("id").limit(1).execute()
        # Se a tabela não existe, isso levanta uma exceção
        assert result is not None, f"Tabela {table} não acessível"


def test_tenant_crud():
    """Cria um tenant de teste e confirma que pode ser consultado e deletado."""
    from db.client import supabase

    # Pega o plano 'basic'
    plan = supabase.table("plans").select("id").eq("name", "basic").single().execute()
    assert plan.data, "Plano 'basic' não encontrado"

    # Cria tenant de teste
    tenant = supabase.table("tenants").insert({
        "name": "Tenant Teste DB",
        "slug": "tenant-teste-db-001",
        "plan_id": plan.data["id"]
    }).execute()
    assert tenant.data, "Falha ao criar tenant"
    tenant_id = tenant.data[0]["id"]

    # Consulta de volta
    fetched = supabase.table("tenants").select("*").eq("id", tenant_id).single().execute()
    assert fetched.data["slug"] == "tenant-teste-db-001"

    # Limpeza
    supabase.table("tenants").delete().eq("id", tenant_id).execute()
