package com.patas_sem_lar.mvp.services;


import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class AutorizationService implements UserDetailsService {

    @Autowired
    OrganizationRepository repostory;


    //Service para permitir que o Spring Security possa consultar o banco de dados //
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return repostory.findByName(username);
    }
}
