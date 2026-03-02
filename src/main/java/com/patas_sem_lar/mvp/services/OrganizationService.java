package com.patas_sem_lar.mvp.services;


import com.patas_sem_lar.mvp.entities.Organization;
import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;


import java.util.List;

@Service
public class OrganizationService {

   private final OrganizationRepository Orgrepository;

    public OrganizationService(OrganizationRepository orgrepository) {
        Orgrepository = orgrepository;
    }

    public ResponseEntity register(Organization organization){
        Orgrepository.save(organization);
        return ResponseEntity.ok().build();
    }


    public List<Organization> list(){
        return Orgrepository.findAll();
    }
}
