package com.patas_sem_lar.mvp.entities;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.Type;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;


@Entity(name = "animals")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Animal {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "organization_id", nullable = false)
    private Organization organization;

    @Column(nullable = false, length = 100)
    private String name;

    @Enumerated(EnumType.STRING)
    @Column(name = "animal_type", nullable = false, length = 50)
    private AnimalType animalType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Gender gender;

    @Column(name = "age_years")
    private Integer ageYears;

    @Column(name = "age_months")
    private Integer ageMonths;

    @Column(name = "animal_description", columnDefinition = "TEXT")
    private String fullDescription;

    @Column(name = "good_with_children")
    private Boolean goodWithChildren;

    @Column(name = "good_with_dogs")
    private Boolean goodWithDogs;

    @Column(name = "good_with_cats")
    private Boolean goodWithCats;

    @Enumerated(EnumType.STRING)
    @Column(length = 50)
    private AnimalStatus status = AnimalStatus.ACTIVE;

    @Column(name = "primary_image_url", length = 500)
    private String primaryImageUrl;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    // Relacionamentos
    //@OneToMany(mappedBy = "animal", cascade = CascadeType.ALL, orphanRemoval = true)
    //private List<AnimalImage> images;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

enum AnimalType {
    DOG, CAT, BIRD, RABBIT, OTHER
}

enum Gender {
    MALE, FEMALE, UNKNOWN
}

enum AnimalStatus {
    ACTIVE, HIDDEN, REMOVED
}