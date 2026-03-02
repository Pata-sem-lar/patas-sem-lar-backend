package com.patas_sem_lar.mvp.springsecurity;


import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTCreationException;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.patas_sem_lar.mvp.entities.Organization;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;

@Service
public class TokenService {

    //Senha secreta para a criação do Token no JWT
    @Value("${api.security.token.secret}")
    private String secret;

    //Geração do Token - Encripta os dados//
    public String TokenGenerate(Organization organization){
        try{
            Algorithm algorithm = Algorithm.HMAC256(secret);
            String token = JWT.create()
                    .withIssuer("patas-api")
                    .withSubject(organization.getEmail())
                    .withExpiresAt(genExpirationDate())
                    .sign(algorithm);
            return token;
        } catch (JWTCreationException exeption){
            throw new RuntimeException("Erro geração token", exeption);

        }
    }

    //Faz a consulta do Token//
    public String validateToken(String token){
        try{
            Algorithm algorithm = Algorithm.HMAC256(secret);
            return JWT.require(algorithm)
                    .withIssuer("patas-api")
                    .build()
                    .verify(token)
                    .getSubject();
        }catch (JWTVerificationException exception){
            return null;

        }
    }
    private Instant genExpirationDate(){
        return LocalDateTime.now().plusHours(1).toInstant(ZoneOffset.of("+00:00"));
    }
}
