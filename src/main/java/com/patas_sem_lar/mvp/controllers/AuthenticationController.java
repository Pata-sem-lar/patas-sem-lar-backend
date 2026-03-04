package com.patas_sem_lar.mvp.controllers;


import com.patas_sem_lar.mvp.dto.AuthenticationDTO;
import com.patas_sem_lar.mvp.dto.RegisterDTO;
import com.patas_sem_lar.mvp.dto.TokenResponse;
import com.patas_sem_lar.mvp.entities.Organization;
import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import com.patas_sem_lar.mvp.services.OrganizationService;
import com.patas_sem_lar.mvp.springsecurity.TokenService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthenticationController {
    private final AuthenticationManager authenticationManager;
    private final OrganizationRepository orgRepository;
    private final TokenService tokenService;
    private final OrganizationService organizationService;

    @PostMapping("/login")
    public ResponseEntity login(@Valid @RequestBody AuthenticationDTO dto) {
        return organizationService.login(dto);
    }

    @PostMapping("/register")
    public ResponseEntity register(@Valid @RequestBody RegisterDTO dto) {
        return organizationService.register(dto);
    }

    @GetMapping("/list")
    public List<Organization> list() {
        return orgRepository.findAll();
    }

    @GetMapping("/teste")
    public String teste() {
        return "hello, world";
    }
}
