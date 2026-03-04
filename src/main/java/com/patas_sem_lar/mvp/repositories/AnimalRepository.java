package com.patas_sem_lar.mvp.repositories;

import com.patas_sem_lar.mvp.entities.Animal;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AnimalRepository extends JpaRepository<Animal, Long> {

    // Spring Data JPA auto gera automaticamente a implementacao desses metodos
    List<Animal> findByStatus(String status);

    List<Animal> findByAnimalTypeAndStatus(String animalType, String status);

    List<Animal> findByOrganizationId(Long organizationId);

    // Custom query
    @Query("SELECT ani FROM animals ani WHERE ani.status = 'ACTIVE'")
    List<Animal> findAvailableAnimals();

    // Query with parameters
    @Query("SELECT a FROM animals a WHERE a.animalType = :type AND a.organization.city = :city AND a.status = 'ACTIVE'")
    List<Animal> findByTypeAndCity(@Param("type") String type, @Param("city") String city);
}