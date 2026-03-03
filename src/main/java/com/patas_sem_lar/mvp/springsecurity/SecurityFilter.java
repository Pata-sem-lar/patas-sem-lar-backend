package com.patas_sem_lar.mvp.springsecurity;

import com.patas_sem_lar.mvp.repositories.OrganizationRepository;
import com.patas_sem_lar.mvp.services.OrganizationService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.context.SecurityContextHolderFilter;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class SecurityFilter extends OncePerRequestFilter {

    @Autowired
    private  TokenService tokenService;

    @Autowired
    OrganizationRepository organizationRepository;



    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        var token = this.recoverToken(request);
        if(token != null){

            //Extrai o usuário do Token
            var subject = tokenService.validateToken(token);

            //procura o Organização no banco de dados.
            UserDetails organization = organizationRepository.findByEmail(subject);

            var authentication = new UsernamePasswordAuthenticationToken(organization, null, organization.getAuthorities());

            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
        //chama o proximo Filtro
        filterChain.doFilter(request, response);

    }
    public String recoverToken(HttpServletRequest request){
        var authHeader = request.getHeader("Autorization");
        if(authHeader == null){
            return null;
        }
        return authHeader.replace("Bearer ", "");
    }
}
