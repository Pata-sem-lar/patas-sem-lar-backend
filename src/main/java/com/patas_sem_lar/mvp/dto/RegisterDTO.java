package com.patas_sem_lar.mvp.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegisterDTO(
        @NotBlank(message = "Email é obrigatório")
        @Email(message = "Email inválido")
        String email,
        @NotBlank
        @Size(min = 8, message = "A palavra-passe deve ter no mínimo 8 caracteres")
        String password,
        String name,
        String slug,
        String phone,
        String addressLine1,
        String city,
        String postalCode) {
}
