package com.patas_sem_lar.mvp.controllers;


import com.patas_sem_lar.mvp.dto.AuthenticationDTO;
import com.patas_sem_lar.mvp.dto.RegisterDTO;
import com.patas_sem_lar.mvp.entities.Organization;
import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthenticationController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private OrganizationRepository repository;

    @GetMapping("/login")
    public ResponseEntity login(@RequestBody AuthenticationDTO data){
    var usernamePassword = new UsernamePasswordAuthenticationToken(data.email(), data.password_hash());
    var auth = this.authenticationManager.authenticate(usernamePassword);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/register")
    public ResponseEntity register(@RequestBody RegisterDTO dto){
        if(this.repository.findByEmail(dto.email()) != null){
            return  ResponseEntity.badRequest().build();
        }
        String passwordEncript = new BCryptPasswordEncoder().encode(dto.password_hash());

        Organization organization = new Organization(dto.email(), passwordEncript, dto.postalCode(), dto.slug(), dto.phone(), dto.name(), dto.city(), dto.addressLine1());
        this.repository.save(organization);

        return ResponseEntity.ok().build();
    }



}
