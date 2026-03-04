-- ================================================================
-- Esquema Inicial - Patas Sem Lar
-- ================================================================

-- Organizations table (com autenticação)
CREATE TABLE organizations
(
    id BIGSERIAL PRIMARY KEY,
    -- Autenticação (um login por organização)
    email             VARCHAR(255) UNIQUE NOT NULL,
    password_hash     VARCHAR(255)        NOT NULL,
    -- Informações básicas
    name              VARCHAR(255)        NOT NULL,
    phone             VARCHAR(20),
    website_url       VARCHAR(255),
    logo_url          VARCHAR(500),
    -- Endereço
    address_line1     VARCHAR(255),
    address_line2     VARCHAR(255),
    city              VARCHAR(100),
    state_province    VARCHAR(100),
    postal_code       VARCHAR(20),
    -- Detalhes
    registration_type VARCHAR(50) CHECK (registration_type IN
                                         ('NGO', 'Shelter', 'Rescue', 'Municipal', 'Private')),
    -- Auditoria
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    -- Futuras ideias de implementacao:
    -- Estatísticas
    -- total_animals_posted INTEGER   DEFAULT 0,
    -- latitude DECIMAL(10, 8),
    -- longitude DECIMAL(11, 8),
    -- email_verified BOOLEAN DEFAULT FALSE,
    -- is_verified BOOLEAN DEFAULT FALSE,
);

-- Animals table
CREATE TABLE animals
(
    id_animal BIGSERIAL PRIMARY KEY,
    organization_id    BIGINT       NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    name               VARCHAR(100) NOT NULL,
    animal_type        VARCHAR(50)  NOT NULL CHECK (animal_type IN ('dog', 'cat', 'bird', 'rabbit', 'other')),
    gender             VARCHAR(10)  NOT NULL CHECK (gender IN ('male', 'female', 'unknown')),
    age_years          INTEGER,
    age_months         INTEGER,
    short_description  VARCHAR(500),
    good_with_children BOOLEAN,
    good_with_dogs     BOOLEAN,
    good_with_cats     BOOLEAN,
    primary_image_url  VARCHAR(500),

    -- Ciclo de vida do Post
    status             VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'hidden', 'removed')),
    published_at       TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    removed_at         TIMESTAMP, -- Quando foi removido (auto ou manual)
    created_at         TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP   DEFAULT CURRENT_TIMESTAMP

    -- Para implementar depois:
    -- Métricas de engajamento (opcionais mas úteis)
    -- view_count          INTEGER     DEFAULT 0,
    -- contact_click_count INTEGER     DEFAULT 0,
    -- intake_date         DATE         NOT NULL,
    -- is_vaccinated BOOLEAN DEFAULT FALSE,
    -- is_neutered BOOLEAN DEFAULT FALSE,
    -- is_microchipped BOOLEAN DEFAULT FALSE,
);

-- Animal images table
CREATE TABLE animal_images
(
    id BIGSERIAL PRIMARY KEY,
    animal_id   BIGINT       NOT NULL REFERENCES animals (id_animal) ON DELETE CASCADE,
    image_url   VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    -- Para implementar depois:
    -- display_order INTEGER DEFAULT 0,
    -- is_primary BOOLEAN DEFAULT FALSE,
);

-- Descomentar quando incluir verificacao de conta
-- Password resets (apenas para organizations)
# CREATE TABLE password_resets
# (
#     id BIGSERIAL PRIMARY KEY,
#     organization_id BIGINT              NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
#     email           VARCHAR(255)        NOT NULL,
#     token           VARCHAR(255) UNIQUE NOT NULL,
#     expires_at      TIMESTAMP           NOT NULL,
#     used_at         TIMESTAMP,
#     created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#
#     CONSTRAINT valid_token_expiry CHECK (expires_at > created_at)
# );
#
# -- Email verification tokens (apenas para organizations)
# CREATE TABLE email_verification_tokens
# (
#     id BIGSERIAL PRIMARY KEY,
#     organization_id BIGINT              NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
#     email           VARCHAR(255)        NOT NULL,
#     token           VARCHAR(255) UNIQUE NOT NULL,
#     expires_at      TIMESTAMP           NOT NULL,
#     verified_at     TIMESTAMP,
#     created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );