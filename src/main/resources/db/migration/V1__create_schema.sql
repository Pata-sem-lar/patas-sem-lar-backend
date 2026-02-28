-- ================================================================
-- Esquema Inicial - Patas Sem Lar
-- ================================================================

-- Organizations table (com autenticação)
CREATE TABLE organizations
(
    id BIGSERIAL PRIMARY KEY,

    -- Autenticação (um login por organização)
    email                        VARCHAR(255) UNIQUE NOT NULL,
    password_hash                VARCHAR(255)        NOT NULL,
    last_login_at                TIMESTAMP,

    -- Informações básicas
    name                         VARCHAR(255)        NOT NULL,
    slug                         VARCHAR(255) UNIQUE NOT NULL,
    phone                        VARCHAR(20)         NOT NULL,
    website_url                  VARCHAR(255),
    logo_url                     VARCHAR(500),

    -- Endereço
    address_line1                VARCHAR(255)        NOT NULL,
    address_line2                VARCHAR(255),
    city                         VARCHAR(100)        NOT NULL,
    state_province               VARCHAR(100),
    postal_code                  VARCHAR(20)         NOT NULL,
    country                      VARCHAR(100) DEFAULT 'Portugal',

    -- Detalhes
    description                  TEXT,
    registration_type            VARCHAR(50) CHECK (registration_type IN
                                                    ('NGO', 'Shelter', 'Rescue', 'Municipal', 'Private')),
    adoption_process_description TEXT,

    -- Estatísticas
    total_animals_posted         INTEGER      DEFAULT 0,

    -- Auditoria
    created_at                   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at                   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP

    -- Para implementar depois:
    -- latitude DECIMAL(10, 8),
    -- longitude DECIMAL(11, 8),
    -- is_active BOOLEAN DEFAULT TRUE,
    -- email_verified BOOLEAN DEFAULT FALSE,

    -- is_verified BOOLEAN DEFAULT FALSE,
);

-- Animals table
CREATE TABLE animals
(
    id BIGSERIAL PRIMARY KEY,
    organization_id     BIGINT       NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,

    -- Informações básicas
    name                VARCHAR(100) NOT NULL,
    slug                VARCHAR(255) NOT NULL,
    animal_type         VARCHAR(50)  NOT NULL CHECK (animal_type IN ('dog', 'cat', 'bird', 'rabbit', 'other')),

    -- Físico
    gender              VARCHAR(10)  NOT NULL CHECK (gender IN ('male', 'female', 'unknown')),
    age_years           INTEGER,
    age_months          INTEGER,
    age_category        VARCHAR(20) CHECK (age_category IN ('puppy', 'kitten', 'young', 'adult', 'senior')),
    size                VARCHAR(20) CHECK (size IN ('small', 'medium', 'large', 'extra_large')),
    weight_kg           NUMERIC(5, 2),
    color               VARCHAR(100),

    -- Descrição
    short_description   VARCHAR(500),
    full_description    TEXT,
    -- personality_traits JSONB,
    special_needs       TEXT,

    -- Comportamento
    good_with_children  BOOLEAN,
    good_with_dogs      BOOLEAN,
    good_with_cats      BOOLEAN,
    house_trained       BOOLEAN,
    energy_level        VARCHAR(20) CHECK (energy_level IN ('low', 'medium', 'high', 'very_high')),

    -- Status e Datas (NECESSÁRIO para remoção automática/manual)
    status              VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'removed')),
    intake_date         DATE         NOT NULL,
    published_at        TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    removed_at          TIMESTAMP, -- Quando foi removido (auto ou manual)

    -- Mídia
    primary_image_url   VARCHAR(500),

    -- Métricas de engajamento (opcionais mas úteis)
    view_count          INTEGER     DEFAULT 0,
    contact_click_count INTEGER     DEFAULT 0,

    -- Auditoria
    created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_org_animal_slug UNIQUE (organization_id, slug)

    -- Para implementar depois:
    -- is_vaccinated BOOLEAN DEFAULT FALSE,
    -- is_neutered BOOLEAN DEFAULT FALSE,
    -- is_microchipped BOOLEAN DEFAULT FALSE,
);

-- Animal images table
CREATE TABLE animal_images
(
    id BIGSERIAL PRIMARY KEY,
    animal_id   BIGINT       NOT NULL REFERENCES animals (id) ON DELETE CASCADE,

    image_url   VARCHAR(500) NOT NULL,
    caption     TEXT,
    alt_text    VARCHAR(255),
    width       INTEGER,
    height      INTEGER,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    -- Para implementar depois:
    -- thumbnail_url VARCHAR(500),
    -- display_order INTEGER DEFAULT 0,
    -- is_primary BOOLEAN DEFAULT FALSE,
);

-- Password resets (apenas para organizations)
CREATE TABLE password_resets
(
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT              NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    email           VARCHAR(255)        NOT NULL,
    token           VARCHAR(255) UNIQUE NOT NULL,
    expires_at      TIMESTAMP           NOT NULL,
    used_at         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_token_expiry CHECK (expires_at > created_at)
);

-- Email verification tokens (apenas para organizations)
CREATE TABLE email_verification_tokens
(
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT              NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    email           VARCHAR(255)        NOT NULL,
    token           VARCHAR(255) UNIQUE NOT NULL,
    expires_at      TIMESTAMP           NOT NULL,
    verified_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);