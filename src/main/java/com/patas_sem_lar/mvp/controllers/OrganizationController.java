package com.patas_sem_lar.mvp.controllers;

import com.patas_sem_lar.mvp.entities.Organization;
import com.patas_sem_lar.mvp.services.OrganizationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/organization")
public class OrganizationController {

    @Autowired
    private OrganizationService Orgservice;

    @PostMapping
    public ResponseEntity register(@RequestBody Organization organization){
        Orgservice.register(organization);

        return ResponseEntity.ok().build();
    }

    @GetMapping
    public List<Organization> list(){
        return Orgservice.list();

    }
}
