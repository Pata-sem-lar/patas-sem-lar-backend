package com.patas_sem_lar.mvp.repositories;

import com.patas_sem_lar.mvp.entities.Organization;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Optional;

public interface OrganizationRepository extends JpaRepository<Organization, Long> {

   UserDetails findByEmail(String email);
   boolean existsByEmail(String email);
}
