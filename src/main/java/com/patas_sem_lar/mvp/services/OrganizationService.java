package com.patas_sem_lar.mvp.services;


import com.patas_sem_lar.mvp.dto.AuthenticationDTO;
import com.patas_sem_lar.mvp.dto.RegisterDTO;
import com.patas_sem_lar.mvp.dto.TokenResponse;
import com.patas_sem_lar.mvp.entities.Organization;
import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import com.patas_sem_lar.mvp.springsecurity.TokenService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;


import java.util.List;

@Service
@RequiredArgsConstructor
public class OrganizationService {

    private final OrganizationRepository orgRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final TokenService tokenService;

    public ResponseEntity<Void> register(RegisterDTO dto) {
        if (orgRepository.findByEmail(dto.email()) != null) {
            return ResponseEntity.badRequest().build();
        }

        String passwordHash = passwordEncoder.encode(dto.password());
        orgRepository.save(new Organization(dto, passwordHash));

        return ResponseEntity.ok().build();
    }

    public ResponseEntity<TokenResponse> login(AuthenticationDTO dto) {
        var usernamePassword = new UsernamePasswordAuthenticationToken(dto.email(), dto.password());
        var auth = authenticationManager.authenticate(usernamePassword);
        var token = tokenService.generateToken((Organization) auth.getPrincipal());

        return ResponseEntity.ok(new TokenResponse(token));
    }

    // TODO: alterar os dados retornados aqui para um DTO onde nao retorne dados sensiveis
    public List<Organization> list() {
        return orgRepository.findAll();
    }
}
