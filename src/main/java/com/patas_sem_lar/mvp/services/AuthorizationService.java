package com.patas_sem_lar.mvp.services;


import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthorizationService implements UserDetailsService {

    private final OrganizationRepository repository;

    public AuthorizationService(OrganizationRepository repository) {
        this.repository = repository;
    }

    //Service para permitir que o Spring Security possa consultar o banco de dados //
    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {

        return repository.findByEmail(email);
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration configuration) throws Exception {
        return configuration.getAuthenticationManager();
    }

    //Método usado pelo Spring Security para usar o encode na password
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

}
