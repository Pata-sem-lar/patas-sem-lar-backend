-- ================================================================
-- V3__create_triggers.sql
-- Patas Sem Lar - Triggers e Funções
-- ================================================================

-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_modified_column IS 'Atualiza automaticamente o campo updated_at';

-- Trigger para organizations
CREATE TRIGGER trg_organizations_updated
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Trigger para animals
CREATE TRIGGER trg_animals_updated
    BEFORE UPDATE ON animals
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Função para incrementar contador de animais postados
CREATE OR REPLACE FUNCTION increment_organization_animal_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
UPDATE organizations
SET total_animals_posted = total_animals_posted + 1
WHERE id = NEW.organization_id;
ELSIF TG_OP = 'DELETE' THEN
UPDATE organizations
SET total_animals_posted = GREATEST(total_animals_posted - 1, 0)
WHERE id = OLD.organization_id;
END IF;

RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION increment_organization_animal_count IS 'Mantém contagem de animais postados por organização';

-- Trigger para contar animais
CREATE TRIGGER trg_update_org_animal_count
    AFTER INSERT OR DELETE ON animals
    FOR EACH ROW
EXECUTE FUNCTION increment_organization_animal_count();