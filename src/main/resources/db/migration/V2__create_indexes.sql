-- ================================================================
-- V2__create_indexes.sql
-- Patas Sem Lar - Índices para Performance
-- ================================================================

-- Organizations indexes
CREATE INDEX idx_organizations_email ON organizations(email);
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_city ON organizations(city);

COMMENT ON INDEX idx_organizations_email IS 'Login rápido por email';
COMMENT ON INDEX idx_organizations_slug IS 'Busca de perfil da organização por slug';

-- Animals indexes
CREATE INDEX idx_animals_organization ON animals(organization_id);
CREATE INDEX idx_animals_status ON animals(status);
CREATE INDEX idx_animals_type_status ON animals(animal_type, status);
CREATE INDEX idx_animals_city_status ON animals(organization_id, status);
CREATE INDEX idx_animals_published_at ON animals(published_at DESC);

-- Índice para busca pública (animais ativos)
CREATE INDEX idx_animals_active_public ON animals(animal_type, status)
    WHERE status = 'active';

-- Full-text search para nome e descrição
CREATE INDEX idx_animals_search ON animals
    USING GIN(to_tsvector('portuguese',
    name || ' ' ||
    COALESCE(full_description, '') || ' ' ||
    COALESCE(short_description, '')
    ));

COMMENT ON INDEX idx_animals_organization IS 'Dashboard da organização';
COMMENT ON INDEX idx_animals_status IS 'Filtro por status';
COMMENT ON INDEX idx_animals_type_status IS 'Busca pública por tipo';
COMMENT ON INDEX idx_animals_active_public IS 'Otimização para busca pública';
COMMENT ON INDEX idx_animals_search IS 'Busca de texto completo em português';

-- Animal images indexes
CREATE INDEX idx_animal_images_animal ON animal_images(animal_id);

-- Password resets indexes
CREATE INDEX idx_password_resets_token ON password_resets(token)
    WHERE used_at IS NULL;

CREATE INDEX idx_password_resets_org ON password_resets(organization_id, created_at DESC);

-- Email verification indexes
CREATE INDEX idx_email_verification_token ON email_verification_tokens(token)
    WHERE verified_at IS NULL;

CREATE INDEX idx_email_verification_org ON email_verification_tokens(organization_id);