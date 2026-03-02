package com.patas_sem_lar.mvp.entities;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.jspecify.annotations.Nullable;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

@Entity
@Table(name = "organizations")
@Data
@NoArgsConstructor
public class Organization implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String password_hash;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false, length = 20)
    private String phone;

    @Column(name = "website_url")
    private String websiteUrl;

    @Column(name = "address_line1", nullable = false)
    private String addressLine1;

    @Column(name = "address_line2")
    private String addressLine2;

    @Column(nullable = false, length = 100)
    private String city;

    @Column(name = "state_province", length = 100)
    private String stateProvince;

    // TODO: Incluir funcionalidade para verificar postalCode correto
    @Column(name = "postal_code", nullable = false, length = 20)
    private String postalCode;

    @Column(length = 100)
    private String country = "Portugal";

    /*
    @Column(precision = 10, scale = 8)
    private BigDecimal latitude;
    @Column(precision = 11, scale = 8)
    private BigDecimal longitude;
    */

    @Column(columnDefinition = "TEXT")
    private String description;

    // TODO: Incluir link para a logo da associacao
    @Column(name = "logo_url", length = 500)
    private String logoUrl;

    @Enumerated(EnumType.STRING)
    @Column(name = "registration_type", length = 50)
    private RegistrationType registrationType;

    @Column(name = "adoption_process_description", columnDefinition = "TEXT")
    private String adoptionProcessDescription;

    @Column(name = "total_animals_posted")
    private Integer totalAnimalsPosted = 0;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // Relacionamentos
    @OneToMany(mappedBy = "organization", cascade = CascadeType.ALL)
    private List<Animal> animals;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of();
    }

    //Métodos do UserDetails para validação //

    @Override
    public @Nullable String getPassword() {
        return "";
    }

    @Override
    public String getUsername() {
        return email;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }
}

enum RegistrationType {
    NGO, SHELTER, RESCUE, MUNICIPAL, PRIVATE
}
